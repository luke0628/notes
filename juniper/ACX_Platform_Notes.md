# ACX平台指南结构化笔记

> 基于以下文件整理：
> 1. ACX VXLAN Debug Guide — VXLAN调试指南
> 2. ACX - MDB profile merging of Public & Private LPM distribution — MDB profile合并
> 3. ACX Port Mirroring to CPU / ACX5K Shell Port Mirroring / ACX2K Shell Port Mirroring — 端口镜像
> 4. ACX2K Data Path / ACX5448 Data Path — 数据路径
> 5. ACX2K Host Path / ACX5448 Host Path — 主机路径
> 6. ACX2K CoS / ACX5448 CoS — CoS服务等级
> 7. ACX / MX / PTX Platform Limitations — 平台限制

---

## 目录

1. [ACX系列VXLAN功能特性](#1-acx系列vxlan功能特性)
2. [端口镜像（Port Mirroring）](#2-端口镜像port-mirroring)
3. [ACX2K (Enduro-1 / Fortius) 数据路径](#3-acx2k-enduro-1--fortius-数据路径)
4. [ACX5448 (RIO / Qumran) 数据路径](#4-acx5448-rio--qumran-数据路径)
5. [ACX2K主机路径（Host Path）](#5-acx2k主机路径host-path)
6. [ACX5448主机路径（Host Path）](#6-acx5448主机路径host-path)
7. [ACX2K CoS 配置与调试](#7-acx2k-cos-配置与调试)
8. [ACX5448 CoS 配置与调试](#8-acx5448-cos-配置与调试)
9. [ACX平台限制总结](#9-acx平台限制总结)
10. [MDB Profile合并（Public & Private LPM分布）](#10-mdb-profile合并public--private-lpm分布)
11. [MX平台限制](#11-mx平台限制)
12. [PTX平台限制](#12-ptx平台限制)
13. [附录：关键PFE调试命令速查](#13-附录关键pfe调试命令速查)

---

## 1. ACX系列VXLAN功能特性

### 1.1 平台代号映射

| 代号 | 芯片代号 | 对应平台 | 最低支持版本 | 24.2R1支持 |
|------|---------|---------|-------------|-----------|
| X-men | J2 | ACX7100-32C | 21.4R1 | ✓ |
| X-men | J2 | ACX7100-48L | 21.4R1 | ✓ |
| Ultron | Q2U | ACX7024 | 22.4R1 | ✓ |
| UltronXL | — | ACX7024X | — | ✓ |
| Guardian | J2C | ACX7509 | 22.4R1 | ✓ |
| Gamora | Q2C | ACX7348 | — | ✓ |

### 1.2 VXLAN L2 GW支持（Phase 1）

- **功能**：L2 Gateway，EVPN控制平面+VXLAN覆盖数据平面
- **实例类型**：MAC-VRF，service type vlan-aware
- **BUM转发**：仅支持Ingress Replication
- **ARP/ND抑制**：支持
- **VTEP计数器**：支持入方向和出方向计数器
- **VTEP扩展特性**：支持

> 最低版本：X-men 21.4R1 | Ultron/Guardian 22.4R1 | 24.2R1全支持

### 1.3 VXLAN L3 GW支持（Phase 1）

- **功能**：L3 Gateway，支持Type-2和Type-5 EVPN路由
- **路由方向**：VXLAN↔非VXLAN双向路由
- **用户流量**：IPv4/IPv6
- **ARP/ND代理与抑制**：支持

> 最低版本：X-men 21.4R1 | Ultron/Guardian 22.4R1

### 1.4 EVPN Active/Active多归属（ESI-LAG）

- **ESI支持**：配置在IFD级别
- **BUM剪枝**：Local Bias过滤 + 非DF接口过滤
- **BGP Down时核心隔离**
- **覆盖负载均衡**：VLBNH实现（多Remote Leaf可达同一目的）

### 1.5 Phase-2 VXLAN需求

| 特性 | X-men | Ultron/Guardian/Gamora |
|------|-------|----------------------|
| SP风格VXLAN | 22.1R1 | 22.4R1（24.2R1） |
| Q-in-Q + SP VXLAN | 22.1R1 | 22.4R1 |
| Flexible Ethernet-Service + VXLAN | 22.1R1 | 22.4R1 |
| L2/L3 IFL同一IFD混合 | 22.1R1 | 22.4R1 |
| 灵活VLAN标记（单/双Tag） | 22.1R1 | 22.4R1 |
| MAC VRF（VLAN Based/Bundle） | 22.1R1 | 22.4R1 |
| Spine角色+CRB | 22.1R1 | 22.4R1 |
| 多Trunk接口同端口 | 22.1R1 | 22.4R1 |
| EVPN-VXLAN BPDU保护 | 22.1R1 | 22.4R1 |

### 1.6 重叠VLAN与多EVPN实例

- 支持EVPN-VXLAN routing instance与全局L2 VLAN重叠
- EP/SP风格均支持重叠VLAN
- MAC VRF Service type VLAN based / VLAN aware

> 最低版本：22.2R1

### 1.7 其他VXLAN特性

| 特性 | 最低版本 |
|------|---------|
| VXLAN↔VXLAN stitching单播 | 23.2R1 |
| EVPN-VXLAN↔EVPN-MPLS stitching（PFE支持） | 23.4R1 |
| 纯IPv6 Underlay VXLAN | 23.3R1 |
| 静态路由下一跳为IRB(VLAN/VXLAN) | 23.1R1 |
| ERSPAN端口镜像 | 22.3R1（X-men）/ 24.1R1 |
| Lightweight PE-CE环路检测 | 22.4R1（X-men）/ 24.1R1 |
| Overlay Ping/Traceroute | 22.4R1（X-men）/ 24.1R1 |
| VXLAN链路恢复环路预防 | 22.3R1（X-men）/ 24.1R1 |
| EVPN-VXLAN CoS | 22.4R1（X-men） |
| EVPN-VXLAN ACL/Policer | 22.4R1（X-men）/ 23.1R1 |
| EVPN-VXLAN DSCP外层层重写 | 22.4R1（X-men） |
| Symmetric IRB Type-2 | 22.2R1（X-men）/ 24.1R1 |

### 1.8 VXLAN报文格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|R|R|R|R|I|R|R|R|            Reserved                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                VXLAN Network Identifier (VNI) |   Reserved    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- 非VXLAN接口进入的帧映射到特定VNI
- L2流量发往远端时，VNI编码在VXLAN隧道头中
- 反向方向：VXLAN连接接口上，网关剥离VXLAN头，VNIs用于识别对应VLAN并转发

---

## 2. 端口镜像（Port Mirroring）

### 2.1 ACX5K系列（ACX5048/5096）Shell端口镜像

#### 步骤1：查看IFD端口号映射

```bash
# 进入PFE shell
start shell pfe network fpc0

# 查看IFD到BCM端口映射
show dcbcm ifd all
```

输出示例：
```
ifd name     global-dev  local-dev   port-num   port-name
xe-0/0/0              0          0          1       xe0
xe-0/0/1              0          0          2       xe1
```

#### 步骤2：启用端口镜像

```bash
# 入方向镜像：xe-0/0/0的入流量镜像到xe-0/0/1
set bcm bcmshell "dmirror xe0 mode=Ingress DestPort=xe1"

# 出方向镜像：xe-0/0/0的出流量镜像到xe-0/0/1
set bcm bcmshell "dmirror xe0 mode=Egress DestPort=xe1"

# 双向镜像：xe-0/0/0的出入流量都镜像到xe-0/0/1
set bcm bcmshell "dmirror xe0 mode=All DestPort=xe1"

# 查看当前活跃的端口镜像
set bcm bcmshell "dmirror show"
```

#### 步骤3：关闭镜像

```bash
set bcm bcmshell "dmirror xe0 mode=Off DestPort=xe1"
```

#### 步骤4：验证镜像是否关闭

```bash
set bcm bcmshell "dmirror show"
```

---

### 2.2 ACX5448 Shell端口镜像

#### 步骤1：查找IFD编号

```bash
start shell pfe network fpc0
show ifd brief
```

输出示例：
```
Index  Name         Flags         Slot   State
179  et-0/1/0      0x0000000000008000     0  Up
180  et-0/1/1      0x0000000000008000     0  Up
181  et-0/1/2      0x0000000000008000     0  Up
139  xe-0/0/8      0x0000000000008000     0  Up
```

#### 步骤2：映射IFD到BCM端口

```bash
# 查看IFD对应的BCM端口信息
show pfe ifd <IFD_index>

# 示例：et-0/1/2 (Index 181) -> BCM Port 57
# 示例：xe-0/0/8 (Index 139) -> BCM Port 9
```

#### 步骤3（可选）：查看端口统计

```bash
set bcm bcmshell "show c"
```

#### 步骤4：启用端口镜像

```bash
# 先设置parser安全级别
set parser security 10

# 启用人方向镜像（镜像源端口57，抓10个包，发往目的端口9）
set bcm port_mirror ingress 57 10 9
```

⚠️ **重要警告**：
```
WARNING: Enabling packet mirroring to host io module would
affect packet io performance. This could severely
impact the control plane leading to protocol flaps
if there are packet losses due to reduced
performance of packet io module.
```

#### 步骤5：关闭镜像

```bash
set bcm port_mirror off
```

---

### 2.3 ACX2K Shell端口镜像

#### 步骤1：查看端口映射

```bash
# ACX2K UART/Console下
show bcm port-mapping

# 输出示例：
# bcmport  SGMII port  Interface Name
# 5        ge3         ge-0/1/0
# 6        ge4         ge-0/1/1
```

#### 步骤2：全局禁用镜像检查（VLAN/STP检查）

```bash
set bcm bcmshell "modreg egr_config_1 DISABLE_MIRROR_CHECKS=1"
```

#### 步骤3：启用镜像

```bash
# 入方向镜像：ge-0/1/0入流量镜像到ge-0/1/1
set bcm bcmshell "dmirror ge3 mode=Ingress DestPort=ge4"

# 出方向镜像
set bcm bcmshell "dmirror ge3 mode=Egress DestPort=ge4"

# 双向镜像
set bcm bcmshell "dmirror ge3 mode=All DestPort=ge4"
```

#### 步骤4：关闭镜像

```bash
set bcm bcmshell "dmirror ge3 mode=Off DestPort=ge4"
```

---

## 3. ACX2K (Enduro-1 / Fortius) 数据路径

### 3.1 架构概述

- **芯片**：Broadcom Fortius（Enduro-1系列）
- **平台**：ACX500/1000/2000系列
- **LPM表**：基于TCAM，可存储任意长度的前缀
- **ACX 5048/5096**使用DNX(FE2)芯片，部分命令不同

### 3.2 关键调试命令

#### 查看L3主机路由表

```bash
# PFE下查看L3 entry
set bc bc "l3 defip show"

# 查看IPv4路由表（PFE级别）
show route ip
```

输出示例：
```
IPv4 Route Table 0, default.0, 0x80000:
Destination         NH IP Addr      Type     NH ID Interface
2.2.2/24           -                Resolve   521   RT-ifl 324 xe-0/3/0.0 ifl 324
2.2.2.2            2.2.2.2          Unicast   587   RT-ifl 324 xe-0/3/0.0 ifl 324
```

#### 查看Next Hop硬件表

```bash
# 从L3 entry中获取NH index后：
cprod -A feb0 -c 'set bc bc "d chg l3_entry_only"' | grep <IP_ADDR_HEX>

# 用NH index dump入方向L3 NH
cprod -A feb0 -c 'set bc bc "d chg ing_l3_next_hop <NH_INDEX>"'

# 用NH index dump出方向L3 NH
cprod -A feb0 -c 'set bc bc "d chg egr_l3_next_hop <NH_INDEX>"'

# 查看出方向L3接口
cprod -A feb0 -c 'set bc bc "d chg EGR_L3_INTF <INTF_NUM>"'
```

#### BCM端口映射查询

```bash
# ACX5048/5096
show dcbcm ifd all

# ACX500/1k/2k/4k
show bcm port-mapping

# 查看SVLAN映射
show pfe svlan mapping
```

### 3.3 L2电路数据路径

#### Untagged L2CCC数据流：Port → source_trunk_map → source_vp → ing_dvp_table → ing_l3_next_hop → Destination Port / egr_l3_next_hop

#### Native VLAN L2CCC数据流：Port → vfp_policy_table → source_vp → ing_dvp_table → ing_l3_next_hop → Destination Port / egr_l3_next_hop

#### 关键表查询

```bash
# Source VP
set bc bc "d chg source_vp <idx>"

# Source Trunk Map
set bc bc "d chg source_trunk_map <idx>"

# Ingress DVP表
set bc bc "d chg ing_dvp_table <idx>"

# VLAN转发表
set bc bc "d chg vlan_xlate" | grep VLAN_ID=<id>
```

#### MPLS L2电路验证

```bash
# 查看L2电路连接
show l2circuit connections

# MPLS entry（入标签查找）
cprod -A fpc0 -c 'set bc bc "du chg mpls_entry"' | grep MPLS_LABEL=<hex>

# Egress MPLS VC标签表
set bc bc "d chg egr_mpls_vc_and_swap_label_table <idx>"

# Egress隧道MPLS
set bc bc "d chg egr_ip_tunnel_mpls <idx>"

# Egress MAC DA Profile
set bc bc "d chg EGR_MAC_DA_PROFILE <idx>"
```

---

## 4. ACX5448 (RIO / Qumran / DNX) 数据路径

### 4.1 架构概述

- **芯片**：Broadcom Qumran（DNX / Jericho系列）
- **平台**：ACX5448 / ACX710（RIO/ODIN）
- **虚拟机架构**：JunOS运行在KVM虚拟机中，PFE为独立进程
- **ukern_trace调试**：默认关闭printf，需手动启用

### 4.2 Bridge Domain (BD) 调试

#### 查看BD信息

```bash
# 查看所有BD
show bridge-domain

# 查看BD详细信息（从show bridge-domain获取BD-Index）
show l2 halp bridge-domain <bd_index>
```

输出关键字段：
- **BD VLAN/VSI**：VSI编号
- **mc_grp**：BUM流量的多播组号
- **l2pt-nni-mc_grp**：L2PT NNI端口组
- **uni-mc_grp[STP/LACP/LLDP等]**：各协议L2PT的UNI组

#### 验证BD配置

1. 检查所有IFL是否都在BD中（`show l2 halp bridge-domain`），LIF-GPORT应为非零值
2. 检查所有IFL-LIF-GPORT是否都在多播组中

```bash
# 查看多播组成员
set bcm bcmshell "diag multicast ingress <mc_grp_id> mem"
```

### 4.3 MAC学习调试

```bash
# 启用MAC学习调试
debug l2 halp enable mac-notify
debug l2 halp enable halp
debug l2 halp enable init
debug l2 halp enable utils

# 追踪在DNX_L2ALM_HALP中

# 检查ASIC是否生成了学习事件
set bcm bcmshell "diag count olp"
# OLP0 OlpFifo0EventCounter 为0表示HW未产生事件

# 查看MAC表
set bcm bcmshell "l2 show"
set bcm bcmshell "l2 count vsi=-1"    # 全系统MAC数量
set bcm bcmshell "l2 count vsi=<vsi>" # 指定VSI的MAC数量
```

### 4.4 单播转发调试

```bash
# 查看上一包的完整转发路径
set bcm bcmshell "diag pp last"

# 查看转发决策/TRAP跟踪
set bcm bcmshell "diag pp fdt"

# 查看包解析信息
set bcm bcmshell "diag pp pi"

# 查看丢弃计数（非转发决策导致的丢包，如CoS队列丢弃）
set bcm bcmshell "diag count g"
```

**diag pp last的输出解读**：
- **Port Termination**：入端口
- **Parser**：包格式、初始VID、TC、DP
- **VLAN Translation**：Local LIF、System LIF、VSI
- **Forward Lookup**：Key（DA, FID）→ Result（uc_port, OutLif）
- **FEC Resolution**：出端口和OutLif
- **TM Resolution**：最终出端口和队列

### 4.5 IP单播路由调试

```bash
# 查看IFL的LIF-GPORT映射
show pfe ifl logical-port-mapping

# 使用gport诊断
set bc bc "diag pp gport id=<gport_id>"
# 输出包含VSI、LocalInLif、LocalOutLif、phy_gport等

# 查看VSI决策
set bc bc "diag pp VSI_decision"

# 查看RIF信息
set bc bc "diag pp rif"
# 输出VRF ID、IPv4/IPv6/MPLS使能状态

# 查看路由表（KAPS/TCAM）
set bc bc "kbp kaps_show"

# 查看FEC表
set bc bc "diag alloc fec direct=1 from=<id> to=<id>"
```

**IPv4单播转发流**：
1. 解析VLAN → Local LIF → System LIF → VSI
2. 路由查找（VRF, DIP）→ FEC ID
3. FEC解析 → SINGLE PORT, 出端口, EEP/AC, RIF
4. TM解析 → 最终端口+队列

### 4.6 L2CC（CCC）调试

```bash
# RE级别
show l2circuit connections

# PFE级别
show route ccc

# 查看CCC标签映射
show route pw_label_mapping

# DNX数据库诊断
set bc bc "diag db db_dump 0"

# 查看IFL详细信息
show pfe ifl <ifl_index>
```

### 4.7 VPLS调试

```bash
# RE级别
show vpls connections
show route table mpls.0
show route forwarding-table

# PFE级别
show route mpls
show route bridge
show nhdb type indirect recursive
show nhdb type composite recursive
show nhdb id <ID> extensive

# VPLS的UNI→NNI封装检查
set bcm bcmshell "diag pp gport id=<gport>"

# VPLS入标签检查（SEM B数据库）
set bcm bcmshell "diag db dbd 4"
```

### 4.8 计数器与统计

```bash
# 端口统计
set bc bc "show c"
# 或
set bc bc "show counters"

# 清除计数器
set bc bc "clear counters"
```

---

## 5. ACX2K主机路径（Host Path）

### 5.1 IFP过滤器/应用

```bash
# 查看所有动态过滤器应用
sh filter apps

# 查看特定应用的TCAM条目
sh filter apps <app_id>

# 查看TCAM条目详情
set bcm bcmshell "fp show entry <entry_id>"
```

#### OSPF主机路径示例

```bash
# OSPF app ID = 28（DYN_IFP_OSPF）
sh filter apps 28

# fp show entry会显示action：
# action={act=CosQCpuNew, param0=34(0x22)}  => OSPF发往CPU Queue #34
# action={act=GpCopyToCpu, param0=1}
```

### 5.2 CPU队列和速率限制

| 命令 | 说明 |
|------|------|
| `sh bcm pkt rx cos-config` | 查看CPU队列号和配置 |
| `show bcm pkt cnt` | 查看队列统计 |
| `clear bcm pkt cnt` | 清除队列统计 |

- 每个CPU队列都有速率限制，以保护CPU
- CFM和BFD报文发送到LLQ（低延迟队列）

### 5.3 控制面报文抓取

```bash
# Step 1: 设置安全级别
set parser security 10

# Step 2: 启用包调试模式
set bcm pkt debug-mode enable

# Step 3: 抓取n个RX包
set bcm pkt dump rx <num_pkts> on

# 其他调试命令：
set bcm pkt dump rxq <queue-no> <num-pkts> <verbose-mode>  # 指定队列
set bcm pkt dump tx <num-pkts> <verbose-mode>               # TX包
set bcm pkt <rx-drop|tx-drop> <num-pkts> <verbose-mode>     # 丢弃包
set bcm pkt trace <rx|tx> <num-pkts>                        # 包处理代码追踪
```

---

## 6. ACX5448主机路径（Host Path）

### 6.1 架构概述

ACX5448采用KVM虚拟化架构：

```
+----------------------------------+
|          Linux Host              |
|  +----------------------------+  |
|  |   JunOS VM (vjunos0)      |  |
|  |   - routing protocols      |  |
|  |   - management plane       |  |
|  +----------------------------+  |
|  +----------------------------+  |
|  |   PFE Process              |  |
|  |   (Broadcom SDK)           |  |
|  +----------------------------+  |
+----------------------------------+
```

### 6.2 关键排查文件/路径

| 文件/目录 | 说明 |
|-----------|------|
| `/var/platform/vjunos0_xml_config_tvp_master_acx5448.xml` | JunOS VM配置文件（vehostd/libvirt使用） |
| `/var/platform/config.bcm` | Broadcom Qumran配置 |
| `/var/platform/board.*` | 板级配置文件 |
| `/var/platform/rc*.soc` | SOC初始化脚本 |
| `/var/platform/pvidbschema*` | 特性属性文件（使能ACX5448功能） |
| `/var/log/syslog` | Host dmesg和应用日志 |
| `/var/log/daemon.log` | Vehostd日志 |
| `/var/log/auth.log` | 系统认证和登录日志 |
| `/var/log/audit/audit.log` | SELinux安全日志 |
| `/var/log/i2cd` | I2C控制器日志 |

### 6.3 验证命令

```bash
# 查看Linux bridge
brctl show

# 查看网络接口
ip link show

# 查看VM状态
virsh list --all

# 查看内核模块
lsmod | egrep "kvm|host|i40e|mac"
# 关键模块：vhost_net, macvtap, kvm_intel, kvm, i40e

# 查看socat串口连接（JunOS VM控制台）
ps -aef | grep socat
```

---

## 7. ACX2K CoS 配置与调试

### 7.1 基础验证命令

```bash
# JunOS级别 - 查看下发的CoS转发信息
run show class-of-service forwarding-table

# PFE级别 - 查看CoS配置
show cos classifier
show cos rewrite
show ifd brief
show ifl brief
show cos classifier bindings
show cos rewrite bindings
```

### 7.2 固定分类（Fixed Classification）

```bash
# JunOS配置
set class-of-service interfaces ge-0/1/3 unit 0 forwarding-class network-control

# PFE验证
show cos halp fixed-classification

# VFP检查固定分类条目
set bc bc "fp show entry <vfp_entry_id>"
```

**硬件字段**：
- `VFP_POLICY_TABLE.CHANGE_INT_PRIORITY = 1`
- `VFP_POLICY_TABLE.NEW_INT_PRIORITY = <int_pri>`
  - BE=0, EF=1, AF=2, NC=3

### 7.3 802.1p BA分类

```bash
# JunOS配置示例
set class-of-service interfaces ge-0/1/3 classifiers ieee-802.1 ci

# 查看HALP资源使用
show cos halp classifier dot1p

# 查看端口BCM映射
show bcm port-mapping

# 验证端口配置
set bcm bcmshell "d chg port <bcm_port_id>"
# 关键字段：
# PORT->TRUST_OUTER_DOT1P = 1
# PORT->TRUST_DOT1P_PTR = X
# PORT->USE_INNER_PRI = 1 （用于内层VLAN 802.1p）

# 查看Dot1p→int_pri映射（ING_PRI_CNG_MAP）
# 索引 = TRUST_DOT1P_PTR * 16，每个profile占用16个连续entry
set bcm bcmshell "d chg ing_pri_cng_map <base> 16"

# 未标记包始终映射到int_pri 0（Junos 12.2）
```

### 7.4 DSCP/Inet-prec/DSCPv6分类

```bash
# JunOS配置
set class-of-service interfaces ge-0/1/3 classifiers dscp d1

# 验证端口配置
set bcm bcmshell "d chg port <bcm_port_id>"
# 关键字段：PORT->TRUST_DSCP_V4=1, PORT->TRUST_DSCP_V6=1

# DSCP→int_pri映射（DSCP_TABLE）
# 索引 = bcm_port_id * 64，每个profile占用64个连续entry
set bcm bcmshell "d chg dscp_table <base> 64"
```

**注意**：Fortius（ACX2K）不支持入方向DSCP转换，DSCP字段值与包中相同。

### 7.5 MPLS EXP分类

- Fortius支持单个EXP分类器
- 在MPLS_ENTRY中检查：
  - `DECAP_USE_EXP_FOR_PRI = 1`
  - `DECAP_USE_EXP_FOR_INNER = 1`

```bash
# 查看EXP分类器映射
show cos halp classifier exp

# 验证MPLS entry
set bcm bcmshell "d chg mpls_entry"

# 查看EXP映射profile
set bcm bcmshell "d chg ING_MPLS_EXP_MAPPING"
```

### 7.6 802.1p重写

```bash
# JunOS配置
set class-of-service interfaces ge-0/1/3 rewrite-rules ieee-802.1 r1

# 验证端口重写使能
set bcm bcmshell "g egr_vlan_control_1.<sgmii_port>"
# 关键字段：REMARK_OUTER_DOT1P=1

# 查看EGR_PRI_CNG_MAP
# 索引 = bcm_port_id * 64 + [int_pri<<2|cng]
# int_pri = FC-id, cng=0/1/2（PLP low/medium-high/high）
set bcm bcmshell "d chg EGR_PRI_CNG_MAP <base> 64"
```

### 7.7 DSCP重写

```bash
# JunOS配置
set class-of-service interfaces ge-0/1/3 rewrite-rules dscp rd

# 验证端口
set bcm bcmshell "g egr_vlan_control_1.<sgmii_port>"
# REMARK_OUTER_DSCP=1

# 查看EGR_DSCP_TABLE
# 索引 = bcm_port_id * 64 + [int_pri<<2|cng]
set bcm bcmshell "d chg EGR_DSCP_TABLE <base> 64"
```

### 7.8 EXP重写

- 对LSR/PW/VPN查 `egr_mpls_vc_and_swap_label_table`
- 对隧道查 `egr_ip_tunnel_mpls`

```bash
# 验证EXP重写选择
# egr_mpls_vc_and_swap_label_table.MPLS_EXP_SELECT = 0x1（USE_MAPPING）
# egr_ip_tunnel_mpls.MPLS_EXP_SELECT_0 = 1

# 查看EXP映射profile
# Profile_base = EXP_MAPPING_PTR * 64
# Offset = [int_pri<<4|cng]
set bcm bcmshell "d chg EGR_MPLS_EXP_MAPPING_1"
set bcm bcmshell "d chg EGR_MPLS_EXP_MAPPING_2"
```

### 7.9 ACX2K CoS硬件配置总结表

| 特性 | Enduro-1 (ACX1k/2k) | Enduro-2 (ACX4k) |
|------|---------------------|-------------------|
| **802.1p分类(Port)** | PORT→TRUST_DOT1P_PTR=X, TRUST_OUTER_DOT1P=1, USE_INNER_PRI=1, 在ING_PRI_CNG_MAP[X]编程 | PORT→TRUST_DOT1P_PTR=X, USE_INNER_PRI=1 |
| **保留外层Tag 802.1p (IP路由)** | PORT→USE_INCOMING_DOT1P=1 | — |
| **802.1p分类(SVP/UNI)** | Source_VP→TRUST_DOT1P_PTR=X, TRUST_OUTER_DOT1P=1, USE_INNER_PRI=0/1 | Source_VP→TRUST_DOT1P_PTR=X, USE_INNER_PRI=1 |
| **802.1p重写(Port)** | egr_vlan_control_1.REMARK_OUTER_DOT1P=1, 在EGR_PRI_CNG_MAP[port,cng,pri]编程 | 同左 |
| **802.1p全局serial QoS** | ING_CONFIG_64: IGNORE_PPD0_PRESERVE_QOS=1, IGNORE_PPD2_PRESERVE_QOS=1; EGR_CONFIG_1: DISABLE_PPD2_PRESERVE_QOS=1, DISABLE_PPD0_PRESERVE_QOS=1 | ING_CONFIG_64: IGNORE_PPD3_PRES... |

---

## 8. ACX5448 CoS 配置与调试

### 8.1 VoQ连接信息

```bash
# 查看入方向VoQ连接
set bc bc "cosq conn ing"
# Voq ID | NOF Voqs | Core | Remote Voq Connector | Remote Modid
# 32     | 8        | 0    | 48                  | 0
# 32     | 8        | 1    | 560                 | 0

# 查看出方向VoQ连接
set bc bc "cosq conn egr"
# Voq Connector ID | NOF Connectors | Core | Ingress Voq | Ingress Modid
# 32               | 8             | 0    | 2064        | 0
# 544              | 8             | 0    | 2064        | 1
```

### 8.2 VoQ调试

当日志消息指向特定VoQ时：

```bash
# 查看入方向VoQ组件
cosq comp ing voq=<id>

# 查看出方向端口组件
cosq comp egr port=<id>
```

> **注意**：ACX5448 CoS文档内容有限，更多CoS配置与ACX2K类似（共享Broadcom SDK架构），但ACX5448使用DNX/Jericho芯片组，VoQ队列管理机制不同。

---

## 9. ACX平台限制总结

### 9.1 MPLS LSP统计限制

| 平台 | MPLS LSP Statistics | 状态 |
|------|-------------------|------|
| RIO/ODIN (ACX5448/ACX710) | 不支持 | ASIC计数器资源限制，无Roadmap |
| ACX7100/ACX7024/ACX7509 | 22.4R1开始支持 | PR#1457672 (RIO), PR#1486783 (ODIN) |

```bash
# 配置示例（仅支持平台有效）
show mpls lsp statistics
```

### 9.2 组播速率统计限制

- **所有ACX系列**：`show multicast route group` 显示0 pps
- **PR#1431239**：产品限制
- **ACX7100/ACX7024/ACX7509**：24.1R1-EVO开始支持
- **RIO平台**：ASIC限制，不支持
- **ACX7100**：`show multicast route extensive instance MVPN` 不显示正确统计（PR#1720469）

### 9.3 MPLS ECMP哈希限制（ACX710/ACX5448 DNX平台）

**支持**：
- Top 3 labels（label-1, label-2, label-3）
- MPLS payload IP L3 - IPv4

**不支持**（JUNOS CLI可能仍然显示这些选项，但实际无效）：
- Bottom-labels
- no-labels
- ether-pseudowire control-word
- MPLS payload IP L3 - IPv6
- MPLS Payload L4 port-data

### 9.4 show chassis fpc显示限制

- **ACX7100 / ACX7024**：`show chassis fpc` 不显示CPU/内存（PR#1703972, PR#1735274）
- **原因**：FPC在ACX7100/ACX7024中是逻辑FRU，无物理FPC CPU
- **Scope/Avengers平台**：有FPC CPU，可正常显示
- **X-men/Ultron**：无FPC CPU，显示为空 → **预期行为**（非限制）

### 9.5 防火墙过滤限制（ACX EVO）

```bash
# 可能出现的错误日志：
evo-pfemand[25379]: [Error] BrcmPlusDfw: Unsupported prefixlen 128 Max supported is 64
evo-pfemand[25379]: [Error] BrcmPlusDfw: Unsupported prefixlen configured for the prefix Match 'sourceIpv6Address in firewall profile 'profile-two'.
```

- **参考**：KB70335（ACX EVO支持的人站过滤）/（出站过滤）

---

## 10. MDB Profile合并（Public & Private LPM分布）

> **注意**：本文件原始内容主要包含SharePoint页面元数据，具体技术内容有限。以下基于文件名推断：

- `ACX - MDB profile merging of Public & Private LPM distribution`
- 涉及MDB（Memory Database）profile合并
- 涉及Public和Private LPM（Longest Prefix Match）分布
- 通常与ACX DNX平台的内存资源管理和TCAM/LPM表划分相关

> 具体内容请参考原始SharePoint页面或更新后的文档版本。

---

## 11. MX平台限制

> **注意**：该文件内容仅包含SharePoint页面结构，实际技术内容未提取到。建议直接访问原始SharePoint页面获取：

- **页面**：Routing Platforms Troubleshooting Checklist → MX Platform Limitations
- **作者**：ranpreets@juniper.net

---

## 12. PTX平台限制

> **注意**：该文件内容仅包含SharePoint页面结构，实际技术内容未提取到。建议直接访问原始SharePoint页面获取：

- **页面**：Routing Platforms Troubleshooting Checklist → PTX Platform Limitations
- **作者**：ranpreets@juniper.net

---

## 13. 附录：关键PFE调试命令速查

### ACX2K (Enduro-1 / Fortius)

| 命令 | 说明 |
|------|------|
| `start shell pfe network fpc0` | 进入PFE shell |
| `show bcm port-mapping` | 查看BCM端口映射 |
| `show pfe svlan mapping` | 查看SVLAN映射 |
| `show dcbcm ifd all` | ACX5K: 查看IFD到BCM映射 |
| `set bc bc "l3 defip show"` | 查看LPM路由表 |
| `show route ip` | 查看PFE级IPv4路由表 |
| `cprod -A feb0 -c 'set bc bc "d chg ..."'` | 通过cprod访问硬件表 |
| `set bcm bcmshell "fp show entry <id>"` | 查看IFP TCAM条目 |
| `show cos classifier/rewrite` | 查看CoS配置 |
| `show cos halp fixed-classification` | 查看固定分类 |
| `set bcm bcmshell "d chg port <id>"` | 查看端口寄存器 |

### ACX5448 (RIO / Qumran / DNX)

| 命令 | 说明 |
|------|------|
| `start shell pfe network fpc0` | 进入PFE shell |
| `show ifd brief` | 查看IFD列表 |
| `show pfe ifd <index>` | 查看IFD详细信息（含BCM端口号） |
| `show bridge-domain` | 查看所有Bridge Domain |
| `show l2 halp bridge-domain <id>` | 查看BD详细信息 |
| `set bcm bcmshell "diag pp last"` | 查看上一包的完整转发路径 |
| `set bcm bcmshell "diag pp fdt"` | 查看转发决策追踪 |
| `set bcm bcmshell "diag pp rif"` | 查看RIF信息 |
| `set bcm bcmshell "diag pp gport id=<gport>"` | 查看gport诊断 |
| `set bcm bcmshell "diag alloc fec direct=1 from=X to=Y"` | 查看FEC表 |
| `set bcm bcmshell "diag count g"` | 查看全局包计数器（含丢弃原因） |
| `set bcm bcmshell "diag multicast ingress <id> mem"` | 查看多播组成员 |
| `set bcm bcmshell "l2 show"` | 查看MAC表 |
| `set bc bc "cosq conn ing/egr"` | 查看VoQ连接 |
| `show nhdb id <ID> extensive` | 查看NH详情 |

### 端口镜像

| 平台 | 启用命令 | 关闭命令 |
|------|---------|---------|
| ACX5K | `set bcm bcmshell "dmirror <port> mode=<Ingress/Egress/All> DestPort=<port>"` | `dmirror <port> mode=Off DestPort=<port>` |
| ACX5448 | `set parser security 10` → `set bcm port_mirror ingress <src> <count> <dst>` | `set bcm port_mirror off` |
| ACX2K | `set bcm bcmshell "modreg egr_config_1 DISABLE_MIRROR_CHECKS=1"` → `dmirror <port> mode=<Ingress/Egress/All> DestPort=<port>` | `dmirror <port> mode=Off DestPort=<port>` |

### 控制面报文抓取

| 平台 | 命令 |
|------|------|
| ACX2K | `set parser security 10` → `set bcm pkt debug-mode enable` → `set bcm pkt dump rx <n> on` |
| ACX2K | `show bcm pkt cnt`（队列统计）/ `clear bcm pkt cnt`（清除） |

---

> **文档版本**：基于2026年6月27日提取的SharePoint内容整理
> **来源**：Juniper Networks - Routing Platforms Troubleshooting Checklist / ACX-PFE-INFO
