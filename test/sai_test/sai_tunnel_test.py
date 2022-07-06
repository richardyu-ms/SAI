from sai_test_base import T0TestBase
from sai_utils import *

class IpInIpTnnnelBase(T0TestBase):
    '''
    This class contains base setup for IP in IP tunnel tests
    '''
    def __init__(self, ipv6=False):
        super(IpInIpTnnnelBase, self).__init__()
        self.ipv6 = ipv6

        if ipv6 is True:
            self.tun_ip = "2001:0db8::10:1"
            self.lpb_ip = "2001:0db8::10:10"
            self.tun_lpb_mask = "/128"
        else:
            self.tun_ip = "10.10.10.1"
            self.lpb_ip = "10.10.10.10"
            self.tun_lpb_mask = "/32"

    def setUp(self):
        super(IpInIpTnnnelBase, self).setUp()

        self.oport = self.port24
        self.oport_dev = self.dev_port24
        self.uport = self.port25
        self.uport_dev = self.dev_port25

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

        self.onhop = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ip),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)

        self.onbor = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ip))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)

        self.customer_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ip + '/32'))
        sai_thrift_create_route_entry(self.client,
                                      self.customer_route,
                                      next_hop_id=self.onhop)

        self.onhop_v6 = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress(self.customer_ipv6),
            router_interface_id=self.orif, type=SAI_NEXT_HOP_TYPE_IP)

        self.onbor_v6 = sai_thrift_neighbor_entry_t(
            rif_id=self.orif, ip_address=sai_ipaddress(self.customer_ipv6))
        sai_thrift_create_neighbor_entry(self.client,
                                         self.onbor_v6,
                                         dst_mac_address=self.customer_mac,
                                         no_host_route=True)

        self.customer_v6_route = sai_thrift_route_entry_t(
            vr_id=self.ovrf,
            destination=sai_ipprefix(self.customer_ipv6 + '/128'))
        sai_thrift_create_route_entry(self.client,
                                      self.customer_v6_route,
                                      next_hop_id=self.onhop_v6)

    def tearDown(self):
        sai_thrift_remove_route_entry(self.client, self.customer_v6_route)
        sai_thrift_remove_neighbor_entry(self.client, self.onbor_v6)
        sai_thrift_remove_next_hop(self.client, self.onhop_v6)
        sai_thrift_remove_route_entry(self.client, self.customer_route)
        sai_thrift_remove_neighbor_entry(self.client, self.onbor)
        sai_thrift_remove_next_hop(self.client, self.onhop)
        sai_thrift_remove_router_interface(self.client, self.orif)
        sai_thrift_remove_route_entry(self.client, self.vm_v6_route)
        sai_thrift_remove_route_entry(self.client, self.vm_route)
        sai_thrift_remove_next_hop(self.client, self.tunnel_nhop)
        sai_thrift_remove_tunnel_term_table_entry(self.client,
                                                  self.tunnel_term)
        sai_thrift_remove_tunnel(self.client, self.tunnel)
        sai_thrift_remove_route_entry(self.client, self.tunnel_route)
        sai_thrift_remove_neighbor_entry(self.client, self.unbor)
        sai_thrift_remove_next_hop(self.client, self.unhop)
        sai_thrift_remove_router_interface(self.client, self.urif)
        sai_thrift_remove_router_interface(self.client, self.orif_lpb)
        sai_thrift_remove_router_interface(self.client, self.urif_lpb)
        sai_thrift_remove_virtual_router(self.client, self.ovrf)
        sai_thrift_remove_virtual_router(self.client, self.uvrf)

        super(IpInIpTnnnelBase, self).tearDown()

class IPInIPTunnelDecapTest(IpInIpTnnnelBase):
    """
    Verify the load-balance of l3
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        super(IpInIpTnnnelBase, self).setUp(self)

    def ipv4inipv4decap(self):
        router_mac = '00:77:66:55:44:00'
        ip_src1 = '192.168.0.1'
        ip_src2 = '192.168.0.2'
        ip_dst = '10.10.10.1'
        pkt1 = simple_tcp_packet(eth_dst=router_mac,
                                 eth_src='00:22:22:22:22:22',
                                 ip_dst=ip_dst,
                                 ip_src=ip_src1,
                                 ip_id=105,
                                 ip_ttl=64)
        pkt2 = simple_tcp_packet(eth_dst=router_mac,
                                 eth_src='00:22:22:22:22:22',
                                 ip_dst=ip_dst,
                                 ip_src=ip_src2,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst='02:04:02:01:01:01',
                                    eth_src=router_mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src1,
                                    ip_id=105,
                                    ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(eth_dst='02:04:02:01:01:01',
                                    eth_src=router_mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src2,
                                    ip_id=105,
                                    ip_ttl=63)
        
        send_packet(self, 21, pkt1)
        verify_packet_any_port(self, exp_pkt1, [17, 18])
        send_packet(self, 21, pkt2)
        verify_packet_any_port(self, exp_pkt2, [17, 18])

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


        print("Verifying IPinIP (6 in %d) decapsulation"
              % (6 if self.ipv6 else 4))
        send_packet(self, self.uport_dev, str(ipip_pkt))
        verify_packet(self, pkt, self.oport_dev)
        print("\tOK")

    def runTest(self):
        try:
            self.ipv4inipv4decap()
            self.ipv6inipv4decap()
        finally:
            pass