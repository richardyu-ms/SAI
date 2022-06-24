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
from time import sleep

from sai_test_base import T0TestBase
from sai_thrift.sai_headers import *
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from sai_utils import *

class Vlan_Domain_Forwarding_Test(T0TestBase):
    """
    Verify the basic VLAN forwarding.
    In L2, if segement with VLAN tag and sends to a VLAN port, 
    segment should be forwarded inside a VLAN domain.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self, is_reset_default_vlan=False)

    def runTest(self):
        """
        Test VLAN forwarding
        """
        try:
            print("VLAN forwarding test.")
            for index in range(2, 9):
                print("Forwarding in VLAN {} from {} to port: {}".format(
                    10,
                    self.dev_port_list[1], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[1],
                                        vlan_vid=10,
                                        ip_id=101,
                                        ip_ttl=64)
                    
                send_packet(self, self.dev_port_list[1], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])
            for index in range(10, 17):
                print("Forwarding in VLAN {} from {} to port: {}".format(
                    20,
                    self.dev_port_list[9], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[9],
                                        vlan_vid=20,
                                        ip_id=101,
                                        ip_ttl=64)
                send_packet(self, self.dev_port_list[9], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(
            self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)


class UntagAccessToAccessTest(T0TestBase):
    """
    This test verifies the VLAN function around untag and access ports.
    """
    def setUp(self):
        super().setUp()


    def runTest(self):
        """
        Forwarding between tagged ports with untagged pkt
        """
        print("\nUntagAccessToAccessTest()")
        try:
            for index in range(2, 9):
                print("Sending untagged packet from vlan10 tagged port {} to vlan10 tagged port: {}".format(
                    self.dev_port_list[1], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[1],
                                        ip_id=101,
                                        ip_ttl=64)

                send_packet(self, self.dev_port_list[1], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])
            for index in range(10, 17):
                print("Sending untagged packet from vlan20 tagged port {} to vlan20 tagged port: {}".format(
                    self.dev_port_list[9], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[9],
                                        ip_id=101,
                                        ip_ttl=64)

                send_packet(self, self.dev_port_list[9], pkt)
                verify_packet(self, pkt, self.dev_port_list[index])

        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)

        super().tearDown()


class MismatchDropTest(T0TestBase):
    """
    This test verifies the VLAN function around untag and access ports.
    """
    def setUp(self):
        super().setUp()

    def runTest(self):
        """
        Dropping between tagged ports with mismatched tagged pkt
        """
        print("\nUnmatchDropTest()")
        try:
            for index in range(1, 9):
                print("Sending vlan20 tagged packet from vlan20 tagged port {} to vlan10 tagged port: {}".format(
                    self.dev_port_list[9], 
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[9],
                                        vlan_vid=20,
                                        ip_id=101,
                                        ip_ttl=64)

                send_packet(self, self.dev_port_list[9], pkt)
                verify_no_other_packets(self, timeout=1)
            for index in range(9, 17):
                print("Sending vlan10 tagged packet from {} to vlan20 tagged port: {}".format(
                    self.dev_port_list[1],
                    self.dev_port_list[index]))
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[index],
                                        eth_src=self.local_server_mac_list[1],
                                        vlan_vid=10,
                                        ip_id=101,
                                        ip_ttl=64)

                send_packet(self, self.dev_port_list[1], pkt)
                verify_no_other_packets(self, timeout=1)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)

        super().tearDown()


class TaggedFrameFilteringTest(T0TestBase):
    """
    Drop tagged packet when the destination port from MAC table search is the port which packet comes into the switch.
    """
    def setUp(self):
        super().setUp()
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        self.port1_mac_list = {1,5}
        self.mac_action = SAI_PACKET_ACTION_FORWARD
        for mac_id in self.port1_mac_list:
            self.create_fdb_entry(self.local_server_mac_list[mac_id])

    def runTest(self):
        print("\nTaggedFrameFilteringTest")
        try:
            for mac_id in self.port1_mac_list:
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[mac_id],
                                        eth_src=self.local_server_mac_list[1],
                                        vlan_vid=10,
                                        ip_id=101,
                                        ip_ttl=64)
                send_packet(self, self.dev_port_list[1], pkt)
                verify_no_other_packets(self, timeout=1)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)

        super().tearDown()

    def create_fdb_entry(self,mac_address_):
        """
        create fdb entry
        Args:
            mac_address_: mac_address
        """
        fdb_entry = sai_thrift_fdb_entry_t(
            switch_id=self.switch_id, mac_address=mac_address_, bv_id=10)
        sai_thrift_create_fdb_entry(
            self.client,
            fdb_entry,
            type=SAI_FDB_ENTRY_TYPE_STATIC,
            bridge_port_id=self.dev_port_list[1],
            packet_action=self.mac_action)


class UnTaggedFrameFilteringTest(T0TestBase):
    """
    Drop untagged packet when the destination port from MAC table search
    is the port which packet comes into the switch.
    """
    def setUp(self):
        super().setUp()
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        self.port1_mac_list = {1,5}
        self.mac_action = SAI_PACKET_ACTION_FORWARD
        for mac_id in self.port1_mac_list:
            self.create_fdb_entry(self.local_server_mac_list[mac_id])

    def runTest(self):
        print("\nUnTaggedFrameFilteringTest")
        try:
            for mac_id in self.port1_mac_list:
                pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[mac_id],
                                        eth_src=self.local_server_mac_list[1],
                                        ip_id=101,
                                        ip_ttl=64)
                send_packet(self, self.dev_port_list[1], pkt)
                verify_no_other_packets(self, timeout=1)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)

        super().tearDown()

    def create_fdb_entry(self,mac_address_):
        fdb_entry = sai_thrift_fdb_entry_t(
            switch_id=self.switch_id, mac_address=mac_address_, bv_id=10)
        sai_thrift_create_fdb_entry(
            self.client,
            fdb_entry,
            type=SAI_FDB_ENTRY_TYPE_STATIC,
            bridge_port_id=self.dev_port_list[1],
            packet_action=self.mac_action)


class TaggedVlanFloodingTest(T0TestBase):
    """
    For mac flooding in the VLAN scenario, before learning the mac address from the packet,
    the packet sent to the VLAN port will flood to other ports, and the egress ports
    will be in the same VLAN as the ingress port.
    """
    def setUp(self):
       super().setUp()

    def runTest(self):
        print("\nTaggedVlanFloodingTest")
        try:
            macX = 'EE:EE:EE:EE:EE:EE'
            pkt = simple_udp_packet(eth_dst=macX,
                                    eth_src=self.local_server_mac_list[1],
                                    vlan_vid=10,
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], pkt)
            other_ports = self.dev_port_list[1:8]
            verify_packet_any_port(self,pkt,other_ports)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)

        super().tearDown()


class UnTaggedVlanFloodingTest(T0TestBase):
    """
    UnTaggedVlanFloodingTest
    For mac flooding in the VLAN scenario, before learning the mac address from the packet,
    the packet sent to the VLAN port will flood to other ports, and the egress ports
    will be in the same VLAN as the ingress port.
    """
    def setUp(self):
        super().setUp()

    def runTest(self):
        print("\nUnTaggedVlanFloodingTest")
        try:
            macX = 'EE:EE:EE:EE:EE:EE'
            pkt = simple_udp_packet(eth_dst=macX,
                                    eth_src=self.local_server_mac_list[1],
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], pkt)
            other_ports = self.dev_port_list[1:8]
            verify_packet_any_port(self,pkt,other_ports)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        super().tearDown()


class BroadcastTest(T0TestBase):
    """
    Drop untagged packet when the destination port from MAC table search
    is the port which packet comes into the switch.
    """
    def setUp(self):
        super().setUp()

    def runTest(self):
        print("\nBroadcastTest")
        try:
            macX = 'FF:FF:FF:FF:FF:FF'
            #untag
            untagged_pkt = simple_udp_packet(eth_dst=macX,
                                    eth_src=self.local_server_mac_list[1],
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], untagged_pkt)
            other_ports = self.dev_port_list[1:8]
            verify_packet_any_port(self,untagged_pkt,other_ports)
            #tag
            tagged_pkt = simple_udp_packet(eth_dst=macX,
                                    eth_src=self.local_server_mac_list[1],
                                    vlan_vid=10,
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], tagged_pkt)
            other_ports = self.dev_port_list[1:8]
            verify_packet_any_port(self,tagged_pkt,other_ports)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        super().tearDown()


class UntaggedMacLearningTest(T0TestBase):
    """
    For mac learning in the VLAN scenario, after learning the mac address 
    from the packet, the packet sent to the VLAN port will only send to the 
    port whose MAC address matches the MAC table entry.
    """
    def setUp(self):
        super().setUp()

    def runTest(self):
        print("\nUntaggedMacLearningTest")
        try:
            available_fdb_entry_cnt_past = sai_thrift_get_switch_attribute(
                                                    self.client,
                                                    available_fdb_entry=True)['available_fdb_entry']
            macX = '00:01:01:99:01:99'
            #untag
            untagged_pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[2],
                                    eth_src=macX,
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], untagged_pkt)
            verify_packet(self, untagged_pkt, self.dev_port_list[2])
            sleep(2)  #wait for add mac entry
            available_fdb_entry_cnt_now = sai_thrift_get_switch_attribute(
                                                    self.client,
                                                    available_fdb_entry=True)['available_fdb_entry']
            self.assertEqual(available_fdb_entry_cnt_now-available_fdb_entry_cnt_past,-1)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        super().tearDown()

class TaggedMacLearningTest(T0TestBase):
    """
    For mac learning in the VLAN scenario, after learning the mac address
    from the packet, the packet sent to the VLAN port will only send to the
    port whose MAC address matches the MAC table entry.
    """
    def setUp(self):
        super().setUp()

    def runTest(self):
        print("\nTaggedMacLearningTest")
        try:
            available_fdb_entry_cnt_past = sai_thrift_get_switch_attribute(
                                                    self.client,
                                                    available_fdb_entry=True)['available_fdb_entry']
            macX = '00:01:01:99:01:99'
            tagged_pkt = simple_udp_packet(eth_dst=self.local_server_mac_list[2],
                                    eth_src=macX,
                                    vlan_vid=10,
                                    ip_id=101,
                                    ip_ttl=64)
            send_packet(self, self.dev_port_list[1], tagged_pkt)
            verify_packet(self, tagged_pkt, self.dev_port_list[2])
            sleep(2)  #wait for add mac entry
            available_fdb_entry_cnt_now = sai_thrift_get_switch_attribute(
                                                    self.client,
                                                    available_fdb_entry=True)['available_fdb_entry']
            self.assertEqual(available_fdb_entry_cnt_now-available_fdb_entry_cnt_past,-1)
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown process
        """
        sai_thrift_flush_fdb_entries(self.client, entry_type=SAI_FDB_FLUSH_ENTRY_TYPE_ALL)
        super().tearDown()
