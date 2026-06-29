# Juniper Command Reference

> **Living document** — auto-populated from RSI file analysis.
> Monitors `~/Downloads/` for new RSI/support-info files and parses device info + commands.
> Last updated: 2026-06-14T01:14:49 UTC

---

## How This Works

RSI files downloaded to `~/Downloads/` are automatically scanned. The monitor extracts:
- **Device family** → PTX / MX / ACX
- **OS** → JunOS / JunOS-EVO / VMHost
- **Model & version** (from `show version`)
- **Commands used** (from the RSI output)
- **Scenario** (auto-detected from keywords in logs/configs)

---

## PTX Series

### JunOS

*No PTX JunOS devices analyzed yet. Drop RSI files into ~/Downloads/ and they'll appear here.*

### JunOS-EVO

*No PTX JunOS-EVO devices analyzed yet.*

### VMHost

*No PTX VMHost devices analyzed yet.*

---

## MX Series

### JunOS

*No MX JunOS devices analyzed yet.*

### JunOS-EVO

*No MX JunOS-EVO devices analyzed yet.*

### VMHost

*No MX VMHost devices analyzed yet.*

---

## ACX Series

### JunOS

*No ACX JunOS devices analyzed yet.*

### JunOS-EVO

*No ACX JunOS-EVO devices analyzed yet.*

### VMHost

*No ACX VMHost devices analyzed yet.*

---

## Quick Command Reference by Scenario

### Software Upgrade

| Product | OS | Commands |
|---------|----|----------|

### BGP Troubleshooting

| Product | OS | Commands |
|---------|----|----------|

### OSPF / ISIS

| Product | OS | Commands |
|---------|----|----------|

### Interface / Optics

| Product | OS | Commands |
|---------|----|----------|

### Hardware (FPC / PIC / RE)

| Product | OS | Commands |
|---------|----|----------|

### L3VPN

| Product | OS | Commands |
|---------|----|----------|

### EVPN / VXLAN

| Product | OS | Commands |
|---------|----|----------|

### MACsec

| Product | OS | Commands |
|---------|----|----------|

### Security / Firewall

| Product | OS | Commands |
|---------|----|----------|

### QoS / CoS

| Product | OS | Commands |
|---------|----|----------|

### MPLS / Traffic Engineering

| Product | OS | Commands |
|---------|----|----------|

### System Logging

| Product | OS | Commands |
|---------|----|----------|

### Routing Protocol (General)

| Product | OS | Commands |
|---------|----|----------|

### General Troubleshooting

| Product | OS | Commands |
|---------|----|----------|

### Configuration

| Product | OS | Commands |
|---------|----|----------|

---

## SSH Connection History

*Tracked from zsh history.*

| Timestamp | Host | Command |
|-----------|------|---------|
| 2026-05-31 | 192.168.31.172 (lyu) | `ssh lyu@192.168.31.172 "ls -latr ~/Downloads"` |
| 2026-05-31 | 192.168.31.172 (lyu) | `ssh lyu@192.168.31.172 "echo hello"` |
| 2026-05-31 | 192.168.31.172 (lyu) | `ssh lyu@192.168.31.172 "cat ~/Downloads/"` |
| 2026-05-31 | 192.168.31.172 (lyu) | `ssh lyu@192.168.31.172 "cat ~/Downloads"` |
| 2026-05-31 | 192.168.31.172 (lyu) | `ssh lyu@192.168.31.172 "cat ~/Downloads\"` |
