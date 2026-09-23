# Vodia v70 Integration Deployment

This directory contains the Zangbot Integration for Vodia v70.

## Files

- **manifest.json** — Integration metadata (name, version, events, routing)
- **backend.js** — Webhook handler (transforms Vodia events → Zangbot tickets)
- **ui.html** — User-facing integration UI (status, test button, logs)

## Installation Steps

### 1. Package Integration for Vodia

Zip all three files:
```bash
cd vodia-integration
zip -r zangbot-integration-v1.0.0.zip manifest.json backend.js ui.html
```

### 2. Upload to Vodia

1. Log into Vodia admin panel: `https://lab.getqts.com/`
2. Go to: **Settings → System → Integrations**
3. Click: **Import** or **Upload Integration**
4. Select: `zangbot-integration-v1.0.0.zip`
5. Click: **Install**

### 3. Configure Integration

After import, configure:
- **Display Name**: `Zangbot Infrastructure Router` ✓ (pre-filled)
- **Identifier**: `zangbotinfrastructurerouter` ✓ (pre-filled)
- **Path Prefix**: `/` (required by Vodia)
- **Target URL**: `http://72.62.97.23:8001/webhook/vodia`
- **Events**: Select all monitored events (extension state, call, queue, IVR)

### 4. Enable Integration

1. Toggle: **Enabled** → ON
2. Click: **Save**

### 5. Test

1. Click: **Test Connection** button in integration UI
2. Expected: `✓ Connection successful!`
3. Monitor logs:
   ```bash
   ssh root@72.62.97.23 'journalctl -u zangbot-router -f | grep vodia'
   ```

## Event Flow

```
Vodia Extension Event (offline)
        ↓
Vodia Webhook POST
        ↓
backend.js (transforms)
        ↓
Zangbot Router @ 72.62.97.23:8001
        ↓
Ticket created: {source: "vodia", event: "extension_offline", status: "pending_decision"}
        ↓
User approves via /tickets/{id}/approve
        ↓
Action executed (Phase 3)
```

## Payload Transformation

**Vodia webhook** (incoming):
```json
{
  "type": "extension_state_changed",
  "extension": "101",
  "state": "offline"
}
```

**Transformed** (sent to Zangbot):
```json
{
  "source": "vodia",
  "event": "extension_offline",
  "device_id": "101",
  "details": {
    "type": "extension_state_changed",
    "extension": "101",
    "state": "offline",
    "timestamp": "2026-09-23T04:30:00Z"
  }
}
```

## Troubleshooting

**Integration not appearing in Vodia UI after import?**
- Check manifest.json syntax (valid JSON)
- Verify all three files present in zip
- Try re-importing

**Webhooks not arriving at Zangbot Router?**
- Verify integration is **Enabled** in Vodia
- Check router is running: `systemctl status zangbot-router` on Hostinger
- Monitor router logs: `journalctl -u zangbot-router -f`
- Test manually: `curl -X POST http://72.62.97.23:8001/webhook/vodia -d '...'`

**Connection test fails in UI?**
- Check firewall: UFW may block outbound from Vodia server to Hostinger
- Verify IP/port correct: `72.62.97.23:8001`
- Check DNS resolution on Vodia server

## Advanced: Customize Event Types

Edit `backend.js`, function `parseEvent()` to add/modify Vodia event types:

```javascript
parseEvent(payload) {
  // Add custom event mapping here
  if (payload.type === "custom_event") return "custom_event";
  // ... existing mappings
}
```

Redeploy to Vodia after edits.

## Version History

- **v1.0.0** — Initial release (extension state, call, queue, IVR events)

## Support

Monitor Zangbot Router logs on Hostinger:
```bash
ssh root@72.62.97.23
journalctl -u zangbot-router -f
```

Check router health:
```bash
curl http://72.62.97.23:8001/health
```
