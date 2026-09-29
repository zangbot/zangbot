#!/bin/bash
# synology-monthly-backup.sh
# Monthly backup: Mac zangbot repo -> Synology /volume1/zangbot/
# Runs via cron on Mac - 1st of every month at 3am
# Logs to: ~/zangbot/logs/synology-backup.log
#
# Backup rule: Local (Mac) -> Remote (GitHub) -> Cloud (Synology NAS)

LOG="$HOME/zangbot/logs/synology-backup.log"
SRC="$HOME/zangbot/"
NAS_USER="zangbot"
NAS_HOST="192.168.5.15"
NAS_DST="/volume1/zangbot/mac-backup"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

mkdir -p "$HOME/zangbot/logs"
echo "[$TIMESTAMP] Starting monthly Synology backup" >> "$LOG"

# Use tar over SSH - works on all Synology regardless of rsync service state
# Excludes credentials, runtime files, and personal session context
tar -czf - \
  --exclude='.git' \
  --exclude='*.env' \
  --exclude='.env.*' \
  --exclude='vps-backup/*/venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='rag/chroma_db' \
  --exclude='*.db' \
  --exclude='*.log' \
  --exclude='ZANGBOT-SESSION-CONTEXT.md' \
  -C "$(dirname $SRC)" "$(basename $SRC)" | \
  ssh "${NAS_USER}@${NAS_HOST}" "mkdir -p ${NAS_DST} && cat > ${NAS_DST}/zangbot-$(date +%Y-%m-%d).tar.gz" >> "$LOG" 2>&1

if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Synology backup complete" >> "$LOG"
else
    echo "[$TIMESTAMP] Synology backup FAILED - check rsync output above" >> "$LOG"
fi
