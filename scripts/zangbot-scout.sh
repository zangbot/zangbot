#!/bin/bash
# ============================================================
# Zangbot Field Scout Suite
# Run after arriving on-site to baseline a client network
# Usage: sudo bash /home/zangetsu/scout.sh [SUBNET] [--aggressive]
# Example: sudo bash /home/zangetsu/scout.sh 192.168.1.0/24
# Example: sudo bash /home/zangetsu/scout.sh 192.168.1.0/24 --aggressive
#
# Default timing: T3 (normal/thorough — professional)
# --aggressive:   T4 (faster, louder — use when briefed client)
# ============================================================

set -e

SUBNET="${1:-$(ip route | grep -v tailscale | grep 'src' | awk '{print $1}' | grep '/' | head -1)}"
AGGRESSIVE=false
TIMING="T3"
TIMING_NOTE="Normal/thorough — professional default"

# Check for --aggressive flag
for arg in "$@"; do
  if [ "$arg" = "--aggressive" ]; then
    AGGRESSIVE=true
    TIMING="T4"
    TIMING_NOTE="Aggressive — client has been briefed, detection assessment active"
  fi
done

DATE=$(date +%Y%m%d-%H%M)
OUTDIR="/home/zangetsu/scans/$DATE"
SCANNER=$(hostname)
mkdir -p "$OUTDIR"

echo "================================================"
echo " Zangbot Field Scout Suite — $(date)"
echo " Scanner:  $SCANNER"
echo " Target:   $SUBNET"
echo " Timing:   -$TIMING ($TIMING_NOTE)"
echo " Output:   $OUTDIR"
echo "================================================"

# ── 1. SYSTEM CHECK ──────────────────────────────────────────
echo ""
echo "[1/6] System check..."
{
  echo "=== SYSTEM ==="
  hostname
  uptime
  ip addr show | grep -E 'inet ' | grep -v '127.0.0.1'
  echo "=== TAILSCALE ==="
  tailscale status 2>/dev/null || echo "tailscale not connected"
  echo "=== SCANNER ==="
  nmap --version | head -1
} > "$OUTDIR/00-system.txt"
echo "  ✓ system info saved"

# ── 2. HOST DISCOVERY ────────────────────────────────────────
echo ""
echo "[2/6] Host discovery..."
nmap -sn -$TIMING "$SUBNET" -oN "$OUTDIR/01-hosts.txt" 2>/dev/null
HOSTCOUNT=$(grep 'Host is up' "$OUTDIR/01-hosts.txt" | wc -l)
echo "  ✓ $HOSTCOUNT hosts found"

# ── 3. PORT SCAN TOP 1000 ────────────────────────────────────
echo ""
echo "[3/6] Port scan top 1000 ports..."
if [ "$AGGRESSIVE" = true ]; then
  echo "  ⚡ Aggressive mode — IDS/EDR detection assessment active"
  echo "  If nothing fires — FINDING: aggressive scan went unnoticed"
fi
nmap -sV --open -$TIMING "$SUBNET" -oN "$OUTDIR/02-ports.txt" 2>/dev/null
OPENPORTS=$(grep 'open' "$OUTDIR/02-ports.txt" | grep -v 'nmap\|#' | wc -l)
echo "  ✓ $OPENPORTS open ports found"

# ── 4. SERVICE + OS FINGERPRINT ──────────────────────────────
echo ""
echo "[4/6] Service + OS fingerprint..."
nmap -sV -O --osscan-guess -$TIMING "$SUBNET" -oN "$OUTDIR/03-services.txt" 2>/dev/null
echo "  ✓ service fingerprint complete"

# ── 5. VULN SCRIPTS ──────────────────────────────────────────
echo ""
echo "[5/6] NSE vuln scripts (slowest phase — up to 30min)..."
echo "  Ctrl+C to skip — partial results saved"
timeout 1500 nmap --script="default,vuln" -$TIMING "$SUBNET" -oN "$OUTDIR/04-vulns.txt" 2>/dev/null \
  || echo "  ⚠ vuln scan timed out or interrupted — partial results saved"
echo "  ✓ script scan complete"

# ── 6. SUMMARY ───────────────────────────────────────────────
echo ""
echo "[6/6] Generating summary..."
cat > "$OUTDIR/SUMMARY.txt" << EOF
================================================
 ZANGBOT FIELD SCOUT REPORT
 Date:    $(date)
 Scanner: $SCANNER
 Subnet:  $SUBNET
 Timing:  -$TIMING ($TIMING_NOTE)
================================================

HOSTS ONLINE: $HOSTCOUNT
OPEN PORTS:   $OPENPORTS

DETECTION ASSESSMENT:
  [ ] Client EDR/AV fired during scan
  [ ] IDS/IPS alert triggered
  [ ] Staff reported warning to IT
  [ ] No detection observed — FINDING: scan went unnoticed
  Notes: _______________________________________________

TOP FINDINGS:
$(grep -E 'VULNERABLE|WARNING' "$OUTDIR/04-vulns.txt" | grep -v '#' | head -30)

FILES:
  00-system.txt   — scanner state at scan time
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
echo " Timing:     -$TIMING"
echo " Results:    $OUTDIR/"
echo "================================================"
echo ""
echo "Pull results to zanmac-01:"
echo "  scp -r zangetsu@$(tailscale ip 2>/dev/null | head -1):$OUTDIR ~/zangbot/scans/"
