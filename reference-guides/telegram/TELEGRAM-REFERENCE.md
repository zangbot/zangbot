# Telegram Bot API Reference Guide — Bot Edition

**Version:** Bot API v7.0+  
**Last Updated:** 2026-09-18  
**Update Interval:** Monthly  
**Source:** Official Telegram Bot API docs

---

## Quick Facts

| Aspect | Value |
|--------|-------|
| **Endpoint** | https://api.telegram.org/bot{token}/method |
| **Auth** | URL path token (no additional headers) |
| **Format** | JSON (POST) |
| **Rate Limit** | 30 messages/sec per chat (Telegram enforces) |
| **Response Timeout** | 30 seconds |
| **Max Message Size** | 4096 chars (text), 20MB (file) |

---

## Authentication

### Bot Token Storage

**Format:** `123456789:ABCDefGHIjklmnoPQRstUVwxyz_1a2B3C4D`

**Location:**
- Primary: Bitwarden (`Telegram Bot (Zangbot)`)
- Backup: `~/.hermes/default/vault/telegram-bot.json`

### Token Format
- **Numeric part:** Bot ID (123456789)
- **Alphanumeric part:** Secret token (ABCDefGHI...)
- Never commit token to git; always load from vault

---

## Core Methods

### Send Message
```
POST /rest/api/sendMessage
```

**Parameters:**
```json
{
  "chat_id": 123456789,
  "text": "Message text (max 4096 chars)",
  "parse_mode": "Markdown",  // or HTML, MarkdownV2
  "disable_web_page_preview": false,
  "disable_notification": false,
  "reply_to_message_id": null,
  "reply_markup": {}
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "message_id": 42,
    "chat": {"id": 123456789},
    "date": 1695142800,
    "text": "Message text"
  }
}
```

### Get Me (Verify Bot Works)
```
GET /rest/api/getMe
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "Zangbot",
    "username": "zangbot_bot"
  }
}
```

### Get Updates (Polling)
```
GET /rest/api/getUpdates?offset=0
```

**Response:**
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456,
      "message": {
        "message_id": 1,
        "chat": {"id": 987654321},
        "date": 1695142800,
        "text": "User message"
      }
    }
  ]
}
```

### Edit Message
```
POST /rest/api/editMessageText
```

**Parameters:**
```json
{
  "chat_id": 123456789,
  "message_id": 42,
  "text": "Updated message",
  "parse_mode": "Markdown"
}
```

### Delete Message
```
POST /rest/api/deleteMessage
```

**Parameters:**
```json
{
  "chat_id": 123456789,
  "message_id": 42
}
```

---

## Message Formatting

### Markdown V2 (Recommended)
```
*bold* _italic_ __underline__ ~~strikethrough~~
[inline URL](https://example.com)
[inline mention](tg://user?id=123456789)
`monospace code`
```\`\`\`
preformatted code block
```\`\`\`
```

**Escape characters:** `_ * [ ] ( ) ~ ` # + - = | { } . !`

### HTML
```
<b>bold</b> <i>italic</i> <u>underline</u>
<a href="https://example.com">inline URL</a>
<code>monospace</code>
<pre>preformatted</pre>
```

### Inline Buttons (Reply Markup)
```json
{
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "Button 1", "callback_data": "action_1"},
        {"text": "Button 2", "callback_data": "action_2"}
      ]
    ]
  }
}
```

---

## Webhooks (Push-Based)

### Set Webhook
```
POST /rest/api/setWebhook
```

**Parameters:**
```json
{
  "url": "https://your-domain.com/webhook/telegram",
  "allowed_updates": ["message", "callback_query"]
}
```

### Webhook Payload (Incoming)
```json
{
  "update_id": 123456,
  "message": {
    "message_id": 1,
    "from": {"id": 987654321, "first_name": "User"},
    "chat": {"id": 987654321, "type": "private"},
    "date": 1695142800,
    "text": "User text"
  }
}
```

### Delete Webhook
```
POST /rest/api/deleteWebhook
```

---

## Chat IDs & User IDs

### Private Chat (Direct Message)
- **Chat ID:** Positive number (user's Telegram ID)
- **Example:** 987654321
- **Access:** Only that user can receive

### Group Chat
- **Chat ID:** Negative number (group ID with minus)
- **Example:** -123456789123
- **Access:** All group members can receive

### Channel
- **Chat ID:** Negative number (large)
- **Example:** -1001234567890
- **Access:** Subscribers only

### Get Chat ID
1. Add bot to chat/group
2. Send any message
3. Call `getUpdates`
4. Extract `chat.id` from response

---

## Common Scenarios

### Send Alert to Owner
```python
def send_alert(message: str):
    chat_id = 987654321  # Your Telegram ID
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🚨 Alert: {message}",
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()["ok"]
```

### Send Approval Request (with Buttons)
```python
def request_approval(task_id: str):
    chat_id = 987654321
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"*Task #{task_id}*\\nApprove changes?",
        "parse_mode": "MarkdownV2",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": f"approve_{task_id}"},
                    {"text": "❌ Reject", "callback_data": f"reject_{task_id}"}
                ]
            ]
        }
    }
    response = requests.post(url, json=payload)
    return response.json()
```

### Receive Callback (Button Click)
```python
# Webhook payload when button clicked:
{
  "update_id": 123456,
  "callback_query": {
    "id": "12345",
    "from": {"id": 987654321},
    "chat_instance": "12345",
    "data": "approve_task_1"
  }
}

# Process in your webhook:
if update.get("callback_query"):
    callback_data = update["callback_query"]["data"]
    if callback_data.startswith("approve_"):
        task_id = callback_data.split("_")[1]
        # Execute approval
```

---

## Cascading Effects

**If you change Telegram bot:**

| Change | Effect | Mitigation |
|--------|--------|-----------|
| Revoke bot token | All messages fail (invalid token) | Generate new token, update vault |
| Change webhook URL | Messages won't arrive | Update webhook to new URL |
| Delete bot account | Complete shutdown | Recreate bot, regenerate token |
| Block bot in group | Bot can't send to that group | Re-add bot to group |

**Before changing:**
1. Verify new token/webhook in test group
2. Rollback: Keep old token available until new one confirmed working
3. Update vault after verified working

---

## Troubleshooting

### Message Send Fails with `{"ok": false, "error_code": 401}`

**Cause:** Invalid or revoked token.

**Fix:**
1. Verify token in Bitwarden matches vault
2. Check token format (no extra spaces)
3. Test with `getMe` endpoint
4. If token revoked: generate new token from @BotFather on Telegram

---

### Webhook Not Receiving Updates

**Cause:** Webhook URL unreachable or not HTTPS.

**Fix:**
1. Verify endpoint is HTTPS only (no HTTP)
2. Check certificate is valid (not self-signed unless ignored)
3. Test endpoint manually: `curl -X POST https://your-domain/webhook/telegram`
4. Verify firewall allows inbound on webhook port
5. Check `getMe` works (proves token valid)

---

### Rate Limited (429 Too Many Requests)

**Cause:** Sending >30 messages/sec to same chat.

**Fix:**
- Queue messages
- Add delay between sends (use `sleep(0.1)`)
- Combine multiple messages into one

---

### Message Formatting Broken

**Cause:** Markdown characters not escaped or parse_mode wrong.

**Fix:**
- Use MarkdownV2, escape special chars: `\_\*\[\]\(\)`
- Or use HTML mode instead
- Test in `sendMessage` with `parse_mode: "MarkdownV2"`

---

## Known Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Message text | 4096 chars | Split longer messages |
| File upload | 20MB | Larger files via URL |
| Inline buttons | 10 per message | Split into multiple messages if needed |
| Message edits | Unlimited | But only if text actually changes |
| Forwards | Unlimited | May be rate-limited by Telegram |

---

## Before ANY Telegram Change

1. **Pull this guide** (never guess Telegram API)
2. **Test in private chat first** (not in production channel)
3. **Verify token/webhook** (getMe works?)
4. **Show plan** (what exactly will change?)
5. **Execute** (after approval)
6. **Verify** (test message received)

