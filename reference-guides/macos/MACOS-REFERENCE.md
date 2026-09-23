# macOS Reference Guide — Bot Edition (M5 Pro Deployment)

**Version:** macOS 15+ (Apple Silicon M5 Pro)  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Target:** Mac Mini M5 Pro (Ships Sept 22, 2026)  
**Purpose:** Local inference + bot development environment

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Hardware** | Mac Mini M5 Pro, 64GB RAM, 512GB SSD |
| **OS** | macOS 15+ (Sequoia or later) |
| **CPU** | Apple Silicon M5 (8-core CPU, 10-core GPU) |
| **Architecture** | ARM64 (not x86) |
| **Package Manager** | Homebrew (essential) |
| **Shell** | zsh (default in Catalina+) |
| **Python** | 3.12+ via pyenv or Homebrew |
| **Local LLM** | Ollama (recommended for M-series) |

---

## Initial Setup (Day 1)

### 1. Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
```

### 2. Install Essential Tools
```bash
# Development
brew install git
brew install python@3.12
brew install pyenv
brew install poetry

# System utilities
brew install htop
brew install tree
brew install jq

# SSH (for Hostinger)
brew install openssh

# Database/cache (optional for local dev)
brew install sqlite
brew install redis
```

### 3. Set Up Python
```bash
# Via pyenv (recommended for multiple versions)
pyenv versions
pyenv install 3.12.0
pyenv global 3.12.0
python3 --version

# Or use Homebrew Python
python3 -m venv ~/zangbot-env
source ~/zangbot-env/bin/activate
```

### 4. Clone Zangbot Repository
```bash
cd ~
git clone https://github.com/zangetsu-io/zangbot.git
cd zangbot
pip install -r requirements.txt
```

---

## Local Inference Setup

### Install Ollama (Recommended for M-Series)

**Download:** https://ollama.ai/

```bash
# After install, verify
ollama --version
ollama serve           # Start Ollama daemon
```

### Pull Models
```bash
# In another terminal
ollama pull llama2             # 7B model (~4GB)
ollama pull mistral            # 7B model (~4GB)
ollama pull neural-chat        # 7B chat-tuned (~4GB)

# For smaller/faster inference
ollama pull phi                # 2.7B model (~1.5GB)
ollama pull orca-mini          # 3B model (~2GB)
```

### Test Inference
```bash
# Via CLI
ollama run llama2 "What is the capital of France?"

# Via API (runs on port 11434)
curl http://localhost:11434/api/generate \
  -d '{
    "model": "llama2",
    "prompt": "Why is the sky blue?",
    "stream": false
  }'
```

### Configure Hermes for Local Inference
```bash
# Set Hermes to use Ollama instead of Claude API
# Edit ~/.hermes/profiles/default/hermes.yaml:

backend:
  type: "local"
  endpoint: "http://localhost:11434"
  model: "llama2"  # or mistral, neural-chat
  temperature: 0.7
  max_tokens: 2048
```

---

## File System & Storage

### Disk Space Management
```bash
df -h                          # Disk usage
du -sh ~/*                     # Directory sizes
du -sh ~/.*                    # Hidden directories
open .                         # Open in Finder

# Find large files
find ~ -type f -size +1G -ls   # Files >1GB
```

### Zangbot Directory Structure
```
~/.zangbot/
├── reference-guides/         # Reference docs (this session)
├── clients/                  # Client configs
├── backups/                  # Daily backups
├── vodia-bot/                # Bot source
├── vault/                    # Hermes vault (encrypted)
└── logs/                     # Application logs
```

### Backup Strategy
```bash
# Daily backup to local storage
tar -czf ~/.zangbot/backups/$(date +%Y-%m-%d).tar.gz ~/.zangbot/

# Weekly backup to external USB
rsync -av ~/.zangbot/ /Volumes/ExternalDrive/zangbot-backup/

# Monthly archive to cloud (iCloud, Dropbox)
cp ~/.zangbot/backups/*.tar.gz ~/Dropbox/zangbot-backups/
```

---

## Network & SSH

### SSH Setup
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub                    # Copy to GitHub, Hostinger

# Add to SSH agent
ssh-add -K ~/.ssh/id_ed25519                 # -K = save in Keychain

# Test connection
ssh -T git@github.com                        # GitHub
ssh root@72.62.97.23                         # Hostinger VPS
```

### Configure SSH Config
```bash
# Edit ~/.ssh/config
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    IgnoreUnknown UseKeychain
    UseKeychain yes

Host hostinger-vps
    HostName 72.62.97.23
    User root
    IdentityFile ~/.ssh/id_ed25519
    Port 22
    AddKeysToAgent yes
    UseKeychain yes

# Usage
ssh github.com                  # Connect via config
ssh hostinger-vps               # Shorthand
scp hostinger-vps:/path/file .  # Copy from remote
```

### Port Forwarding (Ollama to Remote)
```bash
# If you need to expose Ollama to Hostinger for webhooks
ssh -R 11434:localhost:11434 root@hostinger-vps
# Then on Hostinger, Ollama is at localhost:11434
```

---

## Systemd Alternative: launchd

macOS uses `launchd` instead of systemd. Create a bot launch agent:

### Create Launch Agent
```bash
# ~/.config/LaunchAgents/io.zangbot.ollama.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>io.zangbot.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.err</string>
</dict>
</plist>

# Load it
launchctl load ~/.config/LaunchAgents/io.zangbot.ollama.plist
```

### Launchctl Commands
```bash
launchctl load ~/LaunchAgents/service.plist           # Load
launchctl unload ~/LaunchAgents/service.plist         # Unload
launchctl list | grep zangbot                         # Check if loaded
launchctl start io.zangbot.ollama                     # Start
launchctl stop io.zangbot.ollama                      # Stop
```

---

## Development Workflow

### Python Virtual Environment
```bash
# Create
python3 -m venv ~/zangbot-env
source ~/zangbot-env/bin/activate

# Install packages
pip install -r requirements.txt

# Deactivate
deactivate
```

### Git Workflow
```bash
cd ~/zangbot
git status
git add .
git commit -m "feat: add reference guides"
git push origin main

# Pull latest
git pull origin main
```

### Run Local Bot
```bash
source ~/zangbot-env/bin/activate
python3 vodia_bot.py

# In another terminal, test API
curl http://localhost:8000/api/status
```

---

## Cascading Effects (macOS)

**When updating macOS:**
- ❌ Homebrew packages may break (incompatible versions)
- ❌ Python interpreters may re-index (slow first run)
- ❌ SSH keys may need re-entry (Keychain changes)

**When updating Python:**
- ❌ Virtual environment breaks (rebuild needed)
- ❌ Compiled packages fail (binary incompatibility)

**When updating Ollama:**
- ❌ Models may need re-download (format changes)
- ❌ Bot API calls break (endpoint changes)

**When disabling firewall:**
- ❌ Ollama accessible to network (security risk)
- ❌ Local webhooks exposed (privacy)

---

## Troubleshooting

### Python Virtual Environment Issues
```bash
# Venv broken after macOS update
rm -rf ~/zangbot-env
python3 -m venv ~/zangbot-env
source ~/zangbot-env/bin/activate
pip install -r requirements.txt
```

### Homebrew Issues
```bash
brew doctor                    # Diagnose issues
brew update                    # Update Homebrew itself
brew upgrade                   # Upgrade all packages
brew cleanup                   # Remove old versions
```

### Ollama Not Responding
```bash
# Check if running
ps aux | grep ollama

# Kill and restart
killall ollama
ollama serve                   # Restart in foreground

# Check logs
tail -f /tmp/ollama.log
```

### SSH Key Issues
```bash
# Regenerate if needed
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519_new
ssh-add -K ~/.ssh/id_ed25519_new

# Test Hostinger access
ssh -v root@hostinger-vps      # Verbose for debugging
```

### Low Disk Space on Mac Mini
```bash
# With 512GB SSD, monitor carefully
df -h

# Remove large files
rm -rf ~/Library/Caches/*      # Cached data (safe)
rm -rf ~/.ollama/models/*      # Remove unused LLM models
rm -rf ~/.zangbot/backups/old* # Remove old backups
```

---

## Performance Notes

**Mac Mini M5 Pro with 64GB RAM:**
- ✅ Ollama can run 7B models comfortably
- ✅ Multiple Zangbot agents feasible
- ✅ Hermes + Claude Code CLI + local LLM simultaneously
- ⚠️ Monitor temperature (M-series can throttle)

**Optimization Tips:**
```bash
# Check CPU usage
top -o %CPU

# Monitor memory
vm_stat                        # Virtual memory stats
press space to update

# Limit Ollama to 1 model
ollama serve --models=llama2   # Only load this model
```

---

## Monthly Updates

**1st of each month:**
```bash
# Update Homebrew
brew update
brew upgrade

# Update Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Check Ollama models
ollama list

# Update reference guides
cd ~/.zangbot && git pull origin main
```

---

## Before ANY macOS Change

1. **Backup to external drive** (rsync to USB)
2. **Check disk space** (`df -h` — keep 50GB+ free)
3. **List running services** (`launchctl list | grep zangbot`)
4. **Show plan** (what exactly will change?)
5. **Wait for approval**
6. **Execute** (after approval)
7. **Verify** (test Ollama, Zangbot, Hostinger connectivity)

---

## Deployment Timeline

| Date | Task | Duration |
|------|------|----------|
| 2026-09-18 | Build reference guides (this session) | ✅ Done |
| 2026-09-22 | Mac Mini M5 Pro arrives | — |
| 2026-09-23 | Unbox, setup, Homebrew install | 2 hours |
| 2026-09-24 | Clone Zangbot, install Python, test | 1 hour |
| 2026-09-25 | Install Ollama, pull models, verify | 1 hour |
| 2026-09-26 | Configure Hermes for local inference | 1 hour |
| 2026-09-27 | Test bot on local Ollama | 1 hour |
| 2026-09-28 | Sync with Hostinger VPS | 30 min |
| 2026-10-01 | Phase 2: Production audit | — |

---

**Last Updated:** 2026-09-18 | Status: READY FOR MAC MINI DEPLOYMENT (Sept 22, 2026)

