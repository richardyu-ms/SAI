from sai_test_base import T0TestBase
from sai_utils import *
import pdb

class IpInIpTnnnelBase(T0TestBase):
    '''
    This class contains base setup for IP in IP tunnel tests
    '''


    def setUp(self):
        T0TestBase.setUp(self)

        self.oport = self.port_list[2]
        self.oport_dev =self.dev_port_list[2]
        self.uport = self.port_list[22]
        self.uport_dev = self.dev_port_list[22]

        self.tun_ip = "10.10.10.1"
        self.lpb_ip = "10.10.10.10"
        self.tun_lpb_mask = "/32"

        self.vm_ip = "100.100.1.1"
        self.vm_ipv6 = "2001:0db8::100:1"
        self.customer_ip = "100.100.2.1"
        self.customer_ipv6 = "2001:0db8::100:2"
        self.inner_dmac = "00:11:11:11:11:11"
        self.customer_mac = "00:22:22:22:22:11"
        self.unbor_mac = "00:33:33:33:33:11"

        # underlay configuration
        self.uvrf = self.default_vrf

        # overlay configuration
        self.ovrf = self.default_vrf
        tunnel_type = SAI_TUNNEL_TYPE_IPINIP
        term_type = SAI_TUNNEL_TERM_TABLE_ENTRY_TYPE_P2P
        pdb.set_trace()
        # loopback RIFs for tunnel
        self.urif_lpb = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK,
            virtual_router_id=self.uvrf)

        self.orif_lpb = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK,
            virtual_router_id=self.ovrf)

        # route to tunnel
        self.urif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.uvrf,
            port_id=self.uport)

      
        self.unbor = sai_thrift_neighbor_entry_t(
            rif_id=self.urif, ip_address=sai_ipaddress(self.tun_ip))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.unbor,
                                         dst_mac_address=self.unbor_mac,
                                         no_host_route=True)

        self.unhop = sai_thrift_create_next_hop(self.client,
                                                ip=sai_ipaddress(self.tun_ip),
                                                router_interface_id=self.urif,
                                                type=SAI_NEXT_HOP_TYPE_IP)

        self.tunnel_route = sai_thrift_route_entry_t(
            vr_id=self.uvrf,
            destination=sai_ipprefix(self.tun_ip + self.tun_lpb_mask))
        sai_thrift_create_route_entry(self.client,
                                      self.tunnel_route,
                                      next_hop_id=self.unhop)

        # tunnel
        self.tunnel = sai_thrift_create_tunnel(
            self.client,
            type=tunnel_type,
            encap_src_ip=sai_ipaddress(self.lpb_ip),
            underlay_interface=self.urif_lpb,
            overlay_interface=self.orif_lpb)

        # tunnel termination entry
        self.tunnel_term = sai_thrift_create_tunnel_term_table_entry(
            self.client,
            tunnel_type=tunnel_type,
            vr_id=self.uvrf,
            action_tunnel_id=self.tunnel,
            type=term_type,
            dst_ip=sai_ipaddress(self.lpb_ip),
            src_ip=sai_ipaddress(self.tun_ip))

        # tunnel nexthop for VM
        self.tunnel_nhop = sai_thrift_create_next_hop(
            self.client,
            type=SAI_NEXT_HOP_TYPE_TUNNEL_ENCAP,
            tunnel_id=self.tunnel,
            ip=sai_ipaddress(self.tun_ip),
            tunnel_mac=self.inner_dmac)

        # routes to VM via tunnel nexthop
        self.vm_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf, destination=sai_ipprefix(self.vm_ip + '/32'))
        sai_thrift_create_route_entry(self.client,
                                      self.vm_route,
                                      next_hop_id=self.tunnel_nhop)

        self.vm_v6_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf, destination=sai_ipprefix(self.vm_ipv6 + '/128'))
        sai_thrift_create_route_entry(self.client,
                                      self.vm_v6_route,
                                      next_hop_id=self.tunnel_nhop)

        # routes to customer from VM
        self.orif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.ovrf,
            port_id=self.oport)

      
        self.onbor = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ip))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)

        self.onhop = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ip),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)

        self.customer_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ip + '/32'))

        sai_thrift_create_route_entry(self.client,
                                      self.customer_route,
                                      next_hop_id=self.onhop)
       
        self.onbor_v6 = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ipv6))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor_v6,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)
        
        self.onhop_v6 = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ipv6),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)

        self.customer_v6_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ipv6 + '/128'))
        sai_thrift_create_route_entry(self.client,
                                      self.customer_v6_route,
                                      next_hop_id=self.onhop_v6)

    def tearDown(self):
        T0TestBase.tearDown(self)

class IPInIPTunnelDecapTest(IpInIpTnnnelBase):
    """
    Verify the load-balance of l3
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        IpInIpTnnnelBase.setUp(self)

    def ipv4inipv4decap(self):
        pkt = simple_udp_packet(eth_dst=self.customer_mac,
                                eth_src=ROUTER_MAC,
                                ip_dst=self.customer_ip,
                                ip_src=self.vm_ip,
                                ip_id=108,
                                ip_ttl=63)
        inner_pkt = simple_udp_packet(eth_dst=self.inner_dmac,
                                      eth_src=ROUTER_MAC,
                                      ip_dst=self.customer_ip,
                                      ip_src=self.vm_ip,
                                      ip_id=108,
                                      ip_ttl=64)

        ipip_pkt = simple_ipv4ip_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.unbor_mac,
                                            ip_id=0,
                                            ip_src=self.tun_ip,
                                            ip_dst=self.lpb_ip,
                                            inner_frame=inner_pkt['IP'])

        print("Verifying IP4inIP4 decapsulation")
        send_packet(self, self.uport_dev, ipip_pkt)
        verify_packet(self, pkt, self.oport_dev)
        print("\tOK")
        

    def ipv6inipv4decap(self):
        pkt = simple_udpv6_packet(eth_dst=self.customer_mac,
                                  eth_src=ROUTER_MAC,
                                  ipv6_dst=self.customer_ipv6,
                                  ipv6_src=self.vm_ipv6,
                                  ipv6_hlim=63)

        inner_pkt = simple_udpv6_packet(eth_dst=self.inner_dmac,
                                        eth_src=ROUTER_MAC,
                                        ipv6_dst=self.customer_ipv6,
                                        ipv6_src=self.vm_ipv6,
                                        ipv6_hlim=64)

        ipip_pkt = simple_ipv4ip_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.unbor_mac,
                                            ip_id=0,
                                            ip_src=self.tun_ip,
                                            ip_dst=self.lpb_ip,
                                            inner_frame=inner_pkt['IPv6'])


        print("Verifying IPinIP6 decapsulation")
        send_packet(self, self.uport_dev, ipip_pkt)
        verify_packet(self, pkt, self.oport_dev)
        print("\tOK")

    def runTest(self):
        try:
            self.ipv4inipv4decap()
            self.ipv6inipv4decap()
        finally:
            pass