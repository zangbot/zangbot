# Home Network Vuln Scan — Full Results
# Date: 2026-09-27
# Scanner: zangji-3b — phases 1-6 complete
# Subnet: 192.168.5.0/24

---

## Summary

- **Hosts:** 25
- **Open ports:** 136
- **Vulnerabilities flagged:** 62 (VULNERABLE or LIKELY VULNERABLE)
- **Scan time:** ~45 minutes total (T4 aggressive)
- **Bitdefender:** Fired on zanmac-01 — detection working ✅

---

## CVE Findings — What Was Found

### CVE-2011-3192 — Apache Range Header DoS (CONFIRMED VULNERABLE)
- **Hosts affected:** .14 (Ugreen), .15 (zangohana), .16 (zangohana NIC 2)
- **What it is:** Apache HTTP server Range header DoS — allows remote attacker
  to exhaust server memory/CPU with a crafted request
- **Severity:** Medium — DoS only, not code execution
- **Reality check:** This is a Synology DSM internal Apache service and Ugreen
  hub. Not directly internet-exposed. Low real-world risk at home.
- **On a client network:** Flag it. Old Apache version = patch needed.

### CVE-2007-6750 — Apache mod_proxy Slowloris DoS (LIKELY VULNERABLE)
- **Hosts affected:** .14, .15, .16 — same Synology/Ugreen stack
- **What it is:** Slowloris-style attack — holds connections open to exhaust
  Apache thread pool
- **Severity:** Low-Medium — DoS only
- **Reality check:** Internal services, not internet-facing. Same fix as above.
- **On a client network:** Flag alongside CVE-2011-3192 — both point to
  unpatched Apache on internal management interfaces.

### CVE-2005-3299 — phpMyAdmin Local File Inclusion (LIKELY VULNERABLE)
- **Hosts affected:** .14, .15, .16
- **What it is:** Local file inclusion in phpMyAdmin — attacker can read
  arbitrary files from the server
- **Severity:** Medium-High IF internet exposed
- **Reality check:** Synology DSM ships phpMyAdmin internally. Not exposed
  externally. Still worth noting.
- **On a client network:** Hard flag if phpMyAdmin is exposed to LAN.

---

## Per-Host Assessment

| IP | Device | Findings | Risk (home) | Risk (client) |
|---|---|---|---|---|
| .1 | UniFi Gateway | None | ✅ Clean | ✅ Expected |
| .2 .3 | UniFi APs | None | ✅ Clean | ✅ Expected |
| .5 | Gaming PC | None from vuln scripts | ✅ | RDP/VNC flag |
| .10 | zanmac-01 | None | ✅ Clean | ✅ |
| .14 | Ugreen hub | CVE-2011-3192, CVE-2007-6750, CVE-2005-3299 | ⚠️ Low | 🚨 Flag |
| .15 | zangohana | CVE-2011-3192, CVE-2007-6750, CVE-2005-3299 | ⚠️ Low | 🚨 Flag |
| .16 | zangohana NIC2 | CVE-2011-3192, CVE-2007-6750, CVE-2005-3299 | ⚠️ Low | 🚨 Flag |
| .116 | zangpachi | None from vuln scripts | ✅ | InfluxDB flag |
| .123 | zangji-3b | None | ✅ Clean | ✅ |
| All others | IoT/Amazon | None significant | ✅ | Note |

---

## What This Means for Client Work

The CVEs found here are all on **Synology DSM and Ugreen internal services** —
Apache versions bundled with the firmware that haven't been updated.

On a client network these same findings would mean:
- Internal NAS or management interfaces running outdated Apache
- phpMyAdmin exposed on LAN — potential file read if attacker is on network
- Recommendation: firmware update, disable unused web services, firewall rules

**The important lesson:** These aren't exotic vulnerabilities. CVE-2011-3192
is from 2011. CVE-2005-3299 is from 2005. They still show up in 2026 because
firmware updates get skipped. That's a finding that resonates with clients —
"this vulnerability is old enough to vote."

---

## Your Home Network — Action Items

| Finding | Action | Priority |
|---|---|---|
| Synology Apache CVEs | Update DSM firmware | LOW — not internet exposed |
| Ugreen hub CVEs | Check for firmware update | LOW |
| zangpachi InfluxDB | Remove on rebuild | MED — remove before field use |
| IoT on main VLAN | Create IoT VLAN | LOW — future hardening |

---

## Baseline Confirmed

This scan is your home network baseline. On a client visit:
- Run the same suite
- Compare findings against this baseline
- Anything worse than your own home network = immediate finding
- Anything similar = document and prioritize with client

**Files pulled to Mac:**
- `scans/20260927-1515/00-system.txt`
- `scans/20260927-1515/01-hosts.txt`
- `scans/20260927-1515/02-ports.txt`
- `scans/20260927-1515/03-services.txt`
- `scans/20260927-1515/04-vulns.txt`
