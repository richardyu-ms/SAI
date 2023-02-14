# Copyright 2021-present Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This file contains base classes for PTF test cases as well as a set of
additional useful functions.

Tests will usually inherit from one of the base classes to have the controller
and/or dataplane automatically set up.
"""
import os
import time
import inspect
from threading import Thread

from collections import OrderedDict
from unittest import SkipTest

from ptf import config
from ptf.base_tests import BaseTest

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from sai_thrift import sai_rpc
import LogConfig
from data_module.port import Port

from sai_utils import *
import sai_thrift.sai_adapter as adapter

from config.port_configer import PortConfiger
from config.config_db_loader import ConfigDBLoader
from config.port_config_ini_loader import PortConfig, PortConfigInILoader

ROUTER_MAC = '00:77:66:55:44:00'
THRIFT_PORT = 9092

SKIP_TEST_NO_RESOURCES_MSG = 'Not enough resources to run test'
PLATFORM = os.environ.get('PLATFORM')
platform_map = {'broadcom': 'brcm', 'barefoot': 'bfn',
                'mellanox': 'mlnx', 'common': 'common'}


class ThriftInterface(BaseTest):
    """
    Get and format a port map, retrieve test params, and create an RPC client

    Have the following class attributes:
        port_map_loaded: If the Port map loaded when Test init
        transport: Thrift socket object
        test_reboot_mode: reboot mode, which will be read from system env
        test_reboot_stage: reboot stage, which will be read from system env
        test_params: All the values passed via test-params if present
        interface_to_front_mapping: Config from port_map_file for the interface (local) to front(PTF) mapping 
        protocol: Thrift protocol object
        client: RPC client which used in Thrift
    """

    def __init__(self, *args, **kwargs):
        """
        Init ThriftInterface.

        Set the following class attributes:
            port_map_loaded: If the Port map loaded when Test init
            transport: Thrift socket object
            test_reboot_mode: reboot mode, which will be read from system env
            test_reboot_stage: reboot stage, which will be read from system env
            test_params: All the values passed via test-params if present
            interface_to_front_mapping: Config from port_map_file for the interface (local) to front(PTF) mapping 
            protocol: Thrift protocol object
            client: RPC client which used in Thrift
        """
        super().__init__(*args, **kwargs)
        self.port_map_loaded = False
        """
        If the Port map loaded when Test init
        """

        self.transport = None
        """
        Thrift socket object
        """

        self.test_reboot_mode = None
        """
        reboot mode, which will be read from system env
        """
        self.test_reboot_stage = None
        """
        reboot stage, which will be read from system env
        """

        self.interface_to_front_mapping = {}
        """
        Config from port_map_file for the interface (local) to front(PTF) mapping 
        """

        self.test_params = None
        """
        All the values passed via test-params if present
        """

        self.protocol = None
        """
        Thrift protocol object
        """

        self.client = None
        """
        RPC client which used in Thrift
        """


    def setUp(self):
        super(ThriftInterface, self).setUp()
        self.interface_to_front_mapping = {}
        self.port_map_loaded = False
        """
        If the Port map loaded when Test init
        """

        self.transport = None
        """
        Thrift socket object
        """

        self.test_reboot_mode = None
        """
        reboot mode, which will be read from system env
        """
        self.test_reboot_stage = None
        """
        reboot stage, which will be read from system env
        """

        self.interface_to_front_mapping = {}
        """
        Config from port_map_file for the interface (local) to front(PTF) mapping 
        """

        self.test_params = None
        """
        All the values passed via test-params if present
        """

        self.protocol = None
        """
        Thrift protocol object
        """

        self.client = None
        """
        RPC client which used in Thrift
        """


    def setUp(self):
        super(ThriftInterface, self).setUp()

        self.test_params = test_params_get()
        self.loadTestRebootMode()
        self.loadPortMap()
        self.createRpcClient()


    def loadTestRebootMode(self):
        """
        Get if test the reboot mode and what's the reboot mode need to be tested

        In reboot mode, test will run many times in different reboot stage.
        Tests in different stage might be different.

        Set the following class attributes:
            test_reboot_loaded - if the reboot mode already loaded
            test_reboot_mode - reboot mode
            test_reboot_stage - reboot stage, can be [setup|starting|post]
        """
        self.test_reboot_stage = None
        if "test_reboot_mode" in self.test_params:
            self.test_reboot_mode = self.test_params['test_reboot_mode']

        else:
            self.test_reboot_mode = 'cold'

        print("Reboot mode is: {}".format(self.test_reboot_mode))


    def tearDown(self):
        self.transport.close()
        super(ThriftInterface, self).tearDown()


    def loadPortMap(self):
        """
        Get and format port_map

        port_map_file is a port map with following lines format:
        [test_port_no]@[device_port_name]
        e.g.:
             0@Veth1
             1@Veth2
             2@Veth3  ...
        """
        if self.port_map_loaded:
            print("port_map already loaded")
            return

        if "port_map" in self.test_params:
            user_input = self.test_params['port_map']
            splitted_map = user_input.split(",")
            for item in splitted_map:
                iface_front_pair = item.split("@")
                self.interface_to_front_mapping[iface_front_pair[0]] =  \
                    iface_front_pair[1]
        elif "port_map_file" in self.test_params:
            user_input = self.test_params['port_map_file']
            with open(user_input, 'r') as map_file:
                for line in map_file:
                    if (line and (line[0] == '#' or
                                  line[0] == ';' or line[0] == '/')):
                        continue
                    iface_front_pair = line.split("@")
                    self.interface_to_front_mapping[iface_front_pair[0]] =  \
                        iface_front_pair[1].strip()

        self.port_map_loaded = True

    def createRpcClient(self):
        """
        Set up thrift client and contact RPC server
        """

        if 'thrift_server' in self.test_params:
            server = self.test_params['thrift_server']
        else:
            server = 'localhost'

        self.transport = TSocket.TSocket(server, THRIFT_PORT)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = sai_rpc.Client(self.protocol)
        self.transport.open()



class ThriftInterfaceDataPlane(ThriftInterface):
    """
    Sets up the thrift interface and dataplane

    class attributes:
        dataplane: Represent the dataplane used in test, pcap to manipulate the data
    """

    def __init__(self, *args, **kwargs):
        """
        Init ThriftInterfaceDataPlane

        Set the following class attributes:
            dataplane: Represent the dataplane used in test, pcap to manipulate the data
        """
        super().__init__(*args, **kwargs)
        self.dataplane = None
        """
        Represent the dataplane used in test, pcap to manipulate the data
        """


    def setUp(self, skip_reason = None):
        """
        Setup the ThriftInterfaceDataPlane.
        """
        super(ThriftInterfaceDataPlane, self).setUp()

        self.dataplane = ptf.dataplane_instance
        if self.dataplane is not None:
            self.dataplane.flush()
            if config['log_dir'] is not None:
                filename = os.path.join(config['log_dir'], str(self)) + ".pcap"
                self.dataplane.start_pcap(filename)


    def tearDown(self):
        if config['log_dir'] is not None:
            self.dataplane.stop_pcap()
        super(ThriftInterfaceDataPlane, self).tearDown()


class SaiHelperBase(ThriftInterfaceDataPlane):
    """
    SAI test helper base class without initial switch ports setup

    Set the following class attributes:
        self.default_vlan_id
        self.default_vrf
        self.default_1q_bridge
        self.cpu_port_hdl
        self.active_ports_no - number of active ports
        self.port_list - list of all active port objects
        self.portX objects for all active ports (where X is a port number)
        self.port_configer for config ports
    """

    platform = 'common'

    def __init__(self, *args, **kwargs):
        """
        Init the T0 Test Object.
        Set the following class attributes:
            dut: Dut object in test.
            servers: Simulating the server Objects in Test.
            t1_list: Simulating the T1 objects in test

        """
        super().__init__(*args, **kwargs)
        self.default_vlan_id = None
        self.default_vrf = None
        self.default_1q_bridge = None
        self.cpu_port_hdl = None
        self.active_ports_no: int = 0
        """
        Device active ports.
        """

        self.active_port_obj_list: List['Port'] = []
        """
        Device active port obj list.
        Those ports might more than actual port in testing.
        For ports in testing, please use port_obj_list.
        """        
        self.port_list: List = []
        self.port_configer: PortConfiger = None
        self.config_db_loader: ConfigDBLoader = None
        self.port_config_ini_loader: PortConfigInILoader = None
        # TODO: Below two attributes should be move to port_configer
        self.ports_config: Dict = None
        """
        ports_config dict, use to compatiable with old data module
        """
        self.portConfigs: List[PortConfig] = None
        """
        PortConfig object List
        """
        self.bridge_port_list = []
        """
        Bridge port list
        """
        self.def_bridge_port_list = []
        self.def_vlan_member_list = []


    def set_logger_name(self):
        """
        Set Logger name as filename:classname
        """

        file_name = inspect.getfile(self.__class__)
        class_name = self.__class__.__name__
        logger_name = "{}:{}".format(file_name, class_name)
        LogConfig.set_logging(loggerName = logger_name)


    def get_active_port_list(self):
        '''
        Method to get the active port list base on number_of_active_ports

        Sets the following class attributes:

            self.active_ports_no - number of active ports

            self.port_list - list of all active port objects

            self.portX objects for all active ports
        '''

        # get number of active ports
        attr = sai_thrift_get_switch_attribute(
            self.client, number_of_active_ports=True)
        self.active_ports_no = attr['number_of_active_ports']

        # get port_list and portX objects
        attr = sai_thrift_get_switch_attribute(
            self.client, port_list=sai_thrift_object_list_t(
                idlist=[], count=self.active_ports_no))
        self.assertEqual(self.active_ports_no, attr['port_list'].count)
        self.port_list = attr['port_list'].idlist

        #Gets self.portX objects for all active ports
        for i, _ in enumerate(self.port_list):
            setattr(self, 'port%s' % i, self.port_list[i])

    def config_port(self):
        '''
        Method to config the ports.
        '''
        if get_platform() == 'brcm':
            self.config_brcm_port()
        else:
            self.config_bfn_port()


    def config_bfn_port(self):
        self.turn_up_and_check_ports()
        # get default 1Q bridge OID
        self.get_default_1q_bridge_id()

        #remove all default 1Q bridge port
        self.reset_1q_bridge_ports()

    # Port setup method below

    def config_brcm_port(self):

        self.port_list = self.port_configer.get_lane_sorted_port_list()
        self.port_configer.generate_port_obj_list_by_interface_config()
        self.port_configer.assign_port_config(self.port_config_ini_loader.portConfigs)
        self.port_configer.assign_config_db(
            self.config_db_loader.port_config,
            self.port_config_ini_loader.portConfigs)

        attr = sai_thrift_get_switch_attribute(
            self.client, default_trap_group=True)
        default_trap_group = attr['default_trap_group']
        self.port_configer.set_port_attribute(self.active_port_obj_list)
        self.port_obj_list = self.port_configer.turn_up_and_get_checked_ports(
            self.active_port_obj_list)
        #compatiable with portx variables
        self.get_port_id_list = self.port_configer.get_port_id_list(self.port_obj_list)
        self.port_configer.set_test_port_attr(self.port_list)

        if 'port_config_ini' in self.test_params:
            host_intf_table_id, hostif_list = self.port_configer.create_port_hostif_by_port_config_ini(
                port_list=self.active_port_obj_list, trap_group=default_trap_group)
        else:
            host_intf_table_id, hostif_list = self.port_configer.create_host_intf(
                port_list=self.active_port_obj_list, trap_group=default_trap_group)
        self.host_intf_table_id = host_intf_table_id
        self.hostif_list = hostif_list

        self.default_1q_bridge = self.port_configer.get_default_1q_bridge()
        self.port_configer.reset_1q_bridge_ports()


    def turn_up_and_check_ports(self):
        '''
        Method to turn up the ports.
        In case some device not init the port after start the switch.

        Args:
            port_list - list of all active port objects
        '''
        #TODO check if this is common behivor or specified after check on more platform
        print("For Common platform, Only check Port status.")
        

        # For brcm devices, need to init and setup the ports at once after start the switch.
        retries = 10
        down_port_list = []
        for index, oid in enumerate(self.port_list):
            port_attr = sai_thrift_get_port_attribute(
                self.client, oid, oper_status=True)
            print("Turn up port {}".format(oid))
            port_up = True
            if port_attr['oper_status'] != SAI_PORT_OPER_STATUS_UP:
                port_up = False
                for num_of_tries in range(retries):
                    port_attr = sai_thrift_get_port_attribute(
                        self.client, oid, oper_status=True)
                    if port_attr['oper_status'] == SAI_PORT_OPER_STATUS_UP:
                        port_up = True
                        break
                    time.sleep(5)
                    print("port {}:{} is not up, status: {}. Retry. Waiting for Admin State Up.".format(
                        index, oid, port_attr['oper_status']))
            if not port_up:
                down_port_list.append(index)
        if down_port_list:
            print("Ports {} are  down after retries.".format(down_port_list))


    def shell(self):
        '''
        Method use to start a sai shell in a thread.
        '''
        def start_shell():
            sai_thrift_set_switch_attribute(self.client, switch_shell_enable=True)
        thread = Thread(target = start_shell)
        thread.start()


    def recreate_ports(self):
        '''
        Recreate the port base on file specified in 'port_config_ini' param.
        '''
        #TODO check if this is common behivor or specified after check on more platform
        if 'port_config_ini' in self.test_params:
            if 'createPorts_has_been_called' not in config:
                #self.createPorts()
                # check if ports became UP
                #self.checkPortsUp()
                config['createPorts_has_been_called'] = 1


    def get_default_1q_bridge_id(self):
        '''
        Gets default 1q bridge 1d, set it to class attribute 'default_1q_bridge'.

        Sets the following class attributes:

            self.default_1q_bridge - default_1q_bridge_id
        '''

        attr = sai_thrift_get_switch_attribute(
            self.client, default_1q_bridge_id=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.default_1q_bridge = attr['default_1q_bridge_id']


    def reset_1q_bridge_ports(self):
        '''
        Reset all the 1Q bridge ports.
        Needs the following class attributes:
            self.default_1q_bridge - default_1q_bridge oid

            self.active_ports_no - number of active ports

            self.portX objects for all active ports
        '''
        #TODO check if this is common behivor or specified after check on more platform
        #TODO move this function to CommonSaiHelper
        print("For Common platform, expecting bridge ports not been created by default.")


    def check_cpu_port_hdl(self):
        """
        Checks cpu port handler.
        Expect the cpu_port_hdl equals to qos_queue port id, number_of_queues in qos equals to queue index.

        Needs the following class attributes:

            self.cpu_port_hdl - cpu_port_hdl id

        Seds the following class attributes:

            self.cpu_queueX - cpu queue id

        """
        #TODO move this function to CommonSaiHelper
        attr = sai_thrift_get_port_attribute(self.client,
                                             self.cpu_port_hdl,
                                             qos_number_of_queues=True)
        num_queues = attr['qos_number_of_queues']
        q_list = sai_thrift_object_list_t(count=num_queues)
        attr = sai_thrift_get_port_attribute(self.client,
                                             self.cpu_port_hdl,
                                             qos_queue_list=q_list)
        for queue in range(0, num_queues):
            queue_id = attr['qos_queue_list'].idlist[queue]
            setattr(self, 'cpu_queue%s' % queue, queue_id)
            q_attr = sai_thrift_get_queue_attribute(
                self.client,
                queue_id,
                port=True,
                index=True,
                parent_scheduler_node=True)
            self.assertEqual(queue, q_attr['index'])
            #self.assertEqual(self.cpu_port_hdl, q_attr['port'])


    def start_switch(self):
        """
        Start switch.
        """
        self.switch_id = sai_thrift_create_switch(
        self.client, init_switch=True, src_mac_address=ROUTER_MAC)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def warm_start_switch(self):
        """
        Warm start switch.
        """
        self.switch_id = sai_thrift_create_switch(
        self.client, init_switch=True, warm_recover=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


    def set_accepted_exception(self):
        """
        Set accepted exceptions.
        """
        adapter.CATCH_EXCEPTIONS=True


    def setUp(self):
        super(SaiHelperBase, self).setUp()
        if 'port_config_ini' in self.test_params:
            self.port_config_ini_loader = PortConfigInILoader(self.test_params['port_config_ini'])
        else:
            self.port_config_ini_loader = PortConfigInILoader()        
        self.port_config_ini_loader.parse_port_config()
        self.ports_config = self.port_config_ini_loader.ports_config

        if 'config_db_json' in self.test_params:
            self.config_db_loader = ConfigDBLoader(self.test_params['config_db_json'])
        else:
            self.config_db_loader = ConfigDBLoader()
        self.port_configer = PortConfiger(self)
        self.def_bridge_port_list = []
        self.def_bridge_port_list = []
        self.def_vlan_member_list = []
        self.set_logger_name()
        self.set_accepted_exception()
        self.getSwitchPorts()
        # initialize switch
        self.start_switch()

        self.switch_resources = self.saveNumberOfAvaiableResources(debug=True)

        # get default vlan
        attr = sai_thrift_get_switch_attribute(
            self.client, default_vlan_id=True)
        self.default_vlan_id = attr['default_vlan_id']
        self.assertNotEqual(self.default_vlan_id, 0)

        self.recreate_ports()

        # get number of active ports
        self.get_active_port_list()

        # get default vrf
        attr = sai_thrift_get_switch_attribute(
            self.client, default_virtual_router_id=True)
        self.default_vrf = attr['default_virtual_router_id']
        self.assertNotEqual(self.default_vrf, 0)

        self.config_port()

        # get cpu port
        attr = sai_thrift_get_switch_attribute(self.client, cpu_port=True)
        self.cpu_port_hdl = attr['cpu_port']
        self.assertNotEqual(self.cpu_port_hdl, 0)

        # get cpu port queue handles
        self.check_cpu_port_hdl()

        print("Finish SaiHelperBase setup")


    def tearDown(self):
        try:
            for port in self.port_list:
                sai_thrift_clear_port_stats(self.client, port)
                sai_thrift_set_port_attribute(
                    self.client, port, port_vlan_id=0)
            #Todo: Remove this condition after brcm's remove_switch issue fixed
            if get_platform() == 'brcm':
                return
            # always failed in this step
            # self.assertTrue(self.verifyNumberOfAvaiableResources(
            #     self.switch_resources, debug=False))
        finally:
            super(SaiHelperBase, self).tearDown()


    def createPorts(self):
        """
        Create ports after reading from port config file
        """
        def fec_str_to_int(fec):
            """
            Convert fec string to SAI enum

            Args:
                fec (string): fec string from port_config

            Returns:
                int: SAI enum value
            """
            fec_dict = {
                'rs': SAI_PORT_FEC_MODE_RS,
                'fc': SAI_PORT_FEC_MODE_FC
            }
            return fec_dict.get(fec, SAI_PORT_FEC_MODE_NONE)

        # delete the existing ports
        attr = sai_thrift_get_switch_attribute(
            self.client, number_of_active_ports=True)
        self.active_ports_no = attr['number_of_active_ports']
        attr = sai_thrift_get_switch_attribute(
            self.client, port_list=sai_thrift_object_list_t(
                idlist=[], count=self.active_ports_no))
        if self.active_ports_no:
            self.port_list = attr['port_list'].idlist
            for port in self.port_list:
                sai_thrift_remove_port(self.client, port)

        # add new ports from port config file
        self.ports_config = self.port_config_ini_loader.ports_config
        for name, port in self.ports_config.items():
            print("Creating port: %s" % name)
            fec_mode = fec_str_to_int(port.get('fec', None))
            auto_neg_mode = True if port.get(
                'autoneg', "").lower() == "on" else False
            sai_list = sai_thrift_u32_list_t(
                count=len(port['lanes']), uint32list=port['lanes'])
            sai_thrift_create_port(self.client,
                                   hw_lane_list=sai_list,
                                   fec_mode=fec_mode,
                                   auto_neg_mode=auto_neg_mode,
                                   speed=port['speed'],
                                   admin_state=True)


    def checkPortsUp(self, timeout=30):
        """
        Wait for all ports to be UP
        This may be required while testing on hardware
        The test fails if all ports are not UP after timeout

        Args:
            timeout (int): port verification timeout in sec
        """
        allup = False
        timer_start = time.time()

        while allup is False and time.time() - timer_start < timeout:
            allup = True
            for port in self.port_list:
                attr = sai_thrift_get_port_attribute(
                    self.client, port, oper_status=True)
                if attr['oper_status'] != SAI_SWITCH_OPER_STATUS_UP:
                    allup = False
                    break
            if allup:
                break
            time.sleep(5)

        self.assertTrue(allup)

    def getSwitchPorts(self):
        """
        Get device port numbers
        """
        dev_no = 0
        for _, port, _ in config['interfaces']:
            # remove after DASH will be introduced as confuses with "dev" prefix
            # added tg as a shortcut for "traffic generator"
            setattr(self, 'dev_port%d' % dev_no, port)
            setattr(self, 'tg%d' % dev_no, port)
            dev_no += 1

    def printNumberOfAvaiableResources(self, resources_dict):
        """
        Prints numbers of available resources

        Args:
            resources_dict (dict): a dictionary with resources numbers
        """

        print("***** Number of available resources *****")
        for key, value in resources_dict.items():
            print(key, ": ", value)

    def saveNumberOfAvaiableResources(self, debug=False):
        """
        Save number of available resources
        This allows to verify if all the test objects were removed

        Args:
            debug (bool): enables debug option
        Return:
            dict: switch_resources dictionary with available resources
        """

        switch_resources = sai_thrift_get_switch_attribute(
            self.client,
            available_ipv4_route_entry=True,
            available_ipv6_route_entry=True,
            available_ipv4_nexthop_entry=True,
            available_ipv6_nexthop_entry=True,
            available_ipv4_neighbor_entry=True,
            available_ipv6_neighbor_entry=True,
            available_next_hop_group_entry=True,
            available_next_hop_group_member_entry=True,
            available_fdb_entry=True,
            available_ipmc_entry=True,
            available_snat_entry=True,
            available_dnat_entry=True,
            available_double_nat_entry=True,
            number_of_ecmp_groups=True,
            ecmp_members=True)

        if debug:
            self.printNumberOfAvaiableResources(switch_resources)

        return switch_resources

    def verifyNumberOfAvaiableResources(self, init_resources, debug=False):
        """
        Verify number of available resources

        Args:
            init_resources (dict): a dictionary with initial resources numbers
            debug (bool): enable debug option

        Returns:
            bool: True if the numbers of resources are the same as before tests
        """

        available_resources = sai_thrift_get_switch_attribute(
            self.client,
            available_ipv4_route_entry=True,
            available_ipv6_route_entry=True,
            available_ipv4_nexthop_entry=True,
            available_ipv6_nexthop_entry=True,
            available_ipv4_neighbor_entry=True,
            available_ipv6_neighbor_entry=True,
            available_next_hop_group_entry=True,
            available_next_hop_group_member_entry=True,
            available_fdb_entry=True,
            available_ipmc_entry=True,
            available_snat_entry=True,
            available_dnat_entry=True,
            available_double_nat_entry=True,
            number_of_ecmp_groups=True,
            ecmp_members=True)

        for key, value in available_resources.items():
            if value != init_resources[key]:
                if debug:
                    print("Number of %s incorrect! Current value: %d, Init value: %d" % (key, value, init_resources[key]))
                return False

        return True

    @staticmethod
    def status():
        """
        Returns the last operation status.

        Returns:
            int: sai call result
        """
        return adapter.status

    @staticmethod
    def saiWaitFdbAge(timeout):
        """
        Wait for fdb entry to ageout

        Args:
            timeout (int): Timeout value in seconds
        """
        print("Waiting for fdb entry to age")
        aging_interval_buffer = 10
        time.sleep(timeout + aging_interval_buffer)


class SaiHelperUtilsMixin:
    """
    Mixin utils class providing API for convenient SAI objects creation/deletion
    """

    def create_bridge_ports(self, ports=None):
        """
        Create bridge ports base on port_list.
        """
        ports = ports or range(0, len(self.port_list))
        for port_index in ports:
            port_id = getattr(self, 'port%s' % port_index)
            port_bp = sai_thrift_create_bridge_port(
                self.client,
                bridge_id=self.default_1q_bridge,
                port_id=port_id,
                type=SAI_BRIDGE_PORT_TYPE_PORT,
                admin_state=True)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            setattr(self, 'port%s_bp' % port_index, port_bp)
            self.def_bridge_port_list.append(port_bp)

    def destroy_bridge_ports(self):
        for bridge_port in self.def_bridge_port_list:
            sai_thrift_remove_bridge_port(self.client, bridge_port)

    def create_lag_with_members(self, lag_index, ports):
        # create lag
        lag_id = sai_thrift_create_lag(self.client)
        setattr(self, 'lag%s' % lag_index, lag_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_lag_list.append(lag_id)

        # add LAG to bridge
        lag_bp = sai_thrift_create_bridge_port(
            self.client,
            bridge_id=self.default_1q_bridge,
            port_id=lag_id,
            type=SAI_BRIDGE_PORT_TYPE_PORT,
            admin_state=True)

        setattr(self, 'lag%s_bp' % lag_index, lag_bp)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_bridge_port_list.append(lag_bp)

        # add lag members
        for member_index in ports:
            port_id = getattr(self, 'port%s' % member_index)
            lag_member = sai_thrift_create_lag_member(
                self.client, lag_id=lag_id, port_id=port_id)
            setattr(self, "lag%s_member%s" % (lag_index, member_index), lag_member)

            self.def_lag_member_list.append(lag_member)

    def destroy_lags_with_members(self):
        for lag_member in self.def_lag_member_list:
            sai_thrift_remove_lag_member(self.client, lag_member)
        for lag in self.def_lag_list:
            sai_thrift_remove_lag(self.client, lag)

    def create_vlan_with_members(self, vlan_index, members):
        # create vlan
        vlan_id = sai_thrift_create_vlan(self.client, vlan_id=vlan_index)
        setattr(self, 'vlan%s' % vlan_index, vlan_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.def_vlan_list.append(vlan_id)

        # add members
        idx = 0
        for member, tag in members.items():
            tag = SAI_VLAN_TAGGING_MODE_UNTAGGED
            if tag == 'tagged':
                tag = SAI_VLAN_TAGGING_MODE_TAGGED
            vlan_member_id = sai_thrift_create_vlan_member(
                self.client,
                vlan_id=vlan_id,
                bridge_port_id=member,
                vlan_tagging_mode=tag)
            setattr(self, 'vlan%s_member%s' % (vlan_index, idx), vlan_member_id)
            self.def_vlan_member_list.append(vlan_member_id)
            idx = idx + 1

    def destroy_vlans_with_members(self):
        for vlan_member in self.def_vlan_member_list:
            sai_thrift_remove_vlan_member(self.client, vlan_member)
        for vlan in self.def_vlan_list:
            sai_thrift_remove_vlan(self.client, vlan)

    def create_routing_interfaces(self, vlans = None, lags = None, ports = None):
        # iterate through vlans
        if vlans is not None:
            for vlan in vlans:
                vlan_id = getattr(self, "vlan%s" % vlan)
                vlan_rif = sai_thrift_create_router_interface(
                    self.client,
                    type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
                    virtual_router_id=self.default_vrf,
                    vlan_id=vlan_id)
                self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
                setattr(self, "vlan%s_rif" % vlan, vlan_rif)
                self.def_rif_list.append(vlan_rif)

        # iterate through lags
        if lags is not None:
            for lag in lags:
                lag_id = getattr(self, "lag%s" % lag)
                lag_rif = sai_thrift_create_router_interface(
                    self.client,
                    type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                    virtual_router_id=self.default_vrf,
                    port_id=lag_id)
                self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
                setattr(self, "lag%s_rif" % lag, lag_rif)
                self.def_rif_list.append(lag_rif)

        # iterate through ports
        if ports is not None:
            for port in ports:
                port_id = getattr(self, 'port%s' % port)
                port_rif = sai_thrift_create_router_interface(
                    self.client,
                    type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                    virtual_router_id=self.default_vrf,
                    port_id=port_id)
                self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
                setattr(self, "port%s_rif" % port, port_rif)
                self.def_rif_list.append(port_rif)

    def destroy_routing_interfaces(self):
        for rif in self.def_rif_list:
            sai_thrift_remove_router_interface(self.client, rif)


class SaiHelperSimplified(SaiHelperUtilsMixin, SaiHelperBase):
    """
    SAI test helper class for DUT with limited port resources
    without initial switch ports setup
    """

    def __getattr__(self, name):
        """
        Skip the test in case of "port\d+" attribute does not exist
        """
        # NOTE: check only ports for now
        found = re.findall(r'^port\d+$', name)
        if found and found[0]:
            self.skipTest(SKIP_TEST_NO_RESOURCES_MSG)

    def setUp(self):
        super(SaiHelperSimplified, self).setUp()

        # lists of default objects
        self.def_bridge_port_list = []
        self.def_lag_list = []
        self.def_lag_member_list = []
        self.def_vlan_list = []
        self.def_vlan_member_list = []
        self.def_rif_list = []

    def tearDown(self):
        super(SaiHelperSimplified, self).tearDown()


class SaiHelper(SaiHelperUtilsMixin, SaiHelperBase):
    """
    Set common base ports configuration for tests

    Common ports configuration:
    * U/T = untagged/tagged VLAN member
    +--------+------+-----------+-------------+--------+------------+------------+
    | Port   | LAG  | _member   | Bridge port | VLAN   | _member    | RIF        |
    +========+======|===========+=============+========+============+============+
    | port0  |      |           | port0_bp    | vlan10 | _member0 U |            |
    | port1  |      |           | port1_bp    |        | _member1 T |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port2  |      |           | port2_bp    | vlan20 | _member0 U |            |
    | port3  |      |           | port3_bp    |        | _member1 T |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port4  | lag1 | _member4  | lag1_bp     | vlan10 | _member2 U |            |
    | port5  |      | _member5  |             |        |            |            |
    | port6  |      | _member6  |             |        |            |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port7  | lag2 | _member7  | lag2_bp     | vlan20 | _member2 T |            |
    | port8  |      | _member8  |             |        |            |            |
    | port9  |      | _member9  |             |        |            |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port10 |      |           |             |        |            | port10_rif |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port11 |      |           |             |        |            | port11_rif |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port12 |      |           |             |        |            | port12_rif |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port13 |      |           |             |        |            | port13_rif |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port14 | lag3 | _member14 |             |        |            | lag3_rif   |
    | port15 |      | _member15 |             |        |            |            |
    | port16 |      | _member16 |             |        |            |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port17 | lag4 | _member17 |             |        |            | lag4_rif   |
    | port18 |      | _member18 |             |        |            |            |
    | port19 |      | _member19 |             |        |            |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port20 |      |           | port20_bp   | vlan30 | _member0 U | vlan30_rif |
    | port21 |      |           | port21_bp   |        | _member1 T |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port22 | lag5 | _member22 | lag5_bp     | vlan30 | _member2 T |            |
    | port23 |      | _member23 |             |        |            |            |
    +--------+------+-----------+-------------+--------+------------+------------+
    | port24 |                                                                   |
    | port25 |                                                                   |
    | port26 |                                                                   |
    | port27 |                            UNASSIGNED                             |
    | port28 |                                                                   |
    | port29 |                                                                   |
    | port30 |                                                                   |
    | port31 |                                                                   |
    +--------+-------------------------------------------------------------------+
    """

    def create_default_v4_v6_route_entry(self):
        """
        Create default v4 and v6 route entry.
        """
        DEFAULT_IP_V4_PREFIX = '0.0.0.0/0'
        DEFAULT_IP_V6_PREFIX = '0000:0000:0000:0000:0000:0000:0000:0000'
        print("Create default v4&v6 route entry...")
        v6_default = sai_thrift_ip_prefix_t(addr_family=1,
                                            addr=sai_thrift_ip_addr_t(
                                                ip6=DEFAULT_IP_V6_PREFIX),
                                            mask=sai_thrift_ip_addr_t(ip6=DEFAULT_IP_V6_PREFIX))
        self.default_ipv6_route_entry = sai_thrift_route_entry_t(vr_id=self.default_vrf,
                                                                 destination=v6_default)
        status = sai_thrift_create_route_entry(
            self.client,
            route_entry=self.default_ipv6_route_entry,
            packet_action=SAI_PACKET_ACTION_DROP)
        self.assertEqual(status, SAI_STATUS_SUCCESS)

        self.default_ipv4_route_entry = sai_thrift_route_entry_t(vr_id=self.default_vrf,
                                                                 destination=sai_ipprefix(DEFAULT_IP_V4_PREFIX))
        status = sai_thrift_create_route_entry(
            self.client,
            route_entry=self.default_ipv4_route_entry,
            packet_action=SAI_PACKET_ACTION_DROP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def setUp(self):
        super(SaiHelper, self).setUp()

        # lists of default objects
        self.def_bridge_port_list = []
        self.def_lag_list = []
        self.def_lag_member_list = []
        self.def_vlan_list = []
        self.def_vlan_member_list = []
        self.def_rif_list = []

        # create bridge ports
        self.create_bridge_ports(ports=[0, 1, 2, 3, 20, 21])

        self.create_lag_with_members(1, ports=[4, 5, 6])
        self.create_lag_with_members(2, ports=[7, 8, 9])

        # L3 lags
        self.create_lag_with_members(3, ports=[14, 15, 16])
        self.create_lag_with_members(4, ports=[17, 18, 19])
        self.create_lag_with_members(5, ports=[22, 23])

        # create vlan 10 with port0, port1 and lag1
        self.create_vlan_with_members(10, {self.port0_bp: 'untagged',
                                           self.port1_bp: 'tagged',
                                           self.lag1_bp: 'untagged'})

        # create vlan 20 with port2, port3 and lag2
        self.create_vlan_with_members(20, {self.port2_bp: 'untagged',
                                           self.port3_bp: 'tagged',
                                           self.lag2_bp: 'untagged'})

        # create vlan 30 with port20, port21 and lag5
        self.create_vlan_with_members(30, {self.port20_bp: 'untagged',
                                           self.port21_bp: 'tagged',
                                           self.lag5_bp: 'untagged'})

        # setup untagged ports
        sai_thrift_set_port_attribute(self.client, self.port0, port_vlan_id=10)
        sai_thrift_set_lag_attribute(self.client, self.lag1, port_vlan_id=10)
        sai_thrift_set_port_attribute(self.client, self.port2, port_vlan_id=20)

        # create L3 configuration
        self.create_routing_interfaces(vlans=[30])
        self.create_routing_interfaces(lags=[3, 4])
        self.create_routing_interfaces(ports=[10, 11, 12, 13])

        # Create default route for default VRF is mandartory.
        # Issue #1606(https://github.com/opencomputeproject/SAI/issues/1606)
        # Creating route in default VRF will failed if there aren't default routes.
        # Solution
        # Create default route before create route in detaul VRF
        self.create_default_v4_v6_route_entry()

    def tearDown(self):
        sai_thrift_set_port_attribute(self.client, self.port2, port_vlan_id=0)
        sai_thrift_set_lag_attribute(self.client, self.lag1, port_vlan_id=0)
        sai_thrift_set_port_attribute(self.client, self.port0, port_vlan_id=0)

        self.destroy_routing_interfaces()
        self.destroy_vlans_with_members()
        self.destroy_bridge_ports()
        self.destroy_lags_with_members()

        super(SaiHelper, self).tearDown()


class MinimalPortVlanConfig(SaiHelperBase):
    """
    Minimal port and vlan configuration. Create port_num bridge ports and add
    them to VLAN with vlan_id. Configure ports as untagged
    """

    def __init__(self, port_num, vlan_id=100):
        """
        Args:
            port_num (int): Number of ports to configure
            vlan_id (int): ID of VLAN that will be created
        """
        super(MinimalPortVlanConfig, self).__init__()

        self.port_num = port_num
        self.vlan_id = vlan_id

    def setUp(self):
        super(MinimalPortVlanConfig, self).setUp()

        if self.port_num > self.active_ports_no:
            raise ValueError('Number of ports to configure %d is higher '
                             'than number of active ports %d'
                             % (self.port_num, self.active_ports_no))

        self.def_bridge_port_list = []
        self.def_vlan_member_list = []

        # create bridge ports
        for port in self.port_list:
            bp = sai_thrift_create_bridge_port(
                self.client, bridge_id=self.default_1q_bridge,
                port_id=port, type=SAI_BRIDGE_PORT_TYPE_PORT,
                admin_state=True)

            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.def_bridge_port_list.append(bp)

        # create vlan
        self.vlan = sai_thrift_create_vlan(self.client, vlan_id=self.vlan_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        # add ports to vlan
        for bridge_port in self.def_bridge_port_list:
            vm = sai_thrift_create_vlan_member(
                self.client, vlan_id=self.vlan,
                bridge_port_id=bridge_port,
                vlan_tagging_mode=SAI_VLAN_TAGGING_MODE_UNTAGGED)

            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            self.def_vlan_member_list.append(vm)

        # setup untagged ports
        for port in self.port_list:
            status = sai_thrift_set_port_attribute(
                self.client, port, port_vlan_id=self.vlan_id)

            self.assertEqual(status, SAI_STATUS_SUCCESS)

    def tearDown(self):
        # revert untagged ports configuration
        for port in self.port_list:
            sai_thrift_set_port_attribute(
                self.client, port, port_vlan_id=0)

        # remove ports from vlan
        for vlan_member in self.def_vlan_member_list:
            sai_thrift_remove_vlan_member(self.client, vlan_member)

        # remove vlan
        sai_thrift_remove_vlan(self.client, self.vlan)

        # remove bridge ports
        for bridge_port in self.def_bridge_port_list:
            sai_thrift_remove_bridge_port(self.client, bridge_port)

        super(MinimalPortVlanConfig, self).tearDown()


def get_platform():
    """
    Get the platform token.

    If environment variable [PLATFORM] doesn't exist, then the default platform will be 'common'.
    If environment variable [PLATFORM] exist but platform name is unknown raise ValueError.
    If environment variable [PLATFORM] exist but platform name is unspecified,
    then the default platform will be 'common'.
    If specified any one, it will try to concert it from standard name to a shortened name (case insensitive). \r
    \ti.e. Broadcom -> brcm
    """
    pl = 'common'

    if 'PLATFORM' in os.environ:
        pl_low = PLATFORM.lower()
        if pl_low in platform_map.keys():
            pl = platform_map[pl_low]
        elif pl_low in platform_map.values():
            pl = pl_low
        elif PLATFORM == '':
            print("Platform not set. The common platform was selected")
        else:
            raise ValueError("Undefined platform: {}.".format(pl_low))
    else:
        print("Platform not set. The common platform was selected")

    return pl


from platform_helper.common_sai_helper import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]
from platform_helper.bfn_sai_helper import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]
from platform_helper.brcm_sai_helper import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]
from platform_helper.mlnx_sai_helper import * # pylint: disable=wildcard-import; lgtm[py/polluting-import]

class PlatformSaiHelper(SaiHelper):
    """
    Class uses to extend from SaiHelper, base on the [platform] class attribute,
    dynamic select a subclass from the platform_helper.
    """
    def __new__(cls, *args, **kwargs):
        sai_helper_subclass_map = {subclass.platform: subclass for subclass in SaiHelper.__subclasses__()}
        common_sai_helper_subclass_map = {subclass.platform: subclass for subclass in CommonSaiHelper.__subclasses__()}
        pl = get_platform()

        if pl in common_sai_helper_subclass_map:
            target_base_class = common_sai_helper_subclass_map[pl]
        else:
            target_base_class = sai_helper_subclass_map[pl]

        cur_cls = cls
        while cur_cls.__base__ != PlatformSaiHelper:
            cur_cls = cur_cls.__base__

        cur_cls.__bases__ = (target_base_class,)

        instance = target_base_class.__new__(cls, *args, **kwargs)
        return instance
