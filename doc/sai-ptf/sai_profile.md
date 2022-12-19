# SAI-PTF for Warm reboot

| **Title** | **SAI-PTF for Warm reboot** |
| --- | --- |
| **Authors** | **Richard Yu** |
| **Status** | **In review** |
| **Created** | **22/03/2022** |
| **Modified** | **22/03/2022** |
| **SAI-Version** | **V1.7** |

- [SAI-PTF for Warm reboot](#sai-ptf-for-warm-reboot)
  - [Overview](#overviews)
    - [SAI-PTF for Warm reboot](#sai-ptf-for-warm-reboot-1)
  - [Saiserver container and test structure](#saiserver-container-and-test-structure)
    - [sai_prfile](#sai.profile的挂载)
    - [Test Topology](#test-topology)
    - [Testbed](#testbed)
    - [Test Structure](#test-structure)
  - [Upgrade SAI-PTF for different warm reboot stages with](#upgrade-sai-ptf-for-different-warm-reboot-stages-with)
    - [DUT settings during warm reboot](#dut-settings-during-warm-reboot)
    - [Extend the PTF test method for a warm reboot](#extend-the-ptf-test-method-for-a-warm-reboot)
    - [Code for extending the method in SAI-PTF](#code-for-extending-the-method-in-sai-ptf)
  - [Support DUT different running stages during warm reboot](#support-dut-different-running-stages-during-warm-reboot)
    - [Setup the warm reboot - Before the warm reboot](#setup-the-warm-reboot---before-the-warm-reboot)
    - [Starting DUT - During warm reboot](#starting-dut---during-warm-reboot)
    - [Post warmboot - After warm reboot](#post-warmboot---after-warm-reboot)
  - [Example of re-organizing the case into a warm reboot](#example-of-re-organizing-the-case-into-a-warm-reboot)
    - [Context](#context)
    - [Test case detail](#test-case-detail)
  - [Conclusion - Test scenarios and goals for Warm reboot](#conclusion---test-scenarios-and-goals-for-warm-reboot)
      - [reuse existing test cases](#reuse-existing-test-cases)
      - [Cross test cases in one stage](#cross-test-cases-in-one-stage)
      - [Upgrade existing one with new steps](#upgrade-existing-one-with-new-steps)
    - [Validate network device functionalities and configurations](#validate-network-device-functionalities-and-configurations)

## Overview

### SAI-PTF for Warm reboot
In order to use the SAI-PTF structure to verify the functionality in a warm reboot scenario, we need to add the following feature to the SAI-PTF structure
1. Lightweight docker which can expose the SAI interface to invoke the SAI interface remotely
1. PTF test case can support different DUT running statuses with its different processes - setUp, runTest, and tearDown
1. By interacting with sonic-mgmt，One test case can run once can verify whether as expected in different DUT running status - before the restart, starting, and started
1. Reuse already existing functional test cases and re-organize them into a warm reboot structure

## Saiserver container and test structure
In order to test SAI interfaces, we need a lightweight docker container that can help expose the SAI interfaces for a remote invocation.
Testbed structure as below.

### Test Topology
For SAI-PTF, it will use a non-topology network structure for the sai testing. 

<div align=center><img src=img/SAI_PTF_Topology.jpg></div>

### Testbed
Those tests will be run on the testbed structure as below, the components are:
* PTF - running in a server that can connect to the target DUT
* SAI server - running on a dut
<div align=center><img src=img/Device_topology.jpg></div>
*p.s. cause the SAI testing will not depend on any sonic components, then there will be no specific topology(T0 T1 T2) for testing.*

### Test Structure

---

<div align=center><img src=img/Component_topology.jpg></div>

Test structure in the chart above, components are:
* PTF container - run test cases, and use an RPC client to invoke the SAI interfaces on DUT
* SAI Server container - run inside DUT/switch, which exposes the SAI SDK APIs from the libsai
* SAI-Qualify - Test controller, which is used to deploy and control the test running
  * Warmboot-Watcher: Responsible for the communication between sonic-mgmt and ptf, the warm-reboot of saiserver

*For how to start a saiserver container please check the doc at
[PTF-SAIv2 testing guide](https://github.com/Azure/sonic-mgmt/blob/master/docs/testbed/sai_quality/PTF-SAIv2TestingGuide.md) and 
[Example: Start SaiServer Docker In DUT](https://github.com/Azure/sonic-mgmt/blob/master/docs/testbed/sai_quality/ExampleStartSaiServerDockerInDUT.md)*


## Sonic-Mgmt
[sonic-mgmt](https://github.com/sonic-net/sonic-mgmt) is for SONiC testbed deployment and setup, SONiC testing, test report processing.
Ansible is the main tool powering all the tasks for SONiC testing. The tasks include:
* Deploy and setup testbed
* Interact with various devices in testbed in ansible playbooks and in pytest scripts.

[sai-qualify](https://github.com/sonic-net/sonic-mgmt/tree/master/tests/sai_qualify) is a submodule of sonic-mgmt.It mainly has the following functions

1. SONiC testbed deployment and setup
1. pull `SAI` to the ptf ， the script about `saiserver` is pulled to dut
1. start `saiserver` contatiner
1. check whether can connect rpc server in `saiserver`
1. prf test running
1. stop `saiserver` container
1. organize and upload result
1. teardown

Each SAI test case will repeat 3-6 steps.。Wait until all the cases in the caselist are executed, and then go to the 7th step.

In order to meet our needs for warmreboot testing, the architecture of sai-qualify has been adjusted as follows
* Create a new daemon process Warmboot-Watcher to interact directly with ptf, know when to meet reboot from ptf, and tell ptf when reboot is completed.
* Configure the way the `saiserver` container starts by [sai_script](https://github.com/sonic-net/sonic-mgmt/blob/master/tests/scripts/sai_qualify/sai_warm_profile.sh)

So, `sonic-mgmt` pipeline becomes:
1. SONiC testbed deployment and setup
1. pull `SAI` to the ptf ， the script about `saiserver` is pulled to dut
1. <font color='red'>run Warmboot-Watcher daemon thread(more detail see x.x)</font>
1. <font color='red'>[prepare for first start](#Prepare-for-first-start)  by [sai_script](https://github.com/sonic-net/sonic-mgmt/blob/master/tests/scripts/sai_qualify/sai_warm_profile.sh)</font>
1. start `saiserver` contatiner
1. check whether can connect rpc server in `saiserver` 
1. prf test running(mode = warm)
    ```
    ptf sairif.SviLagHostTest --interface '0-0@eth0' ...--interface '0-31@eth31' --relax "--test-params=thrift_server='IP_address';port_config_ini='port_config.ini';test_reboot_mode='warm'"
    ```
    p.s. Need to add the parameters test_reboot_mode='warm';
1. stop `saiserver` container
1. <font color='red'>[restore after warmboot test](#Restoreafter-warmboot-test) by [sai_script](https://github.com/sonic-net/sonic-mgmt/blob/master/tests/scripts/sai_qualify/sai_warm_profile.sh)</font>
1. organize and upload result
1. teardown



## SAI
Warmreboot can be roughly divided into three stages，At different stages, the verification of SAI case will do different things
### pre-reboot:（old_saiserver container running）
Because the testcase will be tested in the normal pipeline, so there is no need to run the case at this stage, only setup，Save the configuration of dut to sai-warmboot.bin with the following code(see [sai_profile](#Sonic-Mgmt))
```python
sai_thrift_set_switch_attribute(inst.client, restart_warm=True)
sai_thrift_set_switch_attribute(inst.client, pre_shutdown=True)
sai_thrift_remove_switch(inst.client)
sai_thrift_api_uninitialize(self.client)
```
### rebooting: (old_saiserver stop, new_saiserver is not ready yet)
We divide the test case into two types。Test cases that require rpc calls (eg: sai_thrift_create_vlan_member) are not tested at this stage. the case that only sends and receives packets (for example: verify_packet) will run at this stage
### post-reboot: (new_saiserver container running)
runTest  
tearDone

### Upgrade SAI-PTF for different warm reboot stages with  
For PTF-SAI structure, it uses three different methods for three different steps in a test
- setUp, make settings
- runTest, run test
- tearDown, remove the setting and clear the test environment

After the above analysis, pre-reboot and post-reboot are the normal three steps of a case. setup, runtest, teardone. All we need to do is add wrapper to the runTest function. The warper contains the process of warm-reboot.
```
def setUp()
@warm_test(is_test_rebooting=True)
def runTest()
def tearDown()
```
## Interaction between SAI and sonic-mgmt

## sai_profile
我们在运行saiserver容器的时候会将dut的sai.profile和sai-warmboot.bin所在的目录都挂载到saiserver容器。
因为当我们使用`docker start saiserver` 时，`saiserver`就会根据`sai.profile`启动。所以如果我们将sai.profile挂载，那么就可以在启动saiserver之前，把配置文件修改好，为启动做好准备。

### Mounting of sai.profile
Path on the `saiserver`: `/etc/sai.d/sai.profile`  
Path on the dut host varies with different PLATFORMs and HWSKUs: it can be obtained through shell commands
```shell
# Obtain our platform as we will mount directories with these names in each dockers
PLATFORM=${PLATFORM:-`$SONIC_CFGGEN -H -v DEVICE_METADATA.localhost.platform`}
# Obtain our HWSKU as we will mount directories with these names in each docker
HWSKU=${HWSKU:-`$SONIC_CFGGEN -d -v 'DEVICE_METADATA["localhost"]["hwsku"]'`}
# The path to store sai.porfile
profile_path=/usr/share/sonic/device/$PLATFORM/$HWSKU
```
### Mounting of sai-warmboot.bin
Path on the `saiserver`：/var/warmboot
path on the dut host：/host/warmboot

### Warm reboot configures sai_profile in stages
Warmreboot includes starting `saiserver` twice
#### Prepare for first start
1.Save the initial `sai.profile` to `sai.profile.bak`，which is for restoring files after warm reboot.
```shell
profile='sai.profile'
cp $profile $profile.bak
-------------------------------
#Sample profile in brcm s6000
cat /etc/sai.d/sai.profile
SAI_INIT_CONFIG_FILE=/usr/share/sonic/hwsku/td2-s6000-32x40G.config.bcm
```
2.add the WARM_REBOOT_WRITE_FILE and SAI_WARM_BOOT_READ_FILE in the profile。
```shell
echo "SAI_WARM_BOOT_WRITE_FILE=/var/warmboot/sai-warmboot.bin" >> $profile
echo "SAI_WARM_BOOT_READ_FILE=/var/warmboot/sai-warmboot.bin" >> $profile
-------------------------------
#Sample profile in brcm s6000
cat /etc/sai.d/sai.profile
SAI_INIT_CONFIG_FILE=/usr/share/sonic/hwsku/td2-s6000-32x40G.config.bcm
SAI_NUM_ECMP_MEMBERS=32
SAI_WARM_BOOT_WRITE_FILE=/var/warmboot/sai-warmboot.bin
SAI_WARM_BOOT_READ_FILE=/var/warmboot/sai-warmboot.bin
```
SAI_WARM_BOOT_WRITE_FILE and SAI_WARM_BOOT_READ_FILE are used to define where SAI will save and load the data backup file.
The configuration data of dut in setup will be backed up to /var/warmboot/sai-warmboot.bin. So even after closing the saiserver container, the backup data will be saved in dut.
#### Prepare for second start
Enable the warm start
```shell
echo "SAI_BOOT_TYPE=1" >> $profile
-------------------------------
# Sample in a brcm s6000
cat /etc/sai.d/sai.profile
SAI_INIT_CONFIG_FILE=/usr/share/sonic/hwsku/td2-s6000-32x40G.config.bcm
SAI_NUM_ECMP_MEMBERS=32
SAI_WARM_BOOT_WRITE_FILE=/var/warmboot/sai-warmboot.bin
SAI_WARM_BOOT_READ_FILE=/var/warmboot/sai-warmboot.bin
SAI_BOOT_TYPE=1
```
#### Restore after warmboot test
```shell
cp $profile.bak $profile
-------------------------------
#Sample profile in brcm s6000
    wgscat /etc/sai.d/sai.profile
SAI_INIT_CONFIG_FILE=/usr/share/sonic/hwsku/td2-s6000-32x40G.config.bcm
```

