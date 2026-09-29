#!/bin/bash
# ============================================================
# zangpachi-5 Full Stack Install
# TechHouseLV / Zangbot Field Ops Unit
# Run once after fresh Pi OS Lite install
# Usage: sudo bash zangpachi-install.sh
# ============================================================

set -e

echo "================================================"
echo " zangpachi-5 Full Stack Install"
echo " TechHouseLV · Zangbot Field Ops"
echo " $(date)"
echo "================================================"
echo ""

# ── 0. SYSTEM UPDATE ─────────────────────────────────────────
echo "[0/8] System update..."
apt-get update -q && apt-get upgrade -y -q
echo "  ✓ system updated"

# ── 1. SYSTEM TOOLS ──────────────────────────────────────────
echo ""
echo "[1/8] System tools..."
apt-get install -y -q \
  git vim tmux htop tree curl wget \
  build-essential pkg-config \
  ufw fail2ban \
  cockpit \
  avahi-daemon
echo "  ✓ system tools installed"

# ── 2. NETWORKING & RECON ────────────────────────────────────
echo ""
echo "[2/8] Networking + recon tools..."
apt-get install -y -q \
  nmap tshark tcpdump \
  netdiscover net-tools \
  arp-scan dnsutils whois \
  masscan nikto \
  aircrack-ng
echo "  ✓ networking tools installed"

# ── 3. PYTHON STACK ──────────────────────────────────────────
echo ""
echo "[3/8] Python stack..."
apt-get install -y -q \
  python3 python3-pip python3-venv \
  python3-dev libffi-dev libssl-dev
pip3 install --break-system-packages \
  scapy requests paramiko rich \
  meshtastic flask
echo "  ✓ python stack installed"

# ── 4. SECURITY TOOLS ────────────────────────────────────────
echo ""
echo "[4/8] Security tools..."
apt-get install -y -q \
  john hydra hashcat \
  binwalk foremost \
  sqlmap \
  sslscan
echo "  ✓ security tools installed"

# ── 5. HARDWARE BRIDGES ──────────────────────────────────────
echo ""
echo "[5/8] Hardware bridges (serial, LoRa)..."
apt-get install -y -q \
  minicom screen picocom \
  i2c-tools python3-smbus
# Enable UART for LoRa/serial
raspi-config nonint do_serial_hw 0
raspi-config nonint do_serial_cons 1
echo "  ✓ hardware bridges installed"

# ── 6. TAILSCALE ─────────────────────────────────────────────
echo ""
echo "[6/8] Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh
echo "  ✓ tailscale installed"
echo "  → Run: sudo tailscale up"

# ── 7. FIREWALL ──────────────────────────────────────────────
echo ""
echo "[7/8] Firewall (ufw)..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 9090/tcp comment 'cockpit dashboard'
ufw allow 41641/udp comment 'tailscale'
ufw --force enable
echo "  ✓ firewall configured"

# ── 8. SUDOERS FOR SCAN TOOLS ────────────────────────────────
echo ""
echo "[8/8] Passwordless sudo for scan tools..."
cat > /etc/sudoers.d/zangpachi-tools << 'SUDOERS'
zangetsu ALL=(ALL) NOPASSWD: /usr/bin/nmap, /usr/sbin/tcpdump, /usr/sbin/netdiscover, /usr/bin/masscan, /usr/sbin/arp-scan, /usr/bin/aircrack-ng, /usr/bin/bash
SUDOERS
chmod 440 /etc/sudoers.d/zangpachi-tools
echo "  ✓ sudoers configured"

# ── DEPLOY SCOUT SCRIPT ──────────────────────────────────────
echo ""
echo "Deploying scout script..."
mkdir -p /home/zangetsu/scans
cat > /home/zangetsu/scout.sh << 'SCOUTEOF'
#!/bin/bash
# Zangbot Scout Suite — see zangbot.net for docs
# Usage: scout.sh [SUBNET] [--aggressive]
sudo bash /opt/zangbot/scripts/zangbot-scout.sh "$@"
SCOUTEOF
chmod +x /home/zangetsu/scout.sh
chown zangetsu:zangetsu /home/zangetsu/scout.sh
echo "  ✓ scout script deployed"

# ── DONE ─────────────────────────────────────────────────────
echo ""
echo "================================================"
echo " INSTALL COMPLETE"
echo ""
echo " Next steps:"
echo "  1. sudo tailscale up    — join Tailscale mesh"
echo "  2. cockpit at https://$(hostname -I | awk '{print $1}'):9090"
echo "  3. Install Pironman5:   curl -sSL https://raw.githubusercontent.com/sunfounder/pironman5/v1/install.sh | sudo bash"
echo "  4. Reboot:              sudo reboot"
echo "================================================"
