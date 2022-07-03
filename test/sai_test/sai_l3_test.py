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


from sai_test_base import T0TestBase
from sai_thrift.sai_headers import *
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from sai_utils import *
import threading
import pdb


class L3IPv4LpmRouteTest(T0TestBase):
    '''
    Verify lpm route path with rif and next hop, the path will change with different ip and subnet.
    
    '''
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        print
        
        port1 = self.port_list[20]
        port2 = self.port_list[21]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        router_mac='00:77:66:55:44:00'

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_sub_addr1 = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        dmac2 = '00:11:22:33:44:66'
        dmac3 = '00:11:22:33:44:77'
        nhop_ip1 = '20.20.20.1'
        nhop_ip1_subnet = '20.20.20.0'
        ip_mask2 = '255.255.255.0'

        vr_id = sai_thrift_create_virtual_router(self.client)

        rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        #Create another rif for the port2
        rif_id2 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port2)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)        
        
        pkt = simple_tcp_packet(eth_dst=router_mac,eth_src='00:22:22:22:22:22',ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=64)

        print("Check the packet go through nhop by a sub net address")
        #Create a sub net route with the nhop and neighbor for subnet
        subnet_nbr = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipprefix(ip_sub_addr1+'/24'))
        sai_thrift_create_neighbor_entry(self.client, subnet_nbr, dst_mac_address=dmac1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        #Subnet address or ip address both work here
        subnet_nhop = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(ip_sub_addr1+'/24'), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        subnet_route = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_sub_addr1+'/24'))
        sai_thrift_create_route_entry(self.client, subnet_route, next_hop_id=subnet_nhop)

        exp_pkt = simple_tcp_packet(eth_dst=dmac1,eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        send_packet(self, 21, pkt)
        verify_packets(self, exp_pkt, [20])

        print("Check the packet go through the rif by a accurate address")
        #for rif, it should be a accurate address
        net_nbr = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipprefix(ip_addr1+'/32'))
        sai_thrift_create_neighbor_entry(self.client, net_nbr, dst_mac_address=dmac2)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        # net_nhop = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(ip_addr1), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        net_route = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_addr1+'/32'))
        sai_thrift_create_route_entry(self.client, net_route, next_hop_id=rif_id1)

        exp_pkt = simple_tcp_packet(eth_dst=dmac2,eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        send_packet(self, 21, pkt)
        verify_packets(self, exp_pkt, [20])

class L3IPv4LpmSubnetTest(T0TestBase):
    '''
    Verify lpm route path with nexthop, the path will change with different length of subnet.
    '''
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        print
        
        port1 = self.port_list[20]
        port2 = self.port_list[21]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        router_mac='00:77:66:55:44:00'

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_sub_addr1 = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        dmac2 = '00:11:22:33:44:66'
        dmac3 = '00:11:22:33:44:77'
        nhop_ip1 = '20.20.20.1'
        nhop_ip1_subnet = '20.20.20.0'
        ip_mask2 = '255.255.255.0'

        vr_id = sai_thrift_create_virtual_router(self.client)

        rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        #Create another rif for the port2
        rif_id2 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port2)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)        
        
        pkt = simple_tcp_packet(eth_dst=router_mac,eth_src='00:22:22:22:22:22',ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=64)

        print("Check the packet go through nhop by a sub net address")
        #Create a sub net route with the nhop and neighbor for subnet
        subnet_nbr = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipprefix(ip_sub_addr1+'/16'))
        sai_thrift_create_neighbor_entry(self.client, subnet_nbr, dst_mac_address=dmac1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        #Subnet address or ip address both work here
        subnet_nhop = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(ip_sub_addr1+'/16'), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        subnet_route = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_sub_addr1+'/16'))
        sai_thrift_create_route_entry(self.client, subnet_route, next_hop_id=subnet_nhop)

        exp_pkt = simple_tcp_packet(eth_dst=dmac1,eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        send_packet(self, 21, pkt)
        verify_packets(self, exp_pkt, [20])

        print("Check the packet go through nhop by a ip address")
        #Create a sub net route with the nhop and neighbor for subnet
        subnet_nbr2 = sai_thrift_neighbor_entry_t(rif_id=rif_id1,ip_address=sai_ipprefix(ip_addr1+'/24'))
        sai_thrift_create_neighbor_entry(self.client, subnet_nbr2, dst_mac_address=dmac3)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        #Subnet address or ip address both work here
        subnet_nhop2 = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(ip_sub_addr1+'/24'), router_interface_id=rif_id1, type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        subnet_route2 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(ip_sub_addr1+'/24'))
        sai_thrift_create_route_entry(self.client, subnet_route2, next_hop_id=subnet_nhop2)

        exp_pkt = simple_tcp_packet(eth_dst=dmac3,eth_src=router_mac,ip_dst='10.10.10.1',ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        send_packet(self, 21, pkt)
        verify_packets(self, exp_pkt, [20])


class L3SviTest(T0TestBase):
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        ip_addr1 = '10.10.10.0'
        dest_ip1 = '10.10.10.1'
        dest_ip2 = '10.10.10.2'
        router_mac='00:77:66:55:44:00'
        dest_mac1='00:11:11:11:11:11'
        dest_mac2='00:22:22:22:22:22'

        port2 = self.port_list[1]
        

        vr_id = sai_thrift_create_virtual_router(self.client)
        # lag1 = sai_thrift_create_lag(self.client)
        # lag1_member17 = sai_thrift_create_lag_member(
        #     self.client, lag_id=lag1, port_id=self.port_list[17])
        # lag1_member18 = sai_thrift_create_lag_member(
        #     self.client, lag_id=lag1, port_id=self.port_list[18])
        # self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        #rif_id1 = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=lag1)

        svi_rif_id = sai_thrift_create_router_interface(self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_VLAN, vlan_id=10)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        #Route to SVI and assign the dmac
        nbr_entry_1 = sai_thrift_neighbor_entry_t(rif_id=svi_rif_id,ip_address=sai_ipaddress(dest_ip1))
        sai_thrift_create_neighbor_entry(self.client, nbr_entry_1, dst_mac_address=dest_mac1)
        #nhop1 = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(dest_ip1), router_interface_id=svi_rif_id, type=SAI_NEXT_HOP_TYPE_IP)
        #route1 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(dest_ip1+'/32'))
        #sai_thrift_create_route_entry(self.client, route1, next_hop_id=nhop1)
        #self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        nbr_entry_2 = sai_thrift_neighbor_entry_t(rif_id=svi_rif_id,ip_address=sai_ipaddress(dest_ip2))
        sai_thrift_create_neighbor_entry(self.client, nbr_entry_2, dst_mac_address=dest_mac2)
        # nhop2 = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(dest_ip2), router_interface_id=svi_rif_id, type=SAI_NEXT_HOP_TYPE_IP)
        # route2 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(dest_ip2+'/32'))
        # sai_thrift_create_route_entry(self.client, route2, next_hop_id=nhop2)
        # self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        # base on the comments in test plan review meeting, change the route to a subnet route
        nhop1 = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(dest_ip1+'/24'), router_interface_id=svi_rif_id, type=SAI_NEXT_HOP_TYPE_IP)
        route1 = sai_thrift_route_entry_t(vr_id=vr_id, destination=sai_ipprefix(dest_ip1+'/24'))
        sai_thrift_create_route_entry(self.client, route1, next_hop_id=nhop1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        pkt1 = simple_tcp_packet(eth_dst=router_mac,eth_src=dest_mac2,ip_dst=dest_ip1,ip_src='192.168.0.1',ip_id=105,ip_ttl=64,vlan_vid=10)
        pkt2 = simple_tcp_packet(eth_dst=router_mac,eth_src=dest_mac2,ip_dst=dest_ip2,ip_src='192.168.0.2',ip_id=105,ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst="00:44:33:22:11:00",eth_src=router_mac,ip_dst=dest_ip1,ip_src='192.168.0.1',ip_id=105,ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(eth_dst=dest_mac2,eth_src=router_mac,ip_dst=dest_ip2,ip_src='192.168.0.2',ip_id=105,ip_ttl=63)
        post_stats = sai_thrift_get_queue_stats(self.client, self.cpu_queue_list[0])
        # tcpdump -i eth17 -nv tcp
        #pdb.set_trace()
        #BUG, expect a flood happen there, no flood
        #sleep a little while for fdb refresh
        time.sleep(1)
        send_packet(self, 1, pkt1)
        #verify_packet_any_port(self, exp_pkt, [17,18])
        verify_no_other_packets(self)        
        print("wait for 2 second for mac learning take effect ")
        time.sleep(1)
        # Unknown, learning happened after forwarding
        send_packet(self, 2, pkt2)
        #verify_packet(self, exp_pkt2, 1)
        #pdb.set_trace()
        idx,res=verify_packet_any_port(self, exp_pkt2, [1])
        print("wait for 2 second for mac move take effect ")
        time.sleep(1)
        send_packet(self, 2, pkt2)        
        #verify_packet_any_port(self, exp_pkt2, [17,18])
        idx,res=verify_packet_any_port(self, exp_pkt2, [2])

        threads = []
        print("Start multi thread mac move test...")
        print("Kick off threads")
        for i in range(0, 10):
            print(".", end = ' ')
            t = threading.Thread(target=self.mac_move, args=(pkt1,pkt2,))
            threads.append(t)
            t.start()
        
        print("")
        print("Wait for threads to finish")
        for i in threads:
            print(".", end = ' ')
            t.join()
        
        print("multi thread mac move finished. Wait 1 second and flush the data plane.")
        time.sleep(1)
        self.dataplane.flush()
        
        send_packet(self, 2, pkt2)
        #verify_packet(self, exp_pkt2, 1)
        #pdb.set_trace()
        idx,res=verify_packet_any_port(self, exp_pkt2, [2])


    def mac_move(self, pkt1, pkt2):
        for i in range(0, 100):
            send_packet(self, 1, pkt1)
            send_packet(self, 2, pkt2)


