# JunOS 协议排错笔记——结构化中文摘要

> 本文档基于 Juniper "Routing Platforms Troubleshooting Checklist" 维基中2026年6月27日上传的38个排错文档整理。
> **每个命令和知识点均标注平台归属**。

---

## 总览：文档框架

**文档首页**: `Routing Platforms Troubleshooting Checklist - Home`
- Juniper内部SharePoint维基站点，面向ATAC/JTAC一线排错工程师
- 提供BGP/OSPF/IS-IS/RSVP/LDP/BFD/PIM/MSDP/VRRP/LACP/MC-LAG/Bridging/EVPN-VXLAN/L3VPN/VPLS/CFM/LFM/SFLOW/COS/PTP/MACSEC/ARP/IPv6-NDP等协议的排错checklist
- 每个协议文档由JTAC/ATAC资深工程师撰写

---

## 一、路由协议

### 1.1 BGP

**平台**: JunOS传统/通用

**关键排错命令**:
```
# 基础验证
show bgp summary                                        # JunOS传统
show configuration protocols bgp group <name> | display set | display inheritance
show bgp neighbor                                        # JunOS传统
show route protocol bgp terse
show route advertising-protocol bgp <peer-ip>           # 检查通告的路由
show route receive-protocol bgp <peer-ip>               # 检查收到的路由
show route hidden                                       # 检查隐藏路由
show route resolution unresolved                        # 检查下一跳未解析路由

# 高级诊断 (24.4+版本)
show bgp diagnostics dropped-route-cache                # JunOS传统
show bgp diagnostics export-evaluation-triggers
show bgp diagnostics import-evaluation-triggers
show bgp diagnostics neighbor
```

**排错步骤**:
1. 验证BGP对等体之间的IP连通性
2. 检查配置参数：本地AS、对等体AS、IP地址
3. 检查认证参数
4. 监控系统日志中BGP相关消息
5. 检查防火墙过滤是否阻塞BGP报文
6. 审查事件消息判断原因:

| Event | 原因 |
|---|---|
| BfdDown | BFD超时 |
| HoldTime | 邻居路由器未响应BGP消息 |
| RecvNotify | 邻居路由器未收到或收到损坏的BGP消息 |
| Stop | 配置干扰BGP协议流量 |
| TransportError | 路由器内存拥塞 |
| NsrNotsupported | NSR不支持的BGP配置 |

**Traceoptions**:
```
set protocols bgp group <group> traceoptions flag all
set protocols bgp group <group> traceoptions file bgp.log size 10m files 5
```

---

### 1.2 BGP RIB-Sharding

**平台**: JunOS传统 (64-bit RPD, 需最小4CPU & 16GB内存)

**关键命令**:
```
set system processes routing bgp rib-sharding number-of-shards <1-31>     # 启用分片
set system processes routing bgp update-threading number-of-threads group-split-size  # 必须同时配置
```

**说明**:
- **默认禁用**，从19.4R1引入
- 将统一BGP RIB拆分为多个子RIB，每个子RIB处理部分BGP路由
- 路由哈希到不同线程实现并发
- 分片数默认等于CPU数量，范围1-31
- NSR与sharding支持于22.2引入
- 支持地址族: IPv4 VPN Unicast/Multicast, IPv6 VPN Unicast/Multicast, IPv4/IPv6 Labeled Unicast
- **注意**: 修改RIB-Sharding配置时RPD会自动重启

---

### 1.3 OSPF

**平台**: JunOS传统/通用

**关键排错命令**:
```
show configuration protocols ospf | display set | display inheritance    # 验证配置
show ospf statistics                                                     # 检查OSPF错误
show ospf route                                                          # 查看OSPF添加的路由
show ospf overview
show ospf database                                                       # LSDB内容
show ospf neighbor detail                                                # 邻居详情
show ospf interface
show ospf log
show route protocol ospf
show ospf database summary
show ospf database extensive
```

**Traceoptions flags**: all, backup-spf, database-description, error, event, flooding, general, graceful-restart, hello, ldp-synchronization, lsa-*, normal, nsr-synchronization, packet-dump, packets, policy, route, spf, state, task, timer

**排错步骤**:
1. 验证配置并ping邻居设备IP
2. 检查OSPF统计数据中的错误
3. 查看OSPF LSDB及其路由
4. 启用traceoptions获取详细信息

---

### 1.4 IS-IS

**平台**: JunOS传统/通用

**关键排错命令**:
```
show configuration protocols isis | display set | display inheritance
show isis statistics                                                    # 查看IIH接收/处理/丢弃统计
show isis adjacency
show isis database
show isis interface
show route protocol isis
monitor traffic interface <ifl>                                        # 抓包确认RE是否收到
```

**排错步骤**:
1. **邻接建立问题** — 检查最少配置:
   - 接口必须属于对应 routing-instance/logical-system
   - ISO地址族必须启用
   - 需要配置IPv4和/或IPv6地址
   - 可通过`no-ipv4-routing`仅用其他地址族建立邻接
   - 需要配置loopback接口（ISO地址作为system-id）
2. **接口上未学到邻接** — 大概率是底层数据连通性问题:
   - 双方互相ping验证
   - MTU不匹配可能导致IIH PDU丢弃，用ping with size 1492测试
3. **邻接卡在INIT状态** — 路由器发现邻居的IIH PDU中不包含自己的IS-REACH TLV，或存在单向转发问题

**注意**: IS-IS PDU在普通接口和GRE隧道上的发送方式有显著差异，可能导致邻接建立问题（参考KB7848）

---

### 1.5 RSVP

**平台**: JunOS传统/通用

**关键命令**:
```
show mpls lsp extensive                                              # LSP事件历史
show rsvp session
show rsvp neighbor

# RSVP Per LSP traceoptions
set protocols rsvp lsp-set single-lsp match-criteria lsp-name <name>
set protocols rsvp lsp-set single-lsp traceoptions flag all detail

# 启用LSP历史记录到syslog (隐藏knob)
set protocols mpls log-lsp-history                                   # PR 1080595
```

**重要参数**:
- **OSD** (optimize-switchover-delay): 延迟LSP切换到新优化路径
- **OHDD** (optimize-hold-dead-delay): 优化切换后延迟拆除旧路径
- **OAT** (optimize-adaptive-teardown delay): 利用TAG库反馈机制，在RPD确认路由已完全切换到新LSP后才触发拆除（19.1+）
  - OAT启动后，OHDD被忽略

**参考KB**: KB34687 (如何判断哪个LSP在使用bypass), KB37028 (查找Tunnel-id和LSP-id)

---

### 1.6 LDP

**平台**: JunOS传统/通用

**关键命令**:
```
ping mpls ldp                                                         # 测试LDP连通性
trace mpls ldp
show ldp database
show ldp session
show ldp statistics
show ldp neighbor
show ldp interface
show ldp overview
show ldp route

# 检查IGP状态
show isis adjacency
show ospf neighbor

# Traceoptions
set protocols ldp traceoptions flag all
set protocols ldp traceoptions file ldp.log size 10m files 10
```

---

### 1.7 BFD

**平台**: JunOS传统/AFT (命令有差异)

**关键排错命令 (RE层面)**:
```
show bfd session detail                                              # JunOS传统
show bfd session extensive
show ppm adjacencies summary                                        # PPM通用
show ppm interfaces detail
show ppm adjacencies detail
show ppm connections detail
show ppm transmissions detail
show pfe statistics traffic protocol bfd                            # PFE级别
```

**PFE层面命令 (MX传统)**:
```
start shell pfe network fpc#
show ppm adjacencies protocol bfd
show ppm statistics protocol bfd
show pfe bfdsession all
show pfe bfdsession id 0x...
show pfe statistics traffic
```

**AFT平台PFE命令**:
```
show ppm adjacencies protocol bfd detail
show ppm control protocol bfd session receive iflIndex <idx> clientId <id>
show ppm processor protocol bfd session receive <ifl_index>
```

**JNH (Junos Next-generation Hardware) 排错**:
```
show jnh 0 exception terse
show jnh 0 exceptions
show jnh 0 trap-info
show jnh inline-ka summary                                         # 内联BFD
show jnh inline-ka db bfd-tx
show jnh inline-ka db bfd-rx
show ddos policer bfd stats
show ddos policer bfd conf
```

**启用JNH ukern日志**:
```
set ukern_trace 8 logging enable
set ukern_trace 8 buffer 100000000
set ukern_trace 8 level detail
debug jnh inline-ka
```

**FW Filter示例**:
```
set firewall family inet filter bfd term 1 from protocol udp
set firewall family inet filter bfd term 1 from port 3784
set firewall family inet filter bfd term 1 then count bfd_in
set firewall family inet filter bfd term 1 then accept
```

**Daemon Live Core**:
```
start shell user root
ps -aux | grep bfd
gcore -s -c /var/tmp/bfd-jtac.core.0 $bfd_pid
```

**注意**: BFD端口号为UDP 3784

---

### 1.8 PIM (Protocol Independent Multicast)

**平台**: JunOS传统/通用

**关键排错命令**:
```
show configuration protocols pim
show configuration routing-instances <> protocols pim
show pim join detail                                                # 检查Join状态
show multicast route extensive                                      # 检查组播路由状态(pps)
show interfaces pd-*                                                # 检查隧道接口
show configuration chassis | display set | match tunnel-services    # 检查通道服务
```

**排错步骤**:
1. 确认是新配置还是现网问题
2. 确定每台路由器角色：Source DR / RP / Transit / Receiver DR
3. Source DR和RP必须能将组播报文封装为单播PIM消息
4. 从Source DR开始排查:
   - 如果组播源地址不在入接口所在网段，需要`accept-remote-source`
   - 入接口防火墙filter可计数、记录、镜像入站组播流量
   - 应有Join状态(`show pim join detail`)
   - 流量转发时应有组播路由状态显示pps(`show multicast route extensive`)
5. 确认每台路由器有到组播源的路由，且TTL值足够大

---

### 1.9 MSDP

**平台**: JunOS传统/通用

**关键排错命令**:
```
show configuration protocols msdp
show msdp source-active
show msdp detail
show msdp statistics
```

**排错步骤**:
1. 检查配置是否为新建
2. 用ping验证主机间连通性
3. 验证RP有隧道接口接收来自Source DR的隧道组播流量: `show interfaces pd-*`
4. 检查MSDP源活跃消息和统计信息
5. 启用traceoptions

---

### 1.10 VRRP

**平台**: JunOS传统/通用

**关键信息**:
- VRRP PDU: SMAC = 00:00:5e:00:01:<GROUP ID>, DMAC = 01:00:5e:00:00:12
- SIP = Master物理IP, DIP = 224.0.0.18 (0xe0000012)

**排错要点**:
1. **Master/Master冲突**: 检查物理IP、VIP、优先级、group配置
2. **基本IP可达性**: ARP是否已解析？ping物理IP和VIP成功？
3. **VRRP TX/RX**: Master是否发送VRRP报文？Backup是否收到？检查接口和lo0的过滤
4. **流量丢失**: 主机GW应为VIP/VMAC，检查VIP MAC filter (mfilter)编程

**重要限制**:
- 同一IFD下不同IFL应配置不同的vrrp-group，避免转发问题（irb不受此限制）
- MAC filter目前按IFD维护，JunOS 17.3R1开始，如果network-services配置为enhanced-ip模式，可对多个VRRP会话使用同一group ID
- 出向filter无法计数VRRP PDU (PR1630058)
- 如果之前作为物理IP的地址现在变为VIP，需要分两次commit

---

## 二、二层/交换协议

### 2.1 LACP 🔥 (ACX7024X ae2成员口问题重点)

**平台**: JunOS传统/MX(PFE)/PTX(PFE)/AFT平台 (命令有差异)

**LACP报文速率**: Fast rate = 1秒, Slow rate = 30秒

**关键排错命令 (RE)**:
```
show lacp interfaces                                               # 查看LACP状态
show lacp statistics interfaces                                     # LACP统计
show lacp timeouts
show interfaces <ae> extensive
show ppm adjacencies summary
show ppm interfaces detail
show ppm adjacencies detail
```

**LACP MUX状态机**:
| 状态 | 含义 |
|---|---|
| DETACHED | LACP未为链路选择聚合器。如果LACP检测到配置不匹配，链路不参与流量 |
| WAITING | LACP已选择聚合器，等待该聚合器所有其他链路加入(2秒等待) |
| ATTACHED | 中间状态：本端就绪，等待对端信号才能启用流量 |
| COLLECTING_DISTRIBUTING | 工作状态，双方就绪，链路参与流量转发 |

**调试方法**:
1. **稳定状态检查**: `show lacp interfaces` → MUX State应为 **Collecting distributing**，Receive State应为 **Current**
2. **配置不匹配(LACP down)**: MUX State = Detached, Receive = Current → 检查成员口到AE映射，双方是否一致
3. **对端未就绪**: MUX State = **Attached** → 本端就绪但对端未就绪
4. **LACP PDU未收到**: 检查Receive State → 不是Current表示LACP模块未收到PDU

**PFE级别命令(MX)**:
```
show ppm statistics protocol lacp                                  # 检查LACP报文是否到达PPMAN
show pfe statistics traffic                                        # 查看PFE本地协议统计
show mtip-cge summary
show mtip-cge X statistics
```

**PTX平台PFE命令**:
```
show pechip trapstats
show pechip pgq_stats
debug cos halp show drop_voqs chip <#>
show ddos policer all stats terse
show halp-pkt agg-cpc-stats
show halp-pkt stats
```

**AFT平台PFE命令**:
```
show ppm adjacencies protocol lacp detail
show ppm control protocol lacp session receive iflIndex <idx> clientId <id>
show ppm processor protocol lacp session receive <ifl_index>
show ppm ports
show host-path ports
show host-path network layer2 ethernet
```

**LACP分布式PPM控制**:
- 禁用分布式: `set protocols lacp ppm centralized`
- 启用分布式: `delete protocols lacp ppm centralized`

**ACX7024X ae2排错要点**:
- 检查 `show lacp interfaces ae2` 查看成员口MUX状态
- 如果卡在Detached → 检查成员口AE映射和对端配置是否一致
- 如果卡在Attached → 对端未就绪，检查对端状态
- 如果卡在Waiting → 链路保护场景，等待其他链路加入
- 检查 `show ppm statistics protocol lacp` 确认LACP报文是否到达PPMAN
- 检查 `show pfe statistics traffic` 确认LACP报文是否到达ukern
- 如果LACP RX不增长 → 底层链路可能有问题
- 排查步骤: `show lacp traceoptions` + `set protocols lacp ppm centralized` + tcpdump抓LACP报文

---

### 2.2 MC-LAG

**平台**: JunOS传统 (MX/TRIO)

**关键排错命令**:
```
show lacp interfaces
show iccp
show interfaces mc-ae id <id>
show bridge mac-table
show l2-learning redundancy-groups remote-macs
show l2-learning instance extensive

# Traceoptions
set protocols iccp traceoptions flag all
set protocols lacp traceoptions flag all
```

**PFE级别命令**:
```
show jnh if X input
show jnh if X output
show jnh X exceptions
show l2mtro 0 mac 0x4 0 XXXXXXXX
show bridge-domain
show bridge-domain entry <bd index in hex>
show bridge-domain irb <bd index in hex>
show l2metro 0 mac hw bridge-domain <>
```

---

### 2.3 Bridging (桥接)

**平台**: JunOS传统/通用

**Service Provider风格配置**:
```
set interfaces xe-4/0/2 flexible-vlan-tagging
set interfaces xe-4/0/2 encapsulation flexible-ethernet-services
set interfaces xe-4/0/2 unit 1400 encapsulation vlan-bridge
set interfaces xe-4/0/2 unit 1400 vlan-id 140
set bridge-domains v1400 vlan-id 1400
set bridge-domains v1400 interface xe-4/0/2.1400
```

**Enterprise风格配置**:
```
set interfaces ge-0/0/0 unit 0 family bridge interface-mode access vlan-id 100
set bridge-domains v100 vlan-id 110
```

**IRB接口配置**:
```
set interfaces irb unit 1400 family inet address 104.203.108.100/22
set bridge-domains v1400 routing-interface irb.1400
```

**常见问题**:

1. **Transit Packet Loss**: 使用bridge filter和irb inet filter定位丢包
2. **Host Bound Traffic Loss**: DHCP/IGMP snooping可能异常丢弃报文，需检查snooping绑定的builtin filter
3. **IRB Down**: 检查irb是否关联L2域(BD/VPLS/EVPN)，L2域是否有UP/UP的接口，STP是否将接口置为discarding
4. **MAC地址未学习**: 应用bridge filter + l2-learning traceoptions
5. **MAC地址漂移**: 通常表示二层环路。短期方案是禁用冗余链路

**关键CLI命令**:
```
show interfaces irb terse
show bridge domain
show bridge mac-table
show bridge statistics
show bridge flood
show spanning-tree interface
show l2-learning mac-move-buffer
show l2-learning global-information
show route forwarding-table family bridge bridge-domain <name>
show arp no-resolve | match <vlan/interface>
```

**PFE命令**:
```
show bridge-domain
show l2 manager mac-address <> bridge-domain <> learn-vlan <>
show route bridge table index <>
show topology nhdb id <>
show nhdb id <> recursive
show l2metro <> bridge-domain <>
```

**注意**: tcpdump在bridge/irb上需要同时在L2和L3接口上抓包:
```
monitor traffic interface ae1.x no-resolve size 1500 layer2-headers
monitor traffic interface irb.x no-resolve size 1500 layer2-headers
```

---

### 2.4 Layer 2 VPN

**平台**: JunOS传统/通用

**关键排错命令**:
```
ping mpls l2vpn <fec129/instance/interface>
show bgp summary
show l2vpn connections
show route table mpls.0
show route table <RI>.l2vpn.0 protocol bgp detail
show route table <RI>.l2vpn.0
show route label <label>
```

---

### 2.5 L2circuit

**平台**: JunOS传统/通用

**关键排错命令**:
```
# 验证LDP/RSVP状态
show ldp neighbor
show ldp session
show ldp database session <IP>
show rsvp neighbor
show rsvp session

# 检查转发
show l2circuit connections extensive
show route table inet.3
show route table mpls.0
show route forwarding-table family mpls
show route forwarding-table ccc <interface name>
```

---

### 2.6 VPLS

**平台**: JunOS传统/通用

**关键排错命令 (L2ALD)**:
```
show route <instance> DVBC detail
show krt table <instance-table> detail
show l2-learning global-information
show l2-learning global-mac-count
show l2-learning mac-move-buffer
show bridge mac-table bridge-domain <name>
show bridge domain brief
show bridge flood bridge-domain <name>
show vpls mac-table instance <name>
show vpls flood instance <name>
show route forwarding-table family bridge bridge-domain <name>
show route forwarding-table family vpls table <>
```

**PFE MAC地址编程检查**:
```
show bridge-domain
show l2 manager mac-address <> bridge-domain <> learn-vlan <>
show route bridge table index <>
show topology nhdb id <>
show route hw nhs <>
show nhdb id <> recursive
show l2metro <> bridge-domain <>
show l2metro <> mac hw bridge-domain <>
```

**jnh ukern trace**:
```
show ukern_trace handle
set ukern_trace <id for JNH_PACKET> buffer 9999999
set ukern_trace <id for JNH_PACKET> level extensive
debug jnh packet tx
```

**Traceoptions**: 在BGP、LDP、VPLS RI和protocol l2-learning上启用

---

### 2.7 CFM (Connectivity Fault Management)

**平台**: JunOS传统/通用

**关键排错命令**:
```
show configuration protocols oam
show oam ethernet connectivity-fault-management ?

# 扩展CFM模式 (增强规模)
set enhanced-cfm-mode
```

**规模信息**: 默认支持8000 MEP和8000 MIP/chassis；启用增强模式后支持32000 MEP和32000 MIP/chassis

**Traceoptions**:
```
set protocols oam ethernet connectivity-fault-management traceoptions flag all
set protocols oam ethernet connectivity-fault-management traceoptions file cfm.log size 50m files 10
```

---

### 2.8 LFM (Link Fault Management)

**平台**: JunOS传统/通用

**关键命令**:
```
show oam ethernet link-fault-management
show oam ethernet link-fault-management detail
clear oam ethernet link-fault-management statistics
clear oam ethernet link-fault-management state   # 清除LFM状态，重启发现过程
```

**调试手段**: 测试remote-loopback进行故障隔离 (参考KB25055)

---

### 2.9 EVPN-VXLAN

**平台**: JunOS传统/AFT/通用

**关键RE命令**:
```
show evpn database extensive
show bridge evpn arp-table
show evpn arp-table
show evpn flood
show bridge flood
show route forwarding-table destination x.x.x.x
show route forwarding-table family bridge
show l2-learning vxlan-tunnel-end-point esi

# 按MAC/ESI/Ethernet Tag检查BGP通告/接收
show route advertising-protocol bgp x.x.x.x evpn-mac-address <mac>
show route advertising-protocol bgp x.x.x.x evpn-esi-value <esi>
show route receive-protocol bgp x.x.x.x evpn-mac-address <mac>

# L2上下文历史
show l2-learning context-history mac/mac-ip/mac-addr <address>
```

**PFE命令**:
```
show l2metro 0 mac sw bridge-domain x
show l2metro 0 mac hw bridge-domain x
show l2 manager mac-table routing-instance x
show l2 manager macip_ctxt_history
show l2 manager mac-ip
show ifl <ifl-#>
show nhdb id # extensive
show jnh 0 decode <hex word>
show bridge-domain
show jnh evpn split_horizon_table 0 <RTT-Index>
show jnh evpn mcnh_table 0
```

**sysctl命令 (EVO/Linux内核)**:
```
sysctl -w debug.vtep_log=1
sysctl -w debug.irb.irb_kernel_debug=1
sysctl -w net.link.ether.inet.arpfsm_debug=1
```

**Traceoptions**:
```
set protocols l2-learning traceoptions flag all
set protocols evpn traceoptions flag all
```

**Flex Filter匹配VXLAN封装流量**:
VXLAN包格式: Ethernet—IPv4—UDP—VXLAN—Ethernet—IPv4—payload
- 内部源IP在: layer-4 + byte-offset 42, bit-length 32
- 内部目的IP在: layer-4 + byte-offset 46, bit-length 32

**排错建议**:
1. 检查ARP是否已由主机解析
2. 如果不是，检查是否为proxy ARP问题
3. 检查type 2路由是否存在
4. 尝试禁用proxy ARP: `no-arp-suppression`
5. MAC漂移问题: 确保各PE使用不同的RD值

---

### 2.10 ARP

**平台**: JunOS传统/AFT/通用

**关键排错命令**:
```
show system queues
show arp no-resolve expiration-time
monitor traffic interface

# BSD shell (EVO/Linux内核)
sysctl -a | grep arp_max
sysctl net.link.ether.inet.arp_dump
```

**PFE命令**:
```
show filter
show filter index 17000 program
show ddos policer arp stats
show ttp statistics
show nhdb management resolve
show nhdb resolve throttle
show jnh 0 exceptions hbc policers
show mqchip 0 counters output stream 1151 queue 2
show ddos policer stats resolve
show nhdb id 746 detail
```

---

### 2.11 IPv6 NDP

**平台**: JunOS传统/通用

**消息类型**:
| Type | 名称 | 说明 |
|---|---|---|
| 133 | Router Solicitation | 主机请求路由器快速发送RA |
| 134 | Router Advertisement | 路由器定期或响应RS发送RA |
| 135 | Neighbor Solicitation | 请求目标链路层地址，同时提供自身地址 |
| 136 | Neighbor Advertisement | 响应NS或主动通告新信息 |

**NDP状态机**:
| 状态 | 说明 |
|---|---|
| DELAY | 邻接解析等待中，可能有流量发往该邻居 |
| INCOMPLETE | 地址解析进行中，链路层地址未知 |
| PROBE | 地址解析进行中，可能有流量发往该邻居 |
| REACHABLE | 在最近可达时间间隔内邻居可到达 |
| STALE | 邻居需要重新解析，可能有流量发往该邻居 |

---

## 三、三层VPN

### 3.1 L3VPN

**平台**: JunOS传统/通用

**控制平面检查**:
```
# 验证路由通告/接收
show bgp summary
show route receive-protocol bgp <peer> x.x.x.x
show route advertising-protocol bgp <peer> x.x.x.x
show route x.x.x.x table <vpn.inet.0>
show route x.x.x.x table <vpn.inet.0> extensive

# 检查底层MPLS路径
show mpls lsp <name> extensive
show rsvp session lsp <name>
show mpls statistics
traceroute mpls rsvp
traceroute mpls ldp
show ldp database session <ldp peer>
```

**转发平面检查**:
```
show route forwarding-table destination <x.x.x.x>
show route forwarding-table destination <x.x.x.x> extensive
show krt queue
```

**PFE报文走查**:
```
show nhdb id <>
show nhdb id <> extensive
show route ip prefix <>
show jnh <> exceptions terse
dmem capture to check if packet goes out
```

---

### 3.2 Rosen MVPN (Draft-Rosen)

**平台**: JunOS传统/通用

文档主要为PPT分享链接，核心排错内容较少。涉及Draft-Rosen MVPN的排错与配置。

---

### 3.3 NGMVPN (Next Generation MVPN)

**平台**: JunOS传统/通用

**MVPN模式**:
1. **SPT-Only (默认)**: 通过MVPN source-active路由学习活跃组播源
2. **RPT-SPT**: 需要配置，不直接支持接在PE上的接收者/源

**I-PMSI vs S-PMSI**:
- I-PMSI: 每个VPN信号一个P2MP LSP (Inclusive)
- S-PMSI: 可为每个selective tunnel配置单独的P2MP LSP (Selective)
```
set routing-instances mvpn provider-tunnel rsvp-te lsp-template default-template
set routing-instances mvpn provider-tunnel selective group 239.1.1.2/32 source 1.1.11.1/32
```

**BUD Node**:
- BUD PE同时有本地接收者并向下游转发MPLS报文
- `vrf-table-label` + `vt` 接口可避免BUD节点收到两份报文副本
```
set interfaces vt-0/0/0 unit 0 family inet
set interfaces vt-0/0/0 unit 0 family mpls
set routing-instances mvpn interface vt-0/0/0.0 multicast
```

**排错命令**:
```
show pim interface instance <instance-name>
show pim join extensive instance <instance-name>
show pim rps details instance <instance-name>
show pim neighbor instance <instance-name>
show multicast route extensive instance <instance-name>
show route table <instance-name>.inet.0
show route table <instance-name>.mvpn.0
show mpls lsp p2mp extensive
show rsvp session p2mp extensive
show bgp summary
show mvpn instance <RI> inet
show mvpn neighbor instance-name <RI>
```

**发送测试组播流量**:
```
ping 224.7.7.7 bypass-routing interface ge-0/0/1 ttl 100
```

---

## 四、接口/光模块

### 4.1 SFPs (光模块排错)

**平台**: JunOS传统/MX/MPC系列 (不同MPC命令有差异)

**RE层面命令**:
```
set system syslog file messages kernel any
set system syslog file messages any any
set interfaces <ae> traceoptions flag all
show interfaces diagnostics optics et-2/0/1
show interfaces extensive et-2/0/1
```

**MPC PFE命令**:
```
show mtip-chmac summary
show mtip-chmac X registers
show mtip-chmac X intr-registers
show mtip-chmac X statistics-err
show mtip-chmac X statistics
show mtip-chpcs X errors
show mtip-chpcs X fec_info
show mtip-chpcs X link-status
show qsfp list
show qsfp X info
show qsfp X diagnostics
show qsfp X alarms
show cfp list
show cfp <#> alarms
show cfp <#> diagnostics
```

**MPC11 PFE命令**:
```
show aftulcd event_list
show picd channel summary
show picd channel fpc <slot> pic <slot> port <port> chan <0-3>
show picd optics cmd diagnostics fpc_slot <slot> pic_slot <slot> port <port>
show picd optics cmd info fpc_slot <slot> pic_slot <slot> port <port>
show picd optics cmd alarm fpc_slot <slot> pic_slot <slot> port <port>
show picd optics cmd enh_diagnostics fpc_slot <slot> pic_slot <slot> port <port>
```

**注意**: 各MPC类型使用的PHY芯片不同，命令有差异。

---

### 4.2 MACSEC

**平台**: JunOS传统/通用

**关键排错命令**:
```
show security macsec connections
show security mka sessions
show security macsec statistics
show security mka statistics
show security mka statistics interface <interface-name>
show security macsec statistics interface <interface-name> detail
```

**排错字段**: 
- `Interface State: Secured - Primary` 表示MKA会话正常
- `Outgoing packet number` 持续增长表示正常加密发送
- MKA统计中不应有 `ICV mismatch` / `Version mismatch` / `CAK mismatch`

---

### 4.3 PTP (Precision Time Protocol)

**平台**: JunOS传统/AFT (ACX与MX能力不同)

**关键排错命令**:
```
show ptp lock-status detail                         # 锁定状态应为 PHASE ALIGNED (State 5)
show ptp master detail                              # 验证主设备可达性
show ptp statistics detail                          # 确认收发计数增长(Stream 0-3为本地备份设备)
show ptp global-information
show ptp clock detail
show ptp slave detail
show ptp port detail
show ptp slave interface <> detail
```

**Firewall Filter匹配PTP报文**:
```
set firewall family inet filter ptp-to-GM term 1 from source-port 319
set firewall family inet filter ptp-to-GM term 1 from source-port 320
```

PTP报文偏移匹配: byte-offset 48, bit-length 8
- 0x0b = Announce报文
- 0x0 = Sync报文

**ACX与MX的PTP差异**: ACX系列有hybrid mode，具体参考Junos文档

**调试步骤**:
1. 锁定状态应为PHASE ALIGNED
2. 验证到主设备路由可达: `ping`, `show route forwarding-table`
3. 检查统计计数是否增长
4. 配置防火墙filter匹配PTP报文进行计数
5. 如无法隔离，禁用备份接口 + `restart clksyncd-service immediately`
6. 最后手段: 双RE重启
7. 无traceoptions可用，需在PFE中debug: `debug clksync manager ptp all debug`

**重要参考**: KB36504 (PFE级别命令列表), KB36531 (PTP行为概述)

---

### 4.4 COS (Class of Service)

**平台**: JunOS传统/通用

**关键排错命令 (RE)**:
```
show interfaces queue <interface> egress
show class-of-service interface <interface> detail
show class-of-service interface <interface> comprehensive
show class-of-service traffic-control-profile <name>
show class-of-service scheduler-map <name>

# Traceoptions
set class-of-service traceoptions flag all
```

**PFE命令 (FPC shell)**:
```
show vbf flow <PFE flow id>
show cos ifl-entry <ifl index> 1
show cos scheduling-policy <sched map id>
show cos halp ifd <ifd index> 1
show cos halp ifd queue-stats <ifd index> 1
show cos halp ifl <ifl index> 1
show cos halp ifl queue-stats <ifl index> 1
show qxchip <pfe id> driver
show qxchip <pfe id> counters
show qxchip <pfe id> 1 l3 <l3 index>
show qxchip <pfe id> q stats <q index>
show qxchip <pfe id> q <q index> queue-length
show qxchip <pfe id> q <q index> extensive
show qxchip <pfe id> memory
```

**ukern trace**: 检查COS和COS_halp的handle ID:
```
show ukern_trace handles
set ukern_trace <> level extensive
set ukern_trace <> logging enable
set ukern_trace <> printf enable
```

---

## 五、虚拟化/其他

### 5.1 cRPD (Containerized RPD)

**平台**: cRPD/Linux (容器化部署)

**部署步骤**:
```
# 安装Docker (Ubuntu 18.04)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
apt install docker-ce

# 加载cRPD镜像
docker load -i junos-routing-crpd-docker-21.3R1.9.tgz

# 创建持久化存储卷
docker volume create crpd01-config
docker volume create crpd01-varlog

# 启动容器(bridged模式)
docker run --rm --detach --name crpd01 -h crpd01 --net=bridge --privileged \
  -v crpd01-config:/config -v crpd01-varlog:/var/log -it crpd:21.3R1.9

# 启动容器(host网络模式，可连接Ixia)
docker run --rm --detach --name crpd03 -h crpd03 --net=host --privileged \
  -v crpd03-config:/config -v crpd03-varlog:/var/log -it crpd:21.3R1.9
```

**管理命令**:
```
docker exec -it crpd01 cli                                   # 访问cRPD CLI
docker exec -it crpd01 bash                                  # 访问bash
docker ps                                                    # 列出运行中容器
docker stats                                                 # 资源使用统计
docker [pause | resume | stop | rm] crpd01                   # 生命周期管理
```

**cRPD限制**: CLI不支持配置接口family和地址(IPv4/IPv6/MPLS除ISO外)，需在Linux shell中管理:
```
ip link show
ip addr show
ip addr add <ip>/<prefix> dev <interface>
ifconfig <interface> up/down
ip monitor link
```

**cRPD核心转储调试**:
```
jdebug crpd01.rpd.core.<timestamp>-<pid>-<num>.gz
```

---

### 5.2 vMX

**平台**: vMX (虚拟机形态MX)

**注意**: 文档主要为链接参考，具体排错步骤有限。作为虚拟化平台，vMX在功能上与物理MX一致，但性能受限。

---

### 5.3 vRR (Virtual Route Reflector)

**平台**: vRR (虚拟路由反射器)

**注意**: 文档主要为参考。vRR专门用于BGP路由反射，不转发数据平面流量。

---

### 5.4 MX-VC (MX Virtual Chassis)

**平台**: MX-VC (MX虚拟集群)

**注意**: 文档主要提供VC场景下的排错参考。

---

### 5.5 Node Slicing

**平台**: JunOS EVO (ACX7000系列)

**注意**: Node Slicing是EVO架构特性。文档可能提供节点切分相关排错信息。

---

### 5.6 BTI Troubleshooting

**平台**: 通用

**注意**: BTI(前身BTI Systems)相关排错。可能涉及光传输/时间同步相关内容。

---

### 5.7 CIENA GPON (TIBIT)

**平台**: CIENA/TIBIT (Juniper合作伙伴)

**注意**: CIENA GPON ONT相关排错文档。

---

### 5.8 SFLOW

**平台**: JunOS传统/通用

**配置示例**:
```
set protocols sflow agent-id 10.85.162.98
set protocols sflow polling-interval 20
set protocols sflow adaptive-sample-rate 5000
set protocols sflow source-ip 10.85.162.98
set protocols sflow collector 10.85.211.108 udp-port 6343
set protocols sflow interfaces et-0/0/0.99
```

**sflowTool (数据包解码)**:
```
# 安装
wget http://www.inmon.com/bin/sflowtool-3.22.tar.gz
tar -xvzf sflowtool-3.22.tar.gz
cd sflowtool-3.22 && ./configure && make && make install

# 使用
sflowtool -p 6343                                         # 格式化输出
sflowtool -p 6434 -l                                      # 逐行输出
sflowtool -p 6343 -c collector.mysite.com -d 9991         # 转发NetFlow v5
```

---

## 附：ACX7024X ae2成员口问题专项排查 (LACP)

基于LACP排错文档，针对ACX7024X的ae2成员口问题，推荐排查路径:

**Step 1: 查看LACP状态**
```
show lacp interfaces ae2
```
- 检查MUX State: 期望为 `Collecting Distributing`
- 检查Receive State: 期望为 `Current`

**Step 2: 识别问题类型**
- MUX=Detached, Recv=Current → **配置不匹配**，检查两端成员口到AE映射
- MUX=Attached → **对端未就绪**，检查对端设备
- MUX=Waiting → **链路保护等待中**
- Recv≠Current → **LACP PDU未收到**

**Step 3: 检查LACP统计**
```
show lacp statistics interfaces ae2
show ppm statistics protocol lacp                        # PFE层面确认报文是否到达
show pfe statistics traffic                              # 确认LACP报文是否到ukern
```

**Step 4: 启用集中式PPM调试**
```
set protocols lacp ppm centralized                       # 禁用分布式PPM
set protocols lacp traceoptions flag all
set protocols lacp traceoptions file lacp.log size 100m
```

**Step 5: 抓包检查**
```
monitor traffic interface ae2
```
确认对端是否在发送LACP报文，检查报文内容是否有误。

---

## 平台标识速查表

| 标识 | 适用范围 |
|---|---|
| **JunOS传统** | 经典JunOS CLI，传统PFE架构(MX/PTX/QFX/EX等) |
| **JunOS EVO** | EVO架构(ACX7000系列) |
| **AFT** | 高级转发架构(MX中MPC11E等) |
| **BRCM** | Broadcom芯片平台(部分ACX/QFX) |
| **TRIO** | Trio芯片组(MX系列) |
| **通用** | 跨平台适用的命令/概念 |
| **cRPD** | 容器化RPD(Linux) |
