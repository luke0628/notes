# JunOS EVO (ACX7024X/ACX7100) — LACP排错 / ae接口调试 / TTrace笔记

> 来源：从 `/home/Lu/` 下约50份HTML文档中提取，经去标签纯文本化后整理。
> 目标设备：ACX7024X (EVO架构, Broadcom Jericho2 ASIC)
> 问题场景：ae2下配置了接口，但 `show lacp interface ae2` 只显示部分成员。

---

## 一、LACP traceoptions 能否配置？

### 1.1 JunOS EVO中**没有**传统的 `traceoptions { file; flag; }` 用于LACP

在EVO架构下，**`traceoptions` 对LACP协议不适用**。EVO使用 **Application Traces（应用层追踪）** 机制替代传统的trace-options。

来源文件：`TRACES [Not trace-options].html` / `Traces [Application traces].html`

> 文档原文标题就是"TRACES [Not trace-options]"，明确指出EVO使用的是应用层trace，不是传统的trace-options。

### 1.2 EVO中的应用层trace机制

#### 查看LACP相关应用trace

LACP协议在EVO中由 `ppm` 或 `lacp` 相关应用处理。可以通过以下方式查看应用trace：

```bash
# CLI方式查看应用trace（有大小限制，约100MB）
labroot@router> show trace application ppm node re0
labroot@router> show trace application lacp node re0

# 实时查看trace（配合复现问题）
labroot@router> show trace application ppm node re0 live

# Shell方式使用 show_trace.py
[vrf:none] root@router:~# show_trace.py -a ppm
[vrf:none] root@router:~# show_trace.py -a lacp

# 指定时间范围（过去X分钟）
[vrf:none] root@router:~# show_trace.py -a ppm -t 200

# 输出到文件
[vrf:none] root@router:~# show_trace.py -a ppm -f /var/tmp/ppm_traces.log
```

相关参数：
```
show_trace.py [-h] [-a APPLICATION] [-n NODE] [-p PID] [-t TIME_CHANGED] [-f OUTPUT_FILE] [-v]
```

来源：`Traces [Application traces].html` (ACX-EVO-PAGE)

### 1.3 开启evo-pfemand debug级别的trace（PFE层面的debug）

可以在CLI配置中设置system trace application（这是EVO配置trace的正式方式）：

```bash
# 配置级：启用evo-pfemand的debug trace
set system trace application evo-pfemand node re0 level debug
set system trace application evo-pfemand node re0 group L2 enabled
set system trace application evo-pfemand node re0 group IF enabled
set system trace application evo-pfemand node re0 group NH enabled

# 也可以指定具体tracepoint
set system trace application evo-pfemand node re0 group L2 tracepoint BrcmPlusL2BD enabled
set system trace application evo-pfemand node re0 group IF tracepoint BrcmIff enabled
set system trace application evo-pfemand node re0 group IF tracepoint BrcmPlusIfl enabled
```

来源：`ACX VXLAN Debug Guide.html`（示例配置）

### 1.4 PFE Shell中启用trace-options

在 `cli-pfe` shell中可以这样操作：

```bash
# 进入PFE CLI
labroot@router> start shell pfe network fpc0
# 或
labroot@router> start shell
[vrf:none] labroot@router:~$ cli-pfe
labroot@router:pfe>

# 启用PFE通用trace-options
pfe> set trace-options pfe flags all enable

# 启用Host Path的trace-options（用于抓取host-bound包）
pfe> set trace-options host-path control state enable
pfe> set trace-options host-path packet state all enable
pfe> set trace-options host-path packet state extensive all enable
pfe> set trace-options host-path packet port transport
pfe> set trace-options host-path packet port io

# 查看trace-options状态
pfe> show trace-options host-path control
pfe> show trace-options host-path packet

# 查看syslog中的packetio日志
pfe> show syslog all | grep packetio

# RE Shell中查看packetio-brcm日志
[vrf:none] root@router:~# journalctl -u packetio-brcm
```

来源：`ACX7100 EVO Troubleshooting.html`, `Hostpath Commands list.txt`, `Troubleshooting FPC.html`

---

## 二、PFE层面查看LACP成员口 — 关键命令

### 2.1 查看ae trunk（聚合组）信息

这是最核心的命令：

```bash
# 进入PFE CLI
labroot@router> start shell pfe network fpc0
labroot@router:pfe>

# 查看ae接口的trunk信息（成员口列表）
pfe> show evo-pfemand trunk ae-ifd-index <ae-ifd-index>

# 示例：查看ae2（假设ae2的IFD index = 1004）
pfe> show evo-pfemand trunk ae-ifd-index 1004
```
输出示例：
```
TrunkId:1 BrcmTid:0x2000001
Ae-Ifd_idx:1004 trunkGport:0xe000001
Ae-Anchor-PpPort:85 Anchor_Unit:Core 0:0
AE-SHM-Encoded-Val:0xbf01

MemCnt ActMemCnt FirstActiveMem Core
------------------------------------
2        2         0x6c000003     0     ← 成员口总数 / 活跃成员口数

SW Info:
bcm-port    status     ShMemEncoding
------------------------------------
0x6c000003  Enabled    0x8001        ← 子成员口的Brcm System Port号
0x6c000005  Enabled    0x8101

HWUnit:0 info:
bcm-port    class_id   flags
----------------------------
3           254        0
```

**关键字段说明：**
- `MemCnt` = 配置的成员口总数
- `ActMemCnt` = 当前活跃的成员口数
- `bcm-port` = Broadcom芯片内部System Port号
- `status` = Enabled/Disabled（成员口在PFE硬件层面是否启用）

来源：`L3 Troubleshooting.txt`, `ACX7100 EVO Troubleshooting.txt`

### 2.2 查看ae成员口（子IFD）的详细信息

```bash
# 查看子接口IFD信息（成员口）
pfe> show evo-pfemand ifd index <child-ifd-index>

# 示例：查看ae2的三个子成员口
pfe> show evo-pfemand ifd index 1008     # → et-0/0/1 (成员口)
pfe> show evo-pfemand ifd index 1009     # → et-0/0/2 (成员口)
pfe> show evo-pfemand ifd index 1010     # → et-0/0/3 (成员口)

# 查看ae接口自身的IFD
pfe> show evo-pfemand ifd index 1004     # → ae2
```

输出关键字段：
```
IfdIdx:1008 IfdName:et-0/0/1 isLocal:true
PortNum:3 IfdPpPort(Local/Anchor):87
brcmGport:0x8000003 brcmSystemPort:0x6c000003
Aggregate:0 AggregateMember:1 AeIfdIdx:1004    ← 确认此IFD是ae成员，属于ae2
lacpTrapInstalled:1 lldpTrapInstalled:1 lldpTrapRefCnt:1  ← LACP trap是否安装到硬件
```

**`lacpTrapInstalled:1` 表示该接口的LACP trap已成功编程到硬件**。如果某个成员口显示为 `lacpTrapInstalled:0`，说明PFE层面没有安装LACP trap，可能导致该成员口不参与LACP协商。

来源：`L3 Troubleshooting.txt` (ACX-EVO-PAGE)

### 2.3 查看IFL（逻辑接口）信息

```bash
pfe> show evo-pfemand ifl
pfe> show evo-pfemand ifl index <ifl-idx>   # LAG IFL
```

来源：`ACX7100 EVO Troubleshooting.txt`

### 2.4 查看Broadcom芯片层LAG信息

```bash
# 进入BCM shell（需要root）
labroot@router> start shell user root
[vrf:none] root@router:~# jbcmsh
BCM.0> tm lag

# 或者通过PFE CLI执行BCM命令
pfe> set evo-pfemand bcmshell cmd "tm lag"
```

来源：`ACX7100 EVO Troubleshooting.txt`

### 2.5 AFT平台专用：PPM层面查看LACP信息

在AFT（Advanced Forwarding and Telemetry）架构下：

```bash
# 进入PFE shell
pfe> show ppm control protocols
pfe> show ppm control protocol lacp session      ← 查看LACP会话信息
pfe> show ppm ports
pfe> show ppm processor packet statistics
pfe> show ppm processor protocol lacp packet statistics  ← LACP包统计
```

来源：`AFT Hostpath.html`

---

## 三、ae接口成员口不完整的排查步骤

场景：ae2配置了N个成员口，但 `show lacp interface ae2` 只显示M个（M < N）。

### Step 1: 确认JunOS CLI层面的ae配置

```bash
# 查看ae接口配置
show configuration interfaces ae2

# 查看ae接口状态（确认配置的成员口数）
show interfaces ae2 extensive | find "Member"

# 确认LACP在ae接口上启用
show lacp interfaces ae2
```

### Step 2: 进入PFE CLI，查看硬件层面的成员口情况

```bash
start shell pfe network fpc0
```

### Step 3: 获取ae2的IFD index

```bash
pfe> show evo-pfemand ifl | match ae2
# 或
pfe> show evo-pfemand trunk ae-ifd-index ?  # 列出所有trunk
```

### Step 4: 查看trunk成员口完整列表和硬件状态

```bash
pfe> show evo-pfemand trunk ae-ifd-index <ae-ifd-index>
```

对比 `MemCnt`（配置总数）和 `ActMemCnt`（活跃数）。看缺少的成员口在HW层面status是Enabled还是Disabled。

### Step 5: 逐个查看子成员口的IFD信息

```bash
# 对每个配置的成员口查看
pfe> show evo-pfemand ifd index <child-ifd-idx>
```

重点检查以下字段：
- **`AggregateMember:1`** — 确认该IFD是ae成员
- **`AeIfdIdx`** — 确认指向正确的ae接口
- **`lacpTrapInstalled:1`** — 确认LACP trap已安装。如果为0，说明PFE没有将LACP trap编程到硬件，该接口可能无法正常参与LACP
- **`brcmSystemPort`** — Broadcom系统端口号，应与trunk输出中的bcm-port对应

### Step 6: 检查KNET filter和host-path

```bash
# 检查PFE filter计数器（LACP包是否被正确接收）
pfe> show evo-pfemand filter counters all

# 检查host-path asic队列
pfe> show evo-pfemand host asic-queues
pfe> show evo-pfemand host pkt-stats

# 查看host-path端口信息
pfe> show host-path ports
pfe> show host-path ports punts
pfe> show host-path packets
```

### Step 7: 检查LACP trap是否被DDoS限速

```bash
# 检查DDoS保护对LACP的影响
show ddos-protection protocols lacp
show ddos-protection protocols lacp statistics
```

### Step 8: 使用journalctl查看系统日志

```bash
# 查看当前启动的日志
journalctl -b | grep -i lacp
journalctl -b | grep -i ae2
journalctl -b | grep -i "evo-pfemand.*lacp"

# 查看全部日志（仅在以上不足时使用）
journalctl -a | grep -i lacp
```

### Step 9: 数据收集（在复现前执行）

```bash
# 完整的RSI收集
request support information | no-more | save /var/tmp/rsi-<router-name>.txt

# 收集journalctl
journalctl -b > /var/tmp/currentJournalCtlLog

# 收集应用trace
show_trace.py -a evo-pfemand -f /var/tmp/evo-pfemand_traces.log
show_trace.py -a ppm -f /var/tmp/ppm_traces.log
```

---

## 四、TTrace / Packet Dump 相关内容

### 4.1 TTrace概述（Packet Dump / TTrace页面）

TTrace 是Juniper PFE层面的包注入+追踪工具。**TTrace不依赖传统的traceoptions配置**，而是通过PFE test命令操作。

来源：`Packet Dump _ TTrace.html`
适用范围：MPC1/MPC2/MPC2 NG/MPC3 NG/MPC7/MPC8/MPC9, MPC3/MPC4, MPC5/MPC6系列

**对于ACX EVO平台（Jericho2/Jericho+），ACX Port Mirror to CPU方式更适合抓包**（见4.4节）。

### 4.2 TTrace标准操作流程（参考，主要适用于Trio芯片）

#### 单芯片架构（MPC1/MPC2/...）
```bash
# Step 1: 获取PFE编号
show jnh ifd X stream

# Step 2: 禁用self_ping，启用packet-via-dmem
test fabric self_ping disable <pfe-#>
test jnh <pfe-#> packet-via-dmem enable <Buffer-size>

# Step 3: 捕获并dump包
test jnh <pfe-#> packet-via-dmem capture 0x3 <Pattern> <offset>
test jnh <pfe-#> packet-via-dmem capture 0
test jnh <pfe-#> packet-via-dmem dump

# Step 4: 运行TTrace（注入包到trace）
test jnh <pfe-#> packet-via-dmem inject trace
# ↑ 注意：总是注入Receive parcel，不要用Transmit parcel
# 如果ttrace超过1000条，使用debug选项
test jnh <pfe-#> packet-via-dmem inject trace debug

# Step 5: 恢复
test jnh <pfe-#> packet-via-dmem disable
test fabric self_ping enable <pfe-#>
```

#### 多芯片架构（MPC3/MPC4 — 多lookup chip）
```bash
test jnh <pfe-#> <lu-#> packet-via-dmem capture 0x3 <Pattern> <offset>
test jnh <pfe-#> <lu-#> packet-via-dmem dump
test jnh <pfe-#> <lu-#> packet-via-dmem inject trace
```

#### TTrace结果分析
参考 `Ttrace-parser script 2.0 (Phase 1)` by Nikhil & Anish
脚本位置：`TTRACE ANALYZER` → `Introduction to Ttrace-parser script 2.0 (Phase 1).pptx`

### 4.3 AFT平台的TTrace命令

来源：`AFT packet dump_ttrace.html`

```bash
# Exception追踪
show jnh exceptions inst <> level terse
debug jnh exceptions inst <> exception "" type DISCARD state enable
set host-path ports punts trace enable
monitor start /var/log/messages

# TTrace（AFT版）
test jnh packet-via-dmem-capture inst <pfe instance> match-string "" parcel-type-mask 0x3 offset <>
test jnh packet-via-dmem-capture inst <pfe instance> parcel-type-mask 0x0
test jnh packet-via-dmem-dump inst <pfe instance>
test cda lkup-chip bkpt set pfeid <pfe instance> ppemask all label parcel_copy_done mode trace flag once
test jnh packet-via-dmem-inject inst <pfe instance> pkt-string ""
test cda lkup-chip ttrace table
test cda lkup-chip ttrace state ttraceid 0
```

### 4.4 ACX EVO平台的实用包捕获方法

#### 方法A: Mirror View（ACX7024X/ACX7100推荐方式）

来源：`ACX Port Mirroring to CPU.html`

```bash
# 进入RE shell (root)
labroot@router> start shell
[vrf:none] root@router:~# /usr/sbin/mirror_view -h

# 语法
mirror_view [-h] [-port PORT] [-tcpdump_filter FILTER]
            [-num_packets N] [-max_run_time SECS]
            [-direction {ingress|egress}] [-file FILE] [-queue QUEUE]

# 示例：捕获ingress方向包，100个包，5秒超时
mirror_view -port et-0/0/0 -num_packets 100 -max_run_time 5 -direction ingress

# 重要：**如果接口属于AE bundle，mirror_view应该引用AE接口而非物理口**
mirror_view -port ae1 -num_packets 10 -max_run_time 60 -direction egress
```

输出文件位于 `/var/tmp/`：
```
/var/tmp/<timestamp>-port-ae1-mirrored.pcap   # 原始pcap（含RCPU头部）
/var/tmp/<timestamp>-port-ae1-decoded.pcap     # 解码后的pcap（纯网络包）
/var/tmp/<timestamp>-port-ae1-sysheader.sys    # 系统头部信息
```

使用tcpdump查看解码后的pcap：
```bash
tcpdump -r /var/tmp/<file> -vvv -XX
```

#### 方法B: BCM Port Mirror（ACX5448/ACX710系列）

来源：`ACX Port Mirroring to CPU.html`, `ACX5K Shell Port Mirroring.html`

```bash
# 进入FPC shell
start shell pfe network fpc0

# 获取IFD索引
(vty)# show ifd brief

# 获取BCM端口号
(vty)# show pfe ifd <index>

# 设置parser security
(vty)# set parser security 10

# 启用端口镜像（到CPU，端口0）
(vty)# set bcm port_mirror ingress <bcm-port> <count> 0

# 示例：捕获BCM端口2的100个ingress包发送到CPU
(vty)# set bcm port_mirror ingress 2 100 0

# 查看ukern_trace
(vty)# show ukern_trace handles
(vty)# show ukern_trace <BCMDNX_MIRROR的ID>

# 调整buffer大小
(vty)# set ukern_trace <id> buffer 131070

# 停止镜像
(vty)# set bcm port_mirror off
```

#### 方法C: Host Path Packet Dump

来源：`Hostpath EVO.html`

```bash
# RE shell (root用户)
start shell user root

# 1. TTP dump — 检查JTD层（TTP隧道层）
[vrf:none] root@router:~# tcpdump -i iri proto 84 -w /var/tmp/ttp_packets.pcap

# 2. PacketIO packet dump — 检查PacketIO层
[vrf:none] root@router:~# tcpdump -i eth1 -s 1500 -w /var/tmp/packetio.pcap

# 3. Parcel dump — 检查PFE收发
[vrf:none] root@router:~# parcel_dump.py -p 0

# 4. TTP capture — 检查特定ae接口的TTP流量
[vrf:none] root@router:~# ttpcapture.py -i ae0
[vrf:none] root@router:~# ttpcapture.py -i et-0/0/0:1

# 5. Parcel dump细化
[vrf:none] root@router:~# parcel_dump.py -p0 -P0 -i ae0
[vrf:none] root@router:~# parcel_dump.py -p0 -P0 -i et-0/0/0:1

# 6. 实时查看PacketIO日志
[vrf:none] root@router:~# journalctl -f -u packetio-brcm
```

ACX平台镜像能力汇总：
| 平台 | CPU镜像方式 |
|------|------------|
| ACX500/1000/1100/2000/2100/2200/4000/5048/5096 | DMirror only（到另一端口）|
| ACX5448/5448-D/5448-M/ACX710 | BCM Port Mirror |
| **ACX7024/ACX7024X** | **Mirror View** |
| ACX7100-32C/48L | Mirror View |
| ACX7509 | Mirror View |

---

## 五、综合：ACX7024X上LACP排错快速命令清单

按问题排查顺序排列：

```bash
# === 1. CLI层面 ===
show lacp interfaces ae2
show interfaces ae2 extensive | match Member
show configuration interfaces ae2 | display set

# === 2. 进入PFE CLI ===
start shell pfe network fpc0

# === 3. 查看ae trunk硬件状态 ===
pfe> show evo-pfemand trunk ae-ifd-index <ae-ifd-idx>

# === 4. 查看每个配置成员口的IFD ===
pfe> show evo-pfemand ifd index <child-ifd-idx>
# 关注: AggregateMember, AeIfdIdx, lacpTrapInstalled, brcmSystemPort

# === 5. 检查PFE filter与host path ===
pfe> show evo-pfemand filter counters all
pfe> show evo-pfemand host asic-queues
pfe> show evo-pfemand host pkt-stats

# === 6. 检查host-path packet ===
pfe> show host-path ports
pfe> show host-path ports punts
pfe> show host-path packets
pfe> show host-path packet-type

# === 7. 收集应用trace ===
# RE shell
show trace application evo-pfemand node re0
show_trace.py -a evo-pfemand -t 200
# 或实时跟踪
show trace application evo-pfemand node re0 live

# === 8. 如需抓包确认 ===
# RE shell (root)
/usr/sbin/mirror_view -port ae2 -num_packets 20 -max_run_time 30

# === 9. 查看系统日志 ===
journalctl -b | grep -i lacp

# === 10. BCMShell层面查看LAG ===
jbcmsh
BCM.0> tm lag
```

---

## 关键结论

1. **LACP traceoptions：无法在EVO上使用传统方式配置。** EVO使用应用层trace机制（`show trace application` / `show_trace.py`）。如需PFE层面debug，使用 `set trace-options pfe flags all enable`（cli-pfe shell中）或配置 `set system trace application evo-pfemand ...`。

2. **PFE层面查看LACP成员口的核心命令：**
   - `show evo-pfemand trunk ae-ifd-index <idx>` — 聚合组硬件成员列表
   - `show evo-pfemand ifd index <child-idx>` — 子成员口详情，**关键检查 `lacpTrapInstalled` 字段**

3. **ae成员口不完整排查要点：**
   - CLI配置确认 → PFE trunk确认 → 逐个子IFD检查 `lacpTrapInstalled` → filter/host-path检查 → DDoS限速检查
   - 如果 `MemCnt ≠ ActMemCnt`：说明有成员口在硬件层面不活跃
   - 如果 `lacpTrapInstalled = 0`：说明LACP trap未被正确安装到硬件

4. **TTrace：** 在ACX EVO上**Mirror View**是推荐的包捕获方法，可直接对ae接口使用 `mirror_view -port ae2 ...`。传统TTrace（`test jnh packet-via-dmem`）主要适用于Trio芯片平台（MPC系列），ACX EVO可以使用 `mirror_view` 或 BCM Port Mirror方式。
