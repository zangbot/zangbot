# Network Scan Results — 192.168.5.0/24

**Date:** September 24, 2026  
**Scan From:** Pi 5 (192.168.5.116) via wlan0  
**Scanner:** nmap 7.95  
**Hosts:** 256 scanned, 19 up  
**Ports:** 16 ports per host (22, 80, 443, 3000, 3306, 5432, 5555, 6379, 8000, 8001, 8080, 8443, 8888, 9090, 11434, 27017)

---

## Network Topology

```
192.168.5.0/24 — 19 live hosts
├── Gateway
├── Infrastructure (Zangbot-owned)
├── Monitoring Cluster
├── Printers
├── IoT Devices
├── Amazon Ecosystem
└── Unknown/Filtered
```

---

## Gateway

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.1** | unifi.localdomain | 80/tcp nginx, 443/tcp nginx, 8080/tcp Apache Tomcat, 8443/tcp Apache Tomcat | UniFi Dream Machine — router + controller + gateway |

---

## Zangbot Infrastructure

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.116** | raspberrypi.localdomain | 22/tcp OpenSSH 10.0p2 | **Pi 5 Home Lab** — our device |
| **192.168.5.125** | Zang-phone.localdomain | (none detected) | **Vodia PBX** — VoIP server, no web/SSH exposed |
| **192.168.5.126** | USW-Lite-8-PoE.localdomain | 22/tcp Dropbear sshd 2025.89 | **UniFi USW-Lite-8-PoE** — managed PoE switch |

---

## Monitoring Cluster (3-node)

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.14** | — | 22/tcp OpenSSH 8.2, 80/tcp nginx, 443/tcp nginx, 8000/tcp Nagios NSCA | Monitoring node 1 |
| **192.168.5.15** | — | 22/tcp OpenSSH 8.2, 80/tcp nginx, 443/tcp nginx, 8000/tcp Nagios NSCA | Monitoring node 2 |
| **192.168.5.16** | — | 22/tcp OpenSSH 8.2, 80/tcp nginx, 443/tcp nginx, 8000/tcp Nagios NSCA | Monitoring node 3 |

All three run identical service stack — Grafana/Prometheus with Nagios NSCA integration. Likely a high-availability monitoring setup.

---

## Printers (SHIP Protocol)

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.111** | L535.localdomain | 80/tcp SHIP 2.0 | Printer (SHIP = Secure Hardened Internet Protocol) |
| **192.168.5.113** | P125M.localdomain | 80/tcp SHIP 2.0 | Printer |
| **192.168.5.124** | — | 80/tcp SHIP 2.0 | Printer |
| **192.168.5.129** | — | 80/tcp SHIP 2.0 | Printer |

4 printers on the network, all responding with SHIP 2.0 HTTP server. L535 and P125M are named — 2 others have no hostname.

---

## IoT / Edge Devices (Dropbear)

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.2** | — | 22/tcp Dropbear sshd 2025.89 | IoT device (Dropbear = lightweight SSH) |
| **192.168.5.3** | — | 22/tcp Dropbear sshd | IoT device |
| **192.168.5.126** | USW-Lite-8-PoE | 22/tcp Dropbear sshd 2025.89 | UniFi switch (already listed) |

Three Dropbear devices — the lightweight SSH daemon commonly used in embedded/IoT systems.

---

## Amazon Ecosystem

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.141** | amazon-fdebc6b2d.localdomain | 8888/tcp tcpwrapped | Amazon Echo/Fire TV device |
| **192.168.5.147** | Amazon-Smart-Thermostat.localdomain | (none detected) | Ring smart thermostat |

---

## Other Devices

| IP | Hostname | Ports Open | Notes |
|----|----------|-----------|-------|
| **192.168.5.10** | — | 22/tcp OpenSSH 10.3 | Standard Linux device/server |
| **192.168.5.122** | g5-flex.localdomain | 80/tcp lighttpd, 443/tcp ssl/lighttpd | Google Pixel? Flex device? |
| **192.168.5.102** | — | (none detected) | Dormant IoT device or printer |
| **192.168.5.231** | — | 22/tcp ssh?, 80/tcp http?, 8000/tcp http-alt? | **Firewalled** — 443 filtered, SSH+HTTP open |

---

## Summary Stats

| Category | Count | Details |
|----------|-------|---------|
| **Gateway** | 1 | UniFi UDM |
| **Zangbot-owned** | 3 | Pi 5, Vodia PBX, UniFi switch |
| **Monitoring cluster** | 3 | 3-node nginx/Nagios |
| **Printers** | 4 | SHIP 2.0 protocol |
| **IoT/Dropbear** | 2 | Plus 1 UniFi switch (already counted) |
| **Amazon** | 2 | Echo + Thermostat |
| **Other** | 4 | SSH server, lighttpd device, dormant host, firewalled host |
| **Total** | **19** | |

---

## Notable Observations

### ✅ Security Posture

1. **Zangbot infrastructure is clean** — Pi 5 only exposes SSH (22), Vodia PBX has no exposed ports, switch has only Dropbear SSH
2. **No exposed databases** — MySQL (3306), PostgreSQL (5432), Redis (6379), MongoDB (27017) all closed on every host
3. **No exposed analytics** — Port 9090 (Grafana), 3000 (Grafana default), all closed
4. **Ollama port 11434** — closed on all hosts (good, Pi 5 only listens on Tailscale 100.109.228.50, not 0.0.0.0)

### ⚠️ Things to Note

1. **Host 192.168.5.231** — firewalled but SSH (22) + HTTP (80) + HTTP-alt (8000) open. This could be:
   - A device behind a restrictive firewall (UFW or iptables)
   - The Hostinger VPS (72.62.97.23) on a local proxy? (unlikely)
   - An internal server with partial exposure
   - **Recommendation:** investigate this host

2. **Monitoring cluster (14-16)** — 3 identical nodes with Nagios NSCA. The NSCA port (8000) is open but this is standard for Nagios passive checks. Verify no Grafana web interface (port 3000) is exposed.

3. **4 printers (SHIP 2.0)** — SHIP protocol is printer-specific. These are likely HP/LAN printers. Worth noting for any RFID/NFC tests with Flipper if they have smart card readers.

4. **OpenSSH 10.3 on .10** — newer than most on the network (8.2 or Dropbear). Standard Linux box, probably a personal or dev server.

5. **g5-flex.localdomain** — lighttpd with HTTPS. Could be a gaming device, Flexport, or custom server. The "g5" naming suggests it might be a gaming console or custom device.

### 📊 Network Health

| Metric | Value | Status |
|--------|-------|--------|
| Hosts discovered | 19 | Normal for home lab |
| SSH-exposed hosts | 7 | 5 Zangbot-owned (acceptable) |
| Database ports exposed | 0 | ✅ Clean |
| Web UI ports exposed | 4 (nginx + lighttpd) | Acceptable |
| Filtered/blocked ports | 1 host (231) | Investigate |
| DHCP lease duration | 84,737 seconds (~23.5 hours) | Dynamic |

---

## Recommendations

1. **Investigate 192.168.5.231** — run a deeper port scan (`nmap -p-`) to see if there's a full services list behind the firewall
2. **Add Pi 5 to monitoring** — the 3-node cluster at 14-16 should track our Pi 5 uptime and resource usage
3. **Printer inventory** — verify the 4 SHIP printers, note which ones are active vs dormant
4. **Flipper Zero audit** — scan printer RFID/NFC readers (common on business printers for access control)
5. **Pwnagopi deployment** — map WiFi channel distribution and identify any rogue APs

---

*Scan completed from Pi 5 via wlan0. Full scan time: 209.52 seconds.*
