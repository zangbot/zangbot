# zangpachi Reference Guide — Pi 5 Field Ops Agent

**Codename:** zangpachi · zangpachi  
**Hardware:** Raspberry Pi 5 8GB · Pironman 5 Pro Max case · 500GB NVMe  
**Role:** Field Ops Agent — first unit on-site, runs scans, tunnels data home  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **IP (LAN)** | 192.168.5.116 |
| **Tailscale IP** | 100.109.228.50 |
| **OS** | Debian 13 (trixie) |
| **Kernel** | 6.18.50 |
| **User** | zangetsulv |
| **RAM** | 8GB |
| **Storage** | 500GB NVMe (primary) + SD card (temp) |
| **Accelerator** | Hailo-8L AI accelerator |
| **Swap** | 2GB zram |
| **Network** | wlan0 — 192.168.5.116 |

---

## SSH Access

```bash
# From Mac (zanmac-01)
ssh zangetsulv@192.168.5.116

# Via Tailscale (anywhere)
ssh zangetsulv@100.109.228.50
```

**Note:** zangbot SSH key access was broken as of 2026-09-27 — use zangetsulv user.

---

## Services Running

| Service | Status | Notes |
|---|---|---|
| Tailscale | ✅ active | Always-on mesh VPN |
| Ollama | ✅ active | phi3:mini for local inference |
| SSH | ✅ active | Port 22 |

---

## Case — Pironman 5 Pro Max

- RGB LEDs: working ✅
- Fans: NOT spinning ❌ — needs case rebuild
- NVMe: 500GB installed ✅
- **Fix needed:** Reseat fan connector during case rebuild

---

## Field Ops Role

When deployed at a client site with zangkia (Travel Router):

```
Client Network
      ↓
   zangkia (Travel Router — isolated SSID + VPN)
      ↓
   zangpachi (physically on client LAN)
      ↓
   Scans: nmap, bettercap, passive recon
      ↓
   Data tunnels home via Tailscale → zanmac-01
```

### Scan Commands

```bash
# Network discovery
sudo nmap -sn 192.168.x.0/24

# Full port scan on target
sudo nmap -sV -p- <target-ip>

# Passive Wi-Fi recon (works alongside zangagotchi)
sudo bettercap -iface wlan0
```

---

## Sync — Handshakes from zangagotchi

```bash
# Pull handshakes from zangagotchi to zangpachi NVMe
rsync -av pi@10.0.0.2:/root/handshakes/ /mnt/nvme/handshakes/
```

---

## Known Issues / Pitfalls

- Fans not spinning — thermal risk under load until case is rebuilt
- zangbot SSH user key auth broken — use zangetsulv
- SD card is temporary boot medium — NVMe is primary storage
- tcpdump not installed by default

---

## Install Missing Tools

```bash
sudo apt install -y nmap tcpdump bettercap rsync
```
