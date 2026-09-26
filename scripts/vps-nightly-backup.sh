#!/bin/bash
# vps-nightly-backup.sh
# Pulls latest code from VPS to Mac, commits changes to GitHub.
# Runs via cron on Mac nightly at 2am.
# Logs to: ~/zangbot/logs/backup.log

LOG="$HOME/zangbot/logs/backup.log"
REPO="$HOME/zangbot"
VPS="root@72.62.97.23"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

mkdir -p "$HOME/zangbot/logs"
echo "[$TIMESTAMP] Starting nightly backup" >> "$LOG"

# Pull latest from VPS (exclude venv, pycache, chroma_db)
rsync -av --exclude='venv/' --exclude='__pycache__/' --exclude='*.pyc' \
  --exclude='chroma_db/' --exclude='*.db' --exclude='*.log' \
  --exclude='.env' \
  "$VPS:/opt/zangbot/"    "$REPO/vps-backup/zangbot-agents/" >> "$LOG" 2>&1

rsync -av --exclude='venv/' --exclude='__pycache__/' --exclude='*.pyc' \
  --exclude='.env' \
  "$VPS:/opt/vodia-bot/"  "$REPO/vps-backup/vodia-bot/"      >> "$LOG" 2>&1

# Commit any changes to GitHub
cd "$REPO"
if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "chore: nightly VPS backup [$TIMESTAMP]"
    git push origin master >> "$LOG" 2>&1
    echo "[$TIMESTAMP] Changes committed and pushed" >> "$LOG"
else
    echo "[$TIMESTAMP] No changes detected" >> "$LOG"
fi

echo "[$TIMESTAMP] Backup complete" >> "$LOG"
