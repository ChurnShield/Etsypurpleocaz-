# Infrastructure & Credentials

## Key Credentials

| Item | Value |
|------|-------|
| Shop ID | `34071205` |
| Shop name | `PurpleOcaz` |
| Etsy API key | `19d2q2xcg1ccipoj4doub0ee` |
| Etsy shared secret | `rj7ou7mzjq` |
| Canva Client ID | `OC-AZyAz47KwCUv` |
| Droplet IP | `167.99.90.58` |
| Project root | `/root/NEW-AI-PROJECT/` |

## Token Files

| File | Purpose |
|------|---------|
| `workflows/etsy_analytics/etsy_tokens.json` | Etsy OAuth access + refresh tokens |
| `workflows/auto_listing_creator/canva_tokens.json` | Canva OAuth access + refresh tokens |

## Environment Files

| File | Contents |
|------|----------|
| `/root/NEW-AI-PROJECT/.env` | Main project env (Etsy keys, Gemini, general config) |
| `/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env` | **Canva OAuth tokens + DO Spaces keys** |
| `/opt/clawdbot.env` | Clawdbot gateway env (port, API keys) |

## DO Spaces

- CDN base: `https://purpleocaz-assets.lon1.digitaloceanspaces.com/`
- Bucket: `purpleocaz-assets` / Region: `lon1`
- **Credentials are in `purpleocaz-canva-mcp/.env`** — NOT `NEW-AI-PROJECT/.env`
- Keys: `DO_SPACES_KEY`, `DO_SPACES_SECRET`
- Load with: `load_dotenv('/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env')`
- **Every `s3.put_object()` MUST include `ACL='public-read'`** — without it uploads return 403
- Spaces URLs are **permanent**. Canva export URLs **expire**. Never mix them up.

## Server

| Component | Details |
|-----------|---------|
| VPS | DigitalOcean `167.99.90.58` (Ubuntu, 2 vCPU / 4 GB, lon1) |
| Firewall | UFW — ports 22, 80, 443 open. Port 8080 closed by default. |
| Web server | Caddy (ports 80/443) |
| Git hosting | GitHub — org `ChurnShield`, repo `Etsypurpleocaz-` |
| CLI auth | `gh` CLI authenticated as `ChurnShield` |
| Python | 3.12 |
| Node.js | 22 |

## Services

| Service | Details |
|---------|---------|
| `clawdbot.service` | systemd at `/etc/systemd/system/clawdbot.service`, working dir `/opt/clawdbot` |
| Telegram bot | `@letshaveitbot` — managed via `plugin:telegram:telegram` MCP |

## Unsplash API

Demo mode — 50 req/hour limit. Cache photos locally under `assets/photos/{niche}/` to avoid repeat calls. Access key in `.env`.

## SSH (mobile / Terminus)

`root@167.99.90.58` port 22. If connection times out: run `sudo ufw allow 22` from the DO web console.
