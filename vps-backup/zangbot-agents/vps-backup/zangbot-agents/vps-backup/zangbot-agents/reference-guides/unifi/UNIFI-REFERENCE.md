# UniFi Network Reference Guide — Bot Edition

**Version:** UniFi Network Application v8.0+ & Cloud Manager  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Source:** Official UniFi API docs + operational experience

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Local Controller API** | `https://<controller-ip>:8443/api/` |
| **Cloud API** | `https://api.ui.com/v1/` |
| **Auth** | Session cookie (local) or API key (cloud) |
| **Format** | JSON request/response |
| **Protocol** | HTTPS only (self-signed certs OK on local) |
| **Rate Limit** | ~10,000 req/min (cloud) |

---

## API Choice: Local vs Cloud

### Local Controller API (Recommended for Lab)
- **Endpoint:** `https://<controller-ip>:8443/api/`
- **Auth:** Session cookie (login first, get cookie)
- **Use case:** Single site, full control, offline works
- **Limitation:** Requires running controller, port 8443 access

### Cloud API (Recommended for Multi-Site)
- **Endpoint:** `https://api.ui.com/v1/`
- **Auth:** API key in `X-API-KEY` header
- **Use case:** Multiple sites, SaaS model, no local controller
- **Limitation:** Requires cloud account, online only

**Decision for Zangbot:** Start with local (lab.getqts.com if available), migrate to cloud API for scale.

---

## Authentication

### Local Controller (Session Cookie)

**Step 1 — Login (Get Session)**
```bash
curl -k -X POST https://192.168.1.1:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' \
  -c cookies.txt
```

**Step 2 — Use Cookie in Subsequent Calls**
```bash
curl -k https://192.168.1.1:8443/api/s/default/stat/device \
  -b cookies.txt
```

### Cloud API (API Key)

**Generate API key:**
1. Login to UniFi Cloud Manager (ui.com)
2. Account → Settings → API Clients
3. Create new key
4. Store securely (Bitwarden + vault)

**Use in requests:**
```bash
curl https://api.ui.com/v1/sites \
  -H "X-API-KEY: your_api_key_here"
```

---

## Core Operations

### List Sites

**Local:**
```
GET /api/self/sites
Response: Array of sites with site IDs
```

**Cloud:**
```
GET /api/v1/sites
Header: X-API-KEY
Response: Array of sites with site IDs
```

---

### VLANs (Local Controller)

#### List VLANs
```
GET /api/s/{site}/rest/networkconf
Response: Array of network objects (each is a VLAN)
```

#### Get Single VLAN
```
GET /api/s/{site}/rest/networkconf/{network_id}
Response: {name, vlan, ipv4_address, ipv4_netmask, ...}
```

#### Create VLAN
```
POST /api/s/{site}/rest/networkconf
Body:
{
  "name": "VLAN 40 - Phones",
  "vlan": 40,
  "ipv4_address": "10.0.40.1",
  "ipv4_netmask": "255.255.255.0",
  "domain_name": "phones.local"  // optional
}
Response: {_id, name, vlan, ...} (created object)
```

#### Update VLAN
```
PUT /api/s/{site}/rest/networkconf/{network_id}
Body: {key: value, ...}  // partial update
Response: {} (empty on success)
```

#### Delete VLAN
```
DELETE /api/s/{site}/rest/networkconf/{network_id}
Response: {} (empty on success)
```

---

### Devices (Local Controller)

#### List Devices
```
GET /api/s/{site}/stat/device
Response: Array of device objects (APs, switches, gateways)
```

#### Get Device Details
```
GET /api/s/{site}/stat/device/{device_id}
Response: {name, model, ip, mac, uptime, state, ...}
```

#### Update Device (e.g., Restart)
```
PUT /api/s/{site}/rest/device/{device_id}
Body: {"reboot": {}}
Response: {} (empty, device will reboot)
```

---

### WiFi Networks (SSIDs)

#### List WiFi Networks
```
GET /api/s/{site}/rest/wlanconf
Response: Array of SSID objects
```

#### Create WiFi Network
```
POST /api/s/{site}/rest/wlanconf
Body:
{
  "name": "Guest Network",
  "ssid": "GuestWiFi",
  "security": "wpapsk",
  "wpa_mode": "WPA2",
  "wpa_enc": "CCMP",
  "x_passphrase": "strong_password_here",
  "is_guest": true
}
Response: {_id, name, ssid, ...} (created object)
```

#### Update WiFi Network
```
PUT /api/s/{site}/rest/wlanconf/{wlan_id}
Body: {key: value, ...}  // partial update
Response: {} (empty on success)
```

---

## Site IDs and Network IDs

### Find Site ID
1. Call `GET /api/self/sites`
2. Look for site name (e.g., "House of Law")
3. Extract `_id` field (alphanumeric like `5f8a0c1234abcd`)

### Find Network ID (VLAN)
1. Call `GET /api/s/{site}/rest/networkconf`
2. Look for network by `name` or `vlan`
3. Extract `_id` field

### Common Site Names (Lab)
- `default` — Default site
- `House of Law` — Customer site
- `TechHouse Lab` — Lab environment

---

## Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Proceed |
| 400 | Bad request | Fix JSON payload, check site/network IDs |
| 401 | Auth failed | Re-login, refresh cookie, check API key |
| 403 | Forbidden | Check permissions, verify site access |
| 404 | Not found | Verify site ID, network ID, device ID exists |
| 500 | Server error | Check controller logs, retry |

---

## Constraints & Limits

| Constraint | Value | Notes |
|-----------|-------|-------|
| Max VLANs per site | 255 | VLAN IDs 1-255 (VLAN 1 reserved) |
| Max WiFi networks | 32 | Per access point (total: 32 SSID) |
| Max devices per site | 1000+ | Depends on controller hardware |
| VLAN naming | 255 chars | UTF-8 allowed |
| SSID length | 32 chars | Max WiFi standard |
| Password length | 64 chars | WiFi WPA-PSK limit |
| Client timeout | 5 min idle | Auto-disconnect if no traffic |

---

## Cascading Dependencies

**When changing a VLAN:**
- ❌ Devices on that VLAN → May lose connectivity if gateway IP changes
- ❌ SIP trunks routing to that VLAN → May re-route if IP changes
- ❌ DHCP scope on that VLAN → Clients won't get IPs if scope disabled
- ❌ Port group assigned to that VLAN → Ports become inaccessible

**When creating a new WiFi network:**
- ✅ Existing WiFi networks → Unaffected (separate SSIDs)
- ❌ Channel conflict → May cause interference if same channel as others
- ❌ Client roaming → Slower if same SSID name as existing network

**When changing default gateway (routing):**
- ❌ All downstream devices → May lose internet/uplink
- ❌ VoIP trunks → May fail if gateway unreachable
- ❌ DNS resolution → May break if DNS server unreachable via new gateway

**When disabling a device:**
- ❌ Clients connected to device → Will disconnect
- ❌ PoE devices (phones, APs) → Lose power if PoE disabled
- ❌ Mesh network → May fragment if mesh node disabled

---

## Troubleshooting

### API Returns 401 Unauthorized (Local Controller)

**Cause:** Session expired or cookie not sent.

**Fix:**
1. Re-login: `POST /api/auth/login` with credentials
2. Save new cookie: `curl ... -c cookies.txt`
3. Retry with new cookie: `curl ... -b cookies.txt`

---

### Cannot Create VLAN (400 Bad Request)

**Common issues:**
1. VLAN ID already in use (check `vlan` field)
2. Network IP overlaps with existing VLAN (check `ipv4_address`)
3. Malformed JSON (check syntax)

**Fix:**
1. Query existing VLANs: `GET /api/s/{site}/rest/networkconf`
2. Find available VLAN ID (1-255, not in use)
3. Use unique subnet: `10.0.X.0/24` (unique X value)
4. Retry create with unique values

---

### WiFi Network Won't Broadcast (SSID Hidden)

**Cause:** `enabled: false` or `hidden_ssid: true` in config.

**Fix:**
1. Query WiFi: `GET /api/s/{site}/rest/wlanconf/{wlan_id}`
2. Check `enabled` and `hidden_ssid` fields
3. Update: `PUT .../wlanconf/{wlan_id}` with `{"enabled": true, "hidden_ssid": false}`
4. Wait 30 sec for AP to refresh

---

### Devices Losing Connectivity After VLAN Change

**Cause:** Default gateway IP changed or VLAN removed from port group.

**Fix:**
1. Verify VLAN still exists: `GET /api/s/{site}/rest/networkconf`
2. Verify device port group includes VLAN: `GET /api/s/{site}/rest/portconf`
3. Ping gateway IP from device: `ping 10.0.X.1`
4. If gateway unreachable: revert VLAN IP change and retry

---

## Known Issues & Workarounds

| Issue | Version | Workaround |
|-------|---------|-----------|
| Local controller slow on large sites (100+ devices) | v8.0+ | Use Cloud API instead, or upgrade controller hardware |
| Cookie expires after 1 hour (local) | all | Re-login periodically or use Cloud API with persistent key |
| VLAN deletion fails if ports still assigned | all | Remove VLAN from all port groups first, then delete |
| WiFi client roaming slow between APs | all | Use same SSID/security on all APs, keep channel consistent |

---

## Port Profiles & Device Configuration

### Port Profile (VLAN Assignment)

```
GET /api/s/{site}/rest/portconf
Response: Array of port profile objects
```

Each port can be assigned a VLAN or multiple VLANs (tagged).

**Common port configurations:**
- `all` — Default (all VLANs, native vlan 1)
- `corporate` — VLAN 10 (office)
- `guest` — VLAN 20 (guest network)
- `phones` — VLAN 40 (SIP trunks, Vodia)

---

## Before ANY UniFi Change

1. **Pull this guide** (never guess UniFi API)
2. **Query current state** (GET endpoints)
3. **Check cascading effects** (VLAN → devices → VoIP?)
4. **Build dependency map** (what breaks if I do this?)
5. **Show plan** (before/after, rollback steps)
6. **Wait for approval** (explicit "Go")
7. **Execute** (after approval)
8. **Verify** (read back system, check device status)

---

## Common Workflows

### Add New VLAN for SIP Trunks

1. List existing VLANs: `GET /api/s/{site}/rest/networkconf`
2. Choose unused VLAN ID (e.g., 40)
3. Choose unused subnet (e.g., 10.0.40.0/24)
4. Create: `POST /api/s/{site}/rest/networkconf` with `vlan: 40, ipv4_address: 10.0.40.1`
5. Assign to switch ports via port group
6. Route from gateway (firewall rules)
7. Test: Ping gateway from SIP endpoint

### Create Guest WiFi Network

1. List existing WiFi networks: `GET /api/s/{site}/rest/wlanconf`
2. Choose unused SSID name
3. Create: `POST /api/s/{site}/rest/wlanconf` with `is_guest: true, security: wpapsk`
4. Verify broadcast: Check `enabled: true, hidden_ssid: false`
5. Test: Connect device to SSID

---

## Official Documentation

- **UniFi Network API:** https://ubntech.wiki/books/unifi-api (local + cloud)
- **UniFi Cloud Manager:** https://ui.com/
- **Related Skills:** live-change-safety-framework

---

**Last Updated:** 2026-09-18 | Status: READY FOR LAB TESTING

