# EVO 通用排错与参考文件 — 结构化中文笔记

> 来源：18份 Juniper EVO 排错参考文件（SharePoint 页面存档）
> 整理时间：2026-06-27

---

## 目录

1. [EVO 平台产品映射与快速入口](#1-evo-平台产品映射与快速入口)
2. [Shell 登录方法汇总（EVO-AFT）](#2-shell-登录方法汇总evo-aft)
3. [数据收集流程](#3-数据收集流程)
4. [EVO Journalctl 收集指南](#4-evo-journalctl-收集指南)
5. [ACX7100 EVO 排错指南](#5-acx7100-evo-排错指南)
6. [EVO 路由/交换排错示例（目录级）](#6-evo-路由交换排错示例目录级)
7. [Hostpath 排错（ACX7100 架构级）](#7-hostpath-排错acx7100-架构级)
8. [PFE 层面命令汇总](#8-pfe-层面命令汇总)
9. [Junos Fusion 排错](#9-junos-fusion-排错)
10. [CMError 知识库与 TRAPSTATS](#10-cmerror-知识库与-trapstats)
11. [EVO Jflow/Sflow 排错](#11-evo-jflowsflow-排错)
12. [ACX7000 JTAC 跳转站](#12-acx7000-jtac-跳转站)
13. [LACP/ae 相关排错说明](#13-lacpae-相关排错说明)
14. [通用排错流程总结](#14-通用排错流程总结)

---

## 1. EVO 平台产品映射与快速入口

> 来源：ACX7000 - JTAC Jump Station

| 产品型号 | 工程代号 | 说明 |
|---------|---------|------|
| ACX7100-32C | X-Men [Storm] | 32口 QSFP28, 4口 QSFP56-DD |
| ACX7100-48L | X-Men [Wolverine] | 48口 |
| ACX509 | Guardian | Guardian 平台 |
| ACX7024 | Ultron | |
| ACX7024X | Ultron-XL | |
| ACX7332 | Gamora-L | |
| ACX7348 | Gamora-M | |
| ACX7020 | Antman Lite | |

### 快速链接目录

- **Debug/Logs**: RSI 日志收集, BCM Debug 命令, Port-Mirror, MEM/CPU Debug
- **Interface**: SFP 排错
- **EVPN/L3VPN**: EVPN-MPLS 配置示例与排错, L3VPN Debug
- **VPLS/L2CKT/L2VPN**
- **HostPath**
- **PTP/GNSS**
- **Limitations**: 已知 Major Bugs/TSB
- **HW/Power**: 硬件/电源调试, Reboot 原因
- **BFD/PPM, CFM/LFM**
- **ACX7509 HW/HA**

---

## 2. Shell 登录方法汇总（EVO-AFT）

> 来源：EVO-AFT _ Shell Logins.txt

### Brackla PFE AFT 登录

```bash
# 方法1：直接进入 PFE CLI
start shell pfe network fpc0

# 方法2：从 shell 进入
start shell
cli-pfe

# 方法3：UKern Shell
start shell
vty fpc0
```

### Brackla PFE Platform 登录

```bash
start shell
vty fpc0.0
```

### Brackla CDA 登录（用于 JSIM/JSPEC 调试）

```bash
start shell user root
cd /usr/bin/
cda-jspec

# 进入后设置安全级别和 writable check
tty(aft)> set sec 20
tty(aft)> set jspec reg_writable_check disable
```

### Scapa FPC AFT 登录

```bash
start shell pfe network fpc0
```

### Scapa FPC Linux 登录

```bash
start shell user root
chvrf iri ssh fpc0
```

---

## 3. 数据收集流程

> 来源：Data collection.txt

### 基础数据收集 (request system debug-info)

- 类似 RSI 的增强版，收集 CLI 命令、RE Shell 命令、FPC Shell 命令、/var/log/ 和 /var/log/traces
- **耗时**: 约 45 分钟到 1 小时
- **存储位置**: `/var/tmp/debug_collector_<timestamp>/`

```bash
# 标准模式
request system debug-info

# Lite 模式（20.4R1 起），运行精选 debug 命令
request system debug-info mode lite

# 完整模式
request system debug-info mode normal
```

### Basic Health Check（ACX7100）

| # | 命令 | 用途 |
|---|------|------|
| 1 | `show system alarms` | 获取告警列表 |
| 2 | `show system errors active detail` | 当前活跃错误 |
| 3 | `show system errors inactive detail` | 历史已清除错误（检测 flapping） |
| 4 | `show chassis environment` | 机箱组件状态和温度 |
| 5 | `show chassis power` | 电源状态 |

### RSI

```bash
request support information | no-more | save /var/tmp/rsi-<router-name>.txt
```

### xmen-fru-get-state（ACX7100 硬件状态收集）

```bash
start shell
xmen-fru-get-state
# 日志文件: /var/log/xmen_debug_<timestamp>.log
```

### Application Traces（板上查看）

```bash
# Option 1: CLI
show trace application app <app_name>

# Option 2: Shell 中过滤
show_trace.py -a hwdre | grep 2020-07-01

# Option 3: 写入文件
show_trace.py -a hwdre -f /var/tmp/hwdre_traces.log

# Option 4: 过去 X 分钟
show_trace.py -a hwdre -t 200
```

### Application Traces（板外查看）

```bash
# 脚本位置（on baas）
/volume/evo/files/public/ui-tools/show_trace.py

# 语法
/volume/evo/files/public/ui-tools/show_trace.py [options] <Log location>
```

---

## 4. EVO Journalctl 收集指南

> 来源：EVO Journalctl Collection.txt

### 当前 Boot 日志

```bash
# RE 上收集
journalctl -b --output="short-precise" > /var/tmp/<file_name>

# FPC 上收集
start shell user root
chvrf iri ssh fpc0
journalctl -b --output="short-precise" > /var/tmp/<file_name>
```

### 所有 Boot 日志

```bash
journalctl -al --output="short-precise" > /var/tmp/<file_name>
```

### 按时间过滤

```bash
journalctl --since "2015-01-10 17:15:00"
journalctl --since yesterday
journalctl --since "2015-01-10" --until "2015-01-11 03:00"
journalctl --since 09:00 --until "1 hour ago"
journalctl --since "5 minutes ago"
journalctl --since "1 hour ago"
journalctl --since "1 day ago"
```

### 错误日志

```bash
journalctl -p 3 -xb
# -p 3 = priority err, -x = extra message, -b = since last boot
```

### 清理 Journalctl

```bash
journalctl --rotate ; journalctl --vacuum-time=1s
journalctl --vacuum-time=1years
```

---

## 5. ACX7100 EVO 排错指南

> 来源：ACX7100 EVO Troubleshooting.txt — 本文档最有价值，包含完整的 ACX7100 EVO 排错流程

### 5.1 Shell 登录层级

```
CLI (labroot@h09-46>)
  ├── start shell → Linux Shell
  │     ├── cli-pfe → PFE CLI (labroot@h09-46:pfe>)
  │     │     └── set evo-pfemand bcmshell cmd "..." → 无root执行BCM命令
  │     └── vty fpc0.0 → UKern Shell (jnx(/dev/pts/7)#)
  └── start shell user root
        └── jbcmsh → BCM Shell (BCM.0>)
```

### 5.2 Hostpath 架构 — 四个关键组件

```
BCM ASIC → BRCM-KNET → Packet-IO → JTD (RE)
```

#### (1) BCM ASIC — Jericho2 (BCM88690)

- 12个 Ethernet Port Macros，SerDes 最高 53.125G (PM50)
- 6个 PM50 连接到一个 device core
- 所有 WAN 方向的 Host-bound 包必须经过 BCM ASIC
- RE 发出的包也经过 BCM ASIC 到物理接口
- 发往 CPU 的帧在单个 PFE/BRCM-ASIC 中限速
- 流量根据协议通过不同队列 punting

**BCM 命令**:
```bash
# 进入 BCM Shell
jbcmsh
BCM.0> diag count g

# 查看 IPV4 主机路由表
BCM.0> DBaL TaBLe DuMP table=IPV4_UNICAST_PRIVATE_HOST

# 查看 LPM 转发表
BCM.0> DBaL TaBLe DuMP table=IPV4_UNICAST_PRIVATE_LPM_FORWARD

# 查看 LAG/Trunk
BCM.0> tm lag

# 查看 LIF (Logical Interface)
BCM.0> gpm lif id=<service-encap-id>
# service-encap-id 来自 show nh id <#> → encap_id (ukern PFE)

# 查看 GPORT
BCM.0> gpm hw gport=<gport-#>
# gport-# 来自 show pfe ifl <#> (ukern PFE)
```

#### (2) BRCM-KNET (Kernel Network Driver)

处理 BCM ASIC 和 Linux host 之间的 DMA。

**KNET 配置功能**:
- 创建 fp0（Guardian 上有 fp0/fp1）Forwarding Port
- fp0 配置为 RCPU 模式，保留 Broadcom 元数据
- 配置 KNET filters，将所有从 ASIC 收到的流量重定向到 fp0

**KNET 排错命令**:
```bash
# 检查控制包是否命中内置 PFE 过滤器
pfe> show evo-pfemand filter counters all

# 检查包是否在 ASIC 队列被限速
pfe> show evo-pfemand host asic-queues
pfe> show evo-pfemand host pkt-stats
pfe> show evo-pfemand host asic-queues sched-config
pfe> show evo-pfemand host protos
```

#### (3) Packet-IO

独立多线程 Linux 应用，通过 Shared DB 或 Socket 与其他 AFT 组件交互。

**数据流**:
- **Ingress**: KNET DMA → fp0 → PacketIO 解析 Brcm metadata → 设置 rx-context-data (ifl, ifd, queue) → 通过 cp0 发送 TTP 封装包到 RE
- **Egress**: RE 发送 TTP 封装包 → PacketIO 解析 TTP header → Brcm Transport 构造 RCPU header → fp0 → DMA 到 chip

**Packet-IO 排错命令**:
```bash
pfe> show host-path ports
pfe> show host-path ports fp0
pfe> show host-path ports punts
pfe> show host-path packet-type
pfe> show host-path packets
pfe> set trace-options host-path control state [enable/disable]
pfe> set trace-options host-path packet state all [enable/disable]
pfe> show trace-options host-path [control/packet]
pfe> show syslog all | grep packetio
```

**重要**: 如果 `packetio-brcm` 进程内存超过 **600-700M**，协议可能因内存不足失败，症状包括控制面不稳定、协议抖动、系统重启。

```bash
systemctl status packetio-brcm
```

#### (4) ukern PFE 命令

```bash
# 路由表
show route ip
show route inet6

# 接口
show pfe ifl <ifl-#>
show pfe vsi-mapping
show pfe gport-ifl-map

# 下一跳
show pfe nhdb mpls-tunnel all
show nhdb id <nh-#>
```

#### (5) EVO-PFEMAN 调试命令

```bash
# 路由查询 (proto: 2=ipv4, 5=mpls, 6=ipv6, 35=bridge)
show route proto 2 prefix x.x.x.x index table-index-#

# 下一跳
show evo-pfemand nh db index <nh-#>
show evo-pfemand nh detail index <nh-#>

# 接口
show evo-pfemand ifl
show evo-pfemand ifd index <ifd-#>

# LAG/Trunk 相关（重要）
show evo-pfemand trunk ae-ifd-index <ae-ifd-index-#>
show evo-pfemand ifl index <ifl-#>
```

### 5.3 节点和应用调试

```bash
# 检查所有节点状态
show system nodes

# 节点属性
show system node-attributes

# 应用状态
show system applications brief node re0
show system applications detail node re0
show system applications app <app-name> detail node re0
show system applications app sysman detail

# RE shell 查看应用列表
sysmanctl app list

# App-controller 调试
show platform app-controller incomplete
show platform app-controller summary
show platform app-controller complete

# Binding Queue 调试
show platform binding-queue summary
show platform binding-queue incomplete
show platform binding-queue pending

# DDS 调试
show platform dependency-state
show platform distributor clients all-clients
show platform distributor eou-status all-clients
```

### 5.4 端口速度配置注意事项

ACX7100-32C:
- 端口 0-31: QSFP28, 默认 100G (可用 QSFP+ 40G)
- 端口 32-35: QSFP56-DD, 默认 400GbE
- 相邻端口速度必须兼容：例如端口2配置为100G时，端口3必须为40G/100G或未使用

**工具**: https://apps.juniper.net/home/port-checker/index.html

---

## 6. EVO 路由/交换排错示例（目录级）

> 来源：Routing & Switching - EVO Trouble Shooting Examples.txt  
> 注意：实际文件内容仅包含目录列表（SharePoint 页面源码），具体排错步骤未捕获到

文档标题列表（含以下主题）：

| 主题 | 说明 |
|------|------|
| **Incomplete Object trace** | 不完整对象跟踪 |
| **Object Collision** | 对象冲突 |
| **Pending Nexthop Object** | 待处理下一跳对象 |
| **RPD fails to receive TTP packet from an Interface** | RPD 无法从接口接收 TTP 包 |
| **Interface stays down even if the PHY is up** | 接口 down 但 PHY up |
| **Traffic blackhole issue with ECMP** | ECMP 流量黑洞 |
| **How to use new trace tool in Evo** | EVO 新跟踪工具用法 |
| **Tracepoint examples (Arp/CoS/FW/IFL/Route/Nexthop)** | Tracepoint 示例 |
| **New Object Infra Debug Commands** | 新对象基础设施调试命令 |
| **Trace hostbound traffic on EVO** | 跟踪 EVO 上 Hostbound 流量 |
| **Trace route/nexthop updates on EVO** | 跟踪路由/下一跳更新 |
| **DDX communication trouble shooting script** | DDX 通信排错脚本 |
| **Evo Hostbound traffic drop trouble shooting** | EVO Hostbound 丢包排错 |

---

## 7. Hostpath 排错（ACX7100 架构级）

> 来源：Hostpath EVO.txt — 文件内容大部分丢失（SharePoint 页面渲染后保存，原始内容未捕获到）

**已提取到的关键词**: `lag`, `hostpath` — 说明该文档确实包含 LAG/ae 相关的 Hostpath 分析内容。

结合 ACX7100 EVO Troubleshooting 文档，Hostpath 整体架构总结如下：

```
物理端口 → BCM ASIC (Jericho2) → BRCM-KNET (DMA) → fp0 → PacketIO → cp0 → JTD (RE)
```

排错链路：
1. ASIC 层面：检查 BCM 表项 → `jbcmsh` → `DBaL TaBLe DuMP`
2. KNET/DMA：检查过滤器计数 → `show evo-pfemand filter counters all`
3. 队列限速：检查 ASIC 队列 → `show evo-pfemand host asic-queues`
4. PacketIO：跟踪 host-path → `show host-path ports`, `show trace-options host-path`

---

## 8. PFE 层面命令汇总

> 来源：ACX7100 EVO Troubleshooting.txt, EVO Jflow_Sflow.txt, Junos Fusion.txt, Quick_PFE_Reference_Sheet_-TRIO_Family.txt

### 8.1 通用 PFE 调试命令

| 命令 | 层级 | 用途 |
|------|------|------|
| `cli-pfe` | PFE CLI | 进入 PFE 命令行界面 |
| `vty fpc0.0` | UKern | 进入 UKern shell |
| `jbcmsh` | BCM | 进入 Broadcom ASIC shell |
| `chvrf iri vty fpc<slot>` | Scapa | Scapa 平台进入 FPC |
| `cda-jspec` | CDA | 进入 JSIM/JSPEC 调试 |

### 8.2 EVO-PFEMAN 命令

| 命令 | 用途 |
|------|------|
| `show evo-pfemand filter counters all` | 检查控制包是否命中 PFE 过滤器 |
| `show evo-pfemand host asic-queues` | 检查 ASIC 队列限速 |
| `show evo-pfemand host pkt-stats` | 查看 host 包统计 |
| `show evo-pfemand host asic-queues sched-config` | ASIC 队列调度配置 |
| `show evo-pfemand host protos` | 查看 host 协议 |
| `show evo-pfemand nh db index <nh-#>` | 查询下一跳数据库 |
| `show evo-pfemand nh detail index <nh-#>` | 下一跳详细信息 |
| `show evo-pfemand ifl` | 逻辑接口列表 |
| `show evo-pfemand ifd index <ifd-#>` | 物理接口详情 |
| `show evo-pfemand trunk ae-ifd-index <idx>` | **LAG/Trunk 接口详情** |
| `show evo-pfemand ifl index <ifl-#>` | **LAG 逻辑接口详情** |

### 8.3 Host-Path 命令

| 命令 | 用途 |
|------|------|
| `show host-path ports` | 查看 host-path 端口 |
| `show host-path ports fp0` | 查看 fp0 端口详情 |
| `show host-path ports punts` | 查看 punt 端口 |
| `show host-path packet-type` | 查看包类型 |
| `show host-path packets` | 查看包统计 |
| `set trace-options host-path control state enable` | 启用 host-path 控制面跟踪 |
| `set trace-options host-path packet state all enable` | 启用 host-path 数据包跟踪 |
| `show trace-options host-path [control/packet]` | 查看跟踪配置 |

### 8.4 UKern PFE 命令

| 命令 | 用途 |
|------|------|
| `show route ip` | 查看 IPv4 路由表 |
| `show route inet6` | 查看 IPv6 路由表 |
| `show pfe ifl <ifl-#>` | 查看逻辑接口信息 |
| `show pfe vsi-mapping` | 查看 VSI 映射 |
| `show pfe gport-ifl-map` | 查看 GPORT-IFL 映射 |
| `show pfe nhdb mpls-tunnel all` | 查看 MPLS Tunnel NH 数据库 |
| `show nhdb id <nh-#>` | 查看 NH 详情 |

### 8.5 BCM ASIC 命令

| 命令 | 用途 |
|------|------|
| `DBaL TaBLe DuMP table=IPV4_UNICAST_PRIVATE_HOST` | 查看 IPv4 主机路由表 |
| `DBaL TaBLe DuMP table=IPV4_UNICAST_PRIVATE_LPM_FORWARD` | 查看 LPM 转发表 |
| `tm lag` | 查看 LAG/Trunk 表 |
| `gpm lif id=<encap-id>` | 查看逻辑接口转发信息 |
| `gpm hw gport=<gport-#>` | 查看硬件 GPORT |
| `diag count g` | 通用诊断计数 |

### 8.6 Jflow/Sflow 命令

详见第11节。

### 8.7 Junos Fusion PFE 命令（卫星设备）

详见第9节。

### 8.8 路由协议查询

```bash
# proto: 2=ipv4, 5=mpls, 6=ipv6, 35=bridge
show route proto <2/5/6/35> prefix x.x.x.x index table-index-#
```

### 8.9 应用与平台调试

| 命令 | 用途 |
|------|------|
| `show system nodes` | 查看所有节点状态 |
| `show system node-attributes` | 节点属性 |
| `show system applications brief node re0` | 应用概要 |
| `show platform app-controller incomplete` | 不完整应用控制器 |
| `show platform binding-queue summary` | Binding Queue 概要 |
| `show platform dependency-state` | 依赖状态 |

---

## 9. Junos Fusion 排错

> 来源：Junos Fusion.txt

### 9.1 已知问题

**SD Fusion 升级到 SCBE3 后不启动**
- 原因：SCBE3 默认启用 hyper mode，但 Junos Fusion 不支持 hyper mode
- 解决：在配置中显式禁用 hyper-mode（全局级别，需要系统重启）
- 参考：`set forwarding-options hyper-mode disable`

### 9.2 卫星设备调试命令（AD 端）

#### 卫星状态查看

```bash
show chassis satellite brief
show chassis satellite terse
show chassis satellite detail
show chassis satellite extensive
show chassis satellite fpc-slot 103
show chassis satellite fpc-slot 103 extensive
show chassis satellite software
show chassis satellite neighbor
show chassis satellite neighbor extensive
show chassis satellite statistics
show chassis satellite upgrade-group extensive
show chassis satellite interface
show chassis satellite interface extensive
show chassis satellite upgrade-group
```

#### 硬件和环境

```bash
show chassis hardware satellite
show chassis routing-engine satellite
show chassis environment satellite
show chassis environment fpc satellite
show chassis environment pem satellite
show chassis environment routing-engine satellite
show chassis temperature-thresholds satellite slot-id 103
show chassis fan satellite slot-id 103
show chassis routing-engine bios satellite slot-id 103
show chassis firmware satellite slot-id 103
show chassis led satellite slot-id 103
```

#### 告警和 Core Dump

```bash
show chassis alarms satellite
show system core-dumps satellite
show system core-dumps satellite 103
```

### 9.3 卫星设备操作

#### 远程 Shell 执行

```bash
request chassis satellite shell-command fpc-slot 104 "cmd"
```

#### 登录卫星设备

```bash
request chassis satellite login fpc-slot 103
```

#### 卫星 Linux 命令示例（登录后）

```bash
ip addr
ifconfig ge-0-0-47c
netstat -nr
tcpdump -i ge-0-0-47c
```

#### 卫星 PFE 调试（通过 AD 跳转）

```bash
request chassis satellite login fpc-slot 103 ; vty
# 进入 vty 后:
show interfaces
show interfaces upstream
show interfaces statistics
show interfaces statistics rate
show ukern_trace handles
show ukern_trace 0
show chassis
show pic
show ifd
show ifl
show sfp list
show interfaces queue-statistics ge-0/0/46
```

#### Anchor 下一跳

```bash
show chassis satellite krt next-hop
show chassis satellite krt anchor-next-hop
show chassis satellite krt route
```

#### 文件操作

```bash
# AD → SD 传文件
request chassis satellite file-copy sd103:/var/tmp/test /var/tmp
# SD → AD 传文件
request chassis satellite file-copy /var/tmp/test sd104:/var/tmp
```

#### 管理操作

```bash
# 重启 SD 守护进程
request chassis satellite restart chassis-management-daemon fpc-slot 103

# 重启 SD
request chassis satellite reboot fpc-slot 104

# 禁用/启用 SD
request chassis satellite disable fpc-slot 103
request chassis satellite enable fpc-slot 103

# 从 SNOS 转换回 Junos
request chassis satellite install fpc-slot 103 "pkg-name"
```

### 9.4 卫星设备日志收集

```bash
# 1. 登录卫星
request chassis satellite login fpc-slot 101

# 2. 打包日志
cd /var/log
su
tar -cvzf /var/tmp/sd101-logs.tgz *

# 3. 复制到 AD
request chassis satellite file-copy sd101:/var/tmp/sd101-logs.tgz /var/tmp
```

---

## 10. CMError 知识库与 TRAPSTATS

> 来源：CMError KBs..txt, CMERROR and TRAPSTATS.txt

### 10.1 Master 索引

| KB# | 标题 |
|-----|------|
| **KB31893** | Master Index of Articles for Troubleshooting PFE ASIC Syslog Events |
| **KB31922** | Shell script collecting data if packet forwarding at PFE is compromised |
| **KB32007** | [Junos] Wedge definition |
| **KB32086** | What is a transient Hardware Error? |
| **KB31867** | Generic pfe-disable event script |

### 10.2 LUCHIP 错误

| KB# | Syslog 匹配模式 | 说明 |
|-----|----------------|------|
| KB31706 | `LUCHIP.* PPE_.* Errors KMB.* parity error` | KMB 奇偶校验错误 |
| KB31716 | `PPE.*Errors lmem data error` | lmem 数据错误 |
| KB31728 | `LUCHIP.*HASH INT Status FPM Error` | Hash 中断 FPM 错误 |
| KB31726 | `LUCHIP.*PPE.*CBO.*mismatch.*rd.*exp` | CBO 不匹配 |
| KB31740 | `toe_interrupt_errors.*LU TOE chip.*Memory Error Thread.*INSTR Addr` | TOE 内存错误 |
| — | `LUCHIP.* IDMEM.*read error` | IDMEM 读错误 |
| KB31732 | `RamBIST:LU-CHIP .* BIST: Memory Error` | BIST 内存错误 |
| KB31743 | `LUCHIP.* DDR.*VERIFY_RETRY_LIMIT of.*exceeded` | DDR 验证重试超限 |
| KB31729 | `PPE HW Fault Trap: Count .*PC .*init_xtxn_fields` | PPE 硬件故障陷阱 |
| KB31727 | `LUCHIP.*pio_handle.*pio_read_u64.*failed` | PIO 读取失败 |
| KB31713 | `Secondary PPE.*zone.*timeout` | 次级 PPE 区域超时 |
| KB31714 | `LUCHIP.*RD_NACK.*TOE Read` | TOE 读 NACK |
| KB31710 | `PPE.*Errors sync xtxn error` | 同步 xtxn 错误 |
| KB31711 | `RMC.*Uninitialized EDMEM.*Read` | EDMEM 未初始化读 |
| KB31731 | `LUCHIP.*RMC.*Correctable ECC .* cnt .* syn .* EDMEM` | RMC 可纠正 ECC |
| KB30724 | `LUCHIP(.) RMC . Uncorrectable ECC 0x6db6db6d6db6db6d @ 0x.* EDMEM` | RMC 不可纠正 ECC |
| KB31712 | `LUCHIP.*Uncorrectable ECC.*EDMEM` | 不可纠正 ECC |
| KB31901 | `LUCHIP(.) .*RMC .* Uncorrectable ECC .* EDMEM` | RMC 不可纠正 ECC |
| KB31709 | `LUCHIP.*Display trap-info logic not initialized` | trap-info 逻辑未初始化 |

### 10.3 MQCHIP 错误

| KB# | Syslog 匹配模式 | 说明 |
|-----|----------------|------|
| KB31599 | `MQCHIP.*CPQ RLDRAM double bit ECC error.*bank.*addr` | RLDRAM 双 bit ECC |
| KB31583 | `MQCHIP.*FI Enqueuing error.*type.*seq.*stream` | FI 入队错误 |
| KB31591 | `MQCHIP.*FI Error-cell sent to reorder engine` | FI 错误单元 |
| KB31593 | `MQCHIP.*MALLOC Pre-Q Reference Count .*decrement below zero` | MALLOC 参考计数 |
| KB31592 | `MQCHIP.*OCM Fo.*Ddrif Parity Error` | DDRIF 奇偶校验错误 |
| KB31739 | `MQCHIP.*PT CPT parity error detected` | CPT 奇偶校验错误 |
| KB31582 | `MQCHIP.*DDRIF WO Checksum Error` | WO 校验和错误 |
| KB31569 | `MQCHIP.*DDRIF FO.*Checksum Error` | FO 校验和错误 |
| KB31568 | `MQCHIP.*FI Cell underflow at the state stage` | FI 单元 underflow |
| KB31581 | `MQCHIP.*FO Request time-out error` | FO 请求超时 |
| KB31688 | `MQCHIP.*CPQ RLDRAM single bit ECC error.*bank.*addr` | RLDRAM 单 bit ECC |

### 10.4 XMCHIP 错误

| KB# | 说明 |
|-----|------|
| KB31702 | `XMCHIP.*FI.*Packet CRC error` |
| KB31696 | `XMCHIP.*MALLOC.*DREF memory parity error` |
| KB31607 | `XMCHIP.*MALLOC: SChunk allocation memory parity error` |
| KB31608 | `XMCHIP.*WI CPQ Free Pointer SRAM Protect: Parity error` |
| KB31619 | `XMCHIP.*DRD.*Protect.*Parity error for DRD memory` |
| KB31698 | `XMCHIP.*PT.*Protect.*Parity error for CPFIFO data memory` |
| KB31701 | `XMCHIP.*DRD.*Wan parcel timout error` |
| KB31617 | `XMCHIP.*DRD.*Fabric parcel timeout error` |
| KB31687 | `XMCHIP.*DDRIF.*Checksum error for FO/WO` |
| KB31684 | `XMCHIP.*MALLOC.*DMEM allocation memory parity error` |
| KB31679 | `XMCHIP.*LI.*Received cookie size different from expected` |
| KB31602 | `XMCHIP.*DRD.*Command sequence error` |
| KB31703 | `XMCHIP.*PT.*Missing SOP.*EOP errors from input blocks` |
| KB31609 | `XMCHIP.*Scheduler: Protect: Parity error for tick table single port SRAM` |
| KB31601 | `XMCHIP.*Scheduler.*Protect.*Parity error for TDM table single port SRAM` |
| KB31610 | `XMCHIP.*FI.*Protect.*Parity error for .* SRAM` |
| KB31600 | `XMCHIP.*DRD0.*Reference count memory decrement error.*PCT` |
| KB31733 | `XMCHIP.*LI.*Received a parcel from the HSL2 interface with EOPE` |
| KB31735 | `XMCHIP.*LI.*Received a parcel with more than 512B accompanying data` |
| KB31737 | `XMCHIP.*WO.*Packet error - Error Packets` |
| KB31736 | `XMCHIP.*PT.*Protect.*Log Error.*Log Address.*Multiple Errors` |
| KB31611 | `XMCHIP.*FI.*Cell underflow at the state stage` |
| KB31734 | `XMCHIP.*FI.*Link sanity checks.*Type` |
| KB31686 | `XMCHIP.*FI.*Aliasing on allocates error.*Pipe count` |
| KB31685 | `XMCHIP.*EPM.*upon free pool` |
| KB31682 | `XMCHIP.*FO.*Request timeout error.*Number of timeouts` |
| KB31680 | `XMCHIP.*WI.*Input pause buffer exceeded.*Check if the transmitter respects pause frames` |
| KB31681 | `XMCHIP.*XXLCE.*Port Interrupts.*Ethernet Rx Stats Parity Error` |
| KB31697 | `XMCHIP.*OCM: .*parity error - Parity Error Address` |
| KB32968 | `XMCHIP.*CPQ*: HCPQ underrun indication` |
| KB32171 | `XMCHIP.*Cell packing interface error` |

### 10.5 EACHIP 错误

| KB# | 说明 |
|-----|------|
| KB31721 | `MQSS.*BCMF CBUF.*SRAM Protect.*Parity error detected for Bank.*Sub-Bank.*memory` |
| KB31719 | `MQSS.*DRD.*Protect.*Parity error corrected for alloc state memory` |
| KB31718 | `MQSS.*LI.*Unroll TAIL length overflow` |
| KB31723 | `EA.*HMCIF.*HMCIF has no chunk index available for incoming WO read` |
| KB31722 | `EA.*HMCIF Rx.*Link.*Response FIFO . Overflow` |
| KB31694 | `EA.*HMCIF Rx.*Link.*HMCIF Rx retry attempts failed` |
| KB31693 | `EA.*HMCIF Rx.*Link.*HMC token overflow` |
| KB31695 | `EA.*HMCIF Rx: Link.: total number of corrected single-bit errors from HMC . exceeded threshold` |
| KB31717 | `MQSS.*FO: Request timeout error - Number of timeouts .*, RC select .*, Stream` |
| KB32091 | `EA.*HMCIF Rx: Link.: A response packet with a FATAL state is received from HMC -State 0x7F` |
| KB32087 | `EA.*Bist XRIF.*failed` |

### 10.6 通用 PFE CMError

| KB# | 说明 |
|-----|------|
| KB32144 | `SECONDARY_TIMEOUT or PRIMARY_TIMEOUT` |
| KB32152 | `PRB_EVENERR or PRB_ODDERR` |
| KB32153 | `idmem_slice.*Corrected single bit ECC error` |
| KB32154 | `Double-bit ECC error` |
| KB32155 | `Uninitialized Read Error` |
| KB32158 | `ucode sb data error` |
| KB32161 | `CBO[.] parity error` |
| KB32162 | `KMB[.] parity error or KMA[.] parity error` |
| KB32163 | `lmem data error` |
| KB32168 | `ucode data error` |
| KB32168 | `HOST LOOPBACK WEDGE DETECTED` |
| KB32163 | `lmem addr error` |

### 10.7 XQSS/MQSS 其他错误

| KB# | 说明 |
|-----|------|
| KB31690 | `XQSS.*Qdepth underrun error in Drop engine 0` |
| KB31691 | `XQSS.*CPQW Freelist Manager run out of available fl pointers` |
| KB31692 | `XQSS.*CPQW Fast request is asserted for empty Queue` |
| KB31720 | `MQSS.* FI: Cell underflow at the state stage` |
| KB32119 | `HMM.*Lane.*TX RLL event` |
| KB32005 | `XMCHIP.*CPQ1.*Queue underrun indication` |
| KB32106 | `PRECL.*XM_engine.*instmem parity error detected` |
| KB32105 | `XMCHIP.*DDRIF: LLISTQ.*Parity error for free pointer SRAM` |
| KB32084 | `MQSS.*BCMW ICM.*Invalid cell sequence.*Packet start without SOP or 16K packet bytes without SOP` |
| KB32085 | `MQSS.*FO.*Parity error detected for output buffer control` |
| KB32090 | `MQSS.*BCMF CBUF.*Parity error corrected for buffer free list memory for bank` |
| KB32088 | `MQSS.*FI.*Parity error detected for bank.*of CP table` |
| KB32089 | `EA.*reports CM err HMC BIST has detected error` |
| KB32137 | `filter.*errors async xtxn error` |
| KB32291 | `EA.*HMCIO TX: AFIFO overflow event detected in Channel` |
| KB32332 | `EA.*HMCIO RX: SFIFO overflow event detected in Channel` |
| KB32333 | `MQSS.*LI.*Received a parcel with more than 512B accompanying data` |
| KB32334 | `MQSS.*Cell packing interface error` |
| KB32335 | `MQSS.*Checksum error detected on` |
| KB32342 | `MQSS.*FI.*Child drop error` |
| KB32343 | `MQSS.*FI.*Cell jump drop error` |
| KB32344 | `EA.*HMCIF Rx: Link.: A response packet with a FATAL state is received from HMC - State: 0x1f` |
| KB32352 | `MQSS.*DRD.*CMD FSM state error` |
| KB32353 | `XL.*cass_xr.*dbuf_protect Corrected XR DBUF` |
| KB33994 | `MQSS.*WANIO_CR.*Parity error detected` |

---

## 11. EVO Jflow/Sflow 排错

> 来源：EVO Jflow_Sflow.txt

### 11.1 Jflow 架构 — 三个模块

```
1. msvcsd App (FPC上)
   功能: 接收和处理采样包、创建流、监听路由对象(NH/AS/IFL)、
         超时处理活跃/非活跃流、导出记录到 Collector

2. msvcs-db App (RE上, 20.4起)
   功能: 学习路由记录的AS信息、与msvcsd建立IPC连接、
         发送AS Path信息到msvcsd

3. svcsd App (RE上)
   功能: 监听Jflow配置对象、下发Jflow配置到msvcsd
```

### 11.2 连接到 AFT-CLI

```bash
# Brackla 平台
cli-pfe

# Scapa 平台
chvrf iri vty fpc<slot-number>
```

所有 AFT-CLI 命令支持 XML 格式输出，添加 `display xml`。

### 11.3 连接到 svcsd LcDD

```bash
chvrf iri telnet localhost `cat /var/run/svcsd.lcdd.port | cut -f 2 -d ' '`
```

### 11.4 连接到 msvcs-db LcDD (20.4+)

```bash
chvrf iri telnet localhost `cat /var/run/MsvcsDb.lcdd.port | cut -f 2 -d ' '`
```

### 11.5 svcsd LcDD 命令（Jflow）

```bash
show node info
show platform info
```

### 11.6 msvcs-db LcDD 命令（Jflow, 20.4+）

```bash
show routes
show as-path summary
show as-path vrf-list family
show as-path routes
show as-path route details
show msvcs-db connection summary
show msvcs-db client
show msvcs-db server disconnected-client summary
```

### 11.7 msvcsd AFT-CLI 命令（Jflow）

| 命令 | 用途 |
|------|------|
| `show msvcsd config` | Jflow 配置 |
| `show msvcsd config collectors` | Collector 配置 |
| `show msvcsd config summary` | 配置概要 |
| `show msvcsd connection summary` (20.4+) | 连接概要 |
| `show msvcsd errors` | 错误信息 |
| `show msvcsd exporter-interface stats` | 导出接口统计 |
| `show msvcsd flow-asic-intf global stats` | ASIC 接口全局统计 |
| `show msvcsd flow-table summary` | 流表概要 |
| `show msvcsd packet processor summary` | 包处理器概要 |
| `show msvcsd stats-fpc` | FPC 统计 |
| `show msvcsd stats-svc-set` | 服务集统计 |
| `show msvcsd timer wheel summary` | 定时器轮概要 |
| `show rtdb summary` | RTDB 概要 |
| `show rtdb ifl-vrf map` | IFL-VRF 映射 |
| `show rtdb nh info` | 下一跳信息 |
| `show rtdb route record family <0/1/2> vrf <idx> ip <ip>` | 路由记录 (0=inet,1=inet6,2=mpls) |
| `show rtdb route-entry vrf-family info family <0/1/2> vrf <idx>` | 路由项信息 |
| `show rtdb snmp-index iflIndex <idx>` | SNMP 索引 |
| `show rtdb stats` | RTDB 统计 |
| `show rtdb target nh-list nhIndex <idx>` | 目标 NH 列表 |
| `show rtdb token-detail` | Token 详情 |
| `show rtdb vrf-list family <0/1/2>` | VRF 列表 |
| `show sample instance summary` | 采样实例概要 |
| `show sample association summary` | 采样关联概要 |

### 11.8 sflow AFT-CLI 命令（19.4+）

| 命令 | 用途 |
|------|------|
| `show sflowd global statistics` | 全局统计 |
| `show sflowd global configuration` | 全局配置 |
| `show sflowd interface statistics [iflName <name>]` | 接口统计 |
| `show sflowd interface configuration [iflName <name>]` | 接口配置 |
| `show sflowd collector statistics [collAddress <addr>]` | Collector 统计 |
| `show sflowd collector configuration [collAddress <addr>]` | Collector 配置 |
| `show sflowd flow-asic-intf global stats` | ASIC 接口统计 |
| `show sflowd ifd [ifd-index <idx>]` | 物理接口 |
| `show sflowd nh-tokens [ifd-index <idx>] [nh-token <tok>]` | NH Token |
| `show sflowd packet-queue stats` | 包队列统计 |
| `show sflowd packet-queue state stats` | 包队列状态 |
| `show sflowd route tree entries proto <p> vrf-index <i> [rt-prefix <p>]` | 路由树 |
| `show sflowd route table vrf entries proto <p> [vrf-index <i>]` | VRF 路由表 |
| `show sflowd route ifls [ifl-index <i>]` | 路由 IFL |
| `show sflowd rpc statistics` | RPC 统计 |
| `show sflowd voq [voq-id <id>]` | VOQ |
| `show sflowd firewall` | 防火墙 |
| `show sflowd firewall fw-index <idx>` | 防火墙索引 |
| `show sflowd tep` | TEP |
| `show sflowd tep tep-name <name>` | TEP 名称 |
| `show sflow am sampler stats` | AM 采样器统计 |
| `show sflow am sampler summary` | AM 采样器概要 |
| `show sflow am lookup stats` | AM 查找统计 |
| `show sflow am collector configuration` | AM Collector 配置 |
| `show sflow am global configuration` | AM 全局配置 |
| `show sflow am global stats` | AM 全局统计 |
| `show sflow am ifd` | AM 物理接口 |
| `show sflow am interface configuration` | AM 接口配置 |
| `show sample instance summary` | 采样实例概要 |
| `show sample association summary` | 采样关联概要 |

### 11.9 svcsd LcDD 命令（Sflow）

```bash
show sflow interfaces [<intf-name>]
show ifl list [<ifl-name>]
show ifl stats
show node info
show platform info
```

---

## 12. ACX7000 JTAC 跳转站

> 来源：ACX7000 - JTAC Jump Station - Home.txt

### 产品与工程名对照

| 产品名 | 工程名 |
|--------|--------|
| ACX7100-32C | X-Men [Storm] |
| ACX7100-48L | X-Men [Wolverine] |
| ACX509 | Guardian |
| ACX7024 | Ultron |
| ACX7024X | Ultron-XL |
| ACX7332 | Gamora-L |
| ACX7348 | Gamora-M |
| ACX7020 | Antman Lite |

### 排错资源索引

- **Scaling**: SNP
- **Features/RLI**: cerebro-master-tracker
- **Debug/Logs**: RSI, BCM Debug, Port-Mirror, MEM/CPU
- **Interface**: SFP Troubleshooting
- **EVPN/L3VPN**: EVPN-MPLS, L3VPN Debug
- **VPLS/L2CKT/L2VPN**
- **HostPath**
- **PTP/GNSS**
- **Limitations**: Known Major Bugs/TSB
- **ACX7000 FIREWALL**
- **HW/Power Debugging**
- **ACX7000 - Reboot Reasons**
- **ACX7509 HW/HA**
- **ACX7K KBs**
- **BFD/PPM**
- **CFM/LFM**

---

## 13. LACP/ae 相关排错说明

### 13.1 可用命令总结

以下是在 ACX7100 EVO 平台上与 LACP/ae/LAG 直接相关的命令：

**PFE CLI 层面**:
```bash
# LAG/Trunk 接口详情（EVO-PFEMAN）
pfe> show evo-pfemand trunk ae-ifd-index <ae-ifd-index-#>
pfe> show evo-pfemand ifl index <ifl-#>     # LAG IFL

# 物理接口
pfe> show evo-pfemand ifd index <ifd-#>      # Child IFD
```

**BCM ASIC 层面**:
```bash
BCM.0> tm lag    # 查看 LAG/Trunk 表
```

**UKern PFE 层面**:
```bash
show pfe ifl <ifl-#>
```

### 13.2 参考文档说明

- **Routing & Switching - EVO Trouble Shooting Examples.txt**: 文件仅捕获到目录列表，包含以下与 LACP/ae 相关的标题：
  - `Interface stays down even if the PHY is up` — 接口 down 但 PHY up，可能与 ae 成员链路相关
  - `Traffic blackhole issue with ECMP` — ECMP 黑洞，可能与 ae 负载均衡相关
  - `RPD fails to receive TTP packet from an Interface` — RPD 无法接收 TTP 包
  - `Trace hostbound traffic on EVO` — 跟踪 Hostbound 流量
  - `Trace route/nexthop updates on EVO` — 跟踪路由/下一跳更新

- **Hostpath EVO.txt**: 页面包含 `lag` 关键词，但具体内容因 SharePoint 渲染问题未被捕获。结合 ACX7100 EVO Troubleshooting 文档，ae 接口的 Hostpath 流程为：
  ```
  物理端口 → BCM ASIC LAG Hash → ae 聚合 → KNET DMA → fp0 → PacketIO → RE
  ```

### 13.3 LACP/ae 排错建议路径

由于缺乏具体的 LACP/ae 排错案例原文，基于上述架构文档，推荐排错路径：

1. **检查 ae 接口状态**:
   ```bash
   show interfaces ae<#>
   show lacp interfaces ae<#>
   ```

2. **检查 PFE 层面 ae 数据库**:
   ```bash
   pfe> show evo-pfemand trunk ae-ifd-index <idx>
   pfe> show evo-pfemand ifl index <ifl-#>
   ```

3. **BCM ASIC 层面检查 LAG 表**:
   ```bash
   BCM.0> tm lag
   ```

4. **检查成员端口状态**:
   ```bash
   pfe> show evo-pfemand ifd index <child-ifd-#>
   ```

5. **检查 Hostpath 是否存在丢包**:
   ```bash
   pfe> show evo-pfemand filter counters all
   pfe> show evo-pfemand host pkt-stats
   pfe> show host-path ports
   ```

---

## 14. 通用排错流程总结

### 14.1 基础诊断流程

```
Step 1: 系统健康检查
  show system alarms
  show system errors active detail
  show chassis environment
  show chassis power
  show system nodes
  show system applications brief

Step 2: 数据收集
  request support information | save
  request system debug-info (45min+)
  journalctl -b (当前boot)
  journalctl -b -1 (前一个boot)

Step 3: 应用层面诊断
  show system applications app <app> detail
  show platform app-controller incomplete
  show platform binding-queue summary
  show platform dependency-state

Step 4: PFE 层面诊断
  cli-pfe → 进入 PFE CLI
  show evo-pfemand filter counters all
  show evo-pfemand host asic-queues
  show evo-pfemand nh db
  show host-path ports

Step 5: ASIC 层面诊断
  jbcmsh → 进入 BCM Shell
  diag count g
  DBaL TaBLe DuMP 相关表

Step 6: 跟踪
  show trace application app <app>
  show_trace.py -a <app>
  set trace-options host-path ...
```

### 14.2 内存问题诊断

```bash
# 检查 packetio-brcm 内存使用
systemctl status packetio-brcm
# 如果超过 600-700M，可能导致:
# - 控制面不稳定
# - 协议抖动
# - 系统重启
```

### 14.3 journalctl 诊断流程

```bash
# 当前 boot (快速)
journalctl -b --output="short-precise" > /var/tmp/current.log

# 错误级别过滤
journalctl -p 3 -xb

# 按时间范围过滤
journalctl --since "1 hour ago"

# 前一个 boot
journalctl -b 1 > /var/tmp/prev1.log
```

### 14.4 CMError 诊断流程

当看到 PFE syslog 中的 CMError 时：
1. 查找对应的 KB 编号（参考第10节）
2. 区分：
   - **可纠正 (Correctable) ECC** — 通常为瞬态错误，参考 KB32086
   - **不可纠正 (Uncorrectable) ECC** — 需要进一步分析
   - **Wedge** — PFE 挂起，参考 KB32007
3. 运行 `show system errors active detail` 查看当前活跃错误
4. 运行 `show system errors inactive detail` 查看历史错误（检测 flapping）
5. 考虑运行 pfe-disable 事件脚本（KB31867）

### 14.5 关键注意事项

| 项目 | 说明 |
|------|------|
| `packetio-brcm` > 600-700M | 控制面不稳定，需关注 |
| **hyper-mode** 与 Fusion | SCBE3 默认启用，Fusion 需要关闭 |
| **ACX7100 端口速度** | 相邻端口速度需兼容 |
| **journalctl 收集** | FPC 上 journalctl 需通过 `chvrf iri ssh fpc0` 进入 |
| **root 权限** | bcmshell 需要 root 登录；无 root 可用 `set evo-pfemand bcmshell cmd` |
| **AFT-CLI 输出格式** | 所有 AFT-CLI 命令支持 XML 格式 |

---

*笔记完*
