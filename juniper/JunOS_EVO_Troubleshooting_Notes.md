# Juniper JunOS EVO 运维排错学习笔记

> 来源：SharePoint 内部知识库 — ACX-EVO-PAGE（作者：Arpit Chaudhary）
> 整理日期：2026-06-27

---

## 目录

1. [Accessing Shells](#1-accessing-shells)
2. [Basic Data Collection](#2-basic-data-collection)
3. [Data Collection（总纲）](#3-data-collection总纲)
4. [Debugging Nodes and Applications](#4-debugging-nodes-and-applications)
5. [Hostpath Commands List](#5-hostpath-commands-list)
6. [Journalctl](#6-journalctl)
7. [L2VPN Troubleshooting](#7-l2vpn-troubleshooting)
8. [L3 Troubleshooting](#8-l3-troubleshooting)
9. [L3VPN Troubleshooting](#9-l3vpn-troubleshooting)
10. [LDP Label Walk](#10-ldp-label-walk)
11. [platform-fru-get-state](#11-platform-fru-get-state)
12. [request system debug-info](#12-request-system-debug-info)
13. [SE-CDO-036 ACX7100 控制面排错（Hostpath）](#13-se-cdo-036-acx7100-控制面排错hostpath)
14. [Traces（应用跟踪）](#14-traces应用跟踪)
15. [Troubleshooting FPC](#15-troubleshooting-fpc)
16. [Troubleshooting Interfaces and Optics](#16-troubleshooting-interfaces-and-optics)

---

## 1. Accessing Shells

### 核心用途
介绍 JunOS EVO 平台上访问各类 Shell/调试终端的方法，包括 PFE CLI、FPC Linux Shell、BCM Broadcom Shell。

### 关键命令/步骤

**CLI-PFE（EVO 平台的 PFE 命令接口）**
```bash
# 方式一：从 JunOS CLI 进入
labroot@h09-46> start shell
[vrf:none] labroot@h09-46:~$ cli-pfe
labroot@h09-46:pfe>

# 方式二：直接进入 PFE network 命名空间
labroot@h09-46> start shell pfe network fpc0
labroot@h09-46:pfe>
```

**FPC Shell（FPC 的 Linux Shell）**
```bash
labroot@h09-46> start shell
[vrf:none] labroot@h09-46:~$ vty fpc0.0
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
jnx(/dev/pts/7)#
```

**BCM SHELL（Broadcom 芯片调试 Shell）**
```bash
labroot@h09-46> start shell user root
Password:
[vrf:none] root@h09-46:~# jbcmsh
BCM.0>

# 或直接执行 BCM 命令：
root@h09-46:~# jbcmcmd.py "l3 Egress Allocation"
# 输出内容：FEC MDB cluster allocation（FEC集群分配信息）
```

**PFE 中执行 BCM 命令**
```bash
labroot@e06-47:pfe> set evo-pfemand bcmshell cmd "l3 Egress Allocation"
```

### 重要提示
- 进入 BCM Shell 需要 root 密码
- `jbcmsh` 进入 BCM 交互式 Shell；`jbcmcmd.py` 直接执行单条 BCM 命令
- PFE network shell 可直接访问 FPC 网络命名空间

---

## 2. Basic Data Collection

### 核心用途
收集 JunOS EVO 设备基本诊断信息的基础 CLI 命令列表。

### 关键命令/步骤

| CLI 命令 | 说明 |
|---|---|
| `show system alarms` | 查看当前告警列表 |
| `show system errors active detail` | 查看当前活跃错误详情 |
| `show system errors inactive detail` | 查看已清除的错误（用于判断是否存在 flap） |
| `show chassis environment` | 查看机箱组件状态和温度 |
| `show chassis power` | 查看电源状态 |
| `request support information \| no-more \| save /var/tmp/rsi-<router-name>.txt` | 收集 RSI（支持信息）并保存到文件 |
| `start shell user root` | 进入 root shell |
| `tar -zcf /var/tmp/re0-all-logs /var/log/*` | 压缩所有日志 |
| `file archive compress source /var/log/* destination /var/tmp/xxx` | 使用 JunOS 命令压缩日志（注：此命令有已知问题 PR 1522339） |

### 重要提示
- 生产环境压��日志大约需要 10 分钟
- 解压日志大约需要 10-15 分钟
- `file archive compress` 命令存在已知缺陷

---

## 3. Data Collection（总纲）

### 核心用途
ACX-EVO 页面上所有排错文档的目录/导航页面，列出了各专项排错指南的链接。

### 文档索引
- **配置指南**: EVPN Config Guide for ACX-EVO
- **调试指南**: L3 Troubleshooting, L2VPN Troubleshooting, L3VPN Troubleshooting, LDP Label Walk, EVPN
- **主机路径**: Architecture, Host-Path
- **数据采集**: RSI and compressed logs, `request system debug-info`, Journalctl, Traces, Debugging Nodes and Applications, Accessing Shells
- **数据路径**: Troubleshooting Interfaces and Optics
- **硬件**: FRU state for Hardware related issues, Troubleshooting FPC

---

## 4. Debugging Nodes and Applications

### 核心用途
检查和调试 JunOS EVO 平台上的节点（Node）和应用（Application）状态。

### 关键命令/步骤

**节点状态检查**
```bash
show system nodes                    # 查看所有节点是否 Active
show system node-attributes          # 查看节点属性
```

**应用状态检查**
```bash
show system applications brief node re0     # 查看 re0 上所有应用的简要状态
show system applications detail node re0    # 查看 re0 上所有应用的详细状态
show system applications app <app name> detail node re0  # 查看指定应用的详细状态
show system applications app sysman detail   # 查看 sysman 应用的详细状态
```

**从 RE Shell 查看应用列表**
```bash
sysmanctl app list
```

**App-Controller 调试命令**
```bash
show platform app-controller incomplete
show platform app-controller summary
show platform app-controller complete
```

**Binding Queue（BQ）调试命令**
```bash
show platform binding-queue summary
show platform binding-queue incomplete
show platform binding-queue pending
```

**DDS（分布式依赖服务）调试命令**
```bash
show platform dependency-state
show platform distributor clients all-clients
show platform distributor eou-status all-clients
```

---

## 5. Hostpath Commands List

### 核心用途
ACX7100 主机路径（Hostpath/Host-Path）排错命令集，包括接口统计、PFE 统计、包捕获和 DDoS 防护配置。

### 关键命令/步骤

**基本诊断命令**
```bash
show interfaces extensive <接口名>
show pfe statistics traffic
show system statistics jtd
```

**RE Shell 命令**
```bash
start shell user root
# jbcmcmd.py "diag count g"     # 查看所有端口丢包计数
# ifconfig brcmknet0             # 查看主机路径网络接口
```

**PFE Network Shell 命令**
```bash
start shell pfe network fpc0
pfe> show evo-pfemand filter counters all
pfe> show evo-pfemand host asic-queues
pfe> show evo-pfemand host pkt-stats
pfe> show evo-pfemand host asic-queues sched-config
pfe> show host-path ports
pfe> show host-path ports fp0
pfe> show host-path ports punts
pfe> show host-path packet-type
pfe> show host-path packets
```

**包捕获（Packet IO）**
```bash
# 在 PFE 上开启跟踪
pfe> set trace-options host-path packet state extensive all enable
pfe> set trace-options host-path packet port transport
pfe> set trace-options host-path packet port io

# 在 Shell 中查看 HEX 输出
~# journalctl -f -u packetio-brcm
```

**DDoS 防护配置**
```bash
# 设置带宽和突发值
set system ddos-protection protocols arp aggregate bandwidth 500 burst 1000
set system ddos-protection protocols bgp aggregate bandwidth 2000 burst 4000

# 设置违规自动恢复时间
set system ddos-protection protocols arp aggregate recover-time 10

# 禁用某个协议的 RE DDoS 保护
set system ddos-protection protocols arp aggregate disable-routing-engine

# 清除 DDoS 统计/状态
clear ddos-protection protocols statistics
clear ddos-protection protocols states
```

---

## 6. Journalctl

### 核心用途
在 JunOS EVO 的 RE Linux Shell 中使用 `journalctl` 查看系统日志。

### 关键命令/步骤

```bash
# 进入 Shell
> start shell user root

# 导出当前启动的完整日志
# journalctl -a > /var/tmp/journalctl-log.txt

# 当前启动的日志
journalctl -b > /var/tmp/currentJournalCtlLog

# 前一次启动的日志
journalctl -b 1 > /var/tmp/prev1JournalCtlLog
journalctl -b 2 > /var/tmp/prev2JournalCtlLog

# 所有日志（当以上步骤信息不足时使用）
journalctl -a > /var/tmp/allJournalCtlLog

# 按时间戳范围查看
journalctl -a -S "2020-06-23 14:00:00" -U "2020-06-24 15:05:00"

# 或使用 --since / --until
journalctl -a --since "2020-06-24 12:00:00" --until "2020-06-24 12:05:00"

# 查看最近 X 分钟的日志
labroot@swi-mfc-core-2> set cli timestamp
labroot@swi-mfc-core-2> start shell
journalctl -b --since "60 min ago"
```

### 重要提示
- `journalctl -b` = 本次启动日志；`-b 1` = 上次启动；`-b 2` = 前次启动
- 所有日志导出可能很大，仅在步骤 #2/#3 信息不足时才使用
- 参考文档：https://www.freedesktop.org/software/systemd/man/journalctl.html
- 建议先用时间范围过滤再导出，避免日志文件过大

---

## 7. L2VPN Troubleshooting

### 核心用途
排查 L2VPN（二层 VPN）连接问题，包括 BGP 对等体状态、标签交换路径（LSP）和转发平面验证。

### 关键命令/步骤

**检查 BGP 对等体**
```bash
run show bgp summary
# 关键字段：State|#Active/Received/Accepted/Damped
# bgp.l2vpn.0: 显示 L2VPN 路由数量
```

**检查 L2VPN 连接状态**
```bash
run show l2vpn connections
# St 字段含义：
#   Up - 正常    Dn - 中断
#   EI - 封装无效  EM - 封装不匹配
#   VC-Dn - 虚电路中断
#   OL - 无出标签  IL - 无入标签
#   NP - 接口硬件不存在
#   LD/RD - 本地/远端站点信号中断
```

**检查路由**
```bash
# 查看 L2VPN 路由表
run show route table L2VPN

# 查看 MPLS 转发条目
run show route table mpls.0 next-hop <远端PE地址>

# 查看 MPLS 转发表
run show route forwarding-table table default.mpls
```

**接口检查**
```bash
run show interfaces <接口名>.500
```

### 重要提示
- L2VPN 依赖于 BGP 对等体正常 + LSP 正常
- 入标签（Incoming label）和出标签（Outgoing label）需在 L2VPN connection 输出中确认
- 封装类型必须两端匹配（如 ethernet-vlan）
- `no-control-word` 配置需两端一致

---

## 8. L3 Troubleshooting

### 核心用途
排查三层接口/路由转发问题，包含接口配置、ARP、IPv6 邻居、路由转发表的验证方法。

### 关键命令/步骤

**接口配置示例**
```junos
interfaces {
    et-0/0/0 {
        vlan-tagging;
        unit 0 {
            vlan-tags outer 10;
            family inet {
                address 110.0.0.1/24 {
                    arp 110.0.0.2 mac 00:11:22:33:44:55;
                }
            }
            family inet6 {
                address 2110.0.0.1/24 {
                    arp 2110.0.0.2 mac 00:11:22:33:44:55;
                }
            }
        }
    }
}
```

**验证命令**
```bash
# 查看逻辑接口
run show interfaces et-0/0/0.0

# 查看 ARP 表
run show arp hostname 110.0.0.2

# 查看 IPv6 邻居
run show ipv6 neighbors

# 查看三层转发表
run show route forwarding-table family inet
```

### 重要提示
- 接口状态 Flags 为 `Up` 表示接口正常工作
- 静态 ARP 配置需确认 MAC 地址正确
- 路由转发表中 `ucst` 表示单播转发，`locl` 表示本地地址，`recv` 表示接收

---

## 9. L3VPN Troubleshooting

### 核心用途
排查三层 VPN（L3VPN/VRF）的控制平面和转发平面问题，从 BGP 路由接收到 PFE NH 编程的全链路检查。

### 关键命令/步骤

**基础检查流程**

1. **确认 LSP 正常**
   ```bash
   run show mpls lsp ingress
   # State 应为 Up
   ```

2. **确认从 BGP 收到远端路由**
   ```bash
   run show route receive-protocol bgp <远端PE地址> table <vrf名称>.inet
   ```

3. **检查 MPLS 标签路由**
   ```bash
   run show route table mpls.0 protocol vpn
   ```

4. **检查 VRF 转发表**
   ```bash
   run show route forwarding-table vpn <vrf名称>
   ```

**PFE 层次检查（CLI-PFE）**

5. **查找 VPN 实例的路由表索引**
   ```bash
   pfe> show route table
   ```

6. **查看目标前缀的 NH**
   ```bash
   pfe> show route proto 2 prefix 33.33.33.0/24 index <table_index>
   # proto: 2=ipv4, 5=mpls, 6=ipv6, 35=bridge
   ```

7. **查看 NH 详情**
   ```bash
   pfe> show evo-pfemand nh db index <NH_ID>
   pfe> show evo-pfemand nh detail index <NH_ID>
   ```

8. **如果是 indirect 或 composite NH，需查看 Target NH**
   ```bash
   pfe> show evo-pfemand nh detail index <TARGET_NH_ID>
   ```

### 重要提示
- NH Type 为 `indirect` 或 `software` 时需进一步查看 Target NH
- 转发路径：VRF 路由 → indirect NH → software NH（Push 标签）→ 出接口
- `vrf-table-label` 配置会生成针对 VRF 的 MPLS 标签

---

## 10. LDP Label Walk

### 核心用途
针对 ACX7100 设备，从 MX 到 ACX7100 的 LDP 标签编程正确性验证，逐跳检查入标签→出标签的映射。

### 关键命令/步骤

**步骤 1：在 MX 上查看目标路由的推送标签**
```bash
labroot@twister-re0> show route 10.138.104.2
# inet.3 中显示 Push 标签值（如 Push 79）
```

**步骤 2：在 ACX7100 上检查入标签的转发条目**
```bash
labroot@h09-46> show route forwarding-table label 79
# Routing table: default.mpls
# 期待看到：Swap <新标签值>
```

**步骤 3：在 PFE 中验证 NH 编程**
```bash
labroot@h09-46:pfe> show evo-pfemand nh detail index <sftw NH Index>
# 关键字段：
#   Nh Type      : software
#   Proto        : mpls
#   Label Info   : 显示标签值（如 0005a000 对应标签 90）
#   Brcm-NH      : Broadcom 芯片中的 NH 索引
#   DMAC         : 目标 MAC 地址
#   BCM index    : 芯片级索引（如 200999e9）
```

### 重要提示
- 核心验证点：标签是否正确交换（例如 79 → 90）
- 检查 Brcm-NH 和 BCM index 确认芯片级编程
- 需要确认出接口和下一跳 MAC 地址正确

---

## 11. platform-fru-get-state

### 核心用途
收集所有硬件组件（FRU）的状态信息，包括 CLI 和 Shell 层面的数据，非常适用于硬件相关问题排错。

### 关键命令/步骤

```bash
# 进入 Shell
labroot@h09-44> start shell

# 执行 FRU 状态收集
[vrf:none] labroot@h09-44:~$ platform-fru-get-state
```

### 重要提示
> ⚠️ **注意**：早期版本通过 `xmen-fru-get-state` 运行，现已更名为 `platform-fru-get-state`

- 该命令会执行大量底层硬件探测命令：
  - `dmidecode` - 内存/处理器信息
  - `boot-fpga` - FPGA 状态
  - `i2cset/i2cget` - I2C 总线设备访问
  - `jbcmcmd.py` - Broadcom 芯片寄存器读取
- 执行过程中的 ERROR 可能是正常现象（硬件不存在或权限不足），不代表 FRU 有问题
- 对硬件排错非常有用，建议在硬件相关 case 中收集

---

## 12. request system debug-info

### 核心用途
从 JunOS EVO 设备收集调试信息（日志等），结果存储在 `/var/tmp/debug_collector_<timestamp>` 目录。

### 关键命令/步骤

```bash
# 完整模式
labroot@router> request system debug-info

# Lite 模式（从 20.4R1 开始支持）
labroot@router> request system debug-info mode lite
# 可能参数：lite（仅运行选定的调试命令）/ normal（运行所有调试命令）
```

### 重要提示
> ⚠️ **注意**：并非所有客户都愿意执行此操作！

- 需要知道设备的 root 密码
- 收集时间最长可达 45 分钟（取决于日志大小）
- 非 root 用户运行时部分 CLI 命令无法访问
- Lite 模式从 20.4R1 开始提供

---

## 13. SE-CDO-036 ACX7100 控制面（Hostpath）排错

### 核心用途
ACX7100 控制面（主机路径/Host Path）排错的培训课件，涵盖架构概览、排错命令、队列统计、DDoS 统计、流量捕获和核心转储。

### 课件大纲
1. 引言 - Broadcom DNX 系列介绍
2. ACX7100 Host Path 概览
3. ACX7100 Host Path 构建模块
4. ACX7100 Host Path 命令
5. Host Path 队列速率
6. Host Path 队列统计
7. DDoS 统计
8. 通过 DDoS 配置修改 Host Path 队列速率
9. 转储/捕获 Host Path 流量
10. ACX7100 数据收集
11. 排错数据收集（与传统 JUNOS 的差异）
12. Core dump（核心转储）
13. 重启进程

### 关键命令
（参见上文第 5 节 — Hostpath Commands List）

### 重要提示
- 这是一个 PowerPoint 课件的 HTML 保存版本
- 具体命令细节参考 Hostpath Commands List 文档（第 5 节）
- 与传统 JunOS 相比，EVO 平台的数据收集方式有显著差异

---

## 14. Traces（Application Traces）

### 核心用途
在 JunOS EVO 路由器上查看应用跟踪日志，提供 5 种不同的查看方式。

### 关键命令/步骤

**Option 1：通过 CLI 查看（有限制，只能查看约 100MB 日志）**
```bash
labroot@router> show trace application hwdre node re0 ?
# 参数：
#   application <应用名>    - 指定应用
#   live                 - 实时模式查看
#   node <re0|re1>       - 指定节点
#   pid <PID>            - 指定进程 PID
#   terse                - 精简视图
#   time <分钟>           - 最近 X 分钟的跟踪
```

**Option 2：实时模式（Live）**
```bash
# 在终端实时显示日志，非常适用于复现问题时跟踪
labroot@router> show trace application hwdre node re0 live
```

**Option 3：通过 Shell 脚本（show_trace.py）**
```bash
[vrf:none] root@c21-24:~# show_trace.py -a hwdre | grep 2020-07-01
```

**Option 4：写入文件**
```bash
[vrf:none] root@c21-24:~# show_trace.py -a hwdre -f /var/tmp/hwdre_traces.log
```

**Option 5：按时间过滤**
```bash
[vrf:none] root@c21-24:~# show_trace.py -a hwdre -t 200
# 显示过去 200 分钟内变化的跟踪
```

**show_trace.py 完整参数**
```bash
show_trace.py [-h] [-a APPLICATION] [-n NODE] [-l LOCATION] [-p PID]
              [-t TIME_CHANGED] [-f OUTPUT_FILE] [-v] [-b BABELTRACE_PATH]
              [PATH]
# PATH: 可选的备选跟踪文件夹路径
```

**在 qnbaasshellserver 上使用**
```bash
# 工具路径：/volume/evo/files/public/ui-tools/show_trace.py
/volume/evo/files/public/ui-tools/show_trace.py -a hwdre /volume/CSdata/.../var/log/traces/ | grep 2020-05-06
```

### 重要提示
- Option 1（CLI 方式）只能查看约 100MB 的日志
- Live 模式在复现问题时非常有用
- `show_trace.py` 脚本也存储在 qnbaasshellserver 上供线下分析使用

---

## 15. Troubleshooting FPC

### 核心用途
排查 FPC（灵活 PIC 集中器）硬件故障，包括 HWD 状态检查、日志收集、SysFS 状态确认和 PCIe 验证。

### 关键命令/步骤

**基础检查**
```bash
show chassis hardware
show chassis hardware clei-models
```

**HWD（硬件守护进程）状态检查**
```bash
[vrf:none] root@guardian-sw-c1-re0:~# systemctl -l status hwdre
# Active: active (running) 表示 HWD 正常运行
```

**开启 HWD 调试日志**
```junos
set system trace application hwdre node [re0|re1] level debug
```

**收集 HWD 日志**
```bash
[vrf:none] root@guardian-sw-c1-re0:~# show_trace.py -p `pidof hwdre` -a hwdre >& hwdre.log
```

**开启 evo-pfemand 调试并收集日志**
```bash
root@guardian-sw-c1-re0:pfe> set trace-options pfe flags all enable
[vrf:none] root@guardian-sw-c1-re0:~# journalctl _PID=`pidof evo-pfemand` > evo-pfemand.log
```

**收集 picd 日志**
```bash
# 日志位于 /var/log/picd.log*
```

**FRU 组件初始化状态**
```bash
show platform dmf detail
# 输出较长，用于查看 FRU 组件级别的初始化状态
```

**SysFS 电源和状态检查**
```bash
# 检查 FPC7 是否使能
[root@guardian-sw-c1-re1:/sys/devices/platform/jnx/card/fpc7]# cat enable
[root@guardian-sw-c1-re1:/sys/devices/platform/jnx/card/fpc7]# cat state
# 期望：active
```

**PCIe 验证**
```bash
# 设备 ID 对照：
#   16x100 和 4x400 : 00d1 (RE0) / 00d2 (RE1)
#   20xSFP         : 00E0 (RE0) / 00E1 (RE1)

lspci
lspci -tv
lspci -s <bus:device:func>
```

### 重要提示
- `show platform dmf detail` 输出很长，注意分页
- PCIe 设备 ID 可用于确认 FPC 是否被正确枚举
- SysFS 节点路径：`/sys/devices/platform/jnx/card/fpc<X>/`

---

## 16. Troubleshooting Interfaces and Optics

### 核心用途
排查接口和光模块问题，覆盖 ACX7100 数据路径的 Broadcom PFE ASIC 和 Marvell PHY 调试。

### 关键命令/步骤

**接口基本检查**
```bash
show interface terse
show interfaces <et-x/y/z>
show interfaces <et-x/y/z> detail|extensive|statistics
```

**ACX7100 数据路径组件**
- **Broadcom PFE ASIC** — 位于 FEB 卡上
- **Marvell PHY（主机侧）** — 位于 FPC 上，连接 Broadcom PFE
- **Marvell PHY（线路侧）** — 位于 FPC 上，连接前面板 QSFP 笼
- Broadcom 调试：通过 `jbcmsh` 进入 Broadcom 调试 Shell
- Marvell PHY 调试：在 `cli-pfe` 中使用 `show chassis phy` 和 `test chassis phy` 层级

**BCM Shell 调试命令**
```bash
# 进入 BCM Shell
[vrf:none] root@guardian-sw-c1-re1:~# jbcmsh
BCM.0>

# 查看所有端口状态
BCM.0> port status eth
# 输出：端口号、Enable/Link、速率、Auto-neg、FEC 类型、环回状态

# Serdes 和 PHY 配置详情
BCM.0> phy dsc <bcmPort>
BCM.0> phy dsc <bcmPort> config

# 显示所有端口计数器
BCM.0> show counter
BCM.0> show counter full   # 含报文类型、错误等

# 发送测试流量
BCM.0> tx 100 portbitmap=<bcmPort> size=1000
# 发送 100 个大小 1000 字节的报文

# 查看所有丢弃和处理的报文统计
BCM.0> diag count g
```

### 重要提示
- 接口问题涉及多个组件：PHY → PFE ASIC → FPC 硬件
- Broadcom 相关调试用 `jbcmsh`
- Marvell PHY 相关调试用 `test chassis phy`（在 cli-pfe 中）
- `diag count g` 是查看所有端口丢包情况的快速方法
- `phy dsc` 命令可查看 Serdes 诊断数据（信号完整性等）
