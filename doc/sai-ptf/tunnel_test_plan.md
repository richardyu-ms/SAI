# SAI Tunnel Test plan
- [SAI Tunnel Test plan](#sai-tunnel-test-plan)
- [Overriew](#overriew)
- [Test Configuration](#test-configuration)
- [Test Execution](#test-execution)
  - [Test Group1: IP IN IP Tunnel Decap](#test-group1-ip-in-ip-tunnel-decap)
    - [Case1:  IpIp_Tunnel_Decap_Test_Ipv4inIpv4](#case1-ipip_tunnel_decap_test_ipv4inipv4)
    - [Case2:  IpIp_Tunnel_Decap_Test_Ipv4inIpv4](#case2-ipip_tunnel_decap_test_ipv4inipv4)
    - [Case3:  IpIp_Tunnel_Decap_Test_Ipv6inIpv4](#case3-ipip_tunnel_decap_test_ipv6inipv4)
    - [Case4:  IpIp_Tunnel_Decap_Test_Ipv4inIpv6](#case4-ipip_tunnel_decap_test_ipv4inipv6)
    - [Testing Data Packet](#testing-data-packet)
  - [Test Group2: IP IN IP Tunnel Encap](#test-group2-ip-in-ip-tunnel-encap)
    - [Case1:  IpIp_Tunnel_encap_Test_Ipv4inIpv4](#case1-ipip_tunnel_encap_test_ipv4inipv4)
    - [Case2:  IpIp_Tunnel_encap_Test_Ipv6inIpv6](#case2-ipip_tunnel_encap_test_ipv6inipv6)
    - [Testing Data Packet](#testing-data-packet-1)
  - [Test Group3: IP IN IP P2MP Tunnel Decap](#test-group3-ip-in-ip-p2mp-tunnel-decap)
    - [Case1:  IpIp_P2MP_Tunnel_Decap_Test_With_term_dstip_term_srcip](#case1-ipip_p2mp_tunnel_decap_test_with_term_dstip_term_srcip)
    - [Case2:  IpIp_P2MP_Tunnel_Decap_Test_With_term_dstip_diff_term_srcip](#case2-ipip_p2mp_tunnel_decap_test_with_term_dstip_diff_term_srcip)
    - [Case3:  IpIp_P2MP_Tunnel_Decap_Test_With_diff_dstip_diff_srcip](#case3-ipip_p2mp_tunnel_decap_test_with_diff_dstip_diff_srcip)
    - [Testing Data Packet](#testing-data-packet-2)
  - [Test Group4: IP IN IP Tunnel + ECMP Encap](#test-group4-ip-in-ip-tunnel--ecmp-encap)
    - [Case1:  IpIp_Tunnel_encap_ecmp_Ipv4inIpv4](#case1-ipip_tunnel_encap_ecmp_ipv4inipv4)
    - [Case2:  IpIp_Tunnel_encap_ecmp_Ipv6inIpv6](#case2-ipip_tunnel_encap_ecmp_ipv6inipv6)
    - [Testing Data Packet](#testing-data-packet-3)
  - [Test Group5: Vxlan  Tunnel Decap](#test-group5-vxlan-tunnel-decap)
    - [Case1:  Vxlan_Tunnel_Decap_Test_Underlay_Ipv4](#case1-vxlan_tunnel_decap_test_underlay_ipv4)
    - [Case2:  Vxlan_Tunnel_Decap_Test_Underlay_Ipv6](#case2-vxlan_tunnel_decap_test_underlay_ipv6)
    - [case3:  Vxlan_Tunnel_Decap_Test_Invalid_Term_SrcIp](#case3-vxlan_tunnel_decap_test_invalid_term_srcip)
    - [Testing Data Packet](#testing-data-packet-4)
  - [Test Group6: Vxlan Tunnel Encap](#test-group6-vxlan-tunnel-encap)
    - [Case1:  Vxlan_Tunnel_Encap_Test_Underlay_Ipv4](#case1-vxlan_tunnel_encap_test_underlay_ipv4)
    - [Case2:  Vxlan_Tunnel_Encap_Test_Underlay_Ipv6](#case2-vxlan_tunnel_encap_test_underlay_ipv6)
    - [Test data packet](#test-data-packet)
  - [Test Group7: Vxlan P2MP Tunnel Decap](#test-group7-vxlan-p2mp-tunnel-decap)
    - [Case1:  Vxlan_P2MP_Tunnel_Decap_Test_With_term_dst_ip_term_srcip](#case1-vxlan_p2mp_tunnel_decap_test_with_term_dst_ip_term_srcip)
    - [Case2:  Vxlan_P2MP_Tunnel_Decap_Test_With_term_dst_ip_diff_term_srcip](#case2-vxlan_p2mp_tunnel_decap_test_with_term_dst_ip_diff_term_srcip)
    - [Case3:  Vxlan_P2MP_Tunnel_Decap_Test_With_diff_dst_ip_diff_srcip](#case3-vxlan_p2mp_tunnel_decap_test_with_diff_dst_ip_diff_srcip)
    - [Test data packet](#test-data-packet-1)
  - [Test Group8: IN IN IP ENCAP TTL](#test-group8-in-in-ip-encap-ttl)
    - [Case1: encap_ttl_set_pipe_mode_v4](#case1-encap_ttl_set_pipe_mode_v4)
    - [Case2: encap_ttl_set_pipe_mode_v6](#case2-encap_ttl_set_pipe_mode_v6)
    - [Case3: encap_ttl_set_uniform_mode_v4](#case3-encap_ttl_set_uniform_mode_v4)
    - [Case4: encap_ttl_set_uniform_mode_v6](#case4-encap_ttl_set_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-5)
  - [Test Group9: IP In IP Decap TTL](#test-group9-ip-in-ip-decap-ttl)
    - [Case1: decap_ttl_set_pipe_mode_v4](#case1-decap_ttl_set_pipe_mode_v4)
    - [Case2: decap_ttl_set_pipe_mode_v6](#case2-decap_ttl_set_pipe_mode_v6)
    - [Case3: decap_ttl_set_uniform_mode_v4](#case3-decap_ttl_set_uniform_mode_v4)
    - [Case4: decap_ttl_set_uniform_mode_v6](#case4-decap_ttl_set_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-6)
  - [Test Group10: IN IN IP ENCAP DSCP](#test-group10-in-in-ip-encap-dscp)
    - [Case1: encap_dscp_set_pipe_mode_v4](#case1-encap_dscp_set_pipe_mode_v4)
    - [Case2: encap_dscp_set_pipe_mode_v6](#case2-encap_dscp_set_pipe_mode_v6)
    - [Case3: encap_dscp_set_uniform_mode_v4](#case3-encap_dscp_set_uniform_mode_v4)
    - [Case4: encap_dscp_set_uniform_mode_v6](#case4-encap_dscp_set_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-7)
  - [Test Group11: IP In IP Decap DSCP](#test-group11-ip-in-ip-decap-dscp)
    - [Case1: decap_dscp_set_pipe_mode_v4](#case1-decap_dscp_set_pipe_mode_v4)
    - [Case2: decap_dscp_set_pipe_mode_v6](#case2-decap_dscp_set_pipe_mode_v6)
    - [Case3: decap_dscp_set_uniform_mode_v4](#case3-decap_dscp_set_uniform_mode_v4)
    - [Case4: decap_dscp_set_uniform_mode_v6](#case4-decap_dscp_set_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-8)
  - [Test Group12: IN IN IP ENCAP DSCP REMAP](#test-group12-in-in-ip-encap-dscp-remap)
    - [Case1: encap_dscp_remap_pipe_mode_v4](#case1-encap_dscp_remap_pipe_mode_v4)
    - [Case2: encap_dscp_remap_pipe_mode_v6](#case2-encap_dscp_remap_pipe_mode_v6)
    - [Case3: encap_dscp_remap_uniform_mode_v4](#case3-encap_dscp_remap_uniform_mode_v4)
    - [Case4: encap_dscp_remap_uniform_mode_v6](#case4-encap_dscp_remap_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-9)
  - [Test Group13: IP In IP Decap DSCP REMAP](#test-group13-ip-in-ip-decap-dscp-remap)
    - [Case1: decap_dscp_remap_pipe_mode_v4](#case1-decap_dscp_remap_pipe_mode_v4)
    - [Case2: decap_dscp_remap_pipe_mode_v6](#case2-decap_dscp_remap_pipe_mode_v6)
    - [Case3: decap_dscp_remap_uniform_mode_v4](#case3-decap_dscp_remap_uniform_mode_v4)
    - [Case4: decap_dscp_remap_uniform_mode_v6](#case4-decap_dscp_remap_uniform_mode_v6)
    - [Testing Data Packet](#testing-data-packet-10)
# Overriew
The purpose of this test plan is to test the Tunnel function from SAI.


# Test Configuration

For the test configuration, please refer to Tunnel configuration section of the file 
  - [Config_t0](./config_data/config_t0.md)
  
**Note. All the tests will be based on the configuration above, if any additional configuration is required, it will be specified in the Test case.**

# Test Execution

## Test Group1: IP IN IP Tunnel Decap 
	
### Case1:  IpIp_Tunnel_Decap_Test_Ipv4inIpv4
### Case2:  IpIp_Tunnel_Decap_Test_Ipv4inIpv4
### Case3:  IpIp_Tunnel_Decap_Test_Ipv6inIpv4
### Case4:  IpIp_Tunnel_Decap_Test_Ipv4inIpv6
### Testing Objective <!-- omit in toc --> 

    Tunnel Term Source is 10.1.2.100
    Tunnel Term Dest is 10.10.10.1
    Tunnel Term Source is fc00:1::2:100
    Tunnel Term Dest is 4001:0E98:03EE::0D25

    We will send encapsulated packet from lag2 and expect a decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port1]           |          ingress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet

#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1)/TCP()

#### IPV6 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1)/TCP()

#### IPV4 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()

### Test steps: <!-- omit in toc --> 
1. Generate ingress encap packet as decribed by Testing Data Packet
2. Send encap packet from lag2.
3. Generate expected decap packet as decribed by Testing Data Packet.
4. Recieve decap packet from port1, compare it with expected decap packet.


## Test Group2: IP IN IP Tunnel Encap 
### Case1:  IpIp_Tunnel_encap_Test_Ipv4inIpv4
### Case2:  IpIp_Tunnel_encap_Test_Ipv6inIpv6

### Testing Objective <!-- omit in toc --> 

    We will send decapsulated packet from port1 and expect a encapsulated packet on lag2
    -----------------------------------------------------------------
    Ingress side[port1]           |          Egress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::  |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1)/IP(dst=192.168.20.1,src=192.168.1.1)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25)/IP(fc02::20:1,src=fc02::1:1)/TCP()
- ingres decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1)/TCP()

### Test steps: <!-- omit in toc --> 
1. Generate ingress decap packet as decribed by Testing Data Packet
2. Send encap packet from lag2.
3. Generate expected encap packet as decribed by Testing Data Packet.
4. Recieve encap packet from port1, compare it with expected encap packet.


## Test Group3: IP IN IP P2MP Tunnel Decap 
### Case1:  IpIp_P2MP_Tunnel_Decap_Test_With_term_dstip_term_srcip

### Case2:  IpIp_P2MP_Tunnel_Decap_Test_With_term_dstip_diff_term_srcip
### Case3:  IpIp_P2MP_Tunnel_Decap_Test_With_diff_dstip_diff_srcip

### Testing Objective <!-- omit in toc --> 

    We will send encapsulated packet from lag2 and lag4, then expect decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port1]           |          ingress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    -------------------------------------------------------------
    
### Testing Data Packet
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()

- ingress encap packet with different term src ip =Ether(dst=ROUTER_MAC)/IP(src=10.1.4.100,dst=10.10.10.1)/IP(src=192.168.40.1,dst=192.168.1.1)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()

- ingress encap packet with different term src ip =Ether(dst=ROUTER_MAC)/IP(src=10.1.4.100,dst=10.10.10.100)/IP(src=192.168.20.1,dst=192.168.1.1)/TCP()

### Test steps: <!-- omit in toc --> 
- IpIp_P2MP_Tunnel_Decap_Test_With_valid_dstip_valid_srcip
1. check tunnel term with dest as 10.10.10.1,src as 10.1.2.100, term type as P2MP.
2. Generate ingress encap packet as decribed by Testing Data Packet.
3. Send encap packets with the same term src ip from lag2.
4. Generate expected decap packets as decribed by Testing Data Packet.
5. Recieve decap packets from port1, compare it with expected decap packets.

- IpIp_P2MP_Tunnel_Decap_Test_With_term_dstip_diff_term_srcip
1. Send encap packet with different term src ip from lag2.
2. Recieve decap packets from port1, compare it with expected decap packets.

- IpIp_P2MP_Tunnel_Decap_Test_With_diff_dstip_diff_srcip
1.  Send encap packet with different term src ip and different term dst ip from lag2.
2.  Verify packet drop on lag2

## Test Group4: IP IN IP Tunnel + ECMP Encap 
### Case1:  IpIp_Tunnel_encap_ecmp_Ipv4inIpv4
### Case2:  IpIp_Tunnel_encap_ecmp_Ipv6inIpv6

### Testing Objective <!-- omit in toc --> 

    We will send decapsulated packets from port1 and expect  encapsulated packets on lag2 and lag4 equally.
    -----------------------------------------------------------------
    Ingress side[port1]           |          Egress side[lag2] [lag4]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::  |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 

- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.70.1~100,src=192.168.1.1)/TCP(sport, dport)

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingres decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1)/TCP()

### Test steps: <!-- omit in toc --> 
1. Generate ingress decap packets with dst ip as 192.168.70.1~100, tcp sport as 16666~16765, dst tcp port 36666~36765.
2. Initalize hash seed as 444.
3. Send decap packets from port1.
4. Check if packets are received on lag2 and lag4 equally.


## Test Group5: Vxlan  Tunnel Decap 
	
### Case1:  Vxlan_Tunnel_Decap_Test_Underlay_Ipv4
### Case2:  Vxlan_Tunnel_Decap_Test_Underlay_Ipv6
### case3:  Vxlan_Tunnel_Decap_Test_Invalid_Term_SrcIp

### Testing Objective <!-- omit in toc --> 

    Tunnel Term Source is 10.1.3.100
    Tunnel Term Dest is 10.10.10.2
    Tunnel Term Source is fc00:1::3:100
    Tunnel Term Dest is 4001:0E98:03EE::0D26

    We will send encapsulated packet from lag2 and expect a decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port2]           |          ingress side[lag3]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------

### Testing Data Packet
```Python
        egress_decap_pkt = simple_udp_packet(eth_dst=01:01:00:99:01:01,
                                eth_src=ROUTER_MAC,
                                ip_dst=192.168.1.2,
                                ip_src=192.168.30.1,
                                ip_id=108,
                                ip_ttl=63)

        inner_pkt = simple_udp_packet(eth_dst=ROUTER_MAC,
                                      eth_src=self.inner_vxlan_dmac,
                                      ip_dst=192.168.1.2,
                                      ip_src=192.168.30.101,
                                      ip_id=108,
                                      ip_ttl=64)

        ingress_encap_vxlan_pkt_ipv4_underlay = simple_vxlan_packet(
                                        eth_dst=ROUTER_MAC,
                                        ip_dst=10.10.10.2,
                                        ip_src=10.1.3.100,
                                        ip_id=0,
                                        ip_ttl=64,
                                        ip_flags=0x2,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=1000,
                                        inner_frame=inner_pkt)
        ingress_encap_vxlan_pkt_ipv6_underlay = simple_vxlanv6_packet(
                                          eth_dst=ROUTER_MAC,
                                          ipv6_dst=4001:0E98:03EE::0D26
                                          ipv6_src=fc00:1::3:100,
                                          ipv6_hlim=64,
                                          udp_sport=11638,
                                          with_udp_chksum=False,
                                          vxlan_vni=1000,
                                          inner_frame=inner_pkt)

        invalid_term_srcip_ingress_vxlan_pkt = simple_vxlanv6_packet(
                                  eth_dst=ROUTER_MAC,
                                  ipv6_dst=self.4001:0E98:03EE::0D26,
                                  ipv6_src=test_src_ip,
                                  ipv6_hlim=64,
                                  with_udp_chksum=False,
                                  vxlan_vni=1000,
                                  inner_frame=inner_pkt)
```
### Test steps: <!-- omit in toc --> 
- Vxlan_Tunnel_Decap_Test_Underlay_Ipv4
- Vxlan_Tunnel_Decap_Test_Underlay_Ipv6
1. Generate  ingress_encap_vxlan_pkt as decribed by Testing Data Packet
2. Send encap packet from lag3.
3. Generate expected decap packet as decribed by Testing Data Packet.
4. Recieve decap packet from port2, compare it with expected decap packet.

- Vxlan_Tunnel_Decap_Test_Invalid_Term_SrcIp:
1. Generate invalid_term_srcip_ingress_vxlan_pkt as decribed by Testing Data Packet
2. Send encap packet from lag3.
3. Verify packet drop on port2.

## Test Group6: Vxlan Tunnel Encap 
	
### Case1:  Vxlan_Tunnel_Encap_Test_Underlay_Ipv4
### Case2:  Vxlan_Tunnel_Encap_Test_Underlay_Ipv6

### Testing Objective <!-- omit in toc --> 

    We will send decapsulated  packet from lag3 and expect a encapsulated packet on port2
    -----------------------------------------------------------------
    ingress side[port2]           |          egress side[lag3]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------

### Test data packet
```Python
           egress_decap_pkt = simple_udp_packet(eth_dst=01:01:00:99:01:01,
                                eth_src=ROUTER_MAC,
                                ip_dst=192.168.1.2,
                                ip_src=192.168.30.1,
                                ip_id=108,
                                ip_ttl=63)

        inner_pkt = simple_udp_packet(eth_dst=ROUTER_MAC,
                                      eth_src=self.inner_vxlan_dmac,
                                      ip_dst=192.168.1.2,
                                      ip_src=192.168.30.101,
                                      ip_id=108,
                                      ip_ttl=64)

        ingress_encap_vxlan_pkt_ipv4_underlay = simple_vxlan_packet(
                                        eth_dst=ROUTER_MAC,
                                        ip_dst=10.10.10.2,
                                        ip_src=10.1.3.100,
                                        ip_id=0,
                                        ip_ttl=64,
                                        ip_flags=0x2,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=1000,
                                        inner_frame=inner_pkt)

        egress_encap_vxlan_pkt_ipv6_underlay = simple_vxlanv6_packet(
                                          eth_dst=ROUTER_MAC,
                                          ipv6_src=4001:0E98:03EE::0D26
                                          ipv6_dst=fc00:1::3:100,
                                          ipv6_hlim=64,
                                          udp_sport=11638,
                                          with_udp_chksum=False,
                                          vxlan_vni=1000,
                                          inner_frame=inner_pkt)
```
### Test steps: <!-- omit in toc --> 
1. Generate ingress decap packet as decribed by Testing Data Packet
2. Send encap packet from lag3.
3. Generate expected encap packet as decribed by Testing Data Packet.
4. Recieve encap packet from port2, compare it with expected encap packet.


## Test Group7: Vxlan P2MP Tunnel Decap 
### Case1:  Vxlan_P2MP_Tunnel_Decap_Test_With_term_dst_ip_term_srcip

### Case2:  Vxlan_P2MP_Tunnel_Decap_Test_With_term_dst_ip_diff_term_srcip
### Case3:  Vxlan_P2MP_Tunnel_Decap_Test_With_diff_dst_ip_diff_srcip

### Testing Objective <!-- omit in toc --> 

    We will send encapsulated packet from lag2 and lag4, then expect decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port2]           |          ingress side[lag3]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    -------------------------------------------------------------
    
### Test data packet
```Python
         ingress_decap_pkt = simple_udp_packet(
                                eth_dst=ROUTER_MAC,
                                ip_src=192.168.1.2,
                                ip_dst=192.168.1.101,
                                ip_id=108,
                                ip_ttl=63)

        inner_pkt = simple_udp_packet(eth_src=ROUTER_MAC,
                                      eth_dst=self.inner_vxlan_dmac,
                                      ip_scr=192.168.1.2,
                                      ip_dst=192.168.1.101,
                                      ip_id=108,
                                      ip_ttl=64)

        egress_encap_vxlan_pkt_diif_src_ip= simple_vxlan_packet(
                                        eth_dst=ROUTER_MAC,
                                        ip_src=10.10.10.2,
                                        ip_dst=10.1.3.100,
                                        ip_id=0,
                                        ip_ttl=64,
                                        ip_flags=0x2,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=1000,
                                        inner_frame=inner_pkt)

       egress_encap_vxlan_pkt_diff_src_ip_diff_dst_ip = simple_vxlan_packet(
                                        eth_dst=ROUTER_MAC,
                                        ip_src=10.10.10.100,
                                        ip_dst=10.1.100.100,
                                        ip_id=0,
                                        ip_ttl=64,
                                        ip_flags=0x2,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=1000,
                                        inner_frame=inner_pkt)
```
### Test steps: <!-- omit in toc --> 
- Vxlan_P2MP_Tunnel_Decap_Test_With_valid_dstip_valid_srcip
1. check tunnel term with dest as 10.10.10.2,src as 10.1.3.100, term type as P2MP.
2. Generate ingress encap packet as decribed by Testing Data Packet.
3. Send encap packets with the same term src ip from lag3.
4. Generate expected decap packets as decribed by Testing Data Packet.
5. Recieve decap packets from port2, compare it with expected decap packets.

- Vxlan_P2MP_Tunnel_Decap_Test_With_term_dstip_diff_term_srcip
1. Send encap packet with different term src ip from lag3.
2. Recieve decap packets from port2, compare it with expected decap packets.

- Vxlan_P2MP_Tunnel_Decap_Test_With_diff_dstip_diff_srcip
1.  Send encap packet with different term src ip and different term dst ip from lag3.
2.  Verify packet drop on port2
   
## Test Group8: IN IN IP ENCAP TTL 
	
### Case1: encap_ttl_set_pipe_mode_v4
### Case2: encap_ttl_set_pipe_mode_v6
### Case3: encap_ttl_set_uniform_mode_v4
### Case4: encap_ttl_set_uniform_mode_v6


### Testing Objective <!-- omit in toc --> 
This verifies if TTL field is user-defined for outer header on encapsulation and TTL field of inner header remains the same on decapsulation when using TTL pipe mode.
This verifies the TTL field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation when using TTL unifrom mode.

    We will send decapsulated packet from port1 and expect a encapsulated packet on lag2
    -----------------------------------------------------------------
    Ingress side[port1]           |          Egress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::  |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
- PIPE MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,ttl=50)/IP(dst=192.168.20.1,src=192.168.1.1, ttl=63)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1, ttl=64)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25,ttl=50)/IP(fc02::20:1,src=fc02::1:1,ttl=63)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1,ttl=64)/TCP()

- Uniform MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,ttl=63)/IP(dst=192.168.20.1,src=192.168.1.1, ttl=63)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1, ttl=64)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25, TTL=63)/IP(fc02::20:1,src=fc02::1:1, TTL=63)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1, TTL=64)/TCP()
  
### Test steps: <!-- omit in toc --> 
- encap_ttl_set_pipe_mod
1. Make sure create tunel with encap_ttl_val attribute as 50, encap_ttl_mode attr with SAI_TUNNEL_TTL_MODE_PIPE_MODEL
2. Generate input packet with ip_ttl field as 64.
3. Send input packet from port1.
4. Create Expected ipinip packet with 50 field in outer ip header as ttl_val,inner ip_ttl as 63.
5. Recieve ipinip packet from lag2, compare it with expected ipinip packet.

- encap_ttl_set_uniform_mode
1. Set ipinip tunnel with encap_ttl_mode attr with SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL
2. Generate input  packet with ip_ttl field as 64.
3. Send input packet from port1.
4. Create expected ipinip packet with ip_ttl field for outer ip header as 63,  inner ip_ttl as 63.
5. Recieve ipinip packet from lag2 port, compare it with expected ipinip packet.
   
## Test Group9: IP In IP Decap TTL 
	
### Case1: decap_ttl_set_pipe_mode_v4
### Case2: decap_ttl_set_pipe_mode_v6
### Case3: decap_ttl_set_uniform_mode_v4
### Case4: decap_ttl_set_uniform_mode_v6

### Testing Objective <!-- omit in toc --> 
This verifies if TTL field is user-defined for outer header on encapsulation and TTL field of inner header remains the same on decapsulation when using TTL pipe mode.
This verifies the TTL field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation when using TTL unifrom mode.

    We will send encapsulated packet from lag2 and expect a decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port1]           |          ingress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
- PIPE MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, ttl=64)/IP(src=192.168.20.1,dst=192.168.1.1, ttl=51)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,ttl=50)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, ttl=64)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, ttl=51)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,ttl=50)/TCP()

- UNIFORM MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, ttl=64)/IP(src=192.168.20.1,dst=192.168.1.1, ttl=50)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,ttl=63)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, ttl=64)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, ttl=50)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,ttl=63)/TCP()
### Test steps: <!-- omit in toc --> 
- decap_ttl_set_pipe_mod
1. Set ipinip tunnel encap_ttl_mode attr with SAI_TUNNEL_TTL_MODE_PIPE_MODEL
2. Generate input ipinip packet with ip_ttl field in outer ip header as 64 , one in inner ip header as 51, expected recieved packet with ip_ttl field as 50.
3. Send packet from lag2.
4. Recieve ipinip packet from port1, compare it with expected packet.

- decap_ttl_set_uniform_mode
1. Set ipinip tunnel encap_ttl_mode attr with with SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL
2. Generate input ipinip packet with ip_ttl field in outer ip header as 64 , inner ip_ttl as 50.
3. Send packet from lag2 port.
4. Create expected recieved packet with ip_ttl field as 63.
5. Recieve ipinip packet from port1, compare it with expected packet.

## Test Group10: IN IN IP ENCAP DSCP 
	
### Case1: encap_dscp_set_pipe_mode_v4
### Case2: encap_dscp_set_pipe_mode_v6
### Case3: encap_dscp_set_uniform_mode_v4
### Case4: encap_dscp_set_uniform_mode_v6


### Testing Objective <!-- omit in toc --> 
This verifies if dscp field is user-defined for outer header on encapsulation and dscp field of inner header remains the same on decapsulation when using dscp pipe mode.
This verifies the dscp field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation when using dscp unifrom mode.

    We will send decapsulated packet from port1 and expect a encapsulated packet on lag2
    -----------------------------------------------------------------
    Ingress side[port1]           |          Egress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::  |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet

- PIPE MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,dscp=10)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=18)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=18)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25,dscp=10)/IP(fc02::20:1,src=fc02::1:1,dscp=18)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1,dscp=18)/TCP()

- Uniform MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,dscp=18)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=18)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1,dscp=18)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25, dscp=18)/IP(fc02::20:1,src=fc02::1:1, dscp=18)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1, dscp=18)/TCP()

### Test steps: <!-- omit in toc --> 
- encap_dscp_in_pipe_mode:
1. Set tunnel  encap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_PIPE_MODEL, encap_dscp_val attribute as user defined ip_dscp=10
2. Generate input packet with dscp field as 18.
3. Send input packet from port1.
4. Create expected ipinip packet with dscp field in outer ip header as 10, inner dscp as 18.
5. Recieve ipinip packet from lag2 . Compare it with expected ipinip packet.

- encap_dscp_in_uniform_mode:
1. Set tunnel  encap_dscp_mode attr encap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_PIPE_MODEL
2. Generate input packet with dscp field as 18.
3. Send input packet from port1.
4. Create expected ipinip packet with dscp field in outer ip header as 18, inner dscp as 18.
5. Recieve ipinip packet from lag2 . Compare it with expected ipinip packet.
   
## Test Group11: IP In IP Decap DSCP
	
### Case1: decap_dscp_set_pipe_mode_v4
### Case2: decap_dscp_set_pipe_mode_v6
### Case3: decap_dscp_set_uniform_mode_v4
### Case4: decap_dscp_set_uniform_mode_v6

### Testing Objective <!-- omit in toc --> 
This verifies if dscp field is user-defined for outer header on encapsulation and dscp field of inner header remains the same on decapsulation when using dscp pipe mode.
This verifies thedscp field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation when using dscp unifrom mode.

    We will send encapsulated packet from lag2 and expect a decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port1]           |          ingress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
- PIPE MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, dscp=10)/IP(src=192.168.20.1,dst=192.168.1.1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,dscp=18)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, dscp=10)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,dscp=18)/TCP()

- UNIFORM MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, dscp=10)/IP(src=192.168.20.1,dst=192.168.1.1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,dscp=10)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, dscp=10)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,dscp=10)/TCP()

### Test steps: <!-- omit in toc --> 
- decap_dscp_in_pipe_mode:
1. Set ipinip tunnel encap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_PIPE_MODEL.
2. Generate input ipinip packet with dscp field in outer ip header as 10, inner  dscp as 18. 
3. Send input packet from lag2.
4. Generate expect packet with dscp field as 18.
5. Recieve decap packet from port1. Compare it with expected ip packet.

- decap_dscp_in_unifrom_mode:
1. Set ipinip tunnel decap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL
2. Generate input ipinip packet with dscp field in outer ip header as 10, one in inner ip header as 18. 
3. Send input packet from lag3 port.
4. Generate expect packet with dscp field as 10.
5. Recieve decap packet from port2. Compare it with expected ip packet.

## Test Group12: IN IN IP ENCAP DSCP REMAP
	
### Case1: encap_dscp_remap_pipe_mode_v4
### Case2: encap_dscp_remap_pipe_mode_v6
### Case3: encap_dscp_remap_uniform_mode_v4
### Case4: encap_dscp_remap_uniform_mode_v6


### Testing Objective <!-- omit in toc --> 
This verifies if DSCP field is user-defined for outer header on encapsulation and DSCP field of inner header remains the same on decapsulation when using DSCP pipe mode.
This verifies the DSCP field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation, combining with qos map.

    We will send decapsulated packet from port1 and expect a encapsulated packet on lag2
    -----------------------------------------------------------------
    Ingress side[port1]           |          Egress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::  |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
   
    
- PIPE MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,dscp=10)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=20)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=18)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25,dscp=10)/IP(fc02::20:1,src=fc02::1:1,dscp=20)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1,dscp=18)/TCP()

- Uniform MODE Packet:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=10.1.2.100,src=10.10.10.1,dscp=20)/IP(dst=192.168.20.1,src=192.168.1.1, dscp=20)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(dst=192.168.20.1,src=192.168.1.1,dscp=18)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- expected egress encap packet=Ether(dst=ROUTER_MAC)/IP(dst=fc00:1::2:100,src=4001:0E98:03EE::0D25, dscp=20)/IP(fc02::20:1,src=fc02::1:1, dscp=20)/TCP()
- ingress decap packet = Ether(dst=00:01:01:01:02:a0,src=ROUTER_MAC)/IP(fc02::20:1,src=fc02::1:1, dscp=18)/TCP()

### Test steps: <!-- omit in toc --> 
- encap_dscp_remap_in_pipe_mode:
1. set ipinip tunnel  encap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_PIPE_MODEL with encap_dscp_val attribute as user defined ip_dscp=10
2. Bind port1 with dscp_to_tc_map (18 => 2), Bind lag2 port with tc_to_dscp_map(2 => 20).
3. Generate input packet with dscp field as 18.
4. Send input packet from port1.
5. Create expected ipinip packet with dscp field in outer ip header as 10, inner dscp as 20. 
6. Recieve ipinip packet from lag2 port. Compare it with expected ipinip packet.
7. Remove  dscp_to_tc_map and tc_to_dscp_map.

- encap_dscp_remap_in_uniform_mode:
1. Set ip in ip  tunnel with encap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL
2. Bind port1 with dscp_to_tc_map (18 => 2), Bind lag3 port with tc_to_dscp_map(2 => 20).
3. Generate input packet with dscp field as 18
4. Send input packet from port2.
5. Create expected ipinip packet with dscp field in outer ip header as 20, inner dscp as 20.
6. Recieve ipinip packet from lag3 port. Compare it with expected ipinip packet.
7. Remove  dscp_to_tc_map and tc_to_dscp_map.

## Test Group13: IP In IP Decap DSCP REMAP
	
### Case1: decap_dscp_remap_pipe_mode_v4
### Case2: decap_dscp_remap_pipe_mode_v6
### Case3: decap_dscp_remap_uniform_mode_v4
### Case4: decap_dscp_remap_uniform_mode_v6

### Testing Objective <!-- omit in toc --> 
This verifies if DSCP field is user-defined for outer header on encapsulation and DSCP field of inner header remains the same on decapsulation when using DSCP pipe mode.
This verifies the DSCP field is preserved end-to-end by copying into the outer header on encapsulation and copying from the outer header on decapsulation, combining with qos map.

    We will send encapsulated packet from lag2 and expect a decapsulated packet on port1
    -----------------------------------------------------------------
    Egress side[port1]           |          ingress side[lag2]
    ------------------------------------------------------------------
    ipv4's falls in 192.168.1.0     |        ipv4's falls in 10.1.0.0
    ------------------------------------------------------------------
    ipv6's falls in fc02::   |   ipv6's falls in fc00:1::
    ------------------------------------------------------------------

### Testing Data Packet
- PIPE MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, dscp=10)/IP(src=192.168.20.1,dst=192.168.1.1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,dscp=20)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, dscp=10)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,dscp=20)/TCP()

- UNIFORM MODE PACKET:
#### IPV4 IN IPV4 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=10.1.2.100,dst=10.10.10.1, dscp=10)/IP(src=192.168.20.1,dst=192.168.1.1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=192.168.20.1,dst=192.168.1.1,dscp=20)/TCP()

#### IPV6 IN IPV6 Packet <!-- omit in toc --> 
- ingress encap packet=Ether(dst=ROUTER_MAC)/IP(src=fc00:1::2:100,dst=4001:0E98:03EE::0D25, dscp=10)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1, dscp=18)/TCP()
- expected decap packet = Ether(dst=01:01:00:99:01:01,src=ROUTER_MAC)/IP(src=2001:0000:25DE::CADE,dst=fc02::1:1,dscp=20)/TCP()

### Test steps: <!-- omit in toc --> 
- decap_dscp_remap_in_pipe_mode:
1. Make sure create tunnel_pipe with decap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_PIPE_MODEL, attribute as user defined ip_dscp=tunnel_dscp_val
2. Bind port22 with dscp_to_tc_map (18 => 2), Bind lag2 port with tc_to_dscp_map(2 => 18).
3. Generate input ipinip packet with dscp field in outer ip header as 10, inner dscp field as 18. 
4. Send input packet from lag2 port.
5. Generate expect packet with dscp field as rewrite_dscp_val.
6. Recieve decap packet from port1. Compare it with expected ip packet.
7. Remove  dscp_to_tc_map and tc_to_dscp_map.

- decap_dscp_remap_in_unifrom_mode:
1. Make sure create tunnel_uniform with decap_dscp_mode attr as SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL
2. Bind lag2 port with dscp_to_tc_map (10 => 2), Bind port1 with tc_to_dscp_map(2 => 20).
3. Generate input ipinip packet with dscp field in outer ip header as 10, one in inner ip header as 18. 
4. Send input packet from lag2 port.
5. Create expect packet with dscp field as 20.
6. Recieve decap packet from  port1. Compare it with expected ip packet.
7. Remove  dscp_to_tc_map and tc_to_dscp_map.

