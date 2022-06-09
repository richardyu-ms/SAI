from doctest import testfile
import os
import time
import sys
import inspect

from config.constant import *
from sai_thrift.sai_adapter import *
from sai_base_utils import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]

class VlanT0Config(object):
    """
    Class use to make all the vlan configurations.
    """

    def vlan_config(self, test):
        """
        Common ports configuration:
        +===============+==========+=========+==========+
        |    HostIf     |  VLAN ID |  Ports  | Tag mode |
        +---------------+----------+---------+----------+
        | Ethernet 4-32 |    10    | Port1-8 |  Untag   |
        | Ethernet36-64 |    20    | Port9-16|  Untag   |
        +===============+==========+=========+==========+
        
        +==========+====================+====================+
        |  VLAN ID |  Vlan Interface IP | Vlan Interface MAC |
        +----------+--------------------+--------------------+
        |    10    |    192.168.10.1    |  10:00:01:11:11:11 |
        |    20    |    192.168.20.1    |  20:00:01:22:22:22 |
        +==========+====================+====================+

        Output variables:
        self.vlan10/20
        self.vlan_member
        """
        test.vlan_list = []
        test.vlan_member_list = []
        self.config_vlan(test, [10, 20])
        self.config_vlan_member(test, test.vlan10, 1, 8)
        self.config_vlan_member(test, test.vlan20, 9, 16)
        # self.config_vlan_intf(test, )


    def config_vlan(self, test, vlan_id_list):
        for vlan_id in vlan_id_list:
            vlan_oid = sai_thrift_create_vlan(test.client, vlan_id=vlan_id)
            test.vlan_list.append(vlan_oid)
            setattr(test, 'vlan%s' % (vlan_id), vlan_oid)


    def config_vlan_member(self, test, vlan_oid, port_start, port_end):
        attr = sai_thrift_get_vlan_attribute(test.client, vlan_oid, vlan_id=True)
        vlan_id = attr['vlan_id']
        for port_index in range(port_start, port_end):
            vlan_member = sai_thrift_create_vlan_member(test.client,
                vlan_id = vlan_oid, 
                bridge_port_id=test.bridge_port_list[port_index],
                vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_UNTAGGED)
            test.vlan_member_list.append(vlan_member)
            sai_thrift_set_port_attribute(test.client, test.port_list[port_index], port_vlan_id=vlan_id)


    def remove_vlan_members(self, test):
        print("Teardown lags...")
        for vlan_member in test.vlan_member_list:
            sai_thrift_remove_vlan_member(test.client, vlan_member)


    def remove_vlans(self, test):
        print("Teardown lag members...")
        for vlan in test.vlan_list:
            sai_thrift_remove_vlan(test.client, vlan)