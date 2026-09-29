# zangichi Rebuild Guide — jayofelony v2.9.5.8
# Date: 2026-09-27
# Current: DrSchottky v1.5.6-beta2 (archived)
# Target: jayofelony v2.9.5.8 (active, Debian Trixie)

---

## Why Rebuild

DrSchottky's fork was archived January 2024. No more updates, no bug fixes,
no new plugin support. jayofelony picked up the torch and is the active
community-maintained fork as of 2025-2026.

---

## Pros & Cons

### Upgrading to jayofelony v2.9.5.8

| | |
|---|---|
| ✅ **Active development** | Bug fixes, bettercap updates, new plugins regularly |
| ✅ **bettercap 2.40.2** | Fixes crashes that caused zangichi to lock up |
| ✅ **Debian Trixie** | Same OS as zangpachi and zangji-3b — consistent fleet |
| ✅ **BT-Tether** | SSH over Bluetooth — no more USB cable circus to pull handshakes |
| ✅ **wpa-sec auto-upload** | Handshakes uploaded and cracked automatically when internet available |
| ✅ **aircrackonly** | Validates handshakes — deletes bad pcaps (no more 24-byte duds) |
| ✅ **hashie** | Auto-converts pcap → hashcat format on-device |
| ✅ **webcfg** | Change config from browser — no SSH needed for tweaks |
| ✅ **session-stats** | Graphs on e-ink display — see AI learning progress |
| ✅ **auto-backup** | Pushes handshakes somewhere when internet available |
| ✅ **wigle** | Maps captures geographically — see where handshakes were caught |
| ❌ **Fresh flash required** | Can't upgrade in-place from DrSchottky — new SD card |
| ❌ **Lose current model** | AI brain resets — zangichi starts learning from scratch |
| ❌ **Config rewrite** | config.toml needs to be redone (we have it documented) |
| ❌ **wpa-sec needs API key** | Free but requires registration at wpa-sec.stanev.org |

### Keeping DrSchottky (staying put)

| | |
|---|---|
| ✅ **Working right now** | 7 handshakes, display working, AI running |
| ✅ **No rebuild downtime** | zangichi keeps hunting while you work |
| ❌ **No bug fixes ever** | The crash/lockup issues won't get fixed |
| ❌ **No new plugins** | Community ecosystem moving to jayofelony |
| ❌ **Bettercap crashes** | The lockups you're seeing are likely this |

**Verdict:** Rebuild. The lockups alone justify it. jayofelony fixes them.

---

## What You Gain

### Reliability
The bettercap crash fix is the #1 gain. zangichi was locking up
under load — that's a known bug in the old bettercap version,
fixed in jayofelony's 2.40.2 build. No more pulling cables.

### BT-Tether (biggest workflow change)
```
Before: plug USB cable → set Mac IP → SSH → pull files → unplug
After:  pair once → zangichi appears as BT network device →
        ssh pi@172.20.10.1 from anywhere in Bluetooth range
        no cable, no IP config, no MANU mode
```

### wpa-sec Auto-Cracking
```
zangichi catches handshake
      ↓ (when internet available via USB tether or client WiFi)
auto-uploads to wpa-sec.stanev.org
      ↓
distributed wordlist cracking runs in cloud
      ↓
results appear in your wpa-sec dashboard
      ↓
cracked passwords emailed/shown — free
```
The 6 handshakes from today would have been cracked automatically.

### aircrackonly — Quality over Quantity
Validates every pcap before keeping it. The Eriksen capture
(24 bytes — useless) would have been auto-deleted. Only real,
crackable handshakes kept on disk.

### hashie — Ready for hashcat
Converts pcap → .22000 format (hashcat mode 22000) automatically.
When you want to run hashcat locally on zanmac-01:
```bash
hashcat -m 22000 handshakes/*.22000 wordlist.txt
```
No manual conversion needed.

---

## Flash Instructions

### Step 1 — Get the image
Download: https://github.com/jayofelony/pwnagotchi/releases/latest
File: `pwnagotchi-raspberrypi-os-lite-arm64-v2.9.5.8.img.xz`
(or latest available — check releases page)

### Step 2 — Flash with Pi Imager
- OS: Use Custom Image → select downloaded .img.xz
- Storage: your SD card (32GB recommended, 8GB minimum)
- **DO NOT** use the gear icon customization — pwnagotchi manages its own config
- Just write, no SSH/WiFi pre-config needed

### Step 3 — First boot config.toml
After flash, before first boot — mount the SD card and edit:
`/boot/config.toml`

Paste this config (see below).

### Step 4 — Boot and connect
- Power on zangichi via power bank
- Wait 2-3 min for first boot (slower than normal)
- Connect USB data cable to Mac
- Set Mac USB interface to 10.0.0.1 / 255.255.255.0
- `ssh pi@10.0.0.2` password: `raspberry`
- Change password immediately: `passwd`
- Save to Bitwarden as `zangichi`

### Step 5 — Get wpa-sec API key
1. Go to https://wpa-sec.stanev.org/?get_key
2. Click "Get key" — free, no account needed
3. Copy your key
4. Add to config.toml (see below)
5. `sudo systemctl restart pwnagotchi`

### Step 6 — Verify
```bash
sudo systemctl status pwnagotchi
tail -f /var/log/pwnagotchi.log
```
Look for: `[core] starting pwnagotchi` and display showing face

---

## config.toml

```toml
main.name = "zangichi"
main.lang = "en"
main.iface = "wlan0"
main.mon_start_cmd = "/usr/bin/monstart"
main.mon_stop_cmd = "/usr/bin/monstop"
main.whitelist = [
  "zangetsu7"
]

# AI / personality
main.personality.born_at = 0
main.personality.max_interactions = 40
main.personality.boredom_multiplier = 1.0
main.personality.sad_num_epochs = 0

# Display — Waveshare v3 (CRITICAL — do not change)
ui.display.enabled = true
ui.display.type = "waveshare_3"
ui.display.color = "black"
ui.fps = 0.0

# Grid — share with pwnagotchi community
main.plugins.grid.enabled = true
main.plugins.grid.report = true
main.plugins.grid.exclude = [
  "zangetsu7"
]

# BT-Tether — SSH over Bluetooth (pair with Mac)
main.plugins.bt-tether.enabled = true
main.plugins.bt-tether.devices.mac-os-phone.enabled = true
main.plugins.bt-tether.devices.mac-os-phone.search_order = 1
main.plugins.bt-tether.devices.mac-os-phone.ip = "172.20.10.2"
main.plugins.bt-tether.devices.mac-os-phone.netmask = "255.255.255.0"
main.plugins.bt-tether.devices.mac-os-phone.gateway = "172.20.10.1"
main.plugins.bt-tether.devices.mac-os-phone.dns = "8.8.8.8"

# wpa-sec — auto-upload + cloud crack (get key at wpa-sec.stanev.org)
main.plugins.wpa-sec.enabled = true
main.plugins.wpa-sec.api_key = "YOUR_KEY_HERE"
main.plugins.wpa-sec.api_url = "https://wpa-sec.stanev.org"
main.plugins.wpa-sec.download_results = true
main.plugins.wpa-sec.download_interval = 3600

# aircrackonly — validate handshakes, delete duds
main.plugins.aircrackonly.enabled = true

# hashie — auto-convert pcap to hashcat format
main.plugins.hashie.enabled = true

# webcfg — browser-based config editor
main.plugins.webcfg.enabled = true

# memtemp — memory + temp on display
main.plugins.memtemp.enabled = true
main.plugins.memtemp.scale = "celsius"
main.plugins.memtemp.orientation = "horizontal"

# session-stats — graphs on display
main.plugins.session-stats.enabled = true

# auto-backup — push files when internet available
main.plugins.auto_backup.enabled = true
main.plugins.auto_backup.files = [
  "/root/handshakes"
]
main.plugins.auto_backup.interval = 1

# wigle — map your captures
main.plugins.wigle.enabled = false
# enable if you want geographic mapping:
# main.plugins.wigle.api_key = "YOUR_WIGLE_API_KEY"
```

---

## Post-Rebuild Checklist

- [ ] Display shows zangichi face on boot
- [ ] AUTO mode activates after 2 min
- [ ] `sudo tail -f /var/log/pwnagotchi.log` shows no errors
- [ ] BT-Tether pairs with Mac (`ssh pi@172.20.10.1`)
- [ ] wpa-sec dashboard shows uploads after first handshake
- [ ] aircrackonly deleting bad pcaps (check log)
- [ ] hashie creating .22000 files alongside .pcap files
- [ ] Change default password + save to Bitwarden

---

## What Resets vs. What Carries Over

| Item | Resets? | Notes |
|---|---|---|
| AI model / brain | ✅ Resets | Starts learning from scratch — expected |
| Handshakes | ✅ Lost on old SD | Pull from old SD before rebuild OR already on Mac ✅ |
| Config | ✅ Rewrite | Use config above |
| Password | ✅ Resets to `raspberry` | Change immediately |
| Name | Carries over | `main.name = "zangichi"` in config |
| Whitelist | Carries over | `zangetsu7` in config |

**Handshakes already on Mac:** ✅ Safe — pulled earlier today.
Old SD card can be wiped.

---

## Pi Zero 2W Power Notes

- Pi Zero 2W + pwnagotchi is near the USB power limit
- Running pwnagotchi + USB data simultaneously causes lockups
- **Workflow after rebuild:**
  1. Hunt on power bank (no USB data cable)
  2. When ready to pull: boot into MANU mode OR use BT-Tether
  3. BT-Tether eliminates the cable problem entirely

---

## Files Location on zangichi

```
/root/handshakes/          ← pcap files
/root/handshakes/*.22000   ← hashcat-ready files (after hashie)
/var/log/pwnagotchi.log    ← main log
/etc/pwnagotchi/config.toml ← config (edit here after first boot)
/etc/pwnagotchi/default.toml ← defaults (DO NOT EDIT)
/usr/local/share/pwnagotchi/custom-plugins/ ← drop extra plugins here
```

---

## Roadmap After Rebuild

- [ ] BT-Tether pair with zanmac-01
- [ ] wpa-sec API key configured
- [ ] First handshake auto-uploaded and cracking
- [ ] Tailscale install (internet via BT-Tether → Tailscale → phones home)
- [ ] zangichi added to Tailscale fleet
- [ ] Auto-sync handshakes to zangohana on schedule
