#!/bin/bash
# ============================================================
# zangji-3b Field Scout Suite
# Run after arriving on-site to baseline a client network
# Usage: sudo bash /home/zangetsu/scout.sh [SUBNET]
# Example: sudo bash /home/zangetsu/scout.sh 192.168.1.0/24
# ============================================================

set -e

SUBNET="${1:-$(ip route | grep -v tailscale | grep 'src' | awk '{print $1}' | grep '/' | head -1)}"
DATE=$(date +%Y%m%d-%H%M)
OUTDIR="/home/zangetsu/scans/$DATE"
mkdir -p "$OUTDIR"

echo "================================================"
echo " zangji-3b Scout Suite — $(date)"
echo " Target subnet: $SUBNET"
echo " Output: $OUTDIR"
echo "================================================"

# ── 1. SYSTEM CHECK ──────────────────────────────────────────
echo ""
echo "[1/6] System check..."
echo "=== SYSTEM ===" > "$OUTDIR/00-system.txt"
hostname >> "$OUTDIR/00-system.txt"
uptime >> "$OUTDIR/00-system.txt"
ip addr show | grep -E 'inet ' | grep -v '127.0.0.1' >> "$OUTDIR/00-system.txt"
tailscale status >> "$OUTDIR/00-system.txt" 2>/dev/null || echo "tailscale not connected" >> "$OUTDIR/00-system.txt"
echo "  ✓ system info saved"

# ── 2. HOST DISCOVERY ────────────────────────────────────────
echo ""
echo "[2/6] Host discovery (netdiscover + nmap ping)..."
nmap -sn "$SUBNET" -oN "$OUTDIR/01-hosts.txt" 2>/dev/null
HOSTCOUNT=$(grep 'Host is up' "$OUTDIR/01-hosts.txt" | wc -l)
echo "  ✓ $HOSTCOUNT hosts found"

# ── 3. PORT SCAN TOP 1000 ────────────────────────────────────────
echo ""
echo "[3/6] Port scan top 1000 ports on live hosts..."
echo "  NOTE: T4 aggressive timing is intentional."
echo "  Reveals: IDS/EDR detection, firewall rules, user/staff response to alerts."
echo "  If nothing fires — that is a finding: undetected aggressive scan."
nmap -sV --open -T4 "$SUBNET" -oN "$OUTDIR/02-ports.txt" 2>/dev/null
OPENPORTS=$(grep 'open' "$OUTDIR/02-ports.txt" | grep -v 'nmap\|#' | wc -l)
echo "  ✓ $OPENPORTS open ports found"

# ── 4. SERVICE FINGERPRINT ───────────────────────────────────
echo ""
echo "[4/6] Service + OS fingerprint on live hosts..."
nmap -sV -O --osscan-guess -T4 "$SUBNET" -oN "$OUTDIR/03-services.txt" 2>/dev/null
echo "  ✓ service fingerprint complete"

# ── 5. COMMON VULNS (safe scripts) ───────────────────────────
echo ""
echo "[5/6] Running safe NSE scripts (vuln, default)..."
echo "  NOTE: This is the slowest phase — 20-30min on a busy /24."
echo "  Timeout: 25 min. Kill with Ctrl+C if needed, results so far are saved."
timeout 1500 nmap --script="default,vuln" -T4 "$SUBNET" -oN "$OUTDIR/04-vulns.txt" 2>/dev/null || echo "  ⚠ vuln scan timed out or interrupted — partial results saved"
echo "  ✓ script scan complete"

# ── 6. SUMMARY REPORT ────────────────────────────────────────
echo ""
echo "[6/6] Generating summary..."
cat > "$OUTDIR/SUMMARY.txt" << EOF
================================================
 ZANGBOT FIELD SCOUT REPORT
 Date: $(date)
 Subnet: $SUBNET
 Scanner: zangji-3b
================================================

HOSTS ONLINE: $HOSTCOUNT
OPEN PORTS:   $OPENPORTS
SCAN TIMING:  T4 aggressive (intentional)

DETECTION ASSESSMENT:
  [ ] Client EDR/AV fired during scan
  [ ] IDS/IPS alert triggered
  [ ] Staff reported warning to IT
  [ ] No detection observed — FINDING: aggressive scan went unnoticed
  Notes: _______________________________________________

TOP FINDINGS:
$(grep -E 'open|WARNING|VULNERABLE' "$OUTDIR/04-vulns.txt" | grep -v '#' | head -30)

FILES:
  00-system.txt   — system state at scan time
  01-hosts.txt    — all live hosts
  02-ports.txt    — open ports
  03-services.txt — service/OS fingerprint
  04-vulns.txt    — NSE script results
  SUMMARY.txt     — this file
================================================
EOF

echo ""
echo "================================================"
echo " SCOUT COMPLETE"
echo " Hosts:      $HOSTCOUNT"
echo " Open ports: $OPENPORTS"
echo " Results:    $OUTDIR/"
echo "================================================"
echo ""
echo "Pull results to zanmac-01:"
echo "  scp -r zangetsu@$(tailscale ip 2>/dev/null | head -1):$OUTDIR ~/zangbot/scans/"
