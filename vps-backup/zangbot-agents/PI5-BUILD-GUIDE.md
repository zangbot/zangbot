# Raspberry Pi 5 — Field Agent Build Guide

**Role:** Portable field diagnostics — on-site network auditing, offline LLM inference, packet capture  
**Hardware:** Pi 5 8GB + Pironman 5-MAX (or Mini) + 2x NVMe SSD + Hailo-8L AI accelerator  
**Storage:** SSD 1 (OS + tools) + SSD 2 (Ollama models, pcaps)  
**Model:** Phi 3 Mini (2.8 GB) via Ollama ARM64

---

## Pre-Build Checklist

Before starting, verify you have:
- [ ] Raspberry Pi 5 8GB board
- [ ] Pironman 5-MAX case ($80) or Pironman 5-Mini ($46)
- [ ] NVMe SSD #1: 128 GB (OS + tools)
- [ ] NVMe SSD #2: 512 GB (Ollama models, packet captures)
- [ ] USB-C 27W power supply (Pi 5 official recommended)
- [ ] Ethernet cable
- [ ] MicroSD card (16 GB, for initial flash only)
- [ ] Hailo-8L AI accelerator module (included in Pironman cases)

---

## Step 1: Flash OS

1. Download **Raspberry Pi Imager** from `https://raspberrypi.com/software/`
2. Select **Raspberry Pi 5** → **Raspberry Pi OS Lite (64-bit)**
3. Insert microSD card
4. Click **Write** (takes ~5 minutes)

---

## Step 2: Initial Setup (on Pi Connect / monitor + keyboard)

### 2a. First Boot
Insert microSD, connect Ethernet, power on.

### 2b. Enable SSH
```bash
sudo raspi-config
# Navigate to: Interface Options → SSH → Yes
# Exit to terminal
sudo service ssh start
```

### 2c. Set hostname
```bash
sudo raspi-config
# Navigate to: Network Options → Hostname
# Set: zangbot-pi5 (or your preferred name)
```

### 2d. Update system
```bash
sudo apt update && sudo apt upgrade -y
```

### 2e. Set static IP or DHCP reservation
```bash
# Option A: DHCP reservation in your router (recommended)
# Note the Pi's MAC address:
ip link show | grep -i ether
# Then set a reservation in your router admin

# Option B: Static IP on Pi (less flexible):
sudo nano /etc/dhcpcd.conf
# Add at bottom:
# interface eth0
# static ip_address=192.168.5.116/24
# static routers=192.168.5.1
# static domain_name_servers=192.168.5.1
```

---

## Step 3: SSH Key Authentication

### On your Mac, generate key if you don't have one:
```bash
ssh-keygen -t ed25519 -C "zangbot-pi5-field" -f ~/.ssh/id_ed25519_pi5
```

### Copy key to Pi (password auth required for first time):
```bash
ssh-copy-id -i ~/.ssh/id_ed25519_pi5.pub pi@192.168.5.116
```

### Verify passwordless login:
```bash
ssh -i ~/.ssh/id_ed25519_pi5 pi@192.168.5.116
```

---

## Step 4: Disable Password Auth

```bash
sudo nano /etc/ssh/sshd_config
# Change:
# PasswordAuthentication no
# PermitRootLogin no

sudo systemctl restart ssh
```

### Test before closing — open a NEW terminal and verify:
```bash
ssh -i ~/.ssh/id_ed25519_pi5 pi@192.168.5.116
```
If it connects without a password prompt, you're safe.

---

## Step 5: Install Ollama (ARM64)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Verify installation:
```bash
ollama --version
```

---

## Step 6: Configure Ollama for Pi 5

Create systemd override for memory limits and network access:
```bash
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_QUEUE=5"
MemoryMax=6G
MemoryHigh=5G
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl enable ollama
```

Verify Ollama is accessible:
```bash
curl http://localhost:11434/api/tags
```

---

## Step 7: Deploy Model

```bash
ollama pull phi3:mini
```

Test inference:
```bash
ollama run phi3:mini "What's the IP of this machine?"
```

Verify API from remote (your Mac):
```bash
curl http://192.168.5.116:11434/api/tags
```

---

## Step 8: Set Up Diagnostic Script

Create the field diagnostics script:
```bash
cat > /home/pi/zangbot-diag.sh << 'SCRIPT'
#!/bin/bash
echo "=== Zangbot Field Diagnostics ==="
echo "Time: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "---"
echo "Network:"
ip addr show | grep "inet " | grep -v "127.0.0.1"
echo "---"
echo "Latency test:"
ping -c 3 8.8.8.8 | grep "rtt"
echo "---"
echo "DNS:"
cat /etc/resolv.conf | grep nameserver
echo "---"
echo "Ollama:"
curl -s http://localhost:11434/api/tags | jq '.models[].name' 2>/dev/null
echo "---"
echo "Memory:"
free -h | grep Mem
echo "---"
echo "Temp: $(vcgencmd measure_temp | cut -d= -f2)"
echo "---"
echo "Storage:"
df -h / | tail -1
echo "=== End ==="
SCRIPT

chmod +x /home/pi/zangbot-diag.sh
```

Test:
```bash
/home/pi/zangbot-diag.sh
```

---

## Step 9: Install Diagnostic Tools

```bash
sudo apt install -y tcpdump nmap htop vnstat jq
```

---

## Step 10: Configure Firewall

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 11434/tcp
sudo ufw enable
sudo ufw status
```

---

## Step 11: Mount SSDs

### Check drives:
```bash
lsblk
```

### Format and mount SSD 1 (OS):
```bash
# Assuming NVMe is /dev/nvme0n1
sudo fdisk /dev/nvme0n1
# Or use gdisk for GPT:
sudo gdisk /dev/nvme0n1
# Create partition, format:
sudo mkfs.ext4 /dev/nvme0n1p1
sudo mkdir -p /mnt/nvme1
sudo mount /dev/nvme0n1p1 /mnt/nvme1
```

### Format and mount SSD 2 (Ollama models):
```bash
sudo mkfs.ext4 /dev/nvme1n1p1
sudo mkdir -p /mnt/nvme2
sudo mount /dev/nvme1n1p1 /mnt/nvme2
```

### Add to /etc/fstab for persistent mounts:
```bash
# Get UUIDs:
sudo blkid
# Add to /etc/fstab (replace UUIDs with actual ones):
echo 'UUID=your-nvme1-uuid /mnt/nvme1 ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
echo 'UUID=your-nvme2-uuid /mnt/nvme2 ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
```

### Reboot to verify:
```bash
sudo reboot
# After reboot:
df -h
lsblk
```

---

## Step 12: Configure Ollama Models Path to SSD 2

```bash
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/mnt/nvme2/ollama"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_QUEUE=5"
MemoryMax=6G
MemoryHigh=5G
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

## Step 13: Security Hardening

### Disable unused services:
```bash
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon
```

### Enable automatic security updates:
```bash
sudo apt install -y unattended-upgrades
sudo systemctl enable unattended-upgrades
sudo systemctl start unattended-upgrades
```

### Configure fail2ban:
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Step 14: Verification Suite

Run all checks:
```bash
# 1. SSH access from Mac
ssh -i ~/.ssh/id_ed25519_pi5 pi@192.168.5.116

# 2. Ollama API from Mac
curl http://192.168.5.116:11434/api/tags

# 3. Run diagnostics
/home/pi/zangbot-diag.sh

# 4. Model inference test
curl -s http://localhost:11434/api/generate -d '{"model":"phi3:mini","prompt":"test","stream":false}'

# 5. Reboot test
sudo reboot
# After reboot, verify:
systemctl status ollama
ssh pi@192.168.5.116 "ollama list"
```

---

## Step 15: Store Credentials

### Add to Bitwarden vault (manually):
- **Site:** Pi 5 Field Agent
- **Username:** pi
- **URL:** 192.168.5.116
- **Notes:** SSH key: ~/.ssh/id_ed25519_pi5, Role: field diagnostics

### Store in Hermes vault:
```bash
# Add SSH key to known hosts
ssh-keyscan -H 192.168.5.116 >> ~/.ssh/known_hosts
```

---

## Troubleshooting

### Pi not showing up on network
```bash
# Scan network from Mac:
sudo arp-scan --interface=en0 --localnet | grep -i raspberrypi
# Or check router admin panel for DHCP leases
```

### Ollama not responding
```bash
# Check service:
systemctl status ollama
# Check logs:
journalctl -u ollama --no-pager -f
# Verify port:
ss -tlnp | grep 11434
```

### Can't SSH in
```bash
# Verify SSH is running:
sudo systemctl status ssh
# Check firewall:
sudo ufw status
# Check if key auth works:
ssh -i ~/.ssh/id_ed25519_pi5 -v pi@192.168.5.116
```

### Temperature warnings
```bash
# Check temp:
vcgencmd measure_temp
# Normal idle: 40-50°C
# Under load with cooling: 60-70°C
# Throttle threshold: 85°C
# If throttling, check fan RPM:
vcgencmd measure_clock arm
```

---

## Post-Build: Router Integration

Once Pi 5 is operational, add it to the distributed router:

```yaml
# ~/.zangbot/router-config.yaml
inference_backends:
  local:
    name: Mac Studio Ollama
    endpoint: http://localhost:11434/v1
  pi5:
    name: Pi 5 Field Agent
    endpoint: http://192.168.5.116:11434/v1
    models:
      - id: phi3:mini
    use_case: field diagnostics, offline operation, network tracing
  claude:
    name: Claude API
    endpoint: https://api.anthropic.com/v1
```

---

**Estimated build time:** 60-90 minutes (mostly waiting for downloads/updates)  
**Estimated hardware cost:** $80-150 (case + 2x SSD)  
**Post-build operational cost:** $0/month (local, offline-capable)
