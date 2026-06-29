#!/usr/bin/env python3
"""Merge 6 JunOS EVO notes into one complete knowledge base."""
import os

def read_md(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_section(content, start_marker, end_marker=None):
    idx = content.find(start_marker)
    if idx == -1:
        return ""
    start = idx
    if end_marker:
        end = content.find(end_marker, start + len(start_marker))
        if end == -1:
            return content[start:]
        return content[start:end]
    return content[start:]

d = {
    '基础排错': read_md("/home/Lu/JunOS_EVO_Troubleshooting_Notes.md"),
    'LACP': read_md("/home/Lu/LACP_AE_TTrace_JunOS_EVO_Notes.md"),
    '芯片架构': read_md("/home/Lu/芯片架构结构化笔记.md"),
    'ACX平台': read_md("/home/Lu/ACX_Platform_Notes.md"),
    'EVO排错': read_md("/home/Lu/EVO_Troubleshooting_Notes.md"),
    '已知问题': read_md("/home/Lu/text_extracts/known_issues_notes.md"),
}

output = []
output.append("# Juniper JunOS EVO 完整知识库\n")
output.append("> 来源：SharePoint 内部知识库（ACX-EVO-PAGE / JTAC Jump Station / 各芯片架构文档）")
output.append(f"> 合并日期：2026-06-27")
output.append(f"> 总源文件数：~73个\n")
output.append("---\n")
output.append("## 目录\n")

toc_items = [
    ("一、基础运维与数据收集", "01-基础运维"),
    ("二、Shell访问方法", "02-shell访问"),
    ("三、节点与应用调试", "03-节点应用"),
    ("四、LACP与聚合接口排错", "04-lacp-ae"),
    ("五、L2VPN排错", "05-l2vpn"),
    ("六、L3排错", "06-l3"),
    ("七、L3VPN排错", "07-l3vpn"),
    ("八、LDP标签验证", "08-ldp"),
    ("九、FPC硬件排错", "09-fpc"),
    ("十、接口与光模块排错", "10-接口光模块"),
    ("十一、Hostpath主机路径排错", "11-hostpath"),
    ("十二、Traces应用跟踪", "12-traces"),
    ("十三、TTrace与包捕获", "13-ttrace"),
    ("十四、ACX平台指南", "14-acx平台"),
    ("十五、芯片架构参考", "15-芯片架构"),
    ("十六、Junos Fusion", "16-junos-fusion"),
    ("十七、Jflow/Sflow", "17-jflow-sflow"),
    ("十八、CMError知识库", "18-cmerror"),
    ("十九、ACX7100 EVO排错指南", "19-acx7100-evo"),
    ("二十、已知问题与限制", "20-已知问题"),
    ("二十一、排错通用流程", "21-排错流程"),
    ("附录A：PFE命令速查表", "appendix-a-pfe"),
]
for title, anchor in toc_items:
    output.append(f"  - [{title}](#{anchor})")
output.append("\n---\n")

# Section 1
output.append("## 一、基础运维与数据收集\n{: #01-基础运维}\n")
for marker in ["## 2. Basic Data Collection", "## 12. request system debug-info", "## 6. Journalctl"]:
    seg = extract_section(d['基础排错'], marker, "## 7." if "Journalctl" in marker else "## 3." if "Basic" in marker else "## 13.")
    if seg:
        output.append(seg)
    # 检查是否已经包含了下一个标题，避免重复
    if len(output) > 2 and "## 5." in seg:
        break

# Section 2
output.append("## 二、Shell访问方法\n{: #02-shell访问}\n")
seg = extract_section(d['基础排错'], "## 1. Accessing Shells", "## 2.")
if seg: output.append(seg)
seg = extract_section(d['EVO排错'], "## 2. Shell登录方法汇总", "## 3.")
if seg: output.append(seg)

# Section 3
output.append("## 三、节点与应用调试\n{: #03-节点应用}\n")
seg = extract_section(d['基础排错'], "## 4. Debugging Nodes", "## 5.")
if seg: output.append(seg)

# Section 4 - LACP
output.append("## 四、LACP与聚合接口排错\n{: #04-lacp-ae}\n")
output.append("### 4.1 LACP traceoptions（EVO无传统traceoptions）\n")
seg = extract_section(d['LACP'], "### 1.1", "### 1.3")
if seg: output.append(seg)
seg = extract_section(d['LACP'], "### 1.3", "### 1.4")
if seg: output.append(seg)
seg = extract_section(d['LACP'], "### 1.4", "## 二、")
if seg: output.append(seg)
output.append("### 4.2 PFE层面查看LACP成员口\n")
seg = extract_section(d['LACP'], "## 二、", "## 三、")
if seg: output.append(seg)
output.append("### 4.3 ae成员口不完整排查步骤\n")
seg = extract_section(d['LACP'], "## 三、", "## 四、")
if seg: output.append(seg)

# Section 5-10
sections = [
    ("五、L2VPN排错", "05-l2vpn", "## 7. L2VPN", "## 8."),
    ("六、L3排错", "06-l3", "## 8. L3 Troubleshooting", "## 9."),
    ("七、L3VPN排错", "07-l3vpn", "## 9. L3VPN", "## 10."),
    ("八、LDP标签验证", "08-ldp", "## 10. LDP Label Walk", "## 11."),
    ("九、FPC硬件排错", "09-fpc", "## 15. Troubleshooting FPC", "## 16."),
    ("十、接口与光模块排错", "10-接口光模块", "## 16. Troubleshooting Interfaces", ""),
]
for title, anchor, start, end in sections:
    output.append(f"## {title}\n{{: #{anchor}}}\n")
    seg = extract_section(d['基础排错'], start, end)
    if seg: output.append(seg)

# Section 11 - Hostpath
output.append("## 十一、Hostpath主机路径排错\n{: #11-hostpath}\n")
seg = extract_section(d['基础排错'], "## 5. Hostpath Commands List", "## 6.")
if seg: output.append(seg)
seg = extract_section(d['基础排错'], "## 13. SE-CDO-036", "## 14.")
if seg: output.append(seg)
seg = extract_section(d['EVO排错'], "## 7. Hostpath架构总结", "## 8.")
if seg: output.append(seg)

# Section 12 - Traces
output.append("## 十二、Traces应用跟踪\n{: #12-traces}\n")
seg = extract_section(d['基础排错'], "## 14. Traces", "## 15.")
if seg: output.append(seg)

# Section 13 - TTrace
output.append("## 十三、TTrace与包捕获\n{: #13-ttrace}\n")
seg = extract_section(d['LACP'], "## 四、", "")
if seg: output.append(seg)

# Section 14 - ACX Platform (summary)
output.append("## 十四、ACX平台指南\n{: #14-acx平台}\n")
output.append("> 完整内容见源文件 `ACX_Platform_Notes.md`（997行）\n\n")
for ch in ["VXLAN", "端口镜像", "ACX2K", "ACX5448", "CoS", "平台限制"]:
    seg = extract_section(d['ACX平台'], f"## {ch}", "## ")
    if seg:
        lines = seg.split('\n')
        if len(lines) > 100:
            seg = '\n'.join(lines[:100]) + f"\n\n*（完整 {ch} 内容请参见 ACX_Platform_Notes.md）*\n"
        output.append(seg)

# Section 15 - Chip Arch (summary)
output.append("## 十五、芯片架构参考\n{: #15-芯片架构}\n")
output.append("> 完整内容见源文件 `芯片架构结构化笔记.md`（1025行）\n\n")
seg = extract_section(d['芯片架构'], "## 9. 芯片对比总结", "")
if seg:
    lines = seg.split('\n')
    if len(lines) > 200:
        seg = '\n'.join(lines[:200]) + "\n\n*（完整芯片对比请参见 芯片架构结构化笔记.md）*\n"
    output.append(seg)

# Section 16 - Junos Fusion
output.append("## 十六、Junos Fusion\n{: #16-junos-fusion}\n")
seg = extract_section(d['EVO排错'], "## 9. Junos Fusion排错", "## 10.")
if seg:
    lines = seg.split('\n')
    if len(lines) > 100:
        seg = '\n'.join(lines[:100]) + "\n\n*（完整 Junos Fusion 内容请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

# Section 17 - Jflow/Sflow
output.append("## 十七、Jflow/Sflow\n{: #17-jflow-sflow}\n")
seg = extract_section(d['EVO排错'], "## 11. Jflow/Sflow排错", "## 12.")
if seg:
    lines = seg.split('\n')
    if len(lines) > 80:
        seg = '\n'.join(lines[:80]) + "\n\n*（完整 Jflow/Sflow 内容请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

# Section 18 - CMError
output.append("## 十八、CMError知识库\n{: #18-cmerror}\n")
seg = extract_section(d['EVO排错'], "## 10. CMError知识库", "## 11.")
if seg:
    lines = seg.split('\n')
    if len(lines) > 120:
        seg = '\n'.join(lines[:120]) + "\n\n*（完整 CMError 列表请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

# Section 19 - ACX7100
output.append("## 十九、ACX7100 EVO排错指南\n{: #19-acx7100-evo}\n")
seg = extract_section(d['EVO排错'], "## 5. ACX7100 EVO排错", "## 6.")
if seg:
    lines = seg.split('\n')
    if len(lines) > 250:
        seg = '\n'.join(lines[:250]) + "\n\n*（完整 ACX7100 排错内容请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

# Section 20 - Known Issues
output.append("## 二十、已知问题与限制\n{: #20-已知问题}\n")
output.append("> 完整内容见源文件 `known_issues_notes.md`（797行）\n\n")
for ch in ["MPC10", "MX304", "EVO平台CVBC"]:
    seg = extract_section(d['已知问题'], f"## {ch}", "## ")
    if seg:
        lines = seg.split('\n')
        if len(lines) > 100:
            seg = '\n'.join(lines[:100]) + f"\n\n*（完整 {ch} 内容请参见 known_issues_notes.md）*\n"
        output.append(seg)

# Section 21 - Flow
output.append("## 二十一、排错通用流程\n{: #21-排错流程}\n")
seg = extract_section(d['EVO排错'], "## 14. 通用排错流程总结", "")
if seg:
    lines = seg.split('\n')
    if len(lines) > 100:
        seg = '\n'.join(lines[:100]) + "\n\n*（完整流程请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

# Appendix
output.append("---\n## 附录A：PFE命令速查表\n{: #appendix-a-pfe}\n")
seg = extract_section(d['EVO排错'], "## 8. PFE层面命令汇总表", "## 9.")
if seg:
    lines = seg.split('\n')
    if len(lines) > 150:
        seg = '\n'.join(lines[:150]) + "\n\n*（完整速查表请参见 EVO_Troubleshooting_Notes.md）*\n"
    output.append(seg)

final = '\n'.join(output)
out_path = "/home/Lu/knowledge/juniper-evo-complete-notes.md"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(final)

lines = final.count('\n')
print(f"OK 合并完成: {out_path}")
print(f"行数: {lines}, 大小: {len(final)/1024:.0f}KB")
