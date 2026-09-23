# Zangbot Reference Guides

**Bot-friendly markdown references for all systems. Updated monthly. Single source of truth for planning.**

## Systems Covered

| System | Last Updated | Guide | Focus |
|--------|--------------|-------|-------|
| vodia | 2026-09-18 | [VODIA-REFERENCE.md](vodia/VODIA-REFERENCE.md) | REST API, extensions, ring groups, SIP trunks, deployment |
| hostinger | 2026-09-18 | [HOSTINGER-REFERENCE.md](hostinger/HOSTINGER-REFERENCE.md) | VPS management, SSH, systemd, bot deployment, troubleshooting |
| telegram | 2026-09-18 | [TELEGRAM-REFERENCE.md](telegram/TELEGRAM-REFERENCE.md) | Bot API, webhooks, message formatting, approval buttons |
| unifi | 2026-09-18 | [UNIFI-REFERENCE.md](unifi/UNIFI-REFERENCE.md) | Controller API (local + cloud), VLANs, WiFi, device management |
| ubuntu | 2026-09-18 | [UBUNTU-REFERENCE.md](ubuntu/UBUNTU-REFERENCE.md) | Linux Mint package mgmt, Python env, systemd, network, firewall |
| macos | 2026-09-18 | [MACOS-REFERENCE.md](macos/MACOS-REFERENCE.md) | M5 Pro setup, Homebrew, local LLM (Ollama), launchd, SSH config |
| bitwarden | 2026-09-18 | [BITWARDEN-REFERENCE.md](bitwarden/BITWARDEN-REFERENCE.md) | Vault management, CLI, credential storage, rotation, 2FA, backup |
| hermes | TBD | TBD | Agent, vault, skills, tool integration, desktop app |

## How to Use

When planning a change:
1. **Load the reference guide** for the system(s) you're touching
2. **Cross-reference dependencies** (e.g., "If I change VLAN, what affects SIP trunks?")
3. **Build cascade map** before writing the plan
4. **Include docs-backed constraints** in the plan

## Update Schedule

- **Monthly**: Pull latest official docs, compress into bot-friendly format
- **Trigger**: Any breaking change discovered during operations
- **Owner**: You confirm; I execute the update

## Template

Each system guide follows:
- **Overview**: What this system does, key APIs/endpoints
- **Authentication**: How to connect, credential format
- **Core Operations**: CRUD patterns, common tasks
- **Constraints & Limits**: Quotas, naming rules, max values
- **Troubleshooting**: Common failures, fixes, diagnostic commands
- **Dependencies**: What other systems this affects
- **Known Issues**: Version-specific bugs, workarounds
- **Links**: Official docs, issue trackers
