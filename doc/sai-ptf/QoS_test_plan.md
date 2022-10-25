

#  QoS Test plan (**DRAFT**)
## common_config (will be moved to t0 config file)

In QoS Testing, we use those parameters, for differernt cases the value might be different, they parameters are

### Buffer and packet parameters

- Test packet

PKT_LEN: packet length

PKT_NUM: packets numbers

DEVI: deviation ratio, the accept different ratio between actual value and expected value

- pool 

use the actual packets amount to verify if buffer size satisify requirement (test need fault tolarent)

buffer_size : PKT_NUM X (PKT_LEN X 1.1) (variable, can be adjuest one different test context)

xoff_size: buffer_size X 0.9 （also variable, can be adjust）

- buffer

reserved_buffer_size : PKT_LEN X 1.1

xoff_th: xoff_size / 16 (related to xoff_size for if shared, when shared this should not be exceed, shared it can use the pool size)

xon_th : 10 X PKT_LEN (xon xoff signal between xon_th and xon_offset_th)

xon_offset_th : 10 X PKT_LEN 

shared_dyname_th: refer currernt device config (bits?) (baiwei)

shared_static_th: buffer_size X 0.9 (dropped exceed?)

### QoS Maps
 
QoS MAPs: 
- dscp: mapped in DSCP in 8 section (1:0-7, 2:8-15, 3:16-23, 4:24-31, 5:32-39, 6:40-47, 7:48-55, 8:56-63), map each section to each of the value in tc, pg and queue
- tc, PG, queue, same number amoung TC, PG, Queue (1~8)

### Port

VLAN ports: INGRESS

LAG: EGRESS

**p.s. SAI_QOS_MAP_TYPE_PFC_PRIORITY_TO_PRIORITY_GROUP is not supported by brcm**

**uc: unicast**

**mc: multicast** queues(multicast buffer, need to check with bing or neetha)

**For multicast traffic, a single cell can occupy multiple CQEs(cell queue entries, CQEs are control pointers and are used to store the control information for each cell of packet.)**

**For each multicast traffic, in ingress pool, it should use the space same as the unicast, in egress, they should used space in corresponding queue buffer(queue has multicast and unicast buffer respectively)**

**??Both lossless and lossy mode, when congestion happening, buffer will be used, just the pause frame will send ot not**

**??How to test xoff to xon**

**??Why pool size is around 16 times of xoff size, class of services
|c|SAI_OBJECT_TYPE_BUFFER_POOL:oid:0x180000000009f2|SAI_BUFFER_POOL_ATTR_THRESHOLD_MODE=SAI_BUFFER_POOL_THRESHOLD_MODE_DYNAMIC|SAI_BUFFER_POOL_ATTR_SIZE=32689152|SAI_BUFFER_POOL_ATTR_TYPE=SAI_BUFFER_POOL_TYPE_INGRESS|SAI_BUFFER_POOL_ATTR_XOFF_SIZE=2058240**

**??what is shared_dyname_th, looks like a bit mask?**

**??Cannot get counter...**

**More focus on behivor but not the accurate data.**

**++Watermark clear, functionality.**

**Flex counter, counters. junhua and neetha, and prince for who is owner.**




# Test Group1: Buffer 

## Case1: test_ingress_pg_qos_map
## Case2: test_ingress_pg_config
## Case3: test_ingress_pg_stat_uc
## Case4: test_ingress_headroom_stats_uc
## Case5: test_ingress_overflowed_pkt_recover_uc
## Case6: test_ingress_non_flow_control_drop_uc
## Case7: test_ingress_pg_qos_map_mc
## Case8: test_ingress_pg_config_mc
## Case9: test_ingress_pg_stat_mc
## Case10: test_ingress_headroom_stats_mc
## Case11: test_ingress_overflowed_pkt_recove_mc
## Case12: test_ingress_non_flow_control_drop_mc
## Case13: test_create_buffer_pool_number
## Case14: test_change_ingress_buffer_profile
## Case15: test_ingress_headroom_full_drop_uc
## Case16: test_ingress_headroom_full_drop_mc
## Case17: test_ingress_headroom_reset_uc
## Case18: test_ingress_headroom_reset_mc
## Case19: test_ingress_pg_stats_non_shared_uc
## Case20: test_ingress_pg_stats_shared_uc
## Case21: test_ingress_pg_stats_non_shared_mc
## Case22: test_ingress_pg_stats_shared_mc
## Case23: test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE
## Case24: test_ingress_static_shared_uc
## Case25: test_ingress_static_shared_mc
## Case26: test_exceed_QOS_MAXIMUM_HEADROOM_SIZE
## Case27: test_ingress_overflowed_pkt_recover_mc


### Testing Objective <!-- omit in toc --> 
- test_ingress_pg_qos_map - Verify packet send to the corresponding PG base on the priority group configuration (dscp to tc, tc t0 PG)
- test_ingress_pg_config - Verify if pg can be configured and the data can be retrieve
- test_ingress_pg_stat - Verify buffer pool and ingress priority group releated statictics (no congestion)
- test_ingress_headroom_full_drop - Verify if headroom is filled up (exceed service pool size) then packet is dropped (size and behavior)
- test_ingress_headroom_stats - Verify if headroom is being filled up the related register statictics are changed (Keep sending packet)
- test_ingress_headroom_reset - Verify if headroom is reset after filled up (repeat many times, same number of packets received after recover from congestion)
- test_ingress_pg_stats_shared - Verify if the pg headroom statictics in shared mode (defined xoff size for share mode and stats is the actual size, larger than xoff-th)
- test_ingress_pg_stats_non_shared - Verify if the pg headroom statictics in non_shared mode (defined xoff as zero for non_share mode and stats is the actual size and cannot larger than xoff-th)
- test_ingress_overflowed_pkt_recover - Verify if packets been kept in deferred vector (in mmu) after recovery from congestion, the packets will be sent out as FIFO
- test_ingress_non_flow_control_drop - Verify if lossy port not drop packet on ingress port
- test_create_buffer_pool_number - verify if numbers of ingress and egress buffer pools can be created, Ingress = SAI_SWITCH_ATTR_INGRESS_BUFFER_POOL_NUM, Egress = SAI_SWITCH_ATTR_EGRESS_BUFFER_POOL_NUM.
- test_change_ingress_buffer_profile - verify if change the buffer profile will not break the ingress traffic
- test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE - verify The sum of the headroom size of the ingress priority groups belonging to this port should not exceed the SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE value. This attribute is applicable only for per-port, per-PG headroom model (which means SAI_BUFFER_POOL_ATTR_XOFF_SIZE is zero). For the platforms which don't have this limitation, 0 should be returned.
- test_exceed_QOS_MAXIMUM_HEADROOM_SIZE
- test_ingress_static_shared - verify if the packet will be dropped when the used space larger than static th (continue to use the headroom, verfiy status, pfc at first, then drop, ask baiwei about the behaivor)


### Case Steps <!-- omit in toc --> 

- test_ingress_pg_qos_map

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode, flow_control for PG
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. Send packet with ``server IP`` and with 8 different DSCP values
4. Check the PG counter, receive the packets on different IPG

- test_ingress_pg_config

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode, flow_control for PG
2. Check iPG QOS map on port, dscp_tc, tc_iPG
3. Check value in dscp_tc, tc_iPG map, ``tc``, ``dscp``, ``iPG``
4. Check Port iPGs, assigned profile
5. check the assigned profile attributes, buffer pool, reserved, threshold mode, xoff_th, xon_th, xon_offset_th, share mode
6. Check the buffer pool attributes, size, threshold mode, xoff_size

- test_ingress_pg_stat

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode, flow_control for PG
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. send 10000 packet in a thread (value is transient, fleeting )
4. check the priority group statictics while sending the packet(Get the max number of the statictics during checking), the statictics include: 
   buffer_pool stats:  SAI_BUFFER_POOL_STAT_CURR_OCCUPANCY_BYTES, SAI_BUFFER_POOL_STAT_WATERMARK_BYTES;
   priority_group_stats: 
   SAI_INGRESS_PRIORITY_GROUP_STAT_CURR_OCCUPANCY_BYTES, 
   SAI_INGRESS_PRIORITY_GROUP_STAT_SHARED_CURR_OCCUPANCY_BYTES,
   SAI_INGRESS_PRIORITY_GROUP_STAT_WATERMARK_BYTES,
   SAI_INGRESS_PRIORITY_GROUP_STAT_PACKETS,
   SAI_INGRESS_PRIORITY_GROUP_STAT_BYTES,
   SAI_INGRESS_PRIORITY_GROUP_STAT_DROPPED_PACKETS
5. Verify the statictics numbers are increased.

- test_ingress_headroom_stats

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode, flow_control for PG
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. Disbale port TX to simulate congestion
4. Keep sending ``server IP`` packet with length 1000 until packet drop happen. Recording the packet number as MaxPackets.
5. Keep sending ``server IP`` packet with length 1000,  check the stats of PG, below stats should being increased. When these stats are not incresing, recording current packet number and Verify if the packet number belongs to (MaxPackets*0.8 ,MaxPackets*1.2)
   'SAI_INGRESS_PRIORITY_GROUP_STAT_PACKETS', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_CURR_OCCUPANCY_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_WATERMARK_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_SHARED_CURR_OCCUPANCY_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_SHARED_WATERMARK_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_INGRESS_PRIORITY_GROUP_STAT_XOFF_ROOM_WATERMARK_BYTES', 
6. check the pool stats, below stats should being increased
   'SAI_BUFFER_POOL_STAT_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_WATERMARK_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 

- test_ingress_headroom_full_drop

1. repeat test test_ingress_headroom_stats
2. Keep sending ``server IP`` packet with length 1000, check the pool and PG stats, those stats should increase
   'SAI_INGRESS_PRIORITY_GROUP_STAT_DROPPED_PACKETS', 
   'SAI_BUFFER_POOL_STAT_DROPPED_PACKETS', 

- test_ingress_headroom_reset

1. repeat test test_ingress_headroom_stats (make sure no drop happened)
2. enable the port tx
3. check the received packets (should take fault tolerant, 90% should be back)
4. repeat step 1 ~ 3, many time, packets should be back, not drops


- test_ingress_pg_stats_shared

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode
2. Make sure defind the xoff size in buffer pool, for a shared mode
3. According to common config, set the xoff_th
4. disable port tx
5. send the packets, recording the maximum packet number as MaxPakcets which statisifies that stats should be the actual size
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 
6. repeat step 5 , get maximum packet number, and verify it belongs to (MaxPackets*0.8 ,MaxPackets*1.2)


test_ingress_pg_stats_non_shared

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode
2. Make sure defind the xoff as zero in buffer pool, for a non-shared mode
3. According to common config, set the xoff_th
4. disable port tx
5. send the packets, recording the maximum packet number as MaxPakcets which satisfies that stats should be the xoff_th size for the most
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 
6. repeat step 5 , get maximum packet number, and verify it belongs to (MaxPackets*0.8 ,MaxPackets*1.2)

- test_ingress_overflowed_pkt_recover

1. repeat test test_ingress_headroom_stats (100 packets is good enough, make sure no drop happened, and send with dscp in sequence, 1~8)
2. enable the port tx
3. check the received packet is follow the dscp sequence

- test_ingress_non_flow_control_drop

1. repeat test test_ingress_headroom_stats, but without flow control set on iPGs
2. Keep sending ``server IP`` packet with length 1000, check the pool and PG stats, those stats should **NOT** increase
   'SAI_INGRESS_PRIORITY_GROUP_STAT_DROPPED_PACKETS'

- test_create_buffer_pool_number

1. Get number of ingress and egress buffer pool can be created from switch (ingress_buffer_pool_num, egress_buffer_pool_num)
2. Create allowed number of ingress and egress buffer pool
3. Keep creating more, error happened or return 0

- test_change_ingress_buffer_profile

1. According to common config, config DSCP_TC, TC_IPG, pool, buffer profile in dynamic mode, flow_control for PG
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. send 10000 packet in a thread, and check the packet arrived
4. when sending the packet change, change the buffer profile config
5. check during changing the buffer profile, the packet continue arrived


- test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE
1. create buffer pool with off_size as 0
2. check port attribute SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE
3. check if this attribute can be reteieved  

- test_exceed_QOS_MAXIMUM_HEADROOM_SIZE

1. if test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE resutl non-zero value and no error happened
2. create buffer profile with xoff_th larger than test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE/8
3. assign the profile to iPG
4. check there should be error happened

- test_ingress_static_shared

1. repeat test test_ingress_headroom_stats, but config in stastic mode as the common config
2. Keep sending ``server IP`` packet with length 1000, check the pool and PG stats, those stats should increase
   'SAI_INGRESS_PRIORITY_GROUP_STAT_DROPPED_PACKETS', 
   'SAI_BUFFER_POOL_STAT_DROPPED_PACKETS'



# Test Group2: Queue 

## Case1: test_egress_queue_qos_map
## Case2: test_egress_queue_config
## Case3: test_egress_queue_stat_uc
## Case4: test_egress_headroom_stats_uc
## Case5: test_egress_overflowed_pkt_recover_uc
## Case6: test_egress_flow_control_drop_uc
## Case7: test_egress_queue_qos_map_mc
## Case8: test_egress_queue_config_mc
## Case9: test_egress_queue_stat_mc
## Case10: test_egress_headroom_stats_mc
## Case11: test_egress_overflowed_pkt_recove_mc
## Case12: test_egress_flow_control_drop_mc

## Case13: test_change_egress_buffer_profile
## Case14: test_cpu_queue_qos_map_config
## Case15: test_egress_flow_control_drop_mc
## case16: test_egress_headroom_full_drop_uc
## Case17: test_egress_headroom_full_drop_mc
## Case18: test_egress_headroom_reset_uc
## Case19: test_egress_headroom_reset_mc
## Case20: test_egress_queue_stats_shared_uc
## Case21: test_egress_queue_stats_shared_mc
## Case22: test_egress_queue_stats_non_shared_uc
## Case23: test_egress_queue_stats_non_shared_mc
## Case24: test_egress_static_shared
## Case25: test_egress_overflowed_pkt_recover_mc


### Testing Objective <!-- omit in toc --> 
- test_egress_queue_qos_map - Verify packet send to the corresponding queue base on the priority group configuration (dscp to tc, tc t0 queue)
- test_egress_queue_config - Verify if queue can be configured and the data can be retrieve
- test_egress_queue_stat - Verify buffer pool and egress priority group releated statictics (no congestion)
- test_egress_headroom_full_drop - Verify if headroom is filled up (exceed service pool size) then packet is dropped (size and behavior)
- test_egress_headroom_stats - Verify if headroom is being filled up the related register statictics are changed (Keep sending packet)
- test_egress_headroom_reset - Verify if headroom is reset after filled up (repeat many times, same number of packets received after recover from congestion)
- test_egress_queue_stats_shared - Verify if the queue headroom statictics in shared mode (defined xoff size for share mode and stats is the actual size, larger than xoff-th)
- test_egress_queue_stats_non_shared - Verify if the queue headroom statictics in non_shared mode (defined xoff as zero for non_share mode and stats is the actual size and cannot larger than xoff-th)
- test_egress_overflowed_pkt_recover - Verify if packets been kept in deferred vector (in mmu) after recovery from congestion, the packets will be sent out as FIFO
- test_egress_flow_control_drop - Verify if lossless port not drop packet on egress port
- test_change_egress_buffer_profile - verify if change the buffer profile will not break the egress traffic
- test_egress_static_shared - verify if the packet will be dropped when the used space larger than static th
- test_cpu_queue_qos_map - Verify if the queue buffer and profile configuration can be applied on CPU queues (need to confirm with guohan, CPU pool can be configured by SAI?)


### Case Steps <!-- omit in toc --> 

- test_egress_queue_qos_map

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. Send packet with ``server IP`` and with 8 different DSCP values
4. Check the queue counter, receive the packets on different queue

- test_egress_queue_config

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. Check queue QOS map on port, dscp_tc, tc_queue
3. Check value in dscp_tc, tc_queue map, ``tc``, ``dscp``, ``queue``
4. Check Port queues, assigned profile
5. check the assigned profile attributes, buffer pool, reserved, threshold mode, xoff_th, xon_th, xon_offset_th, share mode
6. Check the buffer pool attributes, size, threshold mode, xoff_size

- test_egress_queue_stat

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. send 10000 packet in a thread (value is transient, fleeting )
4. check the priority group statictics while sending the packet(Get the max number of the statictics during checking), the statictics include: 
   buffer_pool stats:  
   SAI_QUEUE_STAT_PACKETS
   SAI_QUEUE_STAT_BYTES
   SAI_QUEUE_STAT_CURR_OCCUPANCY_LEVEL
   SAI_QUEUE_STAT_WATERMARK_LEVEL
   SAI_QUEUE_STAT_CURR_OCCUPANCY_BYTES
   SAI_QUEUE_STAT_WATERMARK_BYTES
   SAI_QUEUE_STAT_SHARED_CURR_OCCUPANCY_BYTES
   SAI_QUEUE_STAT_SHARED_WATERMARK_BYTES
5. Verify the statictics numbers are increased.

- test_egress_headroom_stats

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. Disbale port TX to simulate congestion
4. Keep sending ``server IP`` packet with length 1000, packet number < pool_size/pkt_length, check the stats of queue, below stats should being increased
   SAI_QUEUE_STAT_PACKETS
   SAI_QUEUE_STAT_BYTES
   SAI_QUEUE_STAT_CURR_OCCUPANCY_LEVEL
   SAI_QUEUE_STAT_WATERMARK_LEVEL
   SAI_QUEUE_STAT_CURR_OCCUPANCY_BYTES
   SAI_QUEUE_STAT_WATERMARK_BYTES
   SAI_QUEUE_STAT_SHARED_CURR_OCCUPANCY_BYTES
   SAI_QUEUE_STAT_SHARED_WATERMARK_BYTES
5. check the pool stats, below stats should being increased
   'SAI_BUFFER_POOL_STAT_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_WATERMARK_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 

- test_egress_headroom_full_drop

1. repeat test test_egress_headroom_stats
2. Keep sending ``server IP`` packet with length 1000, check the pool and queue stats, those stats should increase
   SAI_QUEUE_STAT_DROPPED_PACKETS
   SAI_QUEUE_STAT_DROPPED_BYTES

- test_egress_headroom_reset

1. repeat test test_egress_headroom_stats (make sure no drop happened)
2. enable the port tx
3. check the received packets (should take fault tolerant, 90% should be back)
4. repeat step 1 ~ 3, many time, packets should be back, not drops


- test_egress_queue_stats_shared

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. Make sure defined the xoff size in buffer pool, for a shared mode
3. According to common config, set the xoff_th
4. disable port tx
5. send the packets, check the stats, when packet number from less to larger than (xoff_th/packet_length), stats should be the actual size
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 

test_egress_queue_stats_non_shared

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. Make sure defined the xoff as zero in buffer pool, for a non-shared mode
3. According to common config, set the xoff_th
4. disable port tx
5. send the packets, check the stats, when packet number from less to larger than (xoff_th/packet_length), stats should be the xoff_th size for the most
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_CURR_OCCUPANCY_BYTES', 
   'SAI_BUFFER_POOL_STAT_XOFF_ROOM_WATERMARK_BYTES', 

- test_egress_overflowed_pkt_recover

1. repeat test test_egress_headroom_stats (100 packets is good enough, make sure no drop happened, and send with dscp in sequence, 1~8)
2. enable the port tx
3. check the received packet is follow the dscp sequence

- test_egress_flow_control_drop

1. repeat test test_egress_headroom_stats, but **with** flow control set on PGs and Queues
2. Keep sending ``server IP`` packet with length 1000, check the pool and queue stats, those stats should **NOT** increase
   SAI_QUEUE_STAT_DROPPED_PACKETS
   SAI_QUEUE_STAT_DROPPED_BYTES


- test_change_egress_buffer_profile

1. According to common config, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, flow_control for queue
2. According to common config, config route for desinated ``server IP`` to a ``egress port``
3. send 10000 packet in a thread, and check the packet arrived
4. when sending the packet change, change the buffer profile config
5. check during changing the buffer profile, the packet continue arrived


- test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE
1. create buffer pool with off_size as 0
2. check port attribute SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE
3. check if this attribute can be reteieved  

- test_exceed_QOS_MAXIMUM_HEADROOM_SIZE

1. if test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE resutl non-zero value and no error happened
2. create buffer profile with xoff_th larger than test_SAI_PORT_ATTR_QOS_MAXIMUM_HEADROOM_SIZE/8
3. assign the profile to queue
4. check there should be error happened

- test_egress_static_shared

1. repeat test test_egress_headroom_stats, but config in stastic mode as the common config, and send packets number < (shared_static_th/packet_len)
2. Keep sending ``server IP`` packet with length 1000, check the pool and queue stats, those stats should increase
   SAI_QUEUE_STAT_DROPPED_PACKETS
   SAI_QUEUE_STAT_DROPPED_BYTES 
   SAI_BUFFER_POOL_STAT_DROPPED_PACKET

- test_cpu_queue_qos_map

1. According to common config, binding port queue config to CPU port queues, config DSCP_TC, TC_queue, pool, buffer profile in dynamic mode, no flow_control for queue and PGs
2. Check queue QOS map on port, dscp_tc, tc_queue
3. Check value in dscp_tc, tc_queue map, ``tc``, ``dscp``, ``queue``
4. Check CPU Port queues, assigned profile
5. check the assigned profile attributes, buffer pool, reserved, threshold mode, xoff_th, xon_th, xon_offset_th, share mode
6. Check the buffer pool attributes, size, threshold mode, xoff_size


# Test Group3: QosMap
## Case1: test_diff_dscp_tc_map_diff_port_v4
## Case2: test_one_dscp_tc_map_each_port_v4
## Case3: test_multi_dscp_to_one_tc_v4
## Case4: test_diff_tc_pg_map_diff_port_v4
## Case5: test_one_tc_pg_map_each_port_v4
## Case6: test_multi_tc_to_one_pg_v4
## Case7: test_diff_tc_queue_map_diff_port_v4
## Case8: test_one_tc_queue_map_each_port_v4
## Case9: test_multi_tc_to_one_queue_v4
## Case10: test_diff_dscp_tc_map_diff_port_v6
## Case11: test_one_dscp_tc_map_each_port_v6
## Case12: test_multi_dscp_to_one_tc_v6
## Case13: test_diff_tc_pg_map_diff_port_v6
## Case14: test_one_tc_pg_map_each_port_v6
## Case15: test_multi_tc_to_one_pg_v6
## Case16: test_diff_tc_queue_map_diff_port_v6
## Case17: test_one_tc_queue_map_each_port_v6
## Case18: test_multi_tc_to_one_queue_v6

### Testing Objective <!-- omit in toc --> 

- test_diff_dscp_tc_map_diff_port - Verify assign differernt dscp to tc map to differnt port and check the packet in v4 and v6
- test_one_dscp_tc_map_each_port - Verify assign same dscp to tc map to differernt port and check the packet in v6 and v6
- test_multi_dscp_to_one_tc - Verift assign multi dscp to one tc and change tc on different port and check packet in v4 and v6
- test_diff_tc_pg_map_diff_port - Verify assign differernt tc to pg map to differnt port and check the packet in v4 and v6 
- test_one_tc_pg_map_each_port - Verify assign same tc to pg map to differernt port and check the packet in v6 and v6
- test_multi_tc_to_one_pg - Verift assign multi tc to pg and change pg on different port and check packet in v4 and v6
- test_diff_tc_queue_map_diff_port - Verify assign differernt tc to queue map to differnt port and check the packet in v4 and v6 
- test_one_tc_queue_map_each_port - Verify assign same tc to queue map to differernt port and check the packet in v6 and v6
- test_multi_tc_to_one_queue - Verift assign multi tc to pg and change queue on different port and check packet in v4 and v6


### Case Steps <!-- omit in toc --> 

- test_diff_dscp_tc_map_diff_port

1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map, use differet map on different ingress port, for example, tc = dscp = (port_num+idx)%8  (dscp can be 32 values)
3. For tc to PG map for each port, dscp=tc from 1~8
4. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
5. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
6. Check the corresponding PG counter, receive the packets on different IPG

- test_one_dscp_tc_map_each_port

1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map, use just use one dscp_tc for each port, but each port with differernt value, for example, tc = dscp = (port_num)%8  (dscp can be 32 values)
3. For tc to PG map for each port, dscp=tc from 1~8
4. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
5. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
6. Check the corresponding PG counter, receive the packets on different IPG

- test_multi_dscp_to_one_tc
  
1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map, just use one dscp_tc for each port, but each port with differernt value, for example, dscp = (port_num+index)%8, tc = (port_num)%8  (dscp can be 32 values), index (1-8)
3. For tc to PG map for each port, dscp=tc from 1~8
4. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
5. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
6. Check the corresponding PG counter, receive the packets on different IPG

- test_diff_tc_pg_map_diff_port

1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map for each port, dscp=tc from 1~8
3. For tc to PG map, use differet map on different ingress port, for example, tc = PG = (port_num+idx)%8
4. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
5. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
7. Check the corresponding PG counter, receive the packets on different IPG

- test_one_tc_pg_map_each_port

1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map for each port, dscp=tc from 1~8
2. For tc to PG map, just use one tc_pg for each port, but each port with differernt value, for example, tc = pg = (port_num)%8 (dscp can be 32 values)
3. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
4. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
5. Check the corresponding PG counter, receive the packets on different IPG

- test_multi_tc_to_one_pg

1. According to common config, pool, buffer profile in dynamic mode
2. For dscp to tc map for each port, dscp=tc from 1~8
3. For tc to PG map map, just use one tc_ipg for each port, but each port with differernt value, for example, pg = (port_num)%8, tc = (port_num+index)%8  (dscp can be 32 values), index (1-8)
4. According to the config, config route for group of desinated ``server IP`` to all ``egress port``
5. Send packet with ``server IP`` and with 8 different DSCP values on differnet port
6. Check the corresponding PG counter, receive the packets on different IPG