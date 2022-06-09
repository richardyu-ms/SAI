from t0_base_test import SaiT0HelperBase
from sai_thrift.sai_headers import *
from ptf import config
from ptf.base_tests import BaseTest
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
import time

class InitBasicData(SaiT0HelperBase):
    """
    This is a test class use to trigger some basic verification when set up the basic t0 data configuration.
    """
    #Todo remove this class when T0 data is ready, this class should not be checked into repo
    def setUp(self):
        """
        Test the basic setup proecss
        """
        #this process contains the switch_init process
        SaiT0HelperBase.setUp(self)

    def runTest(self):
        """
        Test the basic runTest proecss
        """
        pass

    def tearDown(self):
        """
        Test the basic tearDown proecss
        """
        pass

class L2FdbForwardingTest(SaiT0HelperBase):
    """
    Verify L2 fdb functionilty
    """
    #Todo remove this class when T0 data is ready, this class should not be checked into repo
    def setUp(self):
        """
        Test the basic setup proecss
        """
        #this process contains the switch_init process
        SaiT0HelperBase.setUp(self)
        print("Sending L2 packet port 1 -> port 2")

        self.pkt = simple_tcp_packet(eth_dst=self.mac2,
                                    eth_src=self.mac1,
                                    ip_dst='172.16.0.1',
                                    ip_id=101,
                                    ip_ttl=64)
            
    def runTest(self):
        """
        Test the basic runTest proecss
        """
        # disable VLAN1000 learning
        # status = sai_thrift_set_vlan_attribute(
        #     self.client, self.vlan1000, learn_disable=True)
        # self.assertEqual(status, SAI_STATUS_SUCCESS)
        # print("MAC Learning disabled on VLAN")
        
        print("Sending packet on port %d, %s -> %s - will flood" %
                (self.port_list[1], self.mac1, self.mac2))
        try:
            send_packet(self, 1, self.pkt)
            time.sleep(5)
            verify_packet(self, self.pkt, 2)

            print("Verification complete")
        finally:
            pass

    def tearDown(self):
        """
        Test the basic tearDown proecss
        """
        pass