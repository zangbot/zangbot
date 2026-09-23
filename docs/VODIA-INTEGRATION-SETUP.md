# Vodia v70 Third-Party Integration Setup for Zangbot Router

**Goal**: Configure Vodia to send events (extension offline, call events, etc.) to Zangbot Router at `http://72.62.97.23:8001/webhook/vodia`

## Vodia v70 Integration Configuration

In Vodia v70, third-party integrations are configured via:
1. **Web UI path**: Settings → System → Integrations (or similar)
2. **Webhook endpoint**: POST to external URL
3. **Events**: Select which PBX events trigger webhooks

## Integration Details for Zangbot Router

| Setting | Value |
|---------|-------|
| **Name** | Zangbot Infrastructure Router |
| **Type** | Webhook / HTTP POST |
| **Endpoint** | `http://72.62.97.23:8001/webhook/vodia` |
| **Method** | POST |
| **Content-Type** | application/json |
| **Events** | Extension offline, Call events, Queue events, IVR events |
| **Retry** | Enabled (if supported) |
| **Timeout** | 10 seconds |

## Webhook Payload Format (Expected by Zangbot)

Zangbot Router expects:
```json
{
  "source": "vodia",
  "event": "extension_offline|call_started|queue_alert|...",
  "device_id": "ext101",
  "details": {
    "reason": "network|timeout|...",
    "duration": 300,
    "data": "..."
  },
  "timestamp": "2026-09-23T04:30:00Z"
}
```

## Setup Steps (Web UI)

1. **Log into Vodia admin panel** at `https://lab.getqts.com/` (or your host)
2. Go to **Settings** → **System** → **Integrations**
3. Click **Add Integration** or **New**
4. Fill in:
   - **Name**: `Zangbot Infrastructure Router`
   - **Type**: `Webhook` or `HTTP POST`
   - **Webhook URL**: `http://72.62.97.23:8001/webhook/vodia`
   - **Events to send**: Select all infrastructure events (extension state changes, call events, queue status, etc.)
5. **Enable** the integration
6. **Save**

## Testing Integration (If Available)

Some Vodia versions allow test sends:
1. Click **Test** or **Send Test Event**
2. Verify the router receives it:
   ```bash
   ssh root@72.62.97.23 'curl -s http://localhost:8001/tickets | grep vodia'
   ```
3. You should see a ticket with `"source": "vodia"` created

## Monitoring Vodia Webhooks on Router

```bash
# Watch Vodia events arriving
ssh root@72.62.97.23 'journalctl -u zangbot-router -f | grep "Vodia"'

# Count Vodia tickets
ssh root@72.62.97.23 'curl -s http://localhost:8001/tickets | grep -c "vodia"'

# Get latest Vodia event
ssh root@72.62.97.23 'curl -s http://localhost:8001/tickets | grep -A10 "vodia" | head -20'
```

## Alternative: REST API Configuration (If UI Unavailable)

If Vodia v70 supports integration configuration via API (check official docs):

```bash
curl -X POST \
  -u admin@lab.getqts.com:PASSWORD \
  https://lab.getqts.com/rest/system/integration \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zangbot Infrastructure Router",
    "type": "webhook",
    "url": "http://72.62.97.23:8001/webhook/vodia",
    "events": ["extension_offline", "call_started", "queue_alert"],
    "enabled": true
  }'
```

## Expected Behavior After Setup

1. **Event occurs in Vodia** (e.g., extension goes offline)
2. **Vodia sends webhook** POST to `http://72.62.97.23:8001/webhook/vodia`
3. **Zangbot Router receives** and creates a ticket
4. **Ticket appears** in `GET /tickets` endpoint with status `pending_decision`
5. **User approves** via `POST /tickets/{id}/approve`
6. **(Phase 3)** Router executes action (e.g., page admin, log event, trigger UniFi action)

## Security Notes

- **No authentication** on webhook endpoint yet (Phase 3: add API key validation)
- **HTTP only** (Phase 3: upgrade to HTTPS + certificate validation)
- **All events logged** in systemd journal for audit

## Troubleshooting

**Integration not sending webhooks:**
1. Check integration is **Enabled** in Vodia UI
2. Verify endpoint is **exactly** `http://72.62.97.23:8001/webhook/vodia`
3. Check firewall: `ufw status` on VPS (should allow outbound HTTP)
4. Monitor router logs: `journalctl -u zangbot-router -f`

**Webhooks arriving but tickets not created:**
1. Check router is running: `systemctl status zangbot-router`
2. Check for payload format mismatch (Vodia may send different structure)
3. Monitor logs for parsing errors: `journalctl -u zangbot-router | grep ERROR`

**Connection refused:**
1. Verify port 8001 is listening: `ssh root@72.62.97.23 'netstat -tuln | grep 8001'`
2. Verify service is running: `ssh root@72.62.97.23 'systemctl status zangbot-router'`
3. Verify firewall allows inbound: Check UFW rules on VPS

## Next: Webhook Payload Mapping

Once Vodia integration is live, we may need to **adapt the router** to Vodia's actual webhook payload format (Step 1 priority after deployment).
