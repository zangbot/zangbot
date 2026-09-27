# zangohana Reference Guide — Synology NAS

**Codename:** zangohana  
**Hardware:** Synology DS423+ · Intel J4125 · 18GB RAM · 7TB storage · Dual NVMe  
**Role:** Storage, Memory, Always-On Local Server  
**Last Updated:** 2026-09-27  

---

## Quick Facts

| Aspect | Value |
|---|---|
| **LAN IP** | 192.168.5.15 |
| **DSM (HTTP)** | http://192.168.5.15:5000 |
| **DSM (HTTPS)** | http://192.168.5.15:5001 |
| **SSH Port** | 22 |
| **Primary user** | zangetsulv (admin) |
| **Bot user** | zangbot (SSH key auth) |
| **OS** | DSM 7.x |

---

## SSH Access

```bash
# Admin user
ssh zangetsulv@192.168.5.15

# Bot user (key-based)
ssh zangbot@192.168.5.15
```

**zangbot SSH key:** Deployed to `/var/services/homes/zangbot/.ssh/authorized_keys`  
**zangbot home:** `/var/services/homes/zangbot/`  
**zangbot shell:** `/bin/sh`  
**zangbot UID:** 1037 / GID: 100 (users group)

---

## sshd_config Key Settings

```
PasswordAuthentication yes
AllowTcpForwarding no
UsePAM yes
ChrootDirectory none
Subsystem sftp internal-sftp -f DAEMON -u 000

# Per-user overrides
Match User root
    AllowTcpForwarding yes
Match User admin
    AllowTcpForwarding yes
Match User anonymous
    AllowTcpForwarding no
```

**Note:** admin account is disabled — zangetsulv is the primary admin.  
**Note:** Always keep a backup admin account. Never delete the only admin.

---

## Volume Layout

| Volume | Size | Purpose | Status |
|---|---|---|---|
| /volume1/bkup | 1.7TB | Backups | ✅ Keep |
| /volume1/docker | 1.3GB | Docker containers | ✅ Keep |
| /volume1/PlexMediaServer | 5.1GB | Plex data | ✅ Keep |
| /volume1/photo | 0 | Photos (Synology Photos) | Review |
| /volume1/sinner | 4KB | Old/unused | 🗑️ Safe to delete |
| /volume1/web | 4KB | Old web files | 🗑️ Safe to delete |
| /volume1/web_packages | 0 | Empty | 🗑️ Safe to delete |
| /volume1/GGG | — | 101-year-old grandma — NEVER TOUCH | 🔒 Sacred |

---

## zangbot Shared Folder

Location: `/volume1/zangbot/`  
Purpose: Hermes/agent working directory, sync target from VPS and Mac

```bash
# Mount on Mac (SMB)
# Finder → Go → Connect to Server
# smb://192.168.5.15/zangbot
# User: zangbot / password: (Bitwarden)

# rsync to NAS
rsync -av ~/zangbot/backups/ zangbot@192.168.5.15:/volume1/zangbot/backups/
```

---

## Firewall / iptables

As of 2026-09-27 — iptables chains all ACCEPT (no rules):
```
Chain INPUT   (policy ACCEPT) — no rules
Chain FORWARD (policy ACCEPT) — no rules  
Chain OUTPUT  (policy ACCEPT) — no rules
```

**TODO:** Harden firewall. Lock down to LAN only. Restrict SSH source IPs.

---

## Backup Role — 3-2-1 Chain

```
zanmac-01 (Mac) — source of truth
      ↓ nightly rsync
zangohana (NAS) — local backup copy 2
      ↓ monthly pull
Hostinger VPS — offsite copy 3
```

Monthly backup script: `~/zangbot/scripts/synology-monthly-backup.sh`

---

## Docker on NAS

Docker is active on the NAS. Check running containers:
```bash
ssh zangetsulv@192.168.5.15 "sudo docker ps"
```

---

## Security Hardening TODO

- [ ] Enable NAS firewall — allow only LAN subnet
- [ ] Disable SSH password auth (key-only)
- [ ] Restrict SSH source to 192.168.5.0/24
- [ ] Review Docker containers and exposed ports
- [ ] Enable 2FA on DSM
- [ ] Audit shared folder permissions
- [ ] Set up fail2ban equivalent (Auto Block in DSM Security)

---

## Known Pitfalls

- `synoservicectl` not available in PATH for non-root users — use `sudo synoservicectl`
- sshd reload command: `sudo synoservicectl --reload sshd`
- Home directories: `/var/services/homes/<user>/` not `/home/`
- DSM web UI cert is self-signed — browser will warn on HTTPS
