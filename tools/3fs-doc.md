<title>3FS性能排查</title>

# 1 现象

<callout emoji="✋">
大量算300 tf 机器出现3fs读写延迟高、性能差的情况
1. 013、014两台节点正常
2. 其它机器均异常
3. 用fio或cp单进程拷贝大文件时，异常节点性能比正常节点性能下降1/3
4. 小文件随机读写延迟相差10倍
</callout>

延迟测试命令

```Bash
fio --name=randread \
    --filename=/3fs/cache/rsq/test.file \
    --size=4G \
    --bs=4k \
    --rw=randread \
    --ioengine=io_uring \
    --iodepth=1 \
    --numjobs=1 \
    --direct=1 \
    --runtime=60 \
    --time_based \
    --group_reporting
```

机器信息

<table><colgroup><col/><col/><col/><col/><col/></colgroup><tbody><tr><td><b>主机名</b></td><td><b>ens1np0（TCP）</b></td><td><b>ens4np0（RoCE）</b></td><td><b>状态</b></td><td><b>备注</b></td></tr><tr><td>lg-cmc-gpu-tf-prod-008.host.lg.shzhisuan.com</td><td>10.100.40.135</td><td>10.100.41.134</td><td>异常机器</td><td rowspan="4">本次测试机器</td></tr><tr><td>lg-cmc-gpu-tf-prod-009.host.lg.shzhisuan.com</td><td>10.100.40.134</td><td>10.100.41.133</td><td>异常机器</td></tr><tr><td>lg-cmc-gpu-tf-prod-013.host.lg.shzhisuan.com</td><td>10.100.40.130</td><td>10.100.41.144</td><td>正常机器</td></tr><tr><td>lg-cmc-gpu-tf-prod-014.host.lg.shzhisuan.com</td><td>10.100.40.143</td><td>10.100.41.142</td><td>正常机器</td></tr><tr><td>lg-cmc-gpu-tf-prod-001.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-005.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-006.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-007.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-008.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-009.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-010.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-011.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-012.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr><tr><td>lg-cmc-gpu-tf-prod-016.host.lg.shzhisuan.com</td><td></td><td></td><td>异常机器</td><td></td></tr></tbody></table>

## 1.1 fio测试

正常机型测试结果：

98%的延迟应该在250us

![](https://feishu.cn/file/NPlObDJeAotVY3xlK6CcbXolnKn)

异常机型测试结果：

96%以上均在2ms

![](https://feishu.cn/file/ZyT7bjtHLo2f8OxnmxWc0w6anhh)

## 1.2 ping测试

> 以009 异常节点做测试，ens4np0网卡对应的ip：10.100.41.133
> 
> 013、014 ens4np0网卡对应的ip分别为：10.100.41.144、10.100.41.142

009异常节点 ping 013正常节点，延迟均在200ms+

![](https://feishu.cn/file/Wq6XbAL7oopd7FxdM4Xc7N99nBc)

013正常节点 ping 014 正常节点，延迟大部分在0.0xxms

![](https://feishu.cn/file/K119bbpjjo7RUIxShxBcjhvZnXc)

![](https://feishu.cn/file/T9O9bUBqeoUYk6x8KmrcEZ3cn1d)

## 1.3 mtr测试

观察输出结果的`Best`字段，发现有问题机型的延迟比正常机型多1倍

```Bash
mtr -I ens4np0 10.100.74.18
```

![](https://feishu.cn/file/AELJbLRWHoALB7xKTjccSKZrn48)

# 2 排查流程

## 2.1 检查网卡队列、pfc、dscp等配置

> 检查ens4np0网卡配置

```Bash
root@lg-cmc-gpu-tf-prod-008:~# mlnx_qos -i ens4np0
DCBX mode: OS controlled
Priority trust state: dscp
dscp2prio mapping:
        prio:0 dscp:07,06,05,04,03,02,01,00,
        prio:1 dscp:15,14,13,12,11,10,09,08,
        prio:2 dscp:23,22,21,20,19,18,17,16,
        prio:3 dscp:31,30,29,28,27,26,25,24,
        prio:4 dscp:39,38,37,36,35,34,33,32,
        prio:5 dscp:40,47,46,45,44,43,42,41,
        prio:6 dscp:48,55,54,53,52,51,50,49,
        prio:7 dscp:63,62,61,60,59,58,57,56,
default priority:
Receive buffer size (bytes): 19872,220896,0,0,0,0,0,0,max_buffer_size=4151520
Cable len: 30
PFC configuration:
        priority    0   1   2   3   4   5   6   7
        enabled     0   0   0   0   0   1   0   0   
        buffer      0   0   0   0   0   1   0   0   
tc: 0 ratelimit: unlimited, tsa: ets, bw: 9%
         priority:  0
tc: 1 ratelimit: unlimited, tsa: ets, bw: 1%
         priority:  1
tc: 2 ratelimit: unlimited, tsa: ets, bw: 80%
         priority:  2
tc: 3 ratelimit: unlimited, tsa: ets, bw: 10%
         priority:  3
tc: 4 ratelimit: unlimited, tsa: strict
         priority:  4
tc: 5 ratelimit: unlimited, tsa: strict
         priority:  5
tc: 6 ratelimit: unlimited, tsa: strict
         priority:  6
tc: 7 ratelimit: unlimited, tsa: strict
         priority:  7
```

设置队列等参数脚本

```Bash
#!/bin/bash

MLNX_ROCE_TOS=162
MLNX_ROCE_CNP_DSCP=48
COMPUTE_IFACES=(ens4np0)
for iface in "${COMPUTE_IFACES[@]}"; do
    # echo "$iface"
    mlnx_qos -i "$iface" --trust=dscp >/dev/null
    mlnx_qos -i "$iface" --cable_len=30
    mlnx_qos -i "$iface" --pfc 0,0,0,0,0,1,0,0 >/dev/null
    mlnx_qos -i "$iface" --prio_tc=0,1,2,3,4,5,6,7 >/dev/null
    # 计算面队列走TC1
    mlnx_qos -i "$iface" --dscp2prio='set,40,5' >/dev/null
    # 流控队列走TC0
    mlnx_qos -i "$iface" --dscp2prio='set,48,6' >/dev/null
    mlnx_qos -i "$iface" -s ets,ets,ets,ets,strict,strict,strict,strict --tcbw=9,1,80,10,0,0,0,0 >/dev/null 2>&1
    # 4151520
    mlnx_qos -i "$iface" --buffer_size 19872,220896,0,0,0,0,0,0 >/dev/null 2>&1
    # enable ECN on priority 5
    echo 1 > /sys/class/net/"$iface"/ecn/roce_np/enable/5
    echo 1 > /sys/class/net/"$iface"/ecn/roce_rp/enable/5
    echo "$MLNX_ROCE_CNP_DSCP" > /sys/class/net/"${iface}"/ecn/roce_np/cnp_dscp
    mlnx_qos -i "$iface" --prio2buffer=0,0,0,0,0,1,0,0 >/dev/null
done

HCA=(mlx5_17)
for mlx in "${HCA[@]}"; do
    echo "$mlx"
    cma_roce_mode -d "$mlx" -p 1 -m 2 1>/dev/null
    cma_roce_tos -d "$mlx" -t "$MLNX_ROCE_TOS" 1>/dev/null
    echo "$MLNX_ROCE_TOS" > /sys/class/infiniband/"$mlx"/tc/1/traffic_class
    mlxreg -d "$mlx" --reg_name ROCE_ACCL --set 'roce_slow_restart_en=0x0,roce_adp_retrans_en=0x1,roce_tx_window_en=0x0,roce_slow_restart_idle_en=0x0' --yes >/dev/null
done

```

## 2.2 cpu频率和模式

主要看`current CPU frequency`，频率和性能模式均正常

```Bash
root@lg-cmc-gpu-tf-prod-013:~# cpupower frequency-info
analyzing CPU 0:
  driver: intel_pstate
  CPUs which run at the same hardware frequency: 0
  CPUs which need to have their frequency coordinated by software: 0
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 800 MHz - 3.90 GHz
  available cpufreq governors: performance powersave
  current policy: frequency should be within 800 MHz and 3.90 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: Unable to call hardware
  current CPU frequency: 3.60 GHz (asserted by call to kernel)
  boost state support:
    Supported: yes
    Active: yes

```

设置高性能模式命令

```Bash
# 配置
cpupower frequency-set -g performance

# 验证
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 查看当前频率
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
```

## 2.3 路由表检查

> 需去报RoCE有优先级较低的默认路由，无异常

```Bash
# route -n
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.100.40.1     0.0.0.0         UG    0      0        0 ens1np0
0.0.0.0         10.100.41.1     0.0.0.0         UG    4096   0        0 ens4np0
10.100.40.0     0.0.0.0         255.255.255.0   U     0      0        0 ens1np0
10.100.41.0     0.0.0.0         255.255.255.0   U     4096   0        0 ens4np0
10.100.41.1     0.0.0.0         255.255.255.255 UH    4096   0        0 ens4np0
172.16.0.0      0.0.0.0         255.240.0.0     U     0      0        0 host0
172.17.0.0      0.0.0.0         255.255.0.0     U     0      0        0 docker0
172.18.64.0     0.0.0.0         255.255.255.0   U     0      0        0 host0

```

## 2.4 ib_write_lat延迟测试

> 跟存储端的rdma网卡进行打流测试，无异常

```Bash
# server端
ib_write_lat -F -n 2000 -s 2 --report_gbits -d mlx5_0 -p6007

# 客户端
ib_write_lat -F -n 2000 -s 2 --report_gbits -d mlx5_17 -p6007 <业务ip>
```

## 2.5 检查3fs配置文件

> 配置文件一致，无异常

```Bash
# 对比配置文件
cat /opt/3fs/etc/hf3fs_fuse_main_launcher.toml
```

检查fuse版本，无异常

```Bash
root@lg-cmc-gpu-tf-prod-008:~# fusermount -V
fusermount version: 2.9.9
root@lg-cmc-gpu-tf-prod-008:~# fusermount3 -V
fusermount3 version: 3.16.2
root@lg-cmc-gpu-tf-prod-008:~# ps -ef | grep 3fs
root      148531       1  1 20:57 ?        00:00:13 /opt/3fs/bin/hf3fs_fuse_main --launcher_cfg /opt/3fs/etc/hf3fs_fuse_main_launcher.toml
root      148596  148531  0 20:57 ?        00:00:00 fusermount3 --auto-unmount -- /3fs/cache
root      206991   75381  0 21:10 pts/2    00:00:00 grep --color=auto 3fs

```

## 2.6 检查3fs客户端和网卡的numa分布

> 正常机型ens4np0网卡在numa1，3fs进程numa0，有问题的机型3fs numa设置亲和1，无效果

```Bash
# 查看进程numa分布
root@lg-cmc-gpu-tf-prod-008:~# ps -ef | grep 3fs
root     2604511 2603349  0 09:58 pts/8    00:00:00 grep --color=auto 3fs
root     3932177       1  1 Jul30 ?        00:08:38 /opt/3fs/bin/hf3fs_fuse_main --launcher_cfg /opt/3fs/etc/hf3fs_fuse_main_launcher.toml
root     3932238 3932177  0 Jul30 ?        00:00:00 fusermount3 --auto-unmount -- /3fs/cache
root@lg-cmc-gpu-tf-prod-008:~# numastat -p 3932177
Per-node process memory usage (in MBs) for PID 3932177 (hf3fs_fuse_main)
                           Node 0          Node 1           Total
                  --------------- --------------- ---------------
Huge                         0.00            0.00            0.00
Heap                         0.00            2.23            2.23
Stack                        0.00            0.10            0.10
Private                     357.14           11.68         368.83
----------------  --------------- --------------- ---------------
Total                       359.47           11.68         371.15


# 查看网卡numa分布
root@lg-cmc-gpu-tf-prod-008:~# cat /sys/class/net/ens4np0/device/numa_node
1
```

## 2.7 检查ib网卡等驱动是否正常加载

> 驱动版本均一致，无异常

```Bash
root@lg-cmc-gpu-tf-prod-008:~# ethtool -i ens4np0
driver: mlx5_core
version: 23.10-1.1.9
firmware-version: 28.39.3560 (MT_0000000838)
expansion-rom-version: 
bus-info: 0000:e6:00.0
supports-statistics: yes
supports-test: yes
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: yes

```

检查rdma驱动加载是否正常

```Bash
root@lg-cmc-gpu-tf-prod-008:~# lsmod | grep "rdma"
rdma_ucm               28672  1
rdma_cm               122880  1 rdma_ucm
iw_cm                  49152  1 rdma_cm
ib_cm                 131072  2 rdma_cm,ib_ipoib
ib_uverbs             135168  141 rdma_ucm,mlx5_ib
ib_core               434176  9 rdma_cm,ib_ipoib,nvidia_peermem,iw_cm,ib_umad,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm
mlx_compat             69632  11 rdma_cm,ib_ipoib,mlxdevm,iw_cm,ib_umad,ib_core,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm,mlx5_core
```

无bond，无需检查802.1q驱动

## 2.8 检查网卡丢包、错包、mtu情况

> 无增长的丢包计数，且错包数量在测试阶段无增长，mtu1500（dhcp自动分配），无异常

```Bash
# ip -s -s link show ens4np0
5: ens4np0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether d8:94:24:4a:af:a2 brd ff:ff:ff:ff:ff:ff
    RX:  bytes packets errors dropped  missed   mcast           
     113679554  916406     54       0       0  764902 
    RX errors:  length    crc   frame    fifo overrun           
                    54      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
      31659318  200165      0       0       0       0 
    TX errors: aborted   fifo  window heartbt transns
                     0      0       0       0       3 
    altname enp230s0np0

# ethtool -S ens4np0 | grep -iE 'discards'
```

## 2.9 show_gids顺序

```Bash
show_gids | grep ens4np0
```

如下是正常的

![](https://feishu.cn/file/MP3CbgPVLowxl8xt9nacudD5nnD)

## 2.10 内核参数检查

> 对比正常和异常机型的内核配置，无异常

```Bash
sysctl -a
```

## 2.11 检查网卡光衰

> 在正常范围内的均无异常

```Bash
ethtool -i ens4np0 | grep "bus-info"
mlxlink -d <bus-info> -m | grep dBm

# 结果在范围内代表正常
Rx Power Current [dBm]             : 1.103,1.290,0.931,1.103 [-9.508..6.999]
Tx Power Current [dBm]             : 1.380,1.638,1.449,1.123 [-8.508..6.999]
```

## 2.12 火焰图分析

从火焰图可以看出在fio测试阶段，正常机器不同阶段读写耗时较少

![](https://feishu.cn/file/WloObAhMRoHN9MxGFsVcMPKNnPb)

![](https://feishu.cn/file/LkIPb2MDqouMOjxM9KCckEN6n4f)

## 2.13 fio进程分析

> 确认 fio 时间花在哪——是在 `try_grab_compound_head`（GUP 页 pin）、`io_uring_enter`、还是 `fuse_direct_IO`，可以明显看出 `try_grab_compound_head`

```Bash
ps -ef | grep fio
perf top -p <PID> # 排除其他进程干扰，聚焦 fio 在忙什么
```

对比结果

```Bash
# 013正常节点 perf top 数据
Overhead  Shared Object                       Symbol                                                                                                                 
  58.57%  [kernel]                            [k] try_grab_compound_head
  11.58%  [kernel]                            [k] gup_pte_range
   3.73%  [kernel]                            [k] update_sg_lb_stats
   1.49%  [kernel]                            [k] _raw_spin_lock
   1.00%  [kernel]                            [k] _raw_spin_lock_irqsave
   0.74%  [kernel]                            [k] fuse_direct_io
   0.68%  [kernel]                            [k] available_idle_cpu
   0.66%  [kernel]                            [k] fuse_lock_owner_id
   0.48%  [kernel]                            [k] psi_group_change
   0.45%  [kernel]                            [k] kmem_cache_alloc_trace
   0.44%  fio                                 [.] get_io_u
   0.40%  [kernel]                            [k] task_work_run
   0.39%  [kernel]                            [k] io_req_io_end
   0.38%  [kernel]                            [k] tctx_task_work
   0.34%  [kernel]                            [k] io_run_task_work
   0.33%  [kernel]                            [k] fuse_invalidate_atime
   0.31%  [kernel]                            [k] fuse_direct_IO
   0.30%  [kernel]                            [k] fput_many
   0.29%  [kernel]                            [k] dequeue_entity
   0.26%  [kernel]                            [k] ttwu_queue_wakelist
   0.24%  [kernel]                            [k] gup_pgd_range
   0.24%  [kernel]                            [k] io_read
   0.23%  [kernel]                            [k] __fget_light
   0.23%  [kernel]                            [k] memset_erms
   0.23%  [kernel]                            [k] send_call_function_single_ipi
   0.23%  [kernel]                            [k] __wake_up_common
   0.23%  [kernel]                            [k] _raw_spin_lock_irq
   0.22%  [kernel]                            [k] __kmalloc
   0.22%  [kernel]                            [k] fuse_get_req


# 008 异常节点 perf top 数据
Overhead  Shared Object                       Symbol                                                                                                                 
  24.72%  [kernel]                            [k] try_grab_compound_head
   5.82%  [kernel]                            [k] gup_pte_range
   1.92%  [kernel]                            [k] kmem_cache_alloc_trace
   1.85%  fio                                 [.] get_io_u
   1.29%  [kernel]                            [k] io_req_io_end
   1.25%  [kernel]                            [k] tctx_task_work
   1.22%  [kernel]                            [k] select_task_rq_fair
   1.15%  [kernel]                            [k] __fget_light
   1.12%  [kernel]                            [k] kmem_cache_alloc
   1.05%  [kernel]                            [k] _raw_spin_lock
   1.04%  [kernel]                            [k] _raw_spin_lock_irqsave
   1.01%  [kernel]                            [k] __get_user_8
   1.00%  [kernel]                            [k] apparmor_file_permission
   0.94%  [kernel]                            [k] gup_pgd_range
   0.91%  [kernel]                            [k] io_prep_rw
   0.79%  [kernel]                            [k] psi_group_change
   0.79%  [kernel]                            [k] fuse_direct_IO
   0.78%  fio                                 [.] put_file
   0.78%  bpf_prog_94ff029fa309f6a4_sys_exit  [k] bpf_prog_94ff029fa309f6a4_sys_exit
   0.76%  [kernel]                            [k] syscall_exit_work
   0.76%  [kernel]                            [k] __perf_event_task_sched_in
   0.75%  libc.so.6                           [.] syscall
   0.73%  [kernel]                            [k] syscall_return_via_sysret
   0.72%  [kernel]                            [k] send_call_function_single_ipi
   0.72%  [kernel]                            [k] __wake_up_common
   0.71%  fio                                 [.] 0x000000000009d3c7
   0.70%  [kernel]                            [k] io_read
   0.69%  [kernel]                            [k] fuse_direct_io
   0.68%  [kernel]                            [k] io_req_prep
   0.64%  [kernel]                            [k] bpf_trace_run2
   0.64%  [kernel]                            [k] cpuacct_charge
   0.64%  [kernel]                            [k] available_idle_cpu
   0.64%  [kernel]                            [k] fuse_get_req
   0.63%  [kernel]                            [k] fuse_file_read_iter
   0.61%  [kernel]                            [k] newidle_balance
   0.59%  [kernel]                            [k] security_file_permission
```

## 2.14 网络排查

根据ping包延迟高联系网络侧排查，正常和异常的GPU机器均接入的同一台交换机同网段，异常机器ping正常机器、异常机器ping异常机器延迟均很高，网络侧反馈2层基本没有交换机参与，且接入交换机端口未见丢包，排除网络问题。

# 3 根因

## 3.1 cpupower idle-info C1_ACPI和C2_ACPI 未禁用（根因）

一句话根因：正常节点机器C1_ACPI和C2_ACPI均是禁用状态，异常机器未禁用。CPU C-state（休眠状态）导致的网络延迟问题。

![](https://feishu.cn/file/Wp5tbXT5toMq8exVj8HcgC7unCh)

## 3.2 根因分析

现代 Intel CPU 在空闲时会进入不同深度的休眠状态（C-state）以省电：

| **状态** | **说明** | **Exit Latency（退出延迟）** |
|-|-|-|
| POLL/C0 | 忙等待/运行态 | 0 |
| C1_ACPI | 轻度休眠 | 1 μs |
| C2_ACPI | 深度休眠 | 170 μs |

`cpupower idle-info` 里的 **Latency** 就是 CPU 从该睡眠态被唤醒、恢复到可执行指令状态所需的时间。

开启状态运行逻辑

- C1_ACPI、C2_ACPI 均**启用**（未标 DISABLED），CPU 在两次网卡中断之间的空闲窗口里，`menu` 调度器（cpuidle governor）会根据历史空闲时长预测，主动把核心切换进 C2_ACPI 省电。
- 当网络包（ICMP echo）到达触发硬件中断时，CPU 需要先从 C2_ACPI **唤醒**，这个唤醒开销是 **170μs**，再加上中断响应、调度延迟，会直接叠加到 ping RTT 里。

关闭状态下运行逻辑

- 所有 C-state 都被 **DISABLED**（只在 C0/POLL 附近运转，实际上是被强制锁在浅层甚至运行态），CPU 核心几乎不进入深睡眠，中断到达时可以**几乎零延迟**响应，所以 ping 延迟更低、更稳定（抖动也更小）。



一般需要把C2禁用，C2 是延迟大头（170μs exit latency），C1 的 1μs 影响小但一起禁更彻底。经过测试只禁C2，性能提升70%，C1一块禁，读写延迟性能跟正常机型一致。

state index 是动态的——不同机器/BIOS 的 `C-state` 列表可能不同（有的有 C6），先用 `cpupower idle-info` 看清楚序号再禁。

`cpupower idle-set` 重启失效。

```Bash
# 查看
cpupower idle-info

# 禁用
cpupower idle-set -d 2 -d 1
```

持久化配置，编辑 `/etc/default/grub`

```Bash
GRUB_CMDLINE_LINUX="... intel_idle.max_cstate=1 processor.max_cstate=1"
```

重启

```Bash
update-grub
reboot
```

禁用后随机读写延迟降低，符合正常机型90%+的延迟在250us左右

![](https://feishu.cn/file/Bevpbpzldob2eFxDJsYcXRd1n28)