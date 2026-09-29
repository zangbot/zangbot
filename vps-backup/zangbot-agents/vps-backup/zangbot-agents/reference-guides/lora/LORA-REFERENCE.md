# zangizen Reference Guide — LoRa Mesh / Meshtastic

**Codename:** zangizen (tribute: Aizen)  
**Hardware:** Seeed Wio Tracker 1110 x2 · Meshtastic firmware  
**Role:** Sensor Mesh · Long-Range Off-Grid Communications · GPS tracking  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **Status** | LIVE ✅ |
| **Devices** | Wio Tracker x2 (Meshtastic) |
| **Nodes seen on first boot** | 19 online |
| **GPS** | 8 satellites locked ✅ |
| **Battery** | 4.19V (100%) |
| **Channel Utilization** | 9% — plenty of headroom |
| **Node ID** | Meshtastic 58c0 (58c0) |
| **Protocol** | Meshtastic (LoRa mesh, no internet required) |

---

## Day 1 Stats

- Powered on, GPS locked in minutes
- Saw **19 nodes online** on the public Meshtastic mesh in range
- Channel utilization only 9% — very healthy
- Both Wio Trackers up and meshing

---

## What Meshtastic Does

- **Off-grid mesh** — devices talk directly to each other via LoRa radio, no Wi-Fi, no internet
- **Range** — 1-10km line of sight, further with repeaters
- **GPS tracking** — each node broadcasts position
- **Text messaging** — send messages across the mesh
- **Encryption** — AES-256 by default
- **Public mesh** — other Meshtastic users in range are visible (19 already)

---

## Wio Tracker 1110 Pinout

USB-C for power and flashing. Built-in:
- LoRa radio (SX1262)
- GPS (L76K)
- Accelerometer
- RGB LED
- Temperature/humidity sensor
- Grove connectors for expansion

---

## Fleet Integration

```
zangizen (Wio Tracker 1) — home base node / gateway
      ↓ LoRa mesh
zangizen (Wio Tracker 2) — field roaming node
      ↓ (Meshtastic app)
zanmac-01 — monitor mesh via Meshtastic app / web client

Field deployment:
  Node 2 goes with zangpachi on-site
  Node 1 stays at home / base
  GPS positions visible on map
  Text comms over LoRa — no client Wi-Fi needed
```

---

## Meshtastic App Setup

```bash
# Web client (browser via USB)
# Connect Wio Tracker via USB-C
# Open: https://client.meshtastic.org
# Select device from serial port list

# Python CLI
pip install meshtastic
meshtastic --port /dev/ttyUSB0 --info
meshtastic --port /dev/ttyUSB0 --sendtext "zangizen online"
```

---

## Channel Configuration

Default channel: `LongFast` (public)  
For private comms between your nodes:

```bash
# Set private channel (do on both nodes)
meshtastic --port /dev/ttyUSB0 --ch-set name "zangmesh" --ch-set psk random --ch-index 0
# Note the generated PSK — set same on both devices
```

---

## Integration with zangpachi

```bash
# On zangpachi — read Meshtastic messages via serial
pip install meshtastic
python3 -c "
import meshtastic
import meshtastic.serial_interface
iface = meshtastic.serial_interface.SerialInterface('/dev/ttyUSB0')
print(iface.nodes)
"
```

This lets zangpachi receive GPS positions and mesh messages, then forward via Tailscale to zanmac-01.

---

## Roadmap

- [ ] Name both nodes (zangizen-1 / zangizen-2)
- [ ] Set private channel for internal comms
- [ ] Wire zangpachi serial → Meshtastic bridge
- [ ] GPS position feed to dashboard
- [ ] Deploy node 2 with zangpachi on field ops
- [ ] Test range — home → client site
