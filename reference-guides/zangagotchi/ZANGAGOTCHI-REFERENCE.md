# zangagotchi Reference Guide — Wi-Fi Recon Unit

**Codename:** zangagotchi · zangichi  
**Hardware:** Raspberry Pi Zero 2W · Waveshare 2.13" e-ink HAT v3 · Alfa USB WiFi  
**Firmware:** Pwnagotchi (DrSchottky fork v1.5.6-beta2 — required for Waveshare v3)  
**Role:** Autonomous Wi-Fi handshake capture · passive recon · field recon unit  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **Status** | LIVE — Hunting ✅ |
| **Display** | Waveshare 2.13" e-ink v3 (waveshare_3) |
| **Default IP (USB)** | 10.0.0.2 |
| **Mac USB interface IP** | 10.0.0.1 |
| **Default user** | pi |
| **Default password** | raspberry (CHANGE THIS) |
| **Handshakes dir** | /root/handshakes/ |
| **Mode** | AUTO (hunting) |

---

## First Boot — Day 1 Stats

- APs seen: 29 active / 71 total in first 2 minutes
- Handshakes captured: 2 in first 2 minutes
- Found another pwnagotchi nearby (SETUP-9192) — attempted peer sync

---

## SSH Access (USB cable)

**Requires data-capable micro USB cable (not charge-only)**

```bash
# Step 1 — plug into DATA port (not power port), assign Mac interface
# Mac: System Settings → Network → USB interface → Manual
# IP: 10.0.0.1 / Mask: 255.255.255.0 / Gateway: 10.0.0.1

# Step 2 — SSH in
ssh pi@10.0.0.2
# password: raspberry (change immediately)
```

---

## config.toml

Location: boot partition of SD card (Fat32, 256MB)

```toml
main.name = "zangagotchi"
main.lang = "en"
main.whitelist = [
  "YourHomeSSID"
]

main.plugins.grid.enabled = true
main.plugins.grid.report = true
main.plugins.grid.exclude = [
  "YourHomeSSID"
]

ui.display.enabled = true
ui.display.type = "waveshare_3"
ui.display.color = "black"
```

---

## Display Reading

```
CH 6  APS 29 (71)          UP 00:02:01
zangagotchi>
  ( ●_● )
PWND 2 (2) [CIA_Field_Office_321]    AUTO ○
```

| Field | Meaning |
|---|---|
| CH | Current Wi-Fi channel being scanned |
| APS X (Y) | X active APs / Y total seen |
| UP | Uptime |
| PWND X (Y) | X handshakes this session / Y total ever |
| [...] | Last network seen |
| AUTO / MANU | Mode — AUTO = hunting, MANU = manual/USB |

---

## Pull Handshakes to Mac

```bash
# Via USB (10.0.0.2)
rsync -av pi@10.0.0.2:/root/handshakes/ ~/zangbot/handshakes/

# Crack with hashcat (on zanmac-01 — GPU power)
hashcat -m 22000 ~/zangbot/handshakes/*.pcap wordlist.txt
```

---

## Field Deployment with zangkia

```
zangkia (Travel Router) broadcasts SSID
      ↓
zangagotchi connects to zangkia SSID for power/data
      ↓ (passive — no active transmission)
Hunts client Wi-Fi independently
      ↓
Handshakes sync to zangpachi via rsync
      ↓
Tunneled home to zanmac-01 via Tailscale
```

---

## Critical Notes

- **Use DrSchottky fork** — official pwnagotchi.ai image does NOT support Waveshare v3
- Image: `pwnagotchi-raspberrypi-os-lite-v1.5.6-beta2.zip`
- Display type must be `waveshare_3` in config — not `waveshare2in13_v3`
- Disconnect/reconnect after first boot (RSA key generation — ~10 min)
- Change default password immediately after first SSH
- Data stored in `/root/handshakes/` — pcap format

---

## TODO

- [ ] Change default password (raspberry → vault)
- [ ] Assign static IP or hostname
- [ ] Install Tailscale for wireless access
- [ ] Wire rsync → zangpachi pipeline
