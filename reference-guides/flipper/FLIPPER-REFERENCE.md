# zanghara Reference Guide — Flipper Zero

**Codename:** zanghara  
**Hardware:** Flipper Zero · Unleashed firmware 093 · 32GB SD  
**Role:** Multi-Tool — RF, NFC, IR, GPIO, USB HID, Sub-GHz  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **Firmware** | Unleashed 093 |
| **SD Card** | 32GB |
| **Wi-Fi Dev Board** | ESP32 (looking for it) |
| **Primary partner** | zangpachi (Pi 5) via USB/GPIO |
| **Codename** | zanghara (tribute: Urahara) |

---

## Capabilities

| Feature | Use Case |
|---|---|
| Sub-GHz RF | Gate openers, keyfobs, sensors |
| NFC/RFID | Card reading, badge cloning (authorized testing) |
| IR | TV/device control, learning remotes |
| iButton | Key systems |
| USB HID | BadUSB payloads, keyboard emulation |
| GPIO | Connect to zangpachi for data bridge |
| Bluetooth | BLE scanning, advertising |

---

## Wi-Fi Dev Board (ESP32)

**Status:** Misplaced — hunting for it  

When found, enables:
- Wi-Fi scanning from Flipper
- Marauder firmware for Wi-Fi attacks (authorized testing)
- HTTP requests from Flipper
- Bridge to zangpachi over Wi-Fi

```
Flipper Zero (zanghara)
      ↓ GPIO / USB
ESP32 Wi-Fi Dev Board
      ↓ Wi-Fi
zangpachi (zangpachi)
      ↓ Tailscale
zanmac-01 (zanmac-01)
```

---

## Unleashed Firmware

Unleashed removes region locks and enables:
- Extended Sub-GHz frequencies
- Extra protocols
- Custom animations
- No OFW restrictions

Update via:
```
qFlipper desktop app → Install from file
OR
Flipper mobile app → Firmware update
```

---

## Connection to zangpachi

### USB Serial
```bash
# On zangpachi
ls /dev/ttyACM*     # Flipper shows as ttyACM0
screen /dev/ttyACM0 230400
```

### GPIO Bridge
- Flipper GPIO pins → Pi 5 GPIO header
- Enables: sensor data relay, RF trigger from Pi, combined field tool

---

## Field Use with zangpachi + zangkia

```
Client site:
  zanghara — Sub-GHz scan, NFC reads, IR capture
  zangpachi — network scan, data collection
  zangkia   — VPN tunnel home
      ↓
  All data syncs to zanmac-01 via Tailscale
```

---

## Storage — SD Card Layout

```
/SD/
  subghz/       — captured RF signals
  nfc/          — NFC card dumps  
  infrared/     — IR remotes
  badusb/       — HID payloads
  apps/         — installed apps
  music_player/ — tunes
```

---

## Legal / Ethics Note

All use is on authorized systems only — client networks with written permission or your own lab (192.168.5.0/24 home network). Flipper is a pentesting research tool, not for unauthorized access.

---

## Flashing Marauder — Lessons Learned

- Use **justcallmekoko.github.io/MarauderInstaller/** — select "Flipper Zero WiFi Dev Board"
- Requires **Chrome/Edge/Brave** — Web Serial API. Safari and Firefox won't work
- Mac defaults to Safari — flash from Windows PC with Chrome or install Chrome on Mac
- Board must be in **bootloader mode** before connecting:
  1. Hold BOOT button
  2. Press + release RESET
  3. Release BOOT
  - No lights in bootloader mode = normal ✅
- Mac sees it as `/dev/cu.usbmodemSN234567892` when in bootloader mode
- Flipper itself shows as `/dev/cu.usbmodemflip_O0td1` (separate device)
- Select `SN234567892` port in the browser popup — not the Flipper port
- Don't unplug during flash — takes 2-5 min

---

## TODO

- [ ] Find Wi-Fi dev board (ESP32)
- [ ] Install Marauder on dev board (Wi-Fi attacks, authorized only)
- [ ] Wire GPIO bridge to zangpachi
- [ ] Test USB serial link to zangpachi
- [ ] Document Sub-GHz captures from home lab
