# Zangbot Field Kit — Deployment Guide

**Version:** 1.0 · 2026-09-27  
**Kit Name:** Field Recon Package  

---

## Kit Composition

| Unit | Codename | Role | What It Sees |
|---|---|---|---|
| Raspberry Pi 3B | zangji-3b | Network recon + leave-behind | IP layer, ports, services, OS, vulns |
| Flipper Zero + ESP32-S2 | zanghara | RF/wireless layer | WiFi probes, deauth, sub-GHz, NFC/RFID |
| Wio Tracker x2 | zangizen | Off-grid mesh comms + GPS | LoRa mesh, position, off-grid messaging |
| UniFi Travel Router | zangkia | Network bridge | zangetsu7 SSID anywhere + VPN home |

---

## How They Work Together

```
CLIENT SITE
───────────────────────────────────────────────────────────
Client network / ethernet
        ↓
    zangkia (Travel Router)
        ↓                    ↓
  zangetsu7 SSID        Tailscale VPN → zanmac-01
        ↓
  zangji-3b ────── nmap/tcpdump ──────→ scan client LAN
  zanghara  ────── Marauder ──────────→ capture WiFi probes, RF signals
        ↓
  zangizen x2 ──── LoRa mesh ─────────→ off-grid comms back to you
  (node 1 in kit, node 2 at home/base)

OFF NETWORK / NO INTERNET
───────────────────────────────────────────────────────────
  zangizen LoRa mesh still works — range 1-10km
  Send text, GPS position, alerts back to base node
  No client WiFi, no internet required
```

---

## Deployment Checklist

### Before leaving home
- [ ] zangji-3b charged / SD card good
- [ ] zanghara charged, Marauder on ESP32 confirmed
- [ ] zangizen x2 charged, mesh tested (both nodes see each other)
- [ ] zangkia charged, zangetsu7 SSID broadcasting
- [ ] Tailscale showing all nodes online from zanmac-01
- [ ] Data cables confirmed (use cable tester — zanghara kit)
- [ ] Power bank(s) packed

### On arrival
```bash
# 1. Deploy zangkia — plug into client ethernet or bridge their WiFi
# 2. Connect zangji-3b to zangetsu7
# 3. Verify Tailscale from zanmac-01
ssh zangetsu@100.110.187.18 "tailscale status"

# 4. Run scout suite
sudo bash /home/zangetsu/scout.sh <client_subnet>

# 5. Deploy zangizen — leave one node, keep one
# 6. Use zanghara to walk the space — probe capture, sub-GHz scan
```

### If leaving zangji-3b behind
```bash
# Add client WiFi so he stays connected without zangkia
sudo nmcli dev wifi connect "ClientSSID" password "ClientPassword"

# Verify Tailscale reachable from home
ssh zangetsu@100.110.187.18 "uptime"

# Schedule recurring scan (runs every 6h)
echo "0 */6 * * * sudo bash /home/zangetsu/scout.sh <subnet> >> /home/zangetsu/scans/cron.log 2>&1" | crontab -
```

---

## What Each Unit Does On-Site

### zangji-3b — Network Layer
```
Sees:   All IP devices, open ports, services, OS versions
Tools:  nmap, tcpdump, netdiscover
Output: /home/zangetsu/scans/YYYYMMDD-HHMM/
Pull:   scp -r zangetsu@100.110.187.18:/home/zangetsu/scans/ ~/zangbot/scans/
```

### zanghara — RF / Wireless Layer
```
Sees:   WiFi probe requests (what devices are looking for)
        Deauth attacks / rogue APs
        Sub-GHz signals (garage doors, keyfobs, sensors)
        NFC/RFID cards (access control)
        IR signals (remotes, cameras)
Tools:  Marauder (ESP32-S2), Unleashed firmware
Output: Logged on Flipper SD card — pull via qFlipper
```

### zangizen — Off-Grid Comms Layer
```
Sees:   Other Meshtastic nodes (public mesh + your base node)
Does:   Send/receive text over LoRa (no internet)
        GPS position broadcast
        Alert you if zangji-3b goes offline (via serial bridge — future)
Range:  1-10km line of sight
```

### zangkia — Network Bridge
```
Does:   Broadcasts zangetsu7 SSID on-site
        VPN tunnel home to zanmac-01
        All your devices feel like home network
        zangji-3b auto-connects — no config needed
```

---

## Comms Priority (when internet is unavailable)

1. **Tailscale** — primary (needs internet)
2. **LoRa mesh (zangizen)** — backup (no internet needed, 1-10km)
3. **Local SSH** — last resort (on-site only, no remote)

---

## Power Budget (rough estimates)

| Unit | Runtime |
|---|---|
| zangji-3b | ~6-8h on 10,000mAh power bank |
| zanghara | ~24h+ (own battery) |
| zangizen | ~24h+ per node (own battery, 4.18V seen) |
| zangkia | Check travel router specs |

---

## Bag Pack List

```
[ ] zangji-3b + micro SD verified
[ ] USB-C power bank (10,000mAh+) for zangji-3b
[ ] Data-verified USB cable (test with cable tester)
[ ] zanghara (Flipper + ESP32-S2 attached)
[ ] zangizen x2 (both Wio Trackers, both charged)
[ ] zangkia (UniFi Travel Router + cable)
[ ] Ethernet cable (for zangkia → client switch)
[ ] USB cable tester (confirmed data cables only)
[ ] Small velcro / zip ties
```

---

## Roadmap

- [ ] zangpachi replaces or supplements zangji-3b for heavy scans
- [ ] zangizen serial bridge to zangji-3b — mesh alerts on Pi
- [ ] Automated scan → zangohana push on schedule
- [ ] Grafana dashboard on zanmac-01 pulling live from zangji-3b
- [ ] zangagotchi (zangichi) added to kit for passive WiFi handshake capture
