# Tech Stack — PurpleOcaz Agentic AI System

Full infrastructure and tooling reference.

---

## Infrastructure

| Component | Details |
|-----------|---------|
| Server | DigitalOcean droplet `167.99.90.58` (Ubuntu, 2 vCPU / 4 GB) |
| Hostname | `moltbot1241onubuntu-s-2vcpu-4gb-lon1-01` |
| Firewall | UFW — ports 22, 80, 443 open. Port 8080 closed by default. |
| Web server | Caddy (ports 80/443) |
| Object storage | DigitalOcean Spaces — CDN: `https://purpleocaz-assets.lon1.digitaloceanspaces.com/` |
| Git hosting | GitHub — org `ChurnShield`, repo `Etsypurpleocaz-` |
| CLI auth | `gh` CLI authenticated as `ChurnShield` |

## Runtime

| Tool | Version / Notes |
|------|-----------------|
| Python | 3.12 |
| Node.js | 22 |
| Claude Code | Opus 4.6 (1M context) — primary AI agent |
| Canva MCP | `purpleocaz-canva-mcp/` — design creation, editing, export via MCP protocol |
| Etsy API | v3 — OAuth2, shop ID `34071205`, shop name `PurpleOcaz` |
| Unsplash API | Demo mode — 50 req/hour limit. Cache photos locally under `assets/photos/{niche}/` to avoid repeat calls. Access key in `.env`. |

## Services

| Service | Details |
|---------|---------|
| `clawdbot.service` | systemd service at `/etc/systemd/system/clawdbot.service` |
| Working dir | `/opt/clawdbot` |
| Gateway | Node.js, `clawdbot-gateway` on port `${CLAWDBOT_GATEWAY_PORT}` |
| Telegram bot | `@letshaveitbot` — managed via `plugin:telegram:telegram` MCP |

## Environment Files

| File | Contents |
|------|----------|
| `/root/NEW-AI-PROJECT/.env` | Main project env (Etsy keys, Gemini, general config) |
| `/root/NEW-AI-PROJECT/.env.example` | Template for `.env` |
| `/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env` | Canva OAuth tokens, DO Spaces keys (`DO_SPACES_KEY`, `DO_SPACES_SECRET`) |
| `/opt/clawdbot.env` | Clawdbot gateway env (port, API keys) |

## Token Files

| File | Purpose |
|------|---------|
| `workflows/auto_listing_creator/canva_tokens.json` | Canva OAuth access + refresh tokens |
| `workflows/etsy_analytics/etsy_tokens.json` | Etsy OAuth access + refresh tokens |

## Key File Paths

| Path | Purpose |
|------|---------|
| `SOUL.md` | Mission and co-founder principles — read every session |
| `STANDUP.md` | Daily standup log |
| `LESSONS.md` | Institutional memory — lessons learned |
| `CHANGELOG.md` | Release changelog |
| `config.py` | Central config — all constants loaded here |
| `config/design_registry.json` | Canva design IDs, element IDs, shadow presets |
| `scripts/generate_tattoo_forms.py` | PDF form generator (reportlab) |
| `scripts/verify_listing.py` | Post-listing verification tool |
| `scripts/run_single_listing.py` | Full pipeline runner (phases 1-5) |
| `lib/orchestrator/` | BaseTool, BaseValidator, ExecutionLogger |
| `lib/common_tools/sqlite_client.py` | Database access layer |
| `lib/common_tools/canva_token_manager.py` | Canva token refresh |
| `data/system.db` | SQLite database |
| `purpleocaz-canva-mcp/src/config/niches.ts` | Shadow presets (`ETSY_CARD_SHADOW_PRESET`) |

## Canva Folder IDs

| Folder | ID |
|--------|----|
| Root (PurpleOcaz) | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails / Hero | `FAHENqKrgvk` |

## Proven Design IDs

| Design | ID | Purpose |
|--------|----|---------|
| Dark business card | `DAHD07F9MsY` | page 1 |
| Light business card | `DAHD15IcxRs` | page 1 |
| Dark appointment card | `DAHENCEJGjk` | black/gold/botanical |
| Light appointment card | `DAHENKnCBoM` | cream/charcoal/gold/botanical |
| Hero thumbnail template | `DAHDc0gyebE` | flatlay with natural shadows |
| Listing pages (5-page) | `DAFx_dsWpTA` | generic pages for all listings |
