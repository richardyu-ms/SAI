import os
import time
import sys
import inspect

from config.constant import *
from sai_thrift.sai_adapter import *
from sai_base_utils import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]

class FdbT0Config(object):
    """
    Class use to make all the fdb configurations.
    """
    def generate_fdb_mac_address_list(self, test):
        test.mac_list = []
        print("Generate mac address...")
        test.mac0 = '00:00:00:00:00:11' 
        test.mac_list.append(test.mac0)

        for i in range(1, 32):  
            tmp = i % 16
            cnt = i // 16
            str1 = '{:x}'.format(tmp) * 10
            str2 = '{:02}'.format(cnt)
            mac = str2 + str1
            mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            setattr(test, 'mac%s' % i, mac)
            test.mac_list.append(mac)


    def create_fdb_entries(self, test):
        """
        Create fdb entries according to below table:
        +==========+=====================================+==========+======+=======================+
        |   Name   |                 MAC                 |	PORT    | VLAN |         HostIf        |
        +----------+-------------------------------------+----------+------+-----------------------+
        |   mac0   |      00:00:00:00:00:11              | Port0    |      |        Ethernet0      | 
        |  mac1-8  |00:11:11:11:11:11 - 00:88:88:88:88:88| Port1-8  | 1000 | Ethernet4-Ethernet32  |
        |  mac9-16 |00:99:99:99:99:99 - 01:00:00:00:00:00| Port9-16 | 2000 | Ethernet36-Ethernet64 |
        | mac17-31 |01:11:11:11:11:11 - 01:ff:ff:ff:ff:ff| Port17-31|      |                       |
        +==========+=====================================+==========+======+=======================+
        """
        print("Create fdb config for L2 testing...")
        self.generate_fdb_mac_address_list(test)
        for i in range(0, 32):
            fdb_entry = sai_thrift_fdb_entry_t(
                switch_id=test.switch_id, 
                mac_address= test.mac_list[i], 
                bv_id=test.vlan10 if i >= 1 and i <= 8 else test.vlan20 if i <= 16 else None)
            sai_thrift_create_fdb_entry(
                test.client,
                fdb_entry,
                type=SAI_FDB_ENTRY_TYPE_STATIC,
                bridge_port_id=test.bridge_port_list[i],
                packet_action=SAI_PACKET_ACTION_FORWARD)
            
