# Bitwarden Reference Guide — Bot Edition

**Version:** Bitwarden v2024+  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Purpose:** Primary credential vault (Zangbot + infrastructure secrets)

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Service** | Bitwarden (encrypted vault) |
| **Access** | Web UI + CLI + browser extension |
| **Protocols** | HTTPS (end-to-end encrypted) |
| **Storage** | Cloud (synced across devices) |
| **Backup** | Local Hermes vault + Bitwarden export |
| **Account Type** | Personal/Premium (for 2FA) |
| **Encryption** | AES-256 + PBKDF2 |

---

## Stored Credentials (Zangbot Infrastructure)

### Currently Saved

| Item | Type | Origin | Purpose | Status |
|------|------|--------|---------|--------|
| Vodia PBX (QTS Lab) lab.getqts.com | Login | Manual | PBX automation API | ✅ Active |
| Hostinger VPS (srv1969889) | Login | Manual | Cloud bot deployment | ✅ Active |
| GitHub (zangetsu-io) | Login | Manual | Portfolio repo | ✅ Active |
| Telegram Bot (Zangbot) | Note | Manual | Approval notifications | ✅ Active |
| UniFi Cloud API Key | Note | Pending | Network automation | 🔄 TBD |
| Bitwarden Master Password | Note | Secure | Master backup | ✅ Stored locally |

---

## Credential Storage Format

### Login Items (Username + Password)
```
Title: Service Name (Domain or Instance)
Username: admin@domain or root
Password: [secure password]
URL: https://service.example.com
Notes: Additional config, API endpoints, etc.
```

**Example: Vodia**
```
Title: Vodia PBX (QTS Lab) lab.getqts.com
Username: QTS Lab
Password: [secure]
URL: https://lab.getqts.com
Notes: 
  - API endpoint: /rest/
  - Auth: HTTP Basic Auth
  - Domain: lab.getqts.com
  - API Enabled: Yes
```

### Note Items (API Keys, Configs)
```
Title: Service Name - Config / Key
Content: Full config or key text
```

**Example: Telegram**
```
Title: Telegram Bot (Zangbot) - Token
Content:
  Bot Token: 123456789:ABCDefGHI...
  Chat ID: 987654321
  Owner: zangetsu
```

---

## Bitwarden CLI Access

### Install CLI
```bash
# macOS
brew install bitwarden-cli

# Ubuntu/Linux
sudo apt install bitwarden-cli
# or
npm install -g @bitwarden/cli

# Verify
bw --version
```

### Login
```bash
bw login your-email@example.com
# Prompts for master password (interactive)

# Or via environment variable (less secure)
export BW_PASSWORD="master_password"
bw login your-email@example.com --passwordenv BW_PASSWORD
```

### Get Credential
```bash
# Get item by name
bw get item "Vodia PBX (QTS Lab)"

# Get password only
bw get password "Vodia PBX (QTS Lab)"

# Get username only
bw get username "Vodia PBX (QTS Lab)"

# List all items
bw list items

# Export all (encrypted)
bw export
```

### API Endpoint (From Note Item)
```bash
# Get Telegram token from note
bw get item "Telegram Bot (Zangbot) - Token" | jq .notes
```

---

## Browser Extension (Web UI Access)

### Install
- Chrome: https://chrome.web store.google.com/detail/...
- Firefox: Firefox Add-ons
- Safari: App Store

### Usage
1. Click Bitwarden icon → Unlock vault
2. Right-click username field → Select credential
3. Auto-fills login form
4. Click lock icon to lock vault (after 5 min idle)

### Keyboard Shortcut (Auto-fill)
```
Ctrl+Shift+L  (Windows/Linux)
Cmd+Shift+L   (macOS)
```

---

## Secure Storage Best Practices

### ✅ DO THIS
- ✅ Use strong master password (20+ chars, mixed case, numbers, symbols)
- ✅ Enable 2FA on Bitwarden account
- ✅ Store master password in secure location (MacBook Keychain, 1Password for master)
- ✅ Export vault quarterly (backup to encrypted external drive)
- ✅ Rotate infrastructure credentials every 90 days
- ✅ Use unique password per service
- ✅ Enable fingerprint unlock on devices
- ✅ Keep Bitwarden app updated
- ✅ Log out after sensitive operations
- ✅ Use CLI for automation (not password literals)

### ❌ NEVER DO THIS
- ❌ Never hardcode Bitwarden password in scripts
- ❌ Never share master password via email/chat
- ❌ Never store master password in plaintext files
- ❌ Never auto-fill passwords on public Wi-Fi (use VPN)
- ❌ Never screenshot credentials
- ❌ Never leave vault unlocked on shared machine
- ❌ Never use same password for Bitwarden as other services
- ❌ Never export vault without encryption
- ❌ Never store vault export in cloud (unencrypted)
- ❌ Never disable 2FA

---

## Dual Storage Strategy

**Primary: Bitwarden (synced across devices)**
- Web UI: Always up-to-date
- CLI: Access from terminal
- Browser ext: Auto-fill on forms
- Devices: Desktop + mobile synced
- Recovery: Bitwarden export available

**Backup: Hermes Local Vault** (encrypted, offline)
- File: `~/.hermes/default/vault/vodia-*.json`
- Access: Local machine only
- Sync: Manual (updated when credentials change)
- Purpose: Offline access if Bitwarden down

**Cascade handling:**
```
Credentials needed
    ↓
Try Bitwarden (online)  → Success: use it
    ↓ (if offline)
Try Hermes vault (local) → Success: use it
    ↓ (if both fail)
Escalate: Ask user manually (last resort)
```

---

## Backup & Recovery

### Export Vault (Encrypted)
```bash
# Via CLI
bw export --organizationId (optional)  # Creates .encrypted.json

# Via Web UI
1. Settings → Tools → Export Vault
2. Format: Encrypted JSON (recommended) or plaintext
3. Choose strong password (different from master)
4. Save to secure location
```

### Restore from Export
```bash
# If Bitwarden account compromised:
1. Log in to Bitwarden web
2. Settings → Tools → Import Data
3. Choose exported file
4. Select format (encrypted or plaintext)
5. Import
```

### Emergency Access (Master Password Lost)
```bash
# If master password lost, no recovery possible
# Bitwarden has no backdoor (by design)
# Solution: Use emergency access contacts

1. Settings → Account → Set up emergency access
2. Add trusted contact (friend, family)
3. If locked out, contact can access vault (with 30-day wait)
```

---

## Cascading Effects

**When Bitwarden account compromised:**
- ❌ All stored passwords exposed (change all of them)
- ❌ 2FA bypass possible (re-secure devices)
- ❌ SSH keys compromised (regenerate)
- ❌ API tokens exposed (rotate immediately)

**When master password weak:**
- ❌ Brute-force attack possible
- ❌ All credentials at risk

**When Bitwarden offline (outage):**
- ✅ Hermes vault (local backup) works
- ✅ Browser cache may help (if recently unlocked)
- ❌ Cannot sync new credentials until online

**When 2FA disabled:**
- ❌ Account hijackable via password compromise alone

---

## Troubleshooting

### Vault Won't Unlock
```bash
# Check if logged in
bw status

# Login again
bw login your-email@example.com

# If locked, unlock
bw unlock [master_password]
```

### CLI Returns "unauthorized"
```bash
# Check session
bw status

# Re-authenticate
bw logout
bw login your-email@example.com

# Export session token (for scripts)
export BW_SESSION="session_token_here"
```

### Lost Master Password
```bash
# No recovery possible (by design)
# Use emergency access if set up, or:
# 1. Create new account
# 2. Restore from export backup
# 3. Update all credentials
```

### Sync Delay (New Password Not Appearing)
```bash
# Manual sync
bw sync

# Check if password saved
bw list items | grep "service_name"
```

---

## Monthly Maintenance

**1st of each month:**
1. Review stored credentials (60+ days old?)
2. Rotate infrastructure passwords
3. Check 2FA status (still enabled?)
4. Update Bitwarden app
5. Export encrypted backup
6. Verify Hermes vault is current

**Quarterly (every 3 months):**
1. Full credential rotation
2. Audit access logs (if available)
3. Backup to external drive
4. Update emergency access contacts

---

## Integration with Hermes

### Hermes Vault Fill (Browser)
```python
# In Hermes agent:
from hermes_tools import browser_vault_fill

# Fill login form from Bitwarden
browser_vault_fill(handle="vodia-pbx-qts-lab")
# ↓ User unlocks Bitwarden in UI
# ↓ Password auto-filled into form
```

### Hermes Vault List
```python
# List all saved logins
from hermes_tools import browser_vault_list

result = browser_vault_list()
# Returns: handles, labels, identifiers (no passwords)
```

### Environment Variables (CI/CD)
```bash
# In GitHub Actions or Hostinger cron:
export VODIA_USER=$(bw get username "Vodia PBX")
export VODIA_PASS=$(bw get password "Vodia PBX")

# Use in script
curl -u $VODIA_USER:$VODIA_PASS https://...
```

---

## Credential Rotation

### Vodia (Every 90 days)
```bash
# 1. Generate new password (20+ chars)
NEW_PASS="$(openssl rand -base64 20)"

# 2. Change in Vodia web UI
# Settings → Administrators → Change password

# 3. Update Bitwarden
bw edit item "Vodia PBX (QTS Lab)"
# Update password field

# 4. Update Hermes vault
# Manually edit ~/.hermes/default/vault/vodia-*.json

# 5. Update bot .env
# Edit /opt/vodia-bot/.env with new password
```

### Hostinger SSH Key (Every 180 days)
```bash
# 1. Generate new key
ssh-keygen -t ed25519 -C "zangetsu@hostinger" -f ~/.ssh/id_ed25519_new

# 2. Add to Hostinger
ssh-copy-id -i ~/.ssh/id_ed25519_new root@hostinger-vps

# 3. Update Bitwarden (add note with new key path)
# 4. Keep old key 30 days for rollback
# 5. Delete old key after tested
```

---

## Before ANY Credential Change

1. **Backup vault** (export encrypted JSON)
2. **List affected systems** (what services use this credential?)
3. **Show change plan** (which credentials changing, why?)
4. **Wait for approval**
5. **Execute** (update credential)
6. **Verify** (test in all systems)
7. **Sync** (Bitwarden → Hermes vault)

---

**Last Updated:** 2026-09-18 | Status: PRODUCTION ACTIVE (Dual-store verified)

