# Ubuntu (Linux Mint) Reference Guide — Bot Edition

**Version:** Linux Mint 22.3 (Ubuntu 24.04 LTS base)  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Platform:** Local development machine for Zangbot

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **OS** | Linux Mint 22.3 (Codename: zena) |
| **Base** | Ubuntu 24.04 LTS |
| **Kernel** | 7.0.0+ |
| **Package Manager** | apt (Debian-based) |
| **Python** | 3.12+ (system) |
| **Shell** | bash 5.2+ |
| **Terminal** | GNOME Terminal (default) |

---

## System Management

### Check OS Version
```bash
lsb_release -a
# or
cat /etc/os-release
```

### Update System
```bash
sudo apt update          # Update package lists
sudo apt upgrade         # Upgrade packages
sudo apt full-upgrade    # Full system upgrade
sudo apt autoremove      # Remove unused packages
```

### Check Disk Space
```bash
df -h                    # Mounted filesystems
du -sh ~/*               # Home directory usage
ncdu ~/                  # Interactive disk usage (install: sudo apt install ncdu)
```

### Check Memory
```bash
free -h                  # RAM usage
top                      # Real-time monitoring
htop                     # Enhanced (install: sudo apt install htop)
```

### Restart/Shutdown
```bash
sudo reboot              # Restart
sudo shutdown -h now     # Shutdown immediately
sudo shutdown -h +10     # Shutdown in 10 minutes
```

---

## Python Environment

### Check Python Version
```bash
python3 --version
which python3
```

### Create Virtual Environment
```bash
python3 -m venv ~/zangbot-env
source ~/zangbot-env/bin/activate
deactivate               # Exit venv
```

### Install Packages
```bash
pip install --upgrade pip
pip install requests flask gunicorn python-dotenv
pip install -r requirements.txt  # From file
```

### Create Requirements File
```bash
pip freeze > requirements.txt
```

### Global Packages (System-Wide)
```bash
sudo apt install python3-flask python3-requests
```

---

## File Management

### Basic Commands
```bash
ls -lah                  # List files (long, all, human-readable)
cd ~                     # Home directory
pwd                      # Current directory
mkdir -p path/to/dir     # Create nested directories
cp source dest           # Copy file
cp -r source dest        # Copy directory (recursive)
mv source dest           # Move/rename
rm file                  # Delete file
rm -rf directory         # Delete directory (recursive)
```

### Search Files
```bash
find ~ -name "*.md"                    # Find by name
grep -r "text" ~/directory             # Search in files
locate file                            # Fast search (index-based)
```

### File Permissions
```bash
chmod 755 file           # Make executable
chmod 600 file           # Secure file (owner read/write)
chown user:group file    # Change owner
```

### Disk Usage
```bash
du -sh directory         # Directory size
du -sh ~/.*              # Hidden directories
```

---

## SSH & Git

### SSH Keys
```bash
ssh-keygen -t ed25519 -C "email@example.com"  # Generate key
cat ~/.ssh/id_ed25519.pub                      # View public key
ssh-add ~/.ssh/id_ed25519                      # Add to agent
```

### SSH Connect
```bash
ssh user@hostname
ssh -p 2222 user@hostname  # Custom port
ssh-copy-id user@hostname  # Copy key to remote
```

### Git
```bash
git config --global user.name "Name"
git config --global user.email "email@example.com"
git clone URL
git status
git add .
git commit -m "message"
git push
git pull
```

---

## Services & Daemons (Systemd)

### List Services
```bash
systemctl list-units --type=service                    # All services
systemctl list-units --type=service --state=running    # Running
```

### Service Control
```bash
sudo systemctl start service-name
sudo systemctl stop service-name
sudo systemctl restart service-name
sudo systemctl enable service-name        # Auto-start on boot
sudo systemctl disable service-name       # Disable auto-start
sudo systemctl status service-name        # Check status
```

### View Logs
```bash
journalctl -u service-name                # Service logs
journalctl -u service-name -f             # Follow (real-time)
journalctl -u service-name -n 50          # Last 50 lines
journalctl --since "2 hours ago"          # Time range
```

---

## Network

### Check Connectivity
```bash
ping 8.8.8.8
curl https://example.com
wget URL
```

### Network Info
```bash
ifconfig                 # IP addresses (install: sudo apt install net-tools)
ip addr                  # IP addresses (modern)
ip route                 # Routing table
netstat -tlnp            # Listening ports (install: sudo apt install net-tools)
ss -tlnp                 # Listening ports (modern)
```

### DNS
```bash
nslookup example.com
dig example.com
cat /etc/resolv.conf     # DNS servers
```

### Port Check
```bash
sudo lsof -i :8000       # Process on port 8000
fuser 8000/tcp           # Find process on port
sudo netstat -tlnp | grep 8000
```

---

## Firewall (ufw)

### Enable/Disable
```bash
sudo ufw enable
sudo ufw disable
sudo ufw status
```

### Allow/Deny
```bash
sudo ufw allow 22/tcp              # Allow SSH
sudo ufw allow 8000/tcp            # Allow port 8000
sudo ufw deny 22/tcp               # Deny port
sudo ufw delete allow 22/tcp       # Remove rule
```

### List Rules
```bash
sudo ufw show added
sudo ufw show numbered
```

---

## Cron Jobs (Scheduled Tasks)

### Edit Cron
```bash
crontab -e               # Edit user crontab
sudo crontab -e          # Edit root crontab
crontab -l               # List cron jobs
```

### Cron Format
```
0 0 * * * /path/to/script.sh    # Daily at midnight
0 */6 * * * /path/to/script.sh  # Every 6 hours
0 1 1 * * /path/to/script.sh    # Monthly (1st at 1am)
```

### Common Jobs
```bash
# Update reference guides monthly
0 0 1 * * ~/.zangbot/update-reference-guides.sh

# Backup configuration daily
0 2 * * * tar -czf ~/.zangbot/backups/$(date +\%Y-\%m-\%d).tar.gz ~/.zangbot/
```

---

## Cascading Effects

**When updating Ubuntu:**
- ❌ Python packages may break (version incompatibility)
- ❌ Services may not restart (dependency changes)
- ❌ SSH keys may need regeneration (security policy)

**When changing firewall rules:**
- ❌ Bots can't reach external APIs (ports blocked)
- ❌ SSH access lost if port 22 blocked

**When deleting files:**
- ❌ Scripts break if referenced (absolute paths fail)
- ❌ Credentials lost if vault file deleted

---

## Troubleshooting

### Package Manager Issues
```bash
sudo apt clean                     # Clear cache
sudo apt autoclean                 # Remove old versions
sudo apt --fix-broken install      # Fix broken installs
sudo dpkg --configure -a           # Configure incomplete packages
```

### Permission Denied
```bash
ls -la file                        # Check permissions
sudo chmod 755 file                # Fix permissions
sudo chown $USER file              # Change owner
```

### Disk Full
```bash
df -h                              # Check usage
du -sh ~/.*                        # Find large dirs
sudo apt autoremove                # Remove unused packages
rm -rf ~/snap                      # Remove snaps (if not used)
```

### Service Won't Start
```bash
journalctl -u service-name -n 50   # Check logs
sudo systemctl status service-name # Detailed status
sudo systemctl reset-failed service-name
```

---

## Before ANY Ubuntu Change

1. **Backup important data** (`~/.zangbot`, SSH keys)
2. **Check available space** (`df -h`)
3. **List running services** (`systemctl list-units --state=running`)
4. **Show change plan** (what exactly will change?)
5. **Wait for approval**
6. **Execute** (after approval)
7. **Verify** (check system is responsive)

---

## Cascading Effects Table

| Change on Ubuntu | Affects | Impact |
|---|---|---|
| Disable firewall | Bot API access from remote | Hostinger webhooks may fail |
| Delete ~/.ssh | Git, SSH access | Cannot push code or SSH to VPS |
| Update Python | All venv packages | May break bot (version mismatch) |
| Full system upgrade | All services | Services may not auto-restart correctly |
| Change hostname | SSH, Git, DNS | Certificates may need regeneration |

---

**Last Updated:** 2026-09-18 | Status: READY FOR LOCAL DEVELOPMENT

