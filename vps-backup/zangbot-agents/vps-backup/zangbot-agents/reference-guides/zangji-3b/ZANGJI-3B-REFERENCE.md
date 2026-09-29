# zangji-3b Reference Guide — Pi 3B Field Scout

**Codename:** zangji-3b  
**Hardware:** Raspberry Pi 3 Model B Rev 1.2 · 1GB RAM · 8GB SD  
**Role:** On-site scout — quick assessment, optional leave-behind for 1-2 weeks  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **Status** | LIVE ✅ |
| **OS** | Debian 13 Trixie (64-bit) |
| **CPU** | 4x ARM Cortex-A53 @ 1.2GHz |
| **RAM** | 1GB |
| **Storage** | 8GB SD — ~4GB free |
| **Local IP** | 192.168.5.123 (DHCP, zangetsu7) |
| **Tailscale IP** | 100.110.187.18 |
| **Username** | zangetsu |
| **Hostname** | zangji-3b |
| **Temp (idle)** | 49.4°C |

---

## Access

```bash
# From local network
ssh zangetsu@192.168.5.123

# From anywhere via Tailscale
ssh zangetsu@100.110.187.18
```

---

## Installed Tools

| Tool | Purpose |
|---|---|
| nmap 7.95 | Network/port scanning |
| tcpdump 4.99 | Packet capture |
| netdiscover | ARP-based host discovery |
| net-tools | ifconfig, netstat, etc |
| tailscale | VPN mesh — phones home automatically |

---

## Network Config

- **Auto-connects:** `zangetsu7` (home + zangkia travel router)
- **NIC:** DHCP — plug and play on any network
- **Tailscale:** Starts on boot, always reachable remotely

### Add client network on-site

```bash
# Over SSH, add client WiFi
sudo nmcli dev wifi connect "ClientSSID" password "ClientPassword"
# Tailscale kicks in automatically once internet is available
```

---

## Field Use

### Quick scan on arrival
```bash
# Discover hosts on client subnet
sudo netdiscover -r 192.168.1.0/24

# Full nmap scan
sudo nmap -sV -O 192.168.1.0/24 -oN /home/zangetsu/scan-$(date +%Y%m%d).txt
```

### Pull scan results remotely (from zanmac-01)
```bash
scp zangetsu@100.110.187.18:/home/zangetsu/scan-*.txt ~/zangbot/scans/
```

### Leave-behind checklist
- [ ] Connected to client network (`nmcli`)
- [ ] Tailscale shows online from zanmac-01
- [ ] Power source confirmed (USB wall adapter or PoE)
- [ ] SSH in from Tailscale IP to verify
- [ ] Set scan to run on cron if needed

---

## Comms Path

```
zangji-3b (client Wi-Fi)
      ↓ Tailscale (automatic)
zanmac-01 — SSH in, run scans, pull data remotely

If zangpachi also on-site:
zangji-3b ←→ zangpachi (local LAN)
      ↓
   both tunnel home independently via Tailscale
```

---

## Build Notes

- Flashed: Raspberry Pi OS Lite 64-bit via Pi Imager
- SSH key: zanmac-01 ed25519 deployed
- Credentials: saved to Bitwarden as `zangji-3b`
- Web Serial / sudo over SSH requires interactive terminal — always SSH in first
- 8GB card is tight but fine for Lite + tools (~4GB headroom)

---

## Roadmap

- [ ] Static DHCP reservation in UniFi (so IP never changes)
- [ ] Cron scan job for leave-behind mode
- [ ] Auto-push scan results to zangohana on schedule
- [ ] Upgrade to 32GB+ SD if storage becomes issue
