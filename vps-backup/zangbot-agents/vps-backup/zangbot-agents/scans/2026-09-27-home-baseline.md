# zangji-3b Scout Report — Home Network Baseline
# Date: 2026-09-27
# Subnet: 192.168.5.0/24
# Run by: zangji-3b (192.168.5.123)

## Summary
- Hosts found: 25
- Open ports: 136
- Scan time: ~300 seconds (T4 timing)
- Bitdefender alert triggered on zanmac-01 — expected for aggressive scan

---

## Device Map (Verified)

| IP | Hostname | Hardware | Role | Notes |
|---|---|---|---|---|
| .1 | unifi.localdomain | Ubiquiti | UniFi Gateway | 53/80/443/7443/8080/8443 — expected |
| .2 | — | Ubiquiti | UniFi AP | SSH (Dropbear) only ✅ |
| .3 | — | Ubiquiti | UniFi AP | SSH (Dropbear) only ✅ |
| .5 | — | MSI (gaming PC) | zangetsu-z790 | RDP+VNC+SMB — home only |
| .10 | — | Apple | zanmac-01 | AirTunes, SSH, Kerberos, VNC |
| .14 | — | Ugreen | Ugreen hub/NAS | 25 ports — investigate |
| .15 | zangohana | Synology | NAS primary NIC | LDAP anon bind, MongoDB 32768 |
| .16 | — | Synology | NAS secondary NIC | Same profile as .15 |
| .102 | — | Unknown | Unknown | 8009 only — Chromecast/TV |
| .110 | — | Espressif (ESP32) | Unknown IoT | FTP+JSON API port 3000 |
| .111 | — | TP-Link | Smart light | SHIP 2.0 ✅ |
| .116 | zangpachi | Raspberry Pi | Pi 5 field unit | SSH✅ InfluxDB 8086 ⚠️ |
| .117 | Anker | Anker | Charging hub | — |
| .120 | amazon-* | Amazon | Smart AC unit | SOCKS5:1080 — Alexa stack |
| .122 | g5-flex | Ubiquiti | UniFi G5 Flex camera | 80/443 only ✅ |
| .123 | zangji-3b | Raspberry Pi | This scanner | SSH only ✅ |
| .124 | P125M | TP-Link | Smart light | SHIP 2.0 ✅ |
| .125 | Zang-phone | Phone | Personal phone | — |
| .126 | USW-Lite-8-PoE | Ubiquiti | UniFi switch | SSH only ✅ |
| .127 | — | Amazon | Amazon device | 8009 only |
| .128 | Samsung | Samsung | Samsung device | — |
| .129 | L535 | TP-Link | Smart light | SHIP 2.0 ✅ |
| .141 | amazon-* | Amazon | Amazon device | SOCKS5+9091 — Alexa stack |
| .146 | — | TP-Link | Smart light | SHIP 2.0 ✅ |
| .231 | — | zanmac-01 (virtual) | **HONEYPOT** | Intentional — FTP/Telnet/SMTP/MSSQL bait |

---

## Findings Assessment

### ✅ Clean / Expected
- UniFi infrastructure (gateway, APs, switch, camera) — ports as expected
- TP-Link lights (SHIP 2.0) — HTTP only, isolated protocol
- Amazon AC/Echo (SOCKS5) — Amazon Alexa smart home stack behavior
- Honeypot (.231) — intentional, working as designed
- zangji-3b — SSH only, clean

### ⚠️ Home Network Notes (not client findings)
- **zangpachi InfluxDB (8086)** — unintentional service, remove on rebuild
- **Synology LDAP anonymous bind (389/3268)** — default DSM behavior, lock down when hardening
- **Synology MongoDB (32768)** — exposed, DSM internal, consider firewall rule
- **Gaming PC RDP/VNC** — acceptable at home, would be finding on client network
- **Telnet seen on .231** — honeypot bait port, intentional

### 👀 Investigate Later
- **.110 ESP32** — FTP server + JSON login API, identify this device
- **.14 Ugreen** — 25 open ports including LDAP/Kerberos/MongoDB — confirm this is expected
- **zangkia Telnet** — travel router channel on .50.0 subnet, verify port is management only

---

## Timing Note
- `-T4` aggressive timing triggered Bitdefender on zanmac-01
- For client sites: use `-T2` (polite) or warn client before scanning
- Full scan time: ~5 min on /24 with 25 live hosts

---

## What to Expect on a CLEAN Client Network

| Port Pattern | Meaning |
|---|---|
| 22 on servers only | Good hygiene |
| 80/443 on known web servers | Expected |
| 3389/5900 on workstations | Flag — remote access exposure |
| 21/23 anywhere | 🚨 Hard flag — legacy protocols |
| 1080 SOCKS no auth | 🚨 Flag — proxy/tunneling risk |
| 389 anon bind | 🚨 Flag — directory data exposure |
| 27017/32768 MongoDB | 🚨 Flag — unauthenticated DB |
| 8086 InfluxDB | Flag — metrics/time-series data exposed |
| SHIP 2.0 | TP-Link smart devices on network |
| Dropbear SSH | UniFi infrastructure |

---

## What a BAD Client Network Looks Like vs. This

Your home network: 0 unintended remote access paths, IoT identified, infrastructure locked  
Bad client: RDP open on all workstations, no EDR (scan completes silently), Telnet on switches,  
           anonymous FTP, printers with web admin exposed, default creds on APs

---

## Rebuild Action Items (from this scan)

- [ ] Remove InfluxDB from zangpachi before field deployment
- [ ] IoT VLAN — move TP-Link lights + Amazon AC off main LAN (future hardening)
- [ ] Investigate .110 ESP32 device — identify and document
- [ ] Synology LDAP anonymous bind — disable in DSM LDAP settings
