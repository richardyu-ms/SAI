# Copyright (c) 2021 Microsoft Open Technologies, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
#    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
#    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
#    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
#
#    See the Apache Version 2.0 License for specific language governing
#    permissions and limitations under the License.
#
#    Microsoft would like to thank the following companies for their review and
#    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
#    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
#
#


from ipaddress import ip_address
from sai_test_base import T0TestBase
from sai_thrift.sai_headers import *
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from sai_utils import *
import pdb

class L2TunnelTest(T0TestBase):
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

        self.oport = self.port_list[24]
        self.oport_dev = self.dev_port_list[24]
        self.uport = self.port_list[25]
        self.uport_dev = self.dev_port_list[25]

        self.vni = 1000
        self.tun_ip = "10.10.10.1"
        self.tun_ipv6 = "2001:0db8::10:1"
        self.lpb_ip = "10.10.10.2"
        self.lpb_ipv6 = "2001:0db8::10:10"
        self.vm_ip = "100.100.1.1"
        self.vm_ipv6 = "2001:0db8::100:1"
        self.customer_ip = "100.100.2.1"
        self.customer_ipv6 = "2001:0db8::100:2"
        self.customer2_ip = "100.200.3.4"
        self.inner_dmac = "00:11:11:11:11:11"
        self.customer_mac = "00:22:22:22:22:22"
        self.customer2_mac = "00:22:22:22:22:55"
        self.unbor_mac = "00:33:33:33:33:33"
        self.ovlan_no = 50

        # underlay configuration
        self.uvrf = sai_thrift_create_virtual_router(self.client)

        # overlay configuraion
        self.ovrf = sai_thrift_create_virtual_router(self.client)

        #Lpbks
        self.ulpbk_rif = sai_thrift_create_router_interface(self.client, type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK, virtual_router_id=self.uvrf)
        self.olpbk_rif = sai_thrift_create_router_interface(self.client, type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK, virtual_router_id=self.ovrf)

        #rifs
        self.urif = sai_thrift_create_router_interface(self.client, type=SAI_ROUTER_INTERFACE_TYPE_PORT, virtual_router_id=self.uvrf, port_id=self.uport)
        self.orif = sai_thrift_create_router_interface(self.client, type=SAI_ROUTER_INTERFACE_TYPE_PORT, virtual_router_id=self.ovrf, port_id=self.oport)

        #underlay route
        self.unbor = sai_thrift_neighbor_entry_t(rif_id=self.urif, ip_address=sai_ipaddress(self.tun_ip))
        sai_thrift_create_neighbor_entry(self.client, self.unbor, dst_mac_address=self.unbor_mac, no_host_route=True)
        self.unhop = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(self.tun_ip), router_interface_id=self.urif, type=SAI_NEXT_HOP_TYPE_IP)
        self.uroute = sai_thrift_route_entry_t(vr_id=self.uvrf,  destination=sai_ipprefix(self.tun_ip + '/32'))
        sai_thrift_create_route_entry(self.client, self.uroute, next_hop_id=self.unhop)

        #Overlay route
        self.onbor = sai_thrift_neighbor_entry_t(rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ip))
        sai_thrift_create_neighbor_entry(self.client, self.onbor, dst_mac_address=self.unbor_mac, no_host_route=True)
        self.onhp =  sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(self.customer_ip), router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)
        self.oroute = sai_thrift_route_entry_t(vr_id=self.ovrf, destination=sai_ipprefix(self.customer_ip + '/32'))
        sai_thrift_create_route_entry(self.client, self.oroute, next_hop_id=self.onhp)


        tunnel_type = SAI_TUNNEL_TYPE_VXLAN
        term_type = SAI_TUNNEL_TERM_TABLE_ENTRY_TYPE_P2P
        ttl_mode = SAI_TUNNEL_TTL_MODE_PIPE_MODEL
        decap_tunnel_map_entry_vrf_exists = False
        decap_tunnel_map_entry_vlan_exists = False

        #overlay vlan and member, and the mac for the member port     
        orif_vlan = sai_thrift_create_router_interface(self.client, type=SAI_ROUTER_INTERFACE_TYPE_VLAN, virtual_router_id=self.ovrf, vlan_id=self.vlans[10].vlan_oid)
        ovlan_member = sai_thrift_create_vlan_member(self.client, vlan_id=self.vlans[10].vlan_oid, bridge_port_id=self.bridge_port_list[21], vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_TAGGED)
        mac2_entry = sai_thrift_fdb_entry_t(switch_id=self.switch_id, mac_address=self.customer2_mac, bv_id=self.vlans[10].vlan_oid)
        sai_thrift_create_fdb_entry(self.client, mac2_entry, type=SAI_FDB_ENTRY_TYPE_STATIC, bridge_port_id=self.bridge_port_list[21])

        # decap and encap vlan mappers
        encap_tunnel_map = sai_thrift_create_tunnel_map(self.client, type=SAI_TUNNEL_MAP_TYPE_VIRTUAL_ROUTER_ID_TO_VNI)

        decap_tunnel_map_vrf = sai_thrift_create_tunnel_map(self.client, type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID)

        decap_tunnel_map_vlan = sai_thrift_create_tunnel_map(self.client, type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID)

        encap_tunnel_map_entry = sai_thrift_create_tunnel_map_entry(
            self.client,
            tunnel_map=encap_tunnel_map,
            tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VIRTUAL_ROUTER_ID_TO_VNI,
            virtual_router_id_key=self.ovrf,
            vni_id_value=self.vni)

        decap_tunnel_map_entry_vrf = sai_thrift_create_tunnel_map_entry(
            self.client,
            tunnel_map=decap_tunnel_map_vrf,
            tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID,
            virtual_router_id_value=self.ovrf,
            vni_id_key=self.vni)

        encap_maps = sai_thrift_object_list_t(count=1, idlist=[encap_tunnel_map])
        decap_maps = sai_thrift_object_list_t(count=2, idlist=[decap_tunnel_map_vrf, decap_tunnel_map_vlan])

        #Create tunnel
        tunnel = sai_thrift_create_tunnel(
                self.client,
                type=tunnel_type,
                encap_src_ip=sai_ipaddress(self.lpb_ip),
                encap_mappers=encap_maps,
                decap_mappers=decap_maps,
                encap_ttl_mode=ttl_mode,
                decap_ttl_mode=ttl_mode,
                underlay_interface=self.ulpbk_rif)
        self.assertNotEqual(tunnel, 0, "Failed to create tunnel with dual decap mappers")

        self.tunnel_term = sai_thrift_create_tunnel_term_table_entry(
                self.client,
                tunnel_type=tunnel_type,
                vr_id=self.uvrf,
                action_tunnel_id=tunnel,
                type=term_type,
                dst_ip=sai_ipaddress(self.lpb_ip))

        self.tunnel_nhop = sai_thrift_create_next_hop(
            self.client,
            type=SAI_NEXT_HOP_TYPE_TUNNEL_ENCAP,
            tunnel_id=tunnel,
            ip=sai_ipaddress(self.tun_ip),
            tunnel_mac=self.inner_dmac,
            tunnel_vni=self.vni)
        self.vm_route = sai_thrift_route_entry_t(
                vr_id=self.ovrf, destination=sai_ipprefix(self.vm_ip + '/32'))
        sai_thrift_create_route_entry(self.client,
                                      self.vm_route,
                                      next_hop_id=self.tunnel_nhop)

    def runTest(self):
        sai_thrift_create_route_entry(self.client,
                                      self.vm_route,
                                      next_hop_id=self.tunnel_nhop)

        l3_pkt = simple_udp_packet(eth_dst=self.customer_mac,
                                    eth_src=ROUTER_MAC,
                                    ip_dst=self.customer_ip,
                                    ip_src=self.vm_ip,
                                    ip_id=108,
                                    ip_ttl=63)
        l3_inner_pkt = simple_udp_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.inner_dmac,
                                            ip_dst=self.customer_ip,
                                            ip_src=self.vm_ip,
                                            ip_id=108,
                                            ip_ttl=64)
        l3_vxlan_pkt = simple_vxlan_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.unbor_mac,
                                            ip_dst=self.lpb_ip,
                                            ip_src=self.tun_ip,
                                            ip_id=0,
                                            ip_ttl=64,
                                            ip_flags=0x2,
                                            udp_sport=11638,
                                            with_udp_chksum=False,
                                            vxlan_vni=self.vni,
                                            inner_frame=l3_inner_pkt)     

        pkt_len = 104
        dec = 4
        l2_pkt = simple_udp_packet(eth_dst=self.customer2_mac,
                                    eth_src=self.inner_dmac,
                                    dl_vlan_enable=True,
                                    vlan_vid=self.ovlan_no,
                                    ip_dst=self.customer2_ip,
                                    ip_src=self.vm_ip,
                                    ip_id=108,
                                    ip_ttl=64,
                                    pktlen=pkt_len)
        l2_inner_pkt = simple_udp_packet(eth_dst=self.customer2_mac,
                                            eth_src=self.inner_dmac,
                                            ip_dst=self.customer2_ip,
                                            ip_src=self.vm_ip,
                                            ip_id=108,
                                            ip_ttl=64,
                                            pktlen=pkt_len - dec)
        l2_vxlan_pkt = simple_vxlan_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.unbor_mac,
                                            ip_dst=self.lpb_ip,
                                            ip_src=self.tun_ip,
                                            ip_id=0,
                                            ip_ttl=64,
                                            ip_flags=0x2,
                                            udp_sport=11638,
                                            with_udp_chksum=False,
                                            vxlan_vni=self.vni,
                                            inner_frame=l2_inner_pkt)

        print("Sending VxLan packet to tunnel with dual decap mappers")
        pdb.set_trace()
        send_packet(self, self.uport_dev, l3_vxlan_pkt)
        verify_packet(self, l3_pkt, self.oport_dev)
        print("\tOK")


class L2TunnelTest2(T0TestBase):
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

        self.oport =  self.port_list[24]
        self.oport_dev = self.dev_port_list[24]
        self.uport = self.port_list[25]
        self.uport_dev = self.dev_port_list[25]

        self.vni = 1000
        self.tun_ip = "10.10.10.1"
        self.tun_ipv6 = "2001:0db8::10:1"
        self.lpb_ip = "10.10.10.2"
        self.lpb_ipv6 = "2001:0db8::10:10"
        self.vm_ip = "100.100.1.1"
        self.vm_ipv6 = "2001:0db8::100:1"
        self.customer_ip = "100.100.2.1"
        self.customer_ipv6 = "2001:0db8::100:2"
        self.customer2_ip = "100.200.3.4"
        self.inner_dmac = "00:11:11:11:11:11"
        self.customer_mac = "00:22:22:22:22:22"
        self.customer2_mac = "00:22:22:22:22:55"
        self.unbor_mac = "00:33:33:33:33:33"
        self.ovlan_no = 50

        # underlay configuration
        self.uvrf = sai_thrift_create_virtual_router(self.client)

        # overlay configuraion
        self.ovrf = sai_thrift_create_virtual_router(self.client)

        # underlay loopback RIF for tunnel
        self.urif_lpb = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK,
            virtual_router_id=self.uvrf)

        self.orif_lpb = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK,
            virtual_router_id=self.ovrf)

        self.urif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.uvrf,
            port_id=self.uport)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        # route to tunnel
        self.unbor = sai_thrift_neighbor_entry_t(
            rif_id=self.urif, ip_address=sai_ipaddress(self.tun_ip))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.unbor,
                                         dst_mac_address=self.unbor_mac,
                                         no_host_route=True)

        self.unbor_v6 = sai_thrift_neighbor_entry_t(
            rif_id=self.urif, ip_address=sai_ipaddress(self.tun_ipv6))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.unbor_v6,
                                         dst_mac_address=self.unbor_mac,
                                         no_host_route=True)


        self.unhop = sai_thrift_create_next_hop(self.client,
                                                ip=sai_ipaddress(self.tun_ip),
                                                router_interface_id=self.urif,
                                                type=SAI_NEXT_HOP_TYPE_IP)

        self.unhop_v6 = sai_thrift_create_next_hop(
            self.client,
            ip=sai_ipaddress(self.tun_ipv6),
            router_interface_id=self.urif,
            type=SAI_NEXT_HOP_TYPE_IP)

        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        self.tunnel_route = sai_thrift_route_entry_t(
            vr_id=self.uvrf, destination=sai_ipprefix(self.tun_ip + '/32'))
        sai_thrift_create_route_entry(self.client,
                                      self.tunnel_route,
                                      next_hop_id=self.unhop)

        self.tunnel_route_v6 = sai_thrift_route_entry_t(
            vr_id=self.uvrf, destination=sai_ipprefix(self.tun_ipv6 + '/128'))
        sai_thrift_create_route_entry(self.client,
                                      self.tunnel_route_v6,
                                      next_hop_id=self.unhop_v6)

        self.orif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.ovrf,
            port_id=self.oport)

        # route to customer from VM
        self.onbor = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ip))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)

        self.onbor_v6 = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ipv6))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor_v6,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)

        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.onhop = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ip),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)

        self.onhop_v6 = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ipv6),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)


        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.customer_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ip + '/32'))
        sai_thrift_create_route_entry(self.client,
                                      self.customer_route,
                                      next_hop_id=self.onhop)

        self.customer_route_v6 = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ipv6 + '/128'))
        sai_thrift_create_route_entry(self.client,
                                      self.customer_route_v6,
                                      next_hop_id=self.onhop_v6)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def runTest(self):
        tunnel_type = SAI_TUNNEL_TYPE_VXLAN
        term_type = SAI_TUNNEL_TERM_TABLE_ENTRY_TYPE_P2MP
        ttl_mode = SAI_TUNNEL_TTL_MODE_PIPE_MODEL

        ovlan = sai_thrift_create_vlan(self.client, vlan_id=self.ovlan_no)
        orif_vlan = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
            virtual_router_id=self.ovrf,
            vlan_id=ovlan)
        ovlan_member = sai_thrift_create_vlan_member(
            self.client,
            vlan_id=ovlan,
            bridge_port_id=self.bridge_port_list[21],
            vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_TAGGED)
        mac2_entry = sai_thrift_fdb_entry_t(
            switch_id=self.switch_id,
            mac_address=self.customer2_mac,
            bv_id=ovlan)
        sai_thrift_create_fdb_entry(self.client,
                                    mac2_entry,
                                    type=SAI_FDB_ENTRY_TYPE_STATIC,
                                    bridge_port_id=self.bridge_port_list[21])

        decap_tunnel_map_entry_vrf_exists = False
        decap_tunnel_map_entry_vlan_exists = False

        try:
            encap_tunnel_map = sai_thrift_create_tunnel_map(
                self.client, type=SAI_TUNNEL_MAP_TYPE_VLAN_ID_TO_VNI)

            decap_tunnel_map_vrf = sai_thrift_create_tunnel_map(self.client, type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID)

            #decap_tunnel_map_vlan = sai_thrift_create_tunnel_map(self.client, type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID)

            encap_maps = sai_thrift_object_list_t(count=1,idlist=[encap_tunnel_map])
            decap_maps = sai_thrift_object_list_t(count=1,idlist=[decap_tunnel_map_vlan])
            q_list = sai_thrift_object_list_t(count=10)
            attr = sai_thrift_get_tunnel_map_attribute(self.client,  tunnel_map_oid=decap_tunnel_map_vlan, entry_list=q_list)

            tunnel = sai_thrift_create_tunnel(self.client,type=tunnel_type,encap_src_ip=sai_ipaddress(self.lpb_ip),encap_mappers=encap_maps,decap_mappers=decap_maps,encap_ttl_mode=ttl_mode,decap_ttl_mode=ttl_mode,underlay_interface=self.urif_lpb)
            self.assertNotEqual(tunnel, 0, "Failed to create tunnel with dual decap mappers")

            tunnel_term = sai_thrift_create_tunnel_term_table_entry(self.client,tunnel_type=tunnel_type,vr_id=self.uvrf,action_tunnel_id=tunnel,type=term_type,dst_ip=sai_ipaddress(self.lpb_ip))

            tunnel_nhop = sai_thrift_create_next_hop(self.client,type=SAI_NEXT_HOP_TYPE_TUNNEL_ENCAP,tunnel_id=tunnel,ip=sai_ipaddress(self.tun_ip),tunnel_mac=self.inner_dmac,tunnel_vni=self.vni)

            vm_route = sai_thrift_route_entry_t(vr_id=self.ovrf, destination=sai_ipprefix(self.vm_ip + '/32'))
            sai_thrift_create_route_entry(self.client,vm_route,next_hop_id=tunnel_nhop)

            pdb.set_trace()
            decap_tunnel_map_entry_vlan = sai_thrift_create_tunnel_map_entry(self.client, tunnel_map=decap_tunnel_map_vlan, tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID, vlan_id_value=self.ovlan_no, vni_id_key=self.vni)
            # encap_tunnel_map_entry = sai_thrift_create_tunnel_map_entry(self.client,tunnel_map=encap_tunnel_map,tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VIRTUAL_ROUTER_ID_TO_VNI,virtual_router_id_key=self.ovrf,vni_id_value=self.vni)
            self.assertNotEqual(decap_tunnel_map_entry_vlan, 0)

            # decap_tunnel_map_entry_vrf = sai_thrift_create_tunnel_map_entry(
            #     self.client,
            #     tunnel_map=decap_tunnel_map_vrf,
            #     tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID,
            #     virtual_router_id_value=self.ovrf,
            #     vni_id_key=self.vni)
            # self.assertNotEqual(decap_tunnel_map_entry_vrf, 0)
            # decap_tunnel_map_entry_vrf_exists = True



            



            l3_pkt = simple_udp_packet(eth_dst=self.customer_mac,
                                       eth_src=ROUTER_MAC,
                                       ip_dst=self.customer_ip,
                                       ip_src=self.vm_ip,
                                       ip_id=108,
                                       ip_ttl=63)
            l3_inner_pkt = simple_udp_packet(eth_dst=ROUTER_MAC,
                                             eth_src=self.inner_dmac,
                                             ip_dst=self.customer_ip,
                                             ip_src=self.vm_ip,
                                             ip_id=108,
                                             ip_ttl=64)
            l3_vxlan_pkt = simple_vxlan_packet(eth_dst=ROUTER_MAC,
                                               eth_src=self.unbor_mac,
                                               ip_dst=self.lpb_ip,
                                               ip_src=self.tun_ip,
                                               ip_id=0,
                                               ip_ttl=64,
                                               ip_flags=0x2,
                                               udp_sport=11638,
                                               with_udp_chksum=False,
                                               vxlan_vni=self.vni,
                                               inner_frame=l3_inner_pkt)

            pkt_len = 104
            dec = 4
            l2_pkt = simple_udp_packet(eth_dst=self.customer2_mac,
                                       eth_src=self.inner_dmac,
                                       dl_vlan_enable=True,
                                       vlan_vid=self.ovlan_no,
                                       ip_dst=self.customer2_ip,
                                       ip_src=self.vm_ip,
                                       ip_id=108,
                                       ip_ttl=64,
                                       pktlen=pkt_len)
            l2_inner_pkt = simple_udp_packet(eth_dst=self.customer2_mac,
                                             eth_src=self.inner_dmac,
                                             ip_dst=self.customer2_ip,
                                             ip_src=self.vm_ip,
                                             ip_id=108,
                                             ip_ttl=64,
                                             pktlen=pkt_len - dec)
            l2_vxlan_pkt = simple_vxlan_packet(eth_dst=ROUTER_MAC,
                                               eth_src=self.unbor_mac,
                                               ip_dst=self.lpb_ip,
                                               ip_src=self.tun_ip,
                                               ip_id=0,
                                               ip_ttl=64,
                                               ip_flags=0x2,
                                               udp_sport=11638,
                                               with_udp_chksum=False,
                                               vxlan_vni=self.vni,
                                               inner_frame=l2_inner_pkt)

            print("Sending VxLan packet to tunnel with dual decap mappers")
            # pdb.set_trace()
            # send_packet(self, self.uport_dev, l3_vxlan_pkt)
            # verify_packet(self, l3_pkt, self.oport_dev)
            # print("\tOK")

            print("Create overlapping decap tunnel_mapper_entry for vlan "
                  "with same vni")
            decap_tunnel_map_entry_vlan = sai_thrift_create_tunnel_map_entry(self.client, tunnel_map=decap_tunnel_map_vlan, tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID, vlan_id_value=self.ovlan_no, vni_id_key=self.vni)
            decap_tunnel_map_entry_vlan_exists = True

            print("Sending L3 VxLan packet with overlapping "
                  "decap mapper entries")
            # send_packet(self, self.uport_dev, l3_vxlan_pkt)
            # verify_packet(self, l3_pkt, self.oport_dev)
            # print("\tOK")

            print("Sending L2 VxLan packet with overlapping "
                  "decap mapper entries, should not be forwarded")
            # send_packet(self, self.uport_dev, l2_vxlan_pkt)
            # verify_no_other_packets(self)
            # print("\tDropped")

            print("Delete overlapping decap tunnel_mapper_entry for vlan")
            pdb.set_trace()
            sai_thrift_remove_tunnel_map_entry(self.client, decap_tunnel_map_entry_vlan)
            decap_tunnel_map_entry_vlan_exists = False

            print("Sending L3 VxLan packet after deleting overlapping "
                  "decap mapper entry for vlan")
            # send_packet(self, self.uport_dev, l3_vxlan_pkt)
            # verify_packet(self, l3_pkt, self.oport_dev)
            # print("\tOK")

            print("Delete decap tunnel_mapper_entry for vrf, then "
                  "replace with decap tunnel_mapper_entry for vlan")
            sai_thrift_remove_tunnel_map_entry(self.client, decap_tunnel_map_entry_vrf)
            decap_tunnel_map_entry_vrf_exists = False

            decap_tunnel_map_entry_vlan = sai_thrift_create_tunnel_map_entry(
                self.client,
                tunnel_map=decap_tunnel_map_vlan,
                tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID,
                vlan_id_value=self.ovlan_no,
                vni_id_key=self.vni)
            decap_tunnel_map_entry_vlan_exists = True

            print("Sending L2 VxLan packet with single decap mapper entry "
                  "for vlan")
            pdb.set_trace()
            send_packet(self, self.uport_dev, l2_vxlan_pkt)
            verify_packet(self, l2_pkt, self.dev_port_list[21])
            print("\tOK")

            print("Sending L3 VxLan packet with single decap mapper entry "
                  "for vlan, should still be routed due to rif in same vrf")
            send_packet(self, self.uport_dev, l3_vxlan_pkt)
            verify_packet(self, l3_pkt, self.oport_dev)
            print("\tOK")

            print("Create overlapping decap tunnel_mapper_entry for vrf "
                  "with same vni")
            decap_tunnel_map_entry_vrf = sai_thrift_create_tunnel_map_entry(
                self.client,
                tunnel_map=decap_tunnel_map_vrf,
                tunnel_map_type=SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID,
                virtual_router_id_value=self.ovrf,
                vni_id_key=self.vni)
            decap_tunnel_map_entry_vrf_exists = True

            print("Sending L3 VxLan packet with overlapping "
                  "decap mapper entries")
            send_packet(self, self.uport_dev, l3_vxlan_pkt)
            verify_packet(self, l3_pkt, self.oport_dev)
            print("\tOK")

            print("Sending L2 VxLan packet with overlapping "
                  "decap mapper entries, should not be forwarded")
            send_packet(self, self.uport_dev, l2_vxlan_pkt)
            verify_no_other_packets(self)
            print("\tDropped")

            print("Delete overlapping decap tunnel_mapper_entry for vrf")
            sai_thrift_remove_tunnel_map_entry(self.client,
                                               decap_tunnel_map_entry_vrf)
            decap_tunnel_map_entry_vrf_exists = False

            print("Sending L3 VxLan packet after deleting overlapping "
                  "decap mapper entry for vrf")
            send_packet(self, self.uport_dev, l3_vxlan_pkt)
            verify_packet(self, l3_pkt, self.oport_dev)
            print("\tOK")

            print("Sending L2 VxLan packet after deleting overlapping "
                  "decap mapper entry for vrf")
            send_packet(self, self.uport_dev, l2_vxlan_pkt)
            verify_packet(self, l2_pkt, self.dev_port_list[21])
            print("\tOK")

        finally:
            pass

