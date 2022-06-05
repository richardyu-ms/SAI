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

"""
This file contains class for brcm specified functions.
"""
from ast import Pass
import pdb
from socket import AddressFamily
from platform_helper.common_sai_helper import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]

DEFAULT_IP_V4_PREFIX = '0.0.0.0/0'
DEFAULT_IP_V6_PREFIX = '0000:0000:0000:0000:0000:0000:0000:0000'
#Todo make those two parameters from input
LOCAL_IP_128V6_PREFIX = 'fe80::f68e:38ff:fe16:bc75/128'
LOCAL_IP_10V6_PREFIX = 'fe80::/10'
PORT_MTU=9122
class BrcmT0SaiHelper(CommonSaiHelper):
    """
    This class contains broadcom(brcm) specified functions for the platform setup and test context configuration.
    """

    platform = 'brcm'
    role_config = 't0'

    # lists of default objects
    self.port_to_hostif_map = {}
    self.port_to_bp_map = {}
    self.hostifs = []
    
    self.def_hostif_list = []
    self.def_bridge_port_list = []
    self.def_lag_list = []
    self.def_lag_member_list = []
    self.def_vlan_list = []
    self.def_vlan_member_list = []
    self.def_rif_list = []
    self.def_nb_list = []
    self.def_nh_list = []
    
    def normal_setup(self):
        """
        Normal setup
        """
        print("BrcmT0SaiHelper::normal_setup")
        self.start_switch()
        self.config_meta_port()


    def config_meta_port(self):
        """
        Default configuation, with metadata and ports configurations.
        """
        self.get_port_list()
        self.create_default_route_intf()
        self.get_default_1q_bridge()
        self.get_default_vlan()
        self.remove_vlan_member()
        self.remove_bridge_port()
        self.create_default_v4_v6_route_entry()
        self.create_local_v6_route()
        self.create_host_intf()
        self.turn_on_port_admin_state()
        #self.set_port_serdes()
        self.config_lag()
        self.config_vlan()

    def start_switch(self):
        """
        Start switch and wait seconds for a warm up.
        """
        switch_init_wait = 1

        self.switch_id = sai_thrift_create_switch(
            self.client, init_switch=True, src_mac_address=ROUTER_MAC)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        print("Waiting for switch to get ready, {} seconds ...".format(switch_init_wait))
        time.sleep(switch_init_wait)


    def get_port_list(self):
        """
        Set the class variable port_list.
        
        Output variable:
            self.port_list
        """
        port_list = sai_thrift_object_list_t(count=100)
        p_list = sai_thrift_get_switch_attribute(
            self.client, port_list=port_list)
        self.port_list = p_list['port_list'].idlist


    def create_default_route_intf(self):
        """
        Create default route interface on loop back interface.

        Output variables:
            self.default_vrf
            self.lpbk_intf
        """
        print("Create loop back interface...")
        attr = sai_thrift_get_switch_attribute(self.client, default_virtual_router_id=True)
        self.default_vrf = attr['default_virtual_router_id']
        self.assertNotEqual(self.default_vrf, 0)
        self.lpbk_intf = sai_thrift_create_router_interface(
            self.client, type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK,
            virtual_router_id=self.default_vrf)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    
    def get_default_1q_bridge(self):
        """
        Get defaule 1Q bridge.

        Output variables:
            self.default_1q_bridge_id
        """
        print("Get default 1Q bridge...")
        def_attr = sai_thrift_get_switch_attribute(
            self.client, default_1q_bridge_id=True)
        self.default_1q_bridge_id = def_attr['default_1q_bridge_id']


    def get_default_vlan(self):
        """
        Get defaule vlan.

        Output variables:
            self.default_vlan_id
        """
        print("Get default vlan...")
        def_attr = sai_thrift_get_switch_attribute(
            self.client, default_vlan_id=True)
        self.default_vlan_id = def_attr['default_vlan_id']

    
    def remove_vlan_member(self):
        """
        Remove vlan member when init the environment.
        """
        print("Remove vlan and members...")
        vlan_member_list = sai_thrift_object_list_t(count=100)
        mbr_list = sai_thrift_get_vlan_attribute(
            self.client, self.default_vlan_id, member_list=vlan_member_list)
        vlan_members = mbr_list['SAI_VLAN_ATTR_MEMBER_LIST'].idlist

        for member in vlan_members:
            sai_thrift_remove_vlan_member(self.client, vlan_member_oid=member)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def remove_bridge_port():
        """
        Remove bridge ports.
        """
        print("Remove bridge ports...")
        bridge_port_list = sai_thrift_object_list_t(count=100)
        bp_list = sai_thrift_get_bridge_attribute(
            self.client, self.default_1q_bridge_id, port_list=bridge_port_list)
        bp_ports = bp_list['port_list'].idlist
        for port in bp_ports:
            sai_thrift_remove_bridge_port(self.client, port)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def create_default_v4_v6_route_entry(self):
        """
        Create default v4 and v6 route entry.

        Output variable:
            self.default_ipv6_route_entry
            self.default_ipv4_route_entry
        """
        print("Create default v4 & v6 route entry...")
        v6_default = sai_thrift_ip_prefix_t(
            addr_family=1, addr=sai_thrift_ip_addr_t(ip6=DEFAULT_IP_V6_PREFIX),
            mask=sai_thrift_ip_addr_t(ip6=DEFAULT_IP_V6_PREFIX))
        entry = sai_thrift_route_entry_t(
            vr_id=self.default_vrf,
            destination=v6_default,
            switch_id=self.switch_id)
        self.default_ipv6_route_entry = sai_thrift_create_route_entry(
            self.client, route_entry=entry, packet_action=SAI_PACKET_ACTION_DROP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        entry = sai_thrift_route_entry_t(
            vr_id=self.default_vrf,
            destination=sai_ipprefix(DEFAULT_IP_V4_PREFIX),
            switch_id=self.switch_id)
        self.default_ipv4_route_entry = sai_thrift_create_route_entry(
            self.client, route_entry=entry, packet_action=SAI_PACKET_ACTION_DROP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def create_local_v6_route(self):
        """
        Create local v6 route base on the configuration of the actual switch.

        Output variable:
            self.local_10v6_route_entry
            self.local_128v6_route_entry
        """
        #Todo make the v6 prefix from actual device config.

        print("Create Local V6 route...")
        entry = sai_thrift_route_entry_t(
            vr_id=self.default_vrf,
            destination=sai_ipprefix(LOCAL_IP_10V6_PREFIX),
            switch_id=self.switch_id)
        self.local_10v6_route_entry = sai_thrift_create_route_entry(
            self.client, route_entry=entry, packet_action=SAI_PACKET_ACTION_FORWARD)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        entry = sai_thrift_route_entry_t(
            vr_id=self.default_vrf,
            destination=sai_ipprefix(LOCAL_IP_128V6_PREFIX),
            switch_id=self.switch_id)
        self.local_128v6_route_entry = sai_thrift_create_route_entry(
            self.client, route_entry=entry, packet_action=SAI_PACKET_ACTION_FORWARD)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def create_host_intf(self):
        """
        Craete host interface.
        Steps:
         1. create host table entry
         2. create host interface trap
         3. set host interface base on the port_config.int (this file contains the lanes, name and index information.)

        Output variables:
            self.host_intf_table_id
            self.ports_config
            self.port_to_hostif_map
            self.hostifs
        """
        print("Create Host intfs...")
        self.host_intf_table_id = sai_thrift_create_hostif_table_entry(
            self.client, type=SAI_HOSTIF_TABLE_ENTRY_TYPE_WILDCARD,
            channel_type=SAI_HOSTIF_TABLE_ENTRY_CHANNEL_TYPE_NETDEV_PHYSICAL_PORT)
        attr = sai_thrift_get_switch_attribute(self.client, default_trap_group=True)
        self.default_trap_group = attr['default_trap_group']
        sai_thrift_create_hostif_trap(
            self.client, trap_type=SAI_HOSTIF_TRAP_TYPE_TTL_ERROR, packet_action=SAI_PACKET_ACTION_TRAP,
            trap_group=self.default_trap_group, trap_priority=0)

        self.ports_config = self.parsePortConfig(
            self.test_params['port_config_ini'])
        for i, _ in enumerate(self.port_list):
            try:
                setattr(self, 'port%s' % i, self.port_list[i])
                hostif = sai_thrift_create_hostif(
                    self.client, 
                    type=SAI_HOSTIF_TYPE_NETDEV,
                    obj_id=self.port_list[i],
                    name=self.ports_config[i]['name'])
                setattr(self, 'host_if%s' % i, hostif)
                self.port_to_hostif_map[i]=hostif
                sai_thrift_set_hostif_attribute(self.client, hostif_oid=hostif, oper_status=False)
                self.def_hostif_list.append(hostif)
                self.hostifs.append(hostif)
            except BaseException as e:
                print("Cannot create hostif, error : {}".format(e))


    def turn_on_port_admin_state(self):
        """
        Turn on port admin state
        """
        print("Set port...")
        for i, port in enumerate(self.port_list):
            sai_thrift_set_port_attribute(
                self.client, port_oid=port, mtu=PORT_MTU, admin_state=True)


    def set_port_serdes(self):
        """
        Set prot Serdes.
        """     
        print("Recreate Port serdes...")
        for i, port in enumerate(self.port_list):
            sai_thrift_set_port_attribute(
                self.client, port_oid=port, mtu=PORT_MTU, admin_state=True)

    def config_lag(self):
        """
        set some basic configuration for lag, its members and rif

        Common ports configuration:
        +=============+==========+=========+
        |   HostIf	  |  VLAN ID |  Ports  |
        +-------------+--------+-----------+
        |Ethernet68-72|	  lag1   |Port17-18|
        |Ethernet76-80|	  lag2	 |Port19-20|
        |Ethernet84-88|	  lag3	 |Port21-22|
        +=============+==========+=========+
        
        Output variables:
            self.lag{1~3}
            self.lag{1~3}_member{1~2}
            self.lag{1~3}_rif
        """
        print("Lag Configuration...")
        self.lag1 = sai_thrift_create_lag(self.client)
        self.def_lag_list.append(self.lag1)

        self.lag1_member1 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag1, pord_id=self.port17)
        self.def_lag_member_list.append(self.lag1_member1)
        self.lag1_member2 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag1, pord_id=self.port18)
        self.def_lag_member_list.append(self.lag1_member2)

        self.lag1_rif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.default_vrf,
            port_id=self.lag1)
        self.def_rif_list.append(self.lag1_rif)


        self.lag2 = sai_thrift_create_lag(self.client)
        self.def_lag_list.append(self.lag2)

        self.lag2_member1 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag2, pord_id=self.port19)
        self.def_lag_member_list.append(self.lag2_member1)
        self.lag2_member2 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag2, pord_id=self.port20)
        self.def_lag_member_list.append(self.lag2_member2)
        self.lag2_rif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.default_vrf,
            port_id=self.lag2)
        self.def_rif_list.append(self.lag2_rif)


        self.lag3 = sai_thrift_create_lag(self.client)
        self.def_lag_list.append(self.lag3)

        self.lag3_member1 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag3, pord_id=self.port21)
        self.def_lag_member_list.append(self.lag3_member1)
        self.lag3_member2 = sai_thrift_create_lag_member(
            self.client, lag_id=self.lag3, pord_id=self.port22)
        self.def_lag_member_list.append(self.lag3_member2)
        self.lag3_rif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
            virtual_router_id=self.default_vrf,
            port_id=self.lag3)
        self.def_rif_list.append(self.lag3_rif)


    def disable_lag_member_ingree_egress(self):
        print("Disable lag member ingress egress...")
        for lag_member in self.def_lag_member_list:
            sai_thrift_set_lag_member_attribute(self.client, lag_member, ingress_disable=True, egress_disable=True)


    def enable_lag_member_ingree_egress(self):
        print("Enable lag member ingress egress...")
        for lag in self.def_lag_member_list:
            sai_thrift_set_lag_member_attribute(self.client, lag_member, ingress_disable=False, egress_disable=False)


    def remove_rifs(self):
        print("Teardown rif...")
        for rif in self.def_rif_list:
            sai_thrift_remove_router_interface(self.client, rif)


    def remove_lag_members(self):
        print("Teardown lag...")
        for lag_member in self.def_lag_member_list:
            sai_thrift_remove_lag_member(self.client, lag_member)


    def remove_lags(self):
        print("Teardown lag member...")
        for lag in self.def_lag_list:
            sai_thrift_remove_lag(self.client, lag)

    def check_load_balance(self):
        """
         #How to check if each port of Lag receive an equal number of packets (if we have n members in a Lag)
        self.packet_numbers =100
        for i in range(0, n):
            self.assertTrue((count[i] >= ((self.packet_numbers / n) * 0.7)),
        """
        #To do
        pass


    def config_vlan(self):
        """
        set some basic configuration for vlan, its members and vlan interface

        Common ports configuration:
        +===============+==========+=========+==========+
        |    HostIf	    |  VLAN ID |  Ports  | Tag mode |
        +---------------+----------+---------+----------+
        | Ethernet 4-32 |	1000   | Port1-8 |  Untag   |
        | Ethernet36-64 |   2000   | Port9-16|  Untag   |
        +===============+==========+=========+==========+
        
        +==========+====================+====================+
        |  VLAN ID |  Vlan Interface IP | Vlan Interface MAC |
        +----------+--------------------+--------------------+
        |	1000   |     192.168.10.1   |  10:00:01:11:11:11 |
        |   2000   |     192.168.20.1   |  20:00:01:22:22:22 |
        +==========+====================+====================+

        Output variables:
        self.vlan1000/2000
        self.vlan_member
        self.lag{1~3}_rif
        """
        print("Vlan Configuration...")
        # create vlan 1000 with port1, port8
        self.vlan1000 = sai_thrift_create_vlan(self.client, vlan_id=1000)
        self.vlan2000 = sai_thrift_create_vlan(self.client, vlan_id=2000)

        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_vlan_list.append(self.vlan1000)
        self.def_vlan_list.append(self.vlan2000)

        for i in range(1, 9):
            vlan_member = sai_thrift_create_vlan_member(
            self.client,
            vlan_id=self.vlan1000,
            bridge_port_id=self.port_to_hostif_map[i],
            vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_UNTAGGED)
            setattr(self, 'vlan1000_member%s_' % i, vlan_member)
            self.def_vlan_member_list.append(self.vlan_member)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            sai_thrift_set_port_attribute(self.client, self.port_list[i], port_vlan_id=1000)

        for i in range(9, 17):
            vlan_member = sai_thrift_create_vlan_member(
            self.client,
            vlan_id=self.vlan2000,
            bridge_port_id=self.port_to_hostif_map[i],
            vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_UNTAGGED)
            setattr(self, 'vlan2000_member%s_' % (i-8), vlan_member)
            self.def_vlan_member_list.append(self.vlan_member)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            sai_thrift_set_port_attribute(self.client, self.port_list[i], port_vlan_id=2000)


    def create_vlan_interface(self):
        print("Create vlan interface...")
        self.vlan1000_rif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
            virtual_router_id=self.default_vrf,
            vlan_id=self.vlan1000)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_rif_list.append(self.vlan1000_rif)
        self.vlan1000_rifnh = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress('192.168.10.1'),
            router_interface_id=self.vlan1000_rif, type=CPU_PORT)


        self.vlan2000_rif = sai_thrift_create_router_interface(
            self.client,
            type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
            virtual_router_id=self.default_vrf,
            vlan_id=self.vlan2000)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_rif_list.append(self.vlan2000_rif)
        self.vlan2000_rifnh = sai_thrift_create_next_hop(
            self.client, ip=sai_ipaddress('192.168.20.1'),
            router_interface_id=self.vlan2000_rif, type=CPU_PORT)

    def create_port_router_interface(self):
        print("Create port router interface and neighbor entry ...")
        for i in range(1, 33):
            if i <= 8:
                ip_str = '192.168.10.1{}'.format(i)
                mac_str = '10:00:{0}{0}:{0}{0}:{0}{0}:{0}{0}'.format(i)
                rif = sai_thrift_create_router_interface(
                    self.client, type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                    port_id=self.port_list[i], virtual_router_id=self.default_vrf) 
                rifnh = sai_thrift_create_next_hop(
                    self.client, ip=sai_ipaddress(ip_str),
                    router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
                neighbor_entry = sai_thrift_neighbor_entry_t(
                        rif_id=self.rif, 
                        ip_address=sai_ipaddress(ip_str),
                        dst_mac_address=mac_str)
            elif i <= 16:
                ip_str = '192.168.20.1{}'.format(i-8)
                mac_str = '20:00:{0}{0}:{0}{0}:{0}{0}:{0}{0}'.format(i-8)
                rif = sai_thrift_create_router_interface(
                    self.client, type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                    port_id=self.port_list[i], virtual_router_id=self.default_vrf) 
                rifnh = sai_thrift_create_next_hop(
                    self.client, ip=sai_ipaddress(ip_str),
                    router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
                neighbor_entry = sai_thrift_neighbor_entry_t(
                    rif_id=self.rif, 
                    ip_address=sai_ipaddress(ip_str),
                    dst_mac_address=mac_str)
            else:
                ip_str = '192.168.0.{}'.format(i)
                mac_str = '00:00:{0}{0}:{0}{0}:{0}{0}:{0}{0}'.format(('%01x' % i))
                rif = sai_thrift_create_router_interface(
                    self.client, type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                    port_id=self.port_list[i], virtual_router_id=self.default_vrf) 
                rifnh = sai_thrift_create_next_hop(
                    self.client, ip=sai_ipaddress(ip_str),
                    router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
                neighbor_entry = sai_thrift_neighbor_entry_t(
                    rif_id=self.rif, 
                    ip_address=sai_ipaddress(ip_str),
                    dst_mac_address=mac_str)
            setattr(self, 'nb%s' % (i), neighbor_entry)


    def create_port_neighbor(self):
        print("Create lag router interface and neighbor entry ...")
        nhop = sai_thrift_create_next_hop(self.client,
            ip=sai_ipaddress('192.168.0.11'),
            router_interface_id=self.lag1_rif,
            type=SAI_NEXT_HOP_TYPE_IP)
        neighbor_entry = sai_thrift_neighbor_entry_t(
            rif_id=self.lag1_rif, ip_address=sai_ipaddress('192.168.0.11'))
        self.lag1_nb = sai_thrift_create_neighbor_entry(self.client, neighbor_entry,
            dst_mac_address='00:11:11:11:11:11')
        self.def_nb_list.append(self.lag1_nb)
        route1 = sai_thrift_route_entry_t(
            vr_id=self.default_vrf, destination=sai_ipprefix('192.168.0.11/32'))
        sai_thrift_create_route_entry(self.client, route1, next_hop_id=nhop)

        nhop = sai_thrift_create_next_hop(self.client,
            ip=sai_ipaddress('192.168.0.12'),
            router_interface_id=self.lag1_rif,
            type=SAI_NEXT_HOP_TYPE_IP)
        neighbor_entry = sai_thrift_neighbor_entry_t(
            rif_id=self.lag2_rif, ip_address=sai_ipaddress('192.168.0.12'))
        self.lag2_nb = sai_thrift_create_neighbor_entry(self.client, neighbor_entry,
            dst_mac_address='00:00:22:22:22:22')
        self.def_nb_list.append(self.lag2_nb)
        route2 = sai_thrift_route_entry_t(
            vr_id=self.default_vrf, destination=sai_ipprefix('192.168.0.12/32'))
        sai_thrift_create_route_entry(self.client, route2, next_hop_id=nhop)

        nhop = sai_thrift_create_next_hop(self.client,
            ip=sai_ipaddress('192.168.0.13'),
            router_interface_id=self.lag1_rif,
            type=SAI_NEXT_HOP_TYPE_IP)
        neighbor_entry = sai_thrift_neighbor_entry_t(
            rif_id=self.lag3_rif, ip_address=sai_ipaddress('192.168.0.13'))
        self.lag3_nb = sai_thrift_create_neighbor_entry(self.client, neighbor_entry,
            dst_mac_address='00:00:33:33:33:33')
        self.def_nb_list.append(self.lag3_nb)
        route3 = sai_thrift_route_entry_t(
            vr_id=self.default_vrf, destination=sai_ipprefix('192.168.0.13/32'))
        sai_thrift_create_route_entry(self.client, route3, next_hop_id=nhop)
        


    def create_neighbor_entry(self):
        print("Create neighbor entry...")
        self.vlan1000_nb_entry = sai_thrift_neighbor_entry_t(
            rif_id=self.vlan1000_rif, 
            ip_address=sai_ipaddress('192.168.10.255'),
            dst_mac_address='FF:FF:FF:FF:FF:FF')
        self.def_nb_list

        self.vlan2000_nb_entry = sai_thrift_neighbor_entry_t(
            rif_id=self.vlan2000_rif, 
            ip_address=sai_ipaddress('192.168.20.255'),
            dst_mac_address='FF:FF:FF:FF:FF:FF')

    def create_bridge_port(self):
        print("Create bridege port on port1-16...")
        for i in range(1, 17):
            port_bp = sai_thrift_create_bridge_port(
            self.client,
            bridge_id=self.default_1q_bridge,
            port_id=self.port_list[i],
            type=SAI_BRIDGE_PORT_TYPE_PORT,
            admin_state=True)
            setattr(self, 'port%s_bp' % i, port_bp)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.port_to_bp_map[i] = port_bp
        

    def disable_mac_learn(self):
        print("Disble Vlan mac learning...")
        for vlan in self.def_vlan_list:
            sai_thrift_set_vlan_attribute(self.client, vlan, learn_disable=False)


    def enable_mac_learn(self):
        print("Enable Vlan mac learning...")
        for vlan in self.def_vlan_list:
            sai_thrift_set_vlan_attribute(self.client, vlan, learn_disable=True)


    def set_native_vlan(self, port_id=None, port_vlan_id=None):
        print("Set Native vlan 1000 on a port...")
        sai_thrift_set_port_attribute(self.client, port_id, port_vlan_id)


    def clear_vlan_counters(self):
        print("Clear Vlan counters...")
        for vlan in self.def_vlan_list:
            sai_thrift_clear_vlan_stats(self.client, vlan)


    def remove_vlan_members(self):
        print("Teardown lags...")
        for vlan_member in self.def_vlan_member_list:
            sai_thrift_remove_vlan_member(self.client, vlan_member)


    def remove_vlans(self):
        print("Teardown lag members...")
        for vlan in self.def_vlan_list:
            sai_thrift_remove_vlan(self.client, vlan)


    def remove_hostifs(self):
        print("Teardown host interfaces...")
        for hostif in self.def_hostif_list:
            sai_thrift_remove_hostif(self.client, hostif)