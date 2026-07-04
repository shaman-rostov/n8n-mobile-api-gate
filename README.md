# Orqflow Mobile API Gateway

The n8n workflow that powers the [Orqflow iOS app](https://github.com/shaman-rostov/n8n-manager-ios) — a mobile manager for self-hosted n8n automation servers.

## How it works

The gateway is a single n8n workflow that:
1. Exposes one webhook endpoint (`POST /webhook/mobile-api-gate`)
2. Validates the request with a secret `gatewayToken` (`X-API-Key` header)
3. Routes `action` commands to n8n's internal REST API
4. Returns structured JSON responses to the iOS app

Your credentials never leave your server — the app talks only to your own n8n instance.

## Requirements

- Self-hosted **n8n v1.0** or later
- n8n REST API enabled (default)

## Installation

### Step 1 — Import the workflow

1. Download [`workflow/orqflow-gateway.json`](workflow/orqflow-gateway.json)
2. In n8n: **Workflows → ⊕ Add workflow → ⋯ → Import from file**
3. Select the downloaded JSON

### Step 2 — Configure the ⚙️ Config node

Open the **⚙️ Config** node and fill in three fields:

| Field | How to get it |
|-------|--------------|
| `gatewayToken` | Generate: `openssl rand -hex 32` |
| `n8nApiKey` | n8n **Settings → API → Create API key** |
| `instanceUrl` | Your n8n URL, e.g. `http://localhost:5678` or `https://n8n.example.com`. Used for internal API calls. |

> **Copy `gatewayToken`** — you'll paste it into the Orqflow iOS app.

### Step 3 — Set up Basic Auth credential (optional)

If you protect your n8n with HTTP Basic Auth:

1. In n8n: **Settings → Credentials → Add credential → HTTP Basic Auth**
2. Name it `n8n API Basic Auth`, enter your username/password
3. Open the **Webhook Gateway** node → select that credential

If you don't use Basic Auth, remove the `authentication: basicAuth` from the Webhook Gateway node.

### Step 4 — Activate

Toggle the workflow **Active** in the top-right corner.

### Step 5 — Connect the iOS app

In Orqflow → Settings (or onboarding):

| Field | Value |
|-------|-------|
| Server URL | Your n8n domain, e.g. `https://n8n.example.com` |
| Basic Auth Username | Only if n8n is behind HTTP Basic Auth |
| Basic Auth Password | Only if n8n is behind HTTP Basic Auth |
| Gateway Token | The token from Step 2 |

Tap **Test Connection** → **Save**.

---

## Supported actions

| Action | Description |
|--------|-------------|
| `list_endpoints` | Connectivity check |
| `get_system_info` | n8n instance info |
| `list_workflows` | Paginated workflow list |
| `get_workflow` | Single workflow details |
| `activate_workflow` | Toggle workflow on |
| `deactivate_workflow` | Toggle workflow off |
| `trigger_workflow` | Run a workflow manually |
| `list_executions` | Paginated execution history |
| `get_execution` | Single execution details |
| `stop_execution` | Stop a running execution |
| `delete_execution` | Delete an execution record |

---

## Security

- `gatewayToken` is validated on every request before any routing occurs
- HTTP Basic Auth (optional) adds a second layer at the webhook level
- The n8n API key is stored only inside the n8n workflow — it never leaves your server
- App credentials are stored in the iOS Keychain (not iCloud, not backed up externally)

---

## Troubleshooting

**"Connection failed" in the app**

Test manually:
```bash
curl -X POST https://n8n.example.com/webhook/mobile-api-gate \
  -H "X-API-Key: your-gateway-token" \
  -H "Content-Type: application/json" \
  -d '{"action":"list_endpoints","params":{}}'
```
Expected: `{"success":true,"action":"list_endpoints","data":{...}}`

**401 Unauthorized**
- Check that `gatewayToken` in the app matches exactly what's in ⚙️ Config
- If using Basic Auth, verify credentials match the n8n credential

**Workflows not loading**
- Verify `n8nApiKey` is valid (Settings → API in n8n)
- Check `instanceUrl` in ⚙️ Config points to the correct n8n address (reachable from within n8n itself)

**n8n runs in Docker**
- Set `instanceUrl` to the internal container address, e.g. `http://n8n:5678`

---

## Privacy Policy

[privacy-policy.md](privacy-policy.md)

---

## License

MIT
