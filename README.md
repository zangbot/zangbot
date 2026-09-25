# Zangbot — MSP Infrastructure Automation

**Status:** Phase 3 — Field Kit Deploying  
**Owner:** Zangetsu | MSP operator, infrastructure automator

---

## What This Is

A distributed automation and observability stack for MSP field operations. Local-first inference, webhook-driven alerting, and a field agent that does network recon, security audits, and on-site diagnostics autonomously.

---

## Hardware Fleet

| Node | Role | Hardware | Status |
|------|------|----------|--------|
| **zanmac-01** | Command Center / Inference HQ | Mac Studio M5 Max 64GB | ✅ Live |
| **zangpachi** | Field Ops Agent | Raspberry Pi 5 8GB + Pironman 5 Pro Max | 🔄 Deploying |
| **zangagotchi** | Wi-Fi Recon / Handshake Collector | Pi Zero 2W + Waveshare 2.13" e-ink | 🔧 Rebuilding |
| **Flipper Zero** | Multi-tool: sub-GHz, NFC, IR, BadUSB | Flipper Zero (Unleashed FW) | ✅ In kit |
| **UniFi Travel Router** | Field network / VPN tunnel home | UniFi Travel Router | ✅ In kit |
| **LoRa Devices** | Sensor mesh / long-range comms | LoRa + ChirpStack | 📋 Planned |
| **zanglap-10124** | Work laptop | ASUS TUF A16, Ryzen 7, 32GB, Win11+Linux | ✅ Active |
| **Hostinger VPS** | Always-on router / fallback inference | 2 vCPU / 8GB Ubuntu 24.04 | ✅ Live |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    COMMAND CENTER                         │
│  zanmac-01 — Mac Studio M5 Max 64GB                      │
│  Ollama (Qwen2.5:7b primary, Phi3 fallback)              │
│  Hermes Agent · Bitwarden · UniFi API · Vodia API        │
└─────────────────────┬────────────────────────────────────┘
                      │ Tailscale mesh
          ┌───────────┼────────────────┐
          │           │                │
┌─────────▼──────┐  ┌─▼───────────┐  ┌▼──────────────────┐
│  Hostinger VPS │  │  zangpachi  │  │  zangagotchi      │
│  FastAPI 8001  │  │  Pi 5 8GB   │  │  Pi Zero 2W       │
│  Webhook route │  │  Pironman   │  │  Pwnagotchi FW    │
│  CDR analytics │  │  500GB NVMe │  │  WaveShare e-ink  │
└────────────────┘  │  Grafana    │  └───────────────────┘
                    │  ntopng     │         ↓ rsync
                    │  Kismet     │    handshakes → NVMe
                    │  Nuclei     │    hashcat offline
                    └──────┬──────┘
                           │ USB/GPIO
                    ┌──────▼──────────────────┐
                    │  FIELD KIT              │
                    │  Flipper Zero           │
                    │  UniFi Travel Router    │
                    │  LoRa sensor mesh       │
                    └─────────────────────────┘
```

---

## Field Kit — zangpachi Tool Suite

**Network Recon:** nmap · arp-scan · masscan · netdiscover  
**Vulnerability:** nuclei · nikto · enum4linux-ng · gobuster  
**Wireless:** kismet · aircrack-ng · reaver · wifite  
**Packet Capture:** Wireshark · termshark · tcpdump · Zeek  
**Traffic Analysis:** ntopng · bandwhich · nethogs · iftop  
**Dashboards:** Grafana on 4.3" Pironman touch screen  
**Local AI:** Ollama + phi3:mini (offline capable)  
**Automation:** Flipper Zero GPIO/UART bridge  
**Wi-Fi Recon:** zangagotchi syncs handshakes to NVMe, hashcat cracks offline  
**LoRa:** Mosquitto MQTT + ChirpStack (planned)

---

## Connections (Verified)

| System | Endpoint | Status |
|--------|----------|--------|
| Ollama inference | localhost:11434 | ✅ Live |
| Hostinger VPS SSH | 72.62.97.23 | ✅ Live |
| Zangbot FastAPI router | 72.62.97.23:8001 | ✅ Live |
| Vodia PBX REST API | lab.getqts.com | ✅ Live |
| UniFi Cloud API | unifi.ui.com | ✅ Live |
| Bitwarden vault | bw CLI | ✅ Live |
| Telegram bot | Hermes notify | ✅ Live |
| Analytics server | analytics.zangbot.online | ✅ Live |

---

## Repo Structure

```
zangbot/
├── index.html                  # zangbot.net — live site
├── README.md                   # this file
├── ZANGPACHI-MASTER-PLAN.md    # zangpachi full build plan
├── agents/                     # Hermes agent configs
├── docs/                       # reference guides
├── rag/                        # RAG system (in progress)
├── reference-guides/           # operational runbooks
├── vodia-integration/          # Vodia PBX automation
├── router-config.yaml          # Zangbot FastAPI router config
└── audit-connections.py        # infrastructure audit script
```

---

## Roadmap

- [x] Phase 1 — Mac Studio HQ online, local inference live
- [x] Phase 2 — VPS router deployed, all integrations verified
- [ ] Phase 3 — zangpachi field agent deployed *(in progress)*
- [ ] Phase 4 — zangagotchi rebuild + Wi-Fi recon pipeline
- [ ] Phase 5 — LoRa sensor mesh + ChirpStack
- [ ] Phase 6 — GitHub portfolio published
- [ ] Phase 7 — Local inference routing (Qwen primary, Claude fallback)
- [ ] Phase 8 — Vodia CDR analytics pipeline live

---

*Built by Zangetsu — MSP operator, infrastructure automator*  
*[zangbot.net](https://zangbot.net) · jdgnothing@gmail.com*
