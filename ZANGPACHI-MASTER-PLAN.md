# ZANGPACHI — Field Ops Master Plan
**"The Guy On The Ground"**

**Hardware:** Raspberry Pi 5 8GB + Pironman 5 Pro Max + 500GB NVMe  
**Role:** On-site network reconnaissance, security auditing, packet capture, AI-assisted triage  
**Callsign:** zangpachi  
**Reports to:** Mac Studio (zangbot) via Tailscale + Telegram  

---

## Hardware Loadout (What's Arriving / Planned)

| Item | Purpose |
|------|---------|
| Raspberry Pi 5 8GB | The brain |
| Pironman 5 Pro Max | Armor — 4.3" touch screen, dual NVMe, Hailo-8 slot, tower cooler, RGB |
| 500GB NVMe SSD | Tools, models, captures, logs |
| Flipper Zero | RF/NFC/sub-GHz/IR recon, BadUSB, physical security testing |
| LoRa devices | Long-range mesh comms, sensor deployment |
| Pwnagotchi | AI WiFi auditor — captures WPA handshakes, client demo showstopper |
| Raspberry Pi Zero 2 W | Runs Pwnagotchi (dedicated device) |

**Key Pironman 5 Pro Max features to exploit:**
- 4.3" IPS touch screen → live Grafana dashboard, status at a glance
- M.2 Hailo-8 slot → on-device AI acceleration (future add)
- Dual NVMe → OS on SSD, models/captures on second slot (second drive: future)
- OLED display → system vitals always visible
- Tower cooler + PWM fans → sustained load without throttle
- USB mic + camera + speaker → future: voice-activated field commands
- RAID 0/1 capable when second drive added

---

## OS Decision: Desktop, Not Lite

**Pick: Raspberry Pi OS (64-bit) with Desktop** — not Lite  
**Reason:** Touch screen is wasted on headless. Wireshark, Grafana, and browser-based tools work on the 4.3" display. Hermes can pop open a terminal. When you plug into a client's monitor (HDMI), you get a full GUI instantly.

```
Raspberry Pi Imager:
  Device: Raspberry Pi 5
  OS: Raspberry Pi OS (64-bit) [full desktop]
  Storage: NVMe SSD (via USB adapter for initial flash OR use rpi-imager with PCIe boot)
```

---

## Phase 1: Base Build (Day 1 — Hardware Assembly + OS)

### 1a. Assemble Pironman 5 Pro Max
Follow SunFounder's assembly guide: https://docs.sunfounder.com/projects/pironman5-pro-max/en/latest/
- Seat Pi 5 into case
- Seat NVMe SSD into M.2 slot 1
- Connect touch screen ribbon cable
- Connect OLED display cable
- Connect PWM fan headers
- Connect power button

### 1b. Flash & Boot
```bash
# Use Raspberry Pi Imager on Mac
# Flash to NVMe via USB enclosure OR microSD first, then migrate
# Set in Imager advanced settings:
#   hostname: zangpachi
#   username: zang
#   SSH: enabled
#   WiFi: your home SSID (for initial setup only)
#   locale: US/Pacific
```

### 1c. First SSH in
```bash
ssh zang@zangpachi.local
# If .local doesn't resolve:
# Check router for DHCP lease → find zangpachi's IP
ssh zang@<IP>
```

### 1d. Hostname & Update
```bash
sudo hostnamectl set-hostname zangpachi
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

---

## Phase 2: VPN First — Phone Home Before Anything Else

**Tailscale is the most important install.** Before zangpachi goes to a client site, it must be able to phone home to you — even behind NAT, CGNAT, hotel WiFi, or client firewall.

### Install Tailscale
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Opens a URL — authenticate with your Tailscale account
# zangpachi joins your tailnet and gets a stable 100.x.x.x IP
sudo tailscale status
```

### Enable exit node (optional — route client traffic home)
```bash
sudo tailscale up --advertise-exit-node
```

### Enable subnet routing (advertise client network back to you)
```bash
# When on client site at 192.168.1.0/24:
sudo tailscale up --advertise-routes=192.168.1.0/24
# You can then reach every device on client network from your Mac
```

### Set Tailscale to start at boot
```bash
sudo systemctl enable tailscaled
```

**From your Mac Studio, you can now always reach zangpachi at its Tailscale IP — no matter where it is in the world.**

---

## Phase 3: The Full Ops Toolkit

### Install All at Once
```bash
# Core network tools
sudo apt install -y \
  nmap \
  arp-scan \
  netdiscover \
  masscan \
  fping \
  tcpdump \
  wireshark \
  tshark \
  mtr \
  iperf3 \
  speedtest-cli \
  iftop \
  nethogs \
  vnstat \
  nload \
  bmon \
  wavemon \
  aircrack-ng \
  kismet \
  iw \
  wireless-tools \
  net-tools \
  dnsutils \
  curl \
  wget \
  jq \
  htop \
  btop \
  tmux \
  git \
  python3-pip \
  sqlite3 \
  fail2ban \
  ufw \
  nikto \
  lynis \
  whois \
  traceroute \
  sshpass \
  rsync \
  screen

echo "Core toolkit installed ✅"
```

### Install termshark (terminal Wireshark UI — beautiful)
```bash
# termshark = TUI for tshark — use when no monitor connected
TERMSHARK_VERSION=$(curl -s https://api.github.com/repos/gcla/termshark/releases/latest | jq -r '.tag_name')
wget "https://github.com/gcla/termshark/releases/download/${TERMSHARK_VERSION}/termshark_${TERMSHARK_VERSION#v}_linux_arm64.tar.gz"
tar -xzf termshark_*.tar.gz
sudo mv termshark_*/termshark /usr/local/bin/
termshark --version
```

### Install nuclei (fast vuln scanner — huge template library)
```bash
# Nuclei by ProjectDiscovery — scans for CVEs, misconfigs, exposed panels
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
# Or grab the binary:
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_arm64.zip
unzip nuclei_linux_arm64.zip
sudo mv nuclei /usr/local/bin/
nuclei -update-templates
```

### Install bandwhich (bandwidth per process — gorgeous output)
```bash
# Shows exactly which process is eating bandwidth
cargo install bandwhich
# OR
wget https://github.com/imsnif/bandwhich/releases/latest/download/bandwhich-v*-aarch64-unknown-linux-musl.tar.gz
tar -xzf bandwhich-*.tar.gz
sudo mv bandwhich /usr/local/bin/
```

### Install gping (visual ping with graph)
```bash
# Ping but with a live graph in terminal — great for showing latency spikes to clients
cargo install gping
# OR grab ARM64 binary from https://github.com/orf/gping/releases
```

### Install httpie (human-friendly curl)
```bash
pip3 install httpie
# Usage: http GET http://192.168.1.1/api/v2/...
```

### Install doggo (modern DNS tool)
```bash
# Beautiful DNS lookups with color, multiple resolvers, DoH support
wget https://github.com/mr-karan/doggo/releases/latest/download/doggo_linux_arm64.tar.gz
tar -xzf doggo_*.tar.gz
sudo mv doggo /usr/local/bin/
```

### Install enum4linux-ng (SMB/NetBIOS enumeration)
```bash
# Finds Windows shares, users, printers on a network
pip3 install impacket
git clone https://github.com/cddmp/enum4linux-ng.git /opt/enum4linux-ng
pip3 install -r /opt/enum4linux-ng/requirements.txt
sudo ln -s /opt/enum4linux-ng/enum4linux-ng.py /usr/local/bin/enum4linux-ng
```

### Install ntopng (network traffic analysis dashboard)
```bash
# Web-based traffic visualization — access via browser on touch screen or remotely
wget https://packages.ntop.org/RaspberryPI/apt-ntop.deb
sudo apt install ./apt-ntop.deb
sudo apt update
sudo apt install -y ntopng
sudo systemctl enable ntopng
sudo systemctl start ntopng
# Access at http://zangpachi.local:3000
```

### Install Grafana (master dashboard for touch screen)
```bash
sudo apt install -y adduser libfontconfig1 musl
wget https://dl.grafana.com/oss/release/grafana-rpi_$(curl -s https://api.github.com/repos/grafana/grafana/releases/latest | jq -r '.tag_name' | tr -d 'v')_armhf.deb
sudo dpkg -i grafana-rpi_*.deb
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
# Access at http://zangpachi.local:3001
```

### Install Ollama + model (on-site AI)
```bash
curl -fsSL https://ollama.ai/install.sh | sh
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/mnt/nvme/ollama"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
MemoryMax=6G
EOF
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl restart ollama

# Pull the model (phi3:mini = 2.3GB, fast on Pi 5)
ollama pull phi3:mini
# Bonus: pull a network-specialist model when we get Hailo-8
```

### Install Hermes
```bash
pip3 install hermes-agent
# Configure with Claude API key (from Bitwarden)
# zangpachi talks back to you on Telegram — same bot, same brain
```

---

## Phase 4: Flipper Zero Integration

### Install qFlipper (firmware manager)
```bash
# qFlipper = official Flipper desktop app
# On Pi OS desktop, download ARM64 AppImage:
wget https://update.flipperzero.one/builds/qFlipper/release/qFlipper-arm64.AppImage
chmod +x qFlipper-arm64.AppImage
# Run from touch screen desktop
```

### Set up Flipper Zero serial comms from Pi
```bash
# Connect Flipper via USB, communicate via serial
sudo apt install -y screen minicom
# Flipper shows as /dev/ttyACM0
screen /dev/ttyACM0 230400
# Or use flipper_toolbox for scripted automation
pip3 install flipperzero-toolbox
```

### Flipper + Pi5 workflow
```
Flipper Zero → captures RF/NFC/RFID data on site
     ↓
USB to zangpachi → zangpachi logs, analyzes, correlates
     ↓
Hermes on zangpachi → AI-assisted interpretation
     ↓
Telegram → report to you remotely
```

---

## Phase 5: LoRa Integration

### Hardware options
- **RAK2287/RAK5146** — Pi HAT LoRaWAN gateway
- **SX1262-based USB dongle** — simplest, plug-and-play
- **Dragino LPS8** — standalone gateway (zangpachi talks to it via IP)

### Install ChirpStack (LoRaWAN network server)
```bash
# ChirpStack runs on zangpachi, receives from LoRa nodes
sudo apt install -y mosquitto mosquitto-clients redis-server postgresql

# Add ChirpStack repo
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1CE2AFD36DBCCA00
sudo echo "deb https://artifacts.chirpstack.io/packages/4.x/deb stable main" | sudo tee /etc/apt/sources.list.d/chirpstack.list
sudo apt update
sudo apt install -y chirpstack chirpstack-gateway-bridge

sudo systemctl enable chirpstack chirpstack-gateway-bridge
sudo systemctl start chirpstack chirpstack-gateway-bridge
# ChirpStack dashboard at http://zangpachi.local:8080
```

### Install Mosquitto MQTT (sensor data bus)
```bash
# Already installed above — configure for LoRa sensor data
sudo tee /etc/mosquitto/conf.d/zangpachi.conf << 'EOF'
listener 1883
allow_anonymous true
log_type all
EOF
sudo systemctl restart mosquitto
```

### LoRa use cases for client sites
- Drop LoRa sensor nodes on client premises → zangpachi collects data
- Battery-powered nodes report: motion, door open, temp, network status
- LoRa range: 1-15km in urban environments — covers entire client building + parking
- No WiFi needed for sensor nodes — reports via LoRa → zangpachi → you

---

## Phase 6: Automated Reporting to Telegram

### Create the zangpachi field report script
```bash
cat > /home/zang/zangpachi-report.sh << 'SCRIPT'
#!/bin/bash
# zangpachi field report — sends to Telegram via Hermes

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
HOSTNAME=$(hostname)
TEMP=$(vcgencmd measure_temp | cut -d= -f2)
UPTIME=$(uptime -p)
IP_ETH=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
IP_TAIL=$(tailscale ip -4 2>/dev/null)
DISK=$(df -h /mnt/nvme 2>/dev/null | tail -1 | awk '{print $3"/"$2" ("$5" used)"}')
MEM=$(free -h | grep Mem | awk '{print $3"/"$2}')

REPORT="🤖 *zangpachi field report*
📅 $TIMESTAMP
🌡️ Temp: $TEMP | Uptime: $UPTIME
🌐 Eth: $IP_ETH | Tailscale: $IP_TAIL
💾 Disk: $DISK | RAM: $MEM"

# Send via Hermes Telegram
hermes send "$REPORT" --markdown
SCRIPT
chmod +x /home/zang/zangpachi-report.sh

# Schedule: report home every hour
(crontab -l 2>/dev/null; echo "0 * * * * /home/zang/zangpachi-report.sh") | crontab -
```

### Create the network scan + report script
```bash
cat > /home/zang/site-scan.sh << 'SCRIPT'
#!/bin/bash
# On-site network scan — run when arriving at client site
# Usage: ./site-scan.sh 192.168.1.0/24

SUBNET=${1:-$(ip route | grep -v default | head -1 | awk '{print $1}')}
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_DIR="/mnt/nvme/scans/${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Starting scan of $SUBNET"

# Fast host discovery
nmap -sn "$SUBNET" -oN "$OUTPUT_DIR/hosts.txt" 2>/dev/null
HOSTS=$(grep "Nmap scan report" "$OUTPUT_DIR/hosts.txt" | wc -l)

# Port + service scan on live hosts
nmap -sV --open -T4 "$SUBNET" -oN "$OUTPUT_DIR/services.txt" -oX "$OUTPUT_DIR/services.xml" 2>/dev/null

# Check for common security issues
nmap --script vuln -T3 "$SUBNET" -oN "$OUTPUT_DIR/vulns.txt" 2>/dev/null &

# ARP table
arp-scan --interface=eth0 --localnet 2>/dev/null > "$OUTPUT_DIR/arp.txt"

echo "📊 Scan complete. $HOSTS hosts found."
echo "📁 Results: $OUTPUT_DIR"

# Send summary to Telegram
hermes send "🔍 *Site Scan Complete*
📍 Subnet: $SUBNET
🖥️ Hosts found: $HOSTS
📁 Saved to: $OUTPUT_DIR
⚠️ Vuln scan running in background" --markdown
SCRIPT
chmod +x /home/zang/site-scan.sh
```

---

## Phase 6b: Flipper Zero — Full Field Ops Integration

The Flipper Zero is zangpachi's physical security co-pilot. It goes where software can't — into RF, NFC, RFID, sub-GHz, and physical access systems.

### What it does on a client site

| Capability | Real-World Use |
|-----------|---------------|
| **Sub-GHz** | Test garage doors, gate remotes, wireless alarm sensors, keyfobs |
| **NFC/RFID 125kHz** | Read/clone badge access cards (HID, EM4100) |
| **NFC 13.56MHz** | Read Mifare cards, Apple Pay emulation, NFC tags |
| **IR (infrared)** | Control TVs, projectors, AC units — useful for recon and demo |
| **BadUSB** | Automated keystroke injection scripts — plug into PC, run commands |
| **iButton** | Dallas keys used in old physical security systems |
| **GPIO** | Directly talks to zangpachi over UART for automation |
| **WiFi (with devboard)** | Deauth, evil twin, probe capture |
| **Bluetooth** | BLE scanning, Bluetooth spam |
| **LoRa (with module)** | Range-extended comms back to zangpachi |

### Flipper firmware: use Unleashed
```
Stock firmware limits some features. Unleashed firmware:
- Removes sub-GHz region restrictions
- Adds extra protocols (NiceFl, Keeloq, etc.)
- More BadUSB scripts
- Community plugins

Download: https://github.com/DarkFlippers/unleashed-firmware/releases
Flash via qFlipper on zangpachi's desktop
```

### Connect Flipper to zangpachi via GPIO/UART
```bash
# Flipper GPIO: TX=pin13, RX=pin14, GND=pin8/9
# Pi GPIO: UART RX=GPIO15(pin10), TX=GPIO14(pin8)
# Enable UART on Pi:
sudo raspi-config → Interface Options → Serial Port
# Hardware serial: YES, serial console: NO

# Test connection:
screen /dev/ttyAMA0 115200
# Or via USB:
screen /dev/ttyACM0 230400
```

### Automate Flipper from zangpachi
```python
# flipper_controller.py — send commands via serial
import serial, time

class FlipperZero:
    def __init__(self, port='/dev/ttyACM0', baud=230400):
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)

    def cmd(self, command):
        self.ser.write(f"{command}\r\n".encode())
        time.sleep(0.5)
        return self.ser.read(self.ser.in_waiting).decode()

    def rfid_read(self):
        return self.cmd("rfid read")

    def nfc_detect(self):
        return self.cmd("nfc detect")

    def subghz_raw_record(self, freq="433920000"):
        return self.cmd(f"subghz rx {freq}")

flipper = FlipperZero()
print(flipper.nfc_detect())
```

### Flipper + Hermes workflow
```
Flipper reads badge/RFID on site
     ↓
Serial to zangpachi
     ↓
Python script logs card ID, type, timestamp
     ↓
Hermes: "What protocol is this? Is it clonable?"
     ↓
Telegram: "⚠️ HID iCLASS card found — legacy, clonable, recommend upgrade"
```

---

## Phase 6c: Pwnagotchi — The AI Handshake Hunter

This is the **wow factor**. Pwnagotchi is a Raspberry Pi Zero 2 W running a custom AI (A2C reinforcement learning) that passively wanders WiFi networks capturing WPA handshakes. It has a face on an e-ink display that shows its mood, how many handshakes it's eaten, and what it's thinking.

**You walk into a client site, put it on the table, and it just starts working. Clients lose their minds.**

### Hardware
- **Raspberry Pi Zero 2 W** (~$15) — dedicated device, separate from zangpachi
- **Waveshare 2.13" e-ink HAT** (~$18) — the face
- **Alfa AWUS036ACS USB WiFi** (~$25) — second radio with monitor mode

### Flash Pwnagotchi
```bash
# Community maintained fork (actively updated):
# https://github.com/jayofelony/pwnagotchi/releases
# Flash .img to microSD with Raspberry Pi Imager
# Edit /boot/config.toml before first boot
```

### /boot/config.toml (key settings)
```toml
main.name = "zangpachi-pwn"
main.lang = "en"
main.whitelist = [
  "YourHomeSSID",
  "YourPhoneHotspot"
]

ui.display.enabled = true
ui.display.type = "waveshare_2"
ui.display.color = "black"

main.plugins.grid.enabled = true
main.plugins.grid.report = true
```

### What it captures
- **WPA handshakes** → `.pcap` files → run through hashcat/aircrack-ng
- **PMKID attacks** → attacks the AP directly, no connected client needed
- **Full WiFi map** — SSIDs, BSSIDs, signal strengths, channel
- AI learns which APs are "juicy" and lingers near them

### Crack on zangpachi
```bash
# Convert .pcap to hashcat format
hcxpcapngtool -o hash.hc22000 capture.pcap

# Run hashcat
hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt

# Or aircrack-ng
aircrack-ng capture.pcap -w /usr/share/wordlists/rockyou.txt
```

### Sync Pwnagotchi → zangpachi automatically
```bash
cat > /home/zang/sync-pwn.sh << 'SCRIPT'
#!/bin/bash
rsync -avz pi@pwnagotchi.local:/root/handshakes/ /mnt/nvme/handshakes/
COUNT=$(ls /mnt/nvme/handshakes/*.pcap 2>/dev/null | wc -l)
hermes send "🦾 *Pwnagotchi sync complete*
📡 Total handshakes: $COUNT" --markdown
SCRIPT
chmod +x /home/zang/sync-pwn.sh
```

### The Client Demo
```
1. Place Pwnagotchi on client's desk
2. Face wakes up: "I'M BORN TO PWN"
3. 10 minutes later: "😋 ATE 3 HANDSHAKES"
4. Sync to zangpachi → hashcat → crack in seconds
5. Show client their own WiFi password
6. Client: 😳
7. You: "That's why we need WPA3 and 802.1X"
8. You: 💰
```

> ⚠️ **Legal:** Always get written authorization before running on any network you don't own. Include WiFi security audit in your MSA or get a separate pen test auth letter.

---

## Phase 7: Touch Screen Dashboard

### Set Grafana as the default touch screen app
```bash
# Auto-launch Chromium in kiosk mode on boot pointing to Grafana
mkdir -p /home/zang/.config/autostart
cat > /home/zang/.config/autostart/dashboard.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Zangpachi Dashboard
Exec=chromium-browser --noerrdialogs --kiosk --incognito http://localhost:3001
X-GNOME-Autostart-enabled=true
EOF
```

### Grafana panels for touch screen
Configure these panels in Grafana:
- **Live bandwidth** (vnstat data source)
- **CPU/Temp/RAM** (node exporter)
- **Connected hosts** (nmap scan results)
- **Tailscale status** (custom script data source)
- **Last scan results** (SQLite data source)
- **Ollama status** (API probe)

---

## Phase 8: Security Hardening

```bash
# Firewall — only allow what's needed
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp        # SSH
sudo ufw allow from 100.0.0.0/8 to any port 11434  # Ollama — Tailscale only
sudo ufw allow from 100.0.0.0/8 to any port 3001   # Grafana — Tailscale only
sudo ufw allow from 100.0.0.0/8 to any port 3000   # ntopng — Tailscale only
sudo ufw enable

# Fail2ban — ban brute force
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Disable unused services
sudo systemctl disable bluetooth cups avahi-daemon

# SSH hardening
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

---

## Full Software Manifest

### Network Discovery
| Tool | Purpose | Command |
|------|---------|---------|
| nmap | Port scan, service ID, vuln scripts | `nmap -sV -T4 192.168.1.0/24` |
| arp-scan | Fast local host discovery | `sudo arp-scan --localnet` |
| netdiscover | Passive ARP recon | `sudo netdiscover -r 192.168.1.0/24` |
| masscan | Blazing fast port scan | `sudo masscan -p80,443,22 192.168.1.0/24` |
| fping | Fast ping sweep | `fping -ag 192.168.1.0/24` |

### Packet Analysis
| Tool | Purpose | Command |
|------|---------|---------|
| Wireshark | Full GUI packet analysis (touch screen) | GUI |
| tshark | CLI Wireshark | `tshark -i eth0 -w capture.pcap` |
| termshark | TUI Wireshark — beautiful | `termshark -i eth0` |
| tcpdump | Fast packet capture | `tcpdump -i eth0 -w out.pcap` |

### Traffic Analysis
| Tool | Purpose | Command |
|------|---------|---------|
| iftop | Real-time bandwidth by connection | `sudo iftop -i eth0` |
| nethogs | Bandwidth per process | `sudo nethogs eth0` |
| bandwhich | Bandwidth per process (prettier) | `sudo bandwhich` |
| bmon | Network bandwidth monitor | `bmon` |
| mtr | Traceroute + ping combined | `mtr 8.8.8.8` |
| gping | Visual ping with graph | `gping 8.8.8.8` |
| vnstat | Long-term traffic stats | `vnstat -l` |
| ntopng | Web-based traffic dashboard | Browser at :3000 |

### Wireless
| Tool | Purpose | Command |
|------|---------|---------|
| kismet | WiFi sniffer/detector | `sudo kismet` |
| aircrack-ng | WiFi security auditing | `sudo airmon-ng start wlan0` |
| wavemon | WiFi monitoring | `wavemon` |
| iw | WiFi management | `iw dev wlan0 scan` |

### Security Scanning
| Tool | Purpose | Command |
|------|---------|---------|
| nuclei | CVE + config vuln scanner | `nuclei -target 192.168.1.0/24` |
| nikto | Web server scanner | `nikto -h http://192.168.1.1` |
| lynis | System security audit | `sudo lynis audit system` |
| enum4linux-ng | SMB/Windows enumeration | `enum4linux-ng 192.168.1.10` |

### DNS & Web
| Tool | Purpose | Command |
|------|---------|---------|
| doggo | Modern DNS tool | `doggo @8.8.8.8 example.com` |
| httpie | Human-friendly curl | `http GET http://192.168.1.1/api` |
| curl | Standard web requests | `curl -I http://host` |
| dig/nslookup | DNS queries | `dig +short example.com` |

### Connectivity Testing
| Tool | Purpose | Command |
|------|---------|---------|
| iperf3 | Bandwidth test between nodes | `iperf3 -c target -t 30` |
| speedtest-cli | Internet speed test | `speedtest-cli` |
| mtr | Network path analysis | `mtr --report 8.8.8.8` |

### Remote & VPN
| Tool | Purpose | Command |
|------|---------|---------|
| Tailscale | Phone home VPN — always on | `tailscale status` |
| SSH | Secure remote access | `ssh zang@zangpachi` |
| WireGuard | Manual VPN (backup) | `wg-quick up wg0` |

### AI
| Tool | Purpose | Command |
|------|---------|---------|
| Ollama | Local LLM inference | `ollama run phi3:mini` |
| Hermes | Zangbot brain on device | `hermes chat` |
| Hailo-8 (future) | AI accelerator for faster inference | PCIe M.2 slot |

### Physical Security (Flipper Zero)
| Capability | Use Case |
|-----------|---------|
| Sub-GHz | Garage doors, keyfobs, wireless sensors |
| NFC/RFID | Badge readers, access control testing |
| Infrared | TVs, ACs, security cameras |
| BadUSB | Automated keystroke injection |
| iButton | Physical key systems |
| LoRa (with module) | Long-range comm to sensor nodes |

### Dashboards & Monitoring
| Tool | URL | Purpose |
|------|-----|---------|
| Grafana | :3001 | Master ops dashboard (touch screen) |
| ntopng | :3000 | Network traffic analysis |
| ChirpStack | :8080 | LoRa device management |

---

## zangpachi vs. Mac Studio — Role Split

| Task | zangpachi | Mac Studio |
|------|-----------|------------|
| On-site scanning | ✅ Primary | ❌ |
| Packet capture | ✅ Primary | ❌ |
| WiFi recon | ✅ Primary | ❌ |
| Flipper Zero ops | ✅ Primary | ❌ |
| LoRa sensor collection | ✅ Primary | ❌ |
| Physical presence | ✅ Only option | ❌ |
| Complex AI reasoning | 🔄 Relay to Claude | ✅ Primary |
| Heavy local inference | ❌ (8GB RAM limit) | ✅ Primary |
| Vodia/UniFi automation | 🔄 Reports findings | ✅ Executes |
| Reporting to Telegram | ✅ Field reports | ✅ Ops reports |

---

## Day 1 Build Order (Tomorrow)

```
[ ] 1. Assemble Pironman 5 Pro Max (follow SunFounder guide)
[ ] 2. Flash OS to NVMe (Raspberry Pi OS 64-bit Desktop)
[ ] 3. Boot, SSH in, set hostname to zangpachi
[ ] 4. sudo apt update && sudo apt full-upgrade -y
[ ] 5. Install Tailscale FIRST → authenticate → verify phone-home
[ ] 6. sudo apt install -y [core toolkit from Phase 3]
[ ] 7. Install Ollama + pull phi3:mini
[ ] 8. Install Hermes + configure (Claude API key from Bitwarden)
[ ] 9. Configure UFW firewall
[ ] 10. Set up field report cron (hourly Telegram ping)
[ ] 11. Set up Grafana touch screen dashboard
[ ] 12. Test site-scan.sh on home network
[ ] 13. Plug in Flipper Zero → verify serial comms
[ ] 14. Store zangpachi credentials in Bitwarden
[ ] 15. Add zangpachi to Mac Studio router config as edge node
[ ] 16. 🎉 Deploy
```

---

## Future Upgrades

| Upgrade | Purpose | Est. Cost |
|---------|---------|----------|
| Hailo-8L M.2 module | 13 TOPS AI inference on-device | ~$70 |
| Second NVMe SSD | RAID or overflow storage | ~$40 |
| USB WiFi adapter (dual-band) | Monitor mode for wireless recon (Pi's onboard WiFi can also do this) | ~$20 |
| LoRa USB dongle (SX1262) | Gateway for LoRa sensor nodes | ~$30 |
| USB-C hub | More ports on site | ~$20 |
| Pelican/hard case | Field transport protection | ~$40 |

---

---

## Phase 9: Commercial Tech Integration *(Post Zangbot Rollout)*

> **Note:** This phase is deferred until the full Zangbot platform is live and proven. Revisit after Phase 8 is complete.

### Vision
Expand from MSP + automation into full **commercial technology integrator**. Core stack is Zangbot (UniFi + Vodia + automation layer), but work with any client environment. Meet clients where they are — integrate what exists, modernize what doesn't.

### Core Stack (What We Drop In)
- **Networking:** UniFi — switches, APs, cameras, access control, gateways
- **Communications:** Vodia PBX — VoIP, UC, call analytics
- **Automation:** Zangbot layer — monitoring, alerting, AI-assisted ops

### Integration Targets (Client Existing Gear)
- Cisco / Meraki / Fortinet networks
- Microsoft Teams / Zoom Rooms
- Verkada / Genetec / Milestone / Hikvision cameras
- Crestron / Extron / QSC / Biamp AV
- HID / Lenel / Avigilon / Brivo access control
- BACnet / KNX / DALI building automation

### Target Certifications
- UniFi Design & Installation
- Vodia Certified Integrator
- Crestron Programmer (DMC-T)
- Dante Audio Certification
- BICSI ICTS (Installer)
- CompTIA Security+ (if not already held)

### Commercial Verticals
- **Office builds** — UC, AV, networking, access control as a package
- **Retail** — POS network, cameras, guest WiFi, digital signage
- **Healthcare** — HIPAA-compliant networking, nurse call integration
- **Hospitality** — property management integration, guest WiFi, IPTV

---

*Last Updated: September 26, 2026*  
*Hardware arrives: September 26, 2026*  
*Owner: Zangetsu / zangpachi*
