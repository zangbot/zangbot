#!/bin/bash
# breakfix-logger.sh
# Called by systemd OnFailure= to log service crashes automatically.
# Captures: timestamp, service name, systemd status, last 20 journal lines.
# Log location: /opt/zangbot/logs/breakfix.log
# Monthly review: tells you what breaks and why — builds your runbook over time.

SERVICE="$1"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
LOG="/opt/zangbot/logs/breakfix.log"

mkdir -p /opt/zangbot/logs

echo "[$TIMESTAMP] FAILURE: $SERVICE" >> "$LOG"
echo "[$TIMESTAMP] --- systemd status ---" >> "$LOG"
systemctl status "$SERVICE" --no-pager -l >> "$LOG" 2>&1
echo "[$TIMESTAMP] --- journal last 20 lines ---" >> "$LOG"
journalctl -u "$SERVICE" -n 20 --no-pager >> "$LOG" 2>&1
echo "[$TIMESTAMP] --- end ---" >> "$LOG"
echo "" >> "$LOG"
