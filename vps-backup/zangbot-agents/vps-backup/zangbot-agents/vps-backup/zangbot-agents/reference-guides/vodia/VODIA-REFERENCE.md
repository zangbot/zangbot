# Vodia PBX Reference Guide — Bot Edition

**Version:** 69.5 (QTS Lab)  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Source:** Official Vodia docs + operational experience

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Protocol** | HTTPS REST API |
| **Base URL** | `https://lab.getqts.com/rest` |
| **Auth** | HTTP Basic Auth (stateless) |
| **Format** | JSON request/response |
| **Rate Limit** | None documented |
| **TLS** | Self-signed OK (skip verification) |

---

## Authentication

### HTTP Basic Auth (Preferred)

```bash
curl -u username:password https://lab.getqts.com/rest/endpoint
```

**Credentials stored in:**
- Primary: Bitwarden vault (`Vodia PBX (QTS Lab)`)
- Backup: `~/.hermes/default/vault/vodia-lab-qts-new.json`

**Username format depends on scope:**

| Scope | Username | Example |
|-------|----------|---------|
| System | `admin` | `admin:password` |
| Domain | `admin@domain` | `admin@lab.getqts.com:password` |
| User | `ext@domain` | `1001@lab.getqts.com:password` |

### Pre-Flight Verification

Before any operation:
```bash
curl -k -u admin:PASSWORD https://lab.getqts.com/rest/system/session
```

Expected: HTTP 200 with JSON. If 403: API access not enabled in Vodia web UI.

---

## Core Operations

### List Domains
```
GET /rest/system/domains
Auth: admin:password
Response: Array of domain objects
```

**Common domains:**
- `lab.getqts.com` (Lab/Test)
- `houseoflaw.clearvoipusa.com` (House of Law)

---

### Extensions (CRUD)

#### List Extensions
```
GET /rest/domain/{domain}/userlist/extensions
Response: {ext_number: {settings}, ...}
```

#### Get Single Extension
```
GET /rest/domain/{domain}/user_settings/{ext}
Response: {name, password, email, state, ...}
```

#### Create Extension
```
POST /rest/domain/{domain}/addacc
Body: {"type": "extensions", "account": "1001"}
Response: {} (empty on success)
```

#### Update Extension
```
PUT /rest/domain/{domain}/user_settings/{ext}
Body: {"name": "John Doe", "email": "john@example.com"}
Response: {} (empty on success)
```

#### Delete Extension
```
DELETE /rest/domain/{domain}/addacc/{ext}
Response: {} (empty on success)
```

**⚠️ RULE:** Extensions are billable (~$24/line/year). Never auto-create. Approval required.

---

### Ring Groups (Hunt Groups)

#### List Ring Groups
```
GET /rest/domain/{domain}/userlist/hunts
Response: {rg_number: {settings}, ...}
```

#### Create Ring Group
```
POST /rest/domain/{domain}/addacc
Body: {"type": "hunts", "account": "199"}
Response: {} (empty on success)
```

#### Configure Ring Group
```
PUT /rest/domain/{domain}/user_settings/{rg_number}
Body:
{
  "display": "Sales Hunt",
  "algo": "round_robin",  # or sequential, random
  "st1_ext": "1001",
  "st1_dur": "30",        # seconds
  "st2_ext": "1002",
  "st2_dur": "30"
}
Response: {} (empty on success)
```

#### Delete Ring Group
```
DELETE /rest/domain/{domain}/addacc/{rg_number}
Response: {} (empty on success)
```

---

### Trunks (SIP/Carriers)

#### List Trunks
```
GET /rest/domain/{domain}/domain_trunks
Response: {trunk_name: {type, endpoint, ...}, ...}
```

#### Get Trunk Details
```
GET /rest/domain/{domain}/domain_trunks/{trunk_name}
Response: {type, endpoint, port, auth_user, ...}
```

---

### Account Types (Full List)

Create via `POST /addacc` with `type` field:

| Type | Purpose | Billable | Auto-Create? |
|------|---------|----------|--------------|
| `extensions` | Phone user | ✅ YES | ❌ NO (approval required) |
| `hunts` | Ring group | ❌ NO | ✅ OK |
| `acds` | Call queue | ❌ NO | ✅ OK |
| `attendants` | Auto Attendant/IVR | ❌ NO | ⚠️ Web UI only (v69.5) |
| `conferences` | Conference room | ❌ NO | ✅ OK |
| `orbits` | Call park | ❌ NO | ⚠️ Web UI only (v69.5) |
| `hoots` | Paging/intercom | ❌ NO | ✅ OK |
| `srvflags` | Service flag | ❌ NO | ⚠️ Web UI only (v69.5) |

---

## Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Proceed |
| 400 | Bad request | Fix JSON payload |
| 401 | Auth failed | Check password |
| 403 | API not enabled | Enable in Settings → System → Administrators |
| 404 | Not found | Verify domain/extension exists |
| 500 | Server error | Check Vodia logs, retry |

---

## Constraints & Limits

| Constraint | Value | Notes |
|-----------|-------|-------|
| Max extensions per domain | 1000+ | Soft limit; depends on license |
| Max ring group members | 4 | Direct hunt routing to extensions |
| Extension name length | 255 chars | UTF-8 allowed |
| Password length | 128 chars | Alphanumeric + symbols |
| API timeout | ~30s | Timeout if no response |

---

## Cascading Dependencies

**When changing an extension:**
- ❌ Ring groups referencing it → Will still try to route to it (may fail)
- ❌ IVR menus routing to it → Will fail if extension disabled
- ❌ Call forwarding rules → Will fail silently

**When disabling a ring group:**
- ❌ Trunks routing to it → Calls won't route (DID fails)

**When changing SIP trunk IP:**
- ❌ All ring groups using it → Calls may not reach them
- ❌ IVR routing to it → May fail if IP unreachable
- ❌ CDR logs → Old calls won't appear under new IP

**Resolution:** Always query trunks, ring groups, and IVR rules **before** making changes. Build dependency map in plan.

---

## Troubleshooting

### Extension Creation Returns HTTP 200 but Extension Doesn't Exist

**Cause:** Type parameter is incorrect or account already exists.

**Fix:**
- Verify `type` is lowercase (`extensions`, not `Extensions`)
- Verify extension number is unique (GET first to check)
- Check Vodia web UI for extension (may have created as different type)

---

### API Returns 403 on All Endpoints

**Cause:** API access not enabled for the admin account.

**Fix:**
1. Log into Vodia web UI (https://lab.getqts.com)
2. Settings → System → Administrators
3. Find account (e.g., "QTS Lab")
4. Check "Enable API Access"
5. Save
6. Retry API call (no password change needed)

---

### Ring Group Creation Works but Members Don't Ring

**Cause:** Ring group created but not configured with members.

**Fix:**
1. Create ring group: `POST /addacc` with `type: "hunts"` and `account: "199"`
2. Configure members: `PUT /user_settings/199` with `st1_ext`, `st1_dur`, etc.
3. Verify: `GET /user_settings/199` should show all members set

---

### Deleting Extension Fails with 404

**Cause:** Extension doesn't exist or was already deleted.

**Fix:**
1. Query extension: `GET /user_settings/{ext}`
2. If 404: Extension is already gone (safe to skip delete)
3. If 200: Verify it's the right extension, retry delete

---

## Known Issues & Workarounds

| Issue | Version | Workaround |
|-------|---------|-----------|
| Auto Attendant creation via API returns 200 but silently fails | v69.5 | Create via web UI at `/dom_attendants_list.htm`, configure via API |
| Call Park (orbits) creation via API silently fails | v69.5 | Create via web UI, configure via API |
| Service Flags creation via API silently fails | v69.5 | Create via web UI, configure via API |
| Extension name with special chars breaks display | all | Use alphanumeric + spaces/hyphens only |

---

## Extension Settings Reference

Common parameters when updating extensions via `PUT /user_settings/{ext}`:

```json
{
  "name": "Display Name",
  "email": "user@example.com",
  "password": "sip_registration_password",
  "vmailbox": "voicemail_dest_ext",
  "ncf": "forward_on_no_answer_dest",
  "cwi": "true",  // call waiting enabled
  "state": "active",
  "disabled": "false"
}
```

---

## Ring Group Settings Reference

Common parameters when configuring ring groups via `PUT /user_settings/{rg}`:

```json
{
  "display": "Ring Group Name",
  "algo": "round_robin",    // or sequential, random
  "st1_ext": "1001",        // 1st extension
  "st1_dur": "30",          // ring duration (seconds)
  "st2_ext": "1002",        // 2nd extension (optional)
  "st2_dur": "30",
  "st3_ext": "1003",        // 3rd extension (optional)
  "st3_dur": "30",
  "st4_ext": "1004",        // 4th extension (optional)
  "st4_dur": "30",
  "hunt_anonymous_dest": "fallback_ext",
  "email": "group@example.com",
  "disabled": "false"
}
```

---

## Official Documentation

- **Vodia API Reference:** https://doc.vodia.com/api-reference (authoritative spec, version-specific)
- **Vodia Web UI:** https://lab.getqts.com (live system)
- **Related Skills:** vodia-rest-api-testing, vodia-bot-automation

---

## Before ANY Change

1. **Pull this guide** (never guess)
2. **Query current state** (GET endpoints)
3. **Build dependency map** (what else is affected?)
4. **Show plan** (wait for approval)
5. **Execute** (after approval)
6. **Verify** (read back system to confirm)

