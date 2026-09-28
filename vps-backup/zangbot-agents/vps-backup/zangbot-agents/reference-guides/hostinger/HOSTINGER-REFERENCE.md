# Hostinger VPS Reference Guide — Bot Edition

**Version:** Ubuntu 22.04 LTS  
**VPS Plan:** KVM 2 (Startup)  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Host:** srv1969889.hstgr.cloud (IP: 72.62.97.23)

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Hostname** | srv1969889.hstgr.cloud |
| **IP Address** | 72.62.97.23 |
| **SSH Port** | 22 |
| **Root User** | root |
| **Credentials** | Bitwarden + `~/.hermes/default/vault/hostinger-vps.json` |
| **OS** | Ubuntu 22.04 LTS |
| **cPanel** | Available (port 2083) |

---

## SSH Access

### Connect
```bash
ssh root@72.62.97.23
```

Or via hostname:
```bash
ssh root@srv1969889.hstgr.cloud
```

### Credentials Location
- Primary: Bitwarden (`Hostinger VPS (srv1969889)`)
- Backup: `~/.hermes/default/vault/hostinger-vps.json`

### SSH Key Management
- SSH keys stored in `/root/.ssh/authorized_keys`
- Deploy via `cpanel-ssh-access` skill or manual `scp`

---

## File Upload to Hostinger

### Method 1: SCP (Recommended)
```bash
scp -P 22 local_file root@72.62.97.23:/path/on/vps
```

### Method 2: Base64 (Workaround for SSH-RSA Issues)

If SCP fails with "Permission denied (publickey,password)":

**On local machine (encode file):**
```bash
base64 -w0 < vodia_bot.py > vodia_bot.py.b64
```

**On VPS (decode file):**
```bash
echo 'BASE64_CONTENT_HERE' | base64 -d > /opt/vodia-bot/vodia_bot.py
chmod 755 /opt/vodia-bot/vodia_bot.py
```

### Method 3: Direct Paste via SSH
```bash
ssh root@72.62.97.23 'cat > /opt/vodia-bot/filename.py << EOF
<paste file content>
EOF'
```

---

## Directory Structure

```
/opt/vodia-bot/              # Bot application directory
├── vodia_bot.py             # Core bot class
├── vodia_bot_api.py         # Flask REST wrapper
├── .env                      # Credentials (permissions 600)
├── .env.example              # Template
├── requirements.txt          # Python dependencies
├── venv/                     # Python virtual environment
└── logs/                     # Application logs

/var/log/vodia-bot/          # Systemd journal logs
├── application.log           # App-level logging
└── error.log                 # Errors only

/etc/systemd/system/         # Systemd service units
└── vodia-bot.service        # Bot service definition
```

---

## Python Environment

### Create Virtual Environment
```bash
python3 -m venv /opt/vodia-bot/venv
source /opt/vodia-bot/venv/bin/activate
pip install flask requests gunicorn python-dotenv
```

### Requirements File
```
flask==3.0.0
requests==2.31.0
gunicorn==21.2.0
python-dotenv==1.0.0
```

### Install from File
```bash
pip install -r /opt/vodia-bot/requirements.txt
```

---

## Systemd Service Management

### Create Service Unit
**File:** `/etc/systemd/system/vodia-bot.service`

```ini
[Unit]
Description=Vodia Bot Service - PBX Automation
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=vodia-bot
Group=vodia-bot
WorkingDirectory=/opt/vodia-bot
ExecStart=/opt/vodia-bot/venv/bin/gunicorn -w 2 -b 0.0.0.0:8000 vodia_bot_api:app
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment="VODIA_HOST=lab.getqts.com"
Environment="VODIA_USER=QTS Lab"
EnvironmentFile=/opt/vodia-bot/.env

[Install]
WantedBy=multi-user.target
```

### Systemd Commands

**Reload service definition:**
```bash
systemctl daemon-reload
```

**Start service:**
```bash
systemctl start vodia-bot
```

**Stop service:**
```bash
systemctl stop vodia-bot
```

**Restart service:**
```bash
systemctl restart vodia-bot
```

**Enable on boot:**
```bash
systemctl enable vodia-bot
```

**Check status:**
```bash
systemctl status vodia-bot
```

**View logs (real-time):**
```bash
journalctl -u vodia-bot -f
```

**View logs (last 50 lines):**
```bash
journalctl -u vodia-bot -n 50
```

**View logs (since last boot):**
```bash
journalctl -u vodia-bot -b
```

---

## Firewall & Ports

### Open Port 8000 (Bot API)
```bash
ufw allow 8000/tcp
ufw status
```

### Check if Port is Listening
```bash
netstat -tlnp | grep 8000
# or
ss -tlnp | grep 8000
```

### Kill Process on Port (if stuck)
```bash
fuser -k 8000/tcp
# Then restart service
systemctl restart vodia-bot
```

---

## Common Operations

### Check Bot is Running
```bash
curl http://localhost:8000/api/status
# Expected: {"status": "ready", "domains": [...]}
```

### Create Bot User (System User)
```bash
useradd -r -s /bin/false vodia-bot
```

### Create Log Directory
```bash
mkdir -p /var/log/vodia-bot
chown vodia-bot:vodia-bot /var/log/vodia-bot
chmod 755 /var/log/vodia-bot
```

### Set Permissions on .env
```bash
chmod 600 /opt/vodia-bot/.env
chown vodia-bot:vodia-bot /opt/vodia-bot/.env
```

### View System Uptime
```bash
uptime
# or
systemctl status vodia-bot | grep Active
```

### Restart VPS
```bash
reboot
# Bot will auto-restart via systemd Restart=always
```

---

## Troubleshooting

### Service Won't Start (Failed status)

**Check logs:**
```bash
journalctl -u vodia-bot -n 100  # Last 100 lines
```

**Common issues:**

1. **"No such file or directory: /var/log/vodia-bot"**
   - Log directory missing. Create it: `mkdir -p /var/log/vodia-bot`

2. **"Port 8000 already in use"**
   - Process still listening. Kill it: `fuser -k 8000/tcp`
   - Then restart: `systemctl restart vodia-bot`

3. **"Permission denied" on .env**
   - File permissions wrong. Fix: `chmod 600 /opt/vodia-bot/.env`

4. **"ModuleNotFoundError: flask"**
   - Python dependencies missing. Install: `pip install -r requirements.txt`

5. **"Hit restart limit (5 failed starts in 60s)"**
   - Service failed 5 times too fast. Fix underlying error, then reset: `systemctl reset-failed vodia-bot`

### Bot Running but API Returns 503

**Cause:** Vodia API unreachable or credentials invalid.

**Fix:**
1. Check Vodia is reachable: `curl -k https://lab.getqts.com/rest/system/session`
2. Check credentials in `.env` file
3. Check bot logs: `journalctl -u vodia-bot -f`

### High CPU or Memory Usage

**Check process:**
```bash
ps aux | grep vodia
top -p $(pgrep -f vodia_bot)
```

**Restart service:**
```bash
systemctl restart vodia-bot
```

---

## Cascading Effects with UniFi

**If you change bot on Hostinger, what breaks on UniFi network?**

| Change on Hostinger | Vodia Impact | Network Impact |
|---|---|---|
| Change bot API port (8000 → 8001) | None (local) | Webhooks may fail if they point to :8000 |
| Restart systemd service | Temporary downtime (10s) | SIP registrations stay alive; new calls may queue |
| Change Vodia credentials in .env | Bot fails to auth | Calls continue; new ring groups won't route |
| Change bot host IP | N/A (fixed IP) | Webhooks from UniFi still work if IP unchanged |

**Always verify:** If bot needs to receive webhooks from UniFi, firewall must allow port 8000 inbound.

---

## cPanel Access (Optional)

**URL:** https://srv1969889.hstgr.cloud:2083 or https://72.62.97.23:2083

**Login:** root / (password from Bitwarden)

**Common tasks:**
- Email management
- File management (public_html)
- DNS records
- Backups
- Add domains

---

## Performance Notes

**VPS Plan:** KVM 2 (Startup)
- vCPU: 1
- RAM: 2GB
- Storage: 50GB SSD
- Bandwidth: 2TB/month

**Recommendations:**
- Single bot service only (don't run multiple bots)
- Monitor RAM usage (2GB is tight for Vodia + Flask)
- If performance degrades, upgrade plan or add swap

---

## Before ANY VPS Change

1. **Pull this guide** (never guess SSH commands)
2. **Test in lab first** (if major change)
3. **Backup config** (save .env, service file)
4. **Show plan** (what exactly will change?)
5. **Execute** (after approval)
6. **Verify** (check systemd status, API works)

