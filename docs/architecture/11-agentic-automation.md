# 11 — Agentic Automation Architecture

How specialist sub-agents layer on top of existing workflows to automate the PurpleOcaz pipeline with human-in-the-loop approval.

---

## Design Principles

1. **Agents propose, Andy approves** — nothing goes live without explicit sign-off
2. **Map to existing tools** — agents orchestrate tools that already exist, not new infrastructure
3. **Single responsibility** — each agent owns one domain (research, design, content, QA, publish, analytics)
4. **Progressive autonomy** — start fully gated, loosen controls as trust builds per agent

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────┐
│                  ORCHESTRATOR                        │
│  Assigns tasks · Routes data · Enforces gates       │
│  (SmallBrain proposes schedule, Andy approves)       │
└──────┬──────────┬──────────┬──────────┬─────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Research │ │  Design  │ │ Listing  │ │    QA    │
│  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Publish  │ │Analytics │ │          │ │          │
│  Agent   │ │  Agent   │ │ (future) │ │ (future) │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Agent Definitions

### 1. Research Agent

**Domain:** Market signals, trends, opportunities

**Existing tools it wraps:**
- `tattoo_trend_monitor` workflow — Google Trends + Etsy search gap analysis
- `market_intelligence` workflow — Reddit + Trends + Etsy scoring
- `ai_news_rss` workflow — AI/industry news aggregation

**Trigger:** Scheduled (daily or weekly)

**Output:** Ranked opportunity list in Google Sheets ("Tattoo Opportunities" tab)

**Approval gate:** None — research is read-only. Andy reviews the Sheets output.

---

### 2. Design Agent

**Domain:** Visual asset creation for listings

**Existing tools it wraps:**
- `product_creator_tool.py` — Tier 1 (AI mockups) + Tier 2 (HTML/Playwright)
- Canva MCP — design export, shadow tools, asset upload
- `image_compositor.py` — hero + boilerplate page layering
- `editable_pdf_generator.py` — Canva template PDFs
- `affiliate_guide_generator.py` — branded getting-started guide

**Trigger:** After Listing Agent generates content (Phase 3 of pipeline)

**Output:** `image_map` + `pdf_map` per listing

**Approval gate:** Image preview before upload. QA Agent validates dimensions/quality.

---

### 3. Listing Agent

**Domain:** SEO content generation + bundling

**Existing tools it wraps:**
- `generate_listing_content_tool.py` — Claude-powered title/description/tags with anti-gravity keywords
- `bundle_creator_tool.py` — auto-groups into Starter Kit / Complete Bundle / Mega Pack

**Trigger:** After Research Agent surfaces new opportunities

**Output:** Generated listings with titles, descriptions, 13 tags, prices, bundle_tags

**Approval gate:** QA Agent validates quality score >= 70. Andy reviews titles before publish.

---

### 4. QA Agent

**Domain:** Quality validation across all outputs

**Existing tools it wraps:**
- `listing_quality_validator.py` — 100-point rubric (title length, tag count, description depth, price)
- `image_quality_validator.py` — dimensions, file size, pass rate
- `etsy_seo_optimizer` workflow — tag analysis + niche-first suggestions

**Trigger:** After Listing Agent and Design Agent complete their work

**Output:** Pass/fail per listing with detailed score breakdown

**Approval gate:** Blocks publish if score < 70. Flags issues for Andy.

---

### 5. Publish Agent

**Domain:** Etsy draft creation + image/PDF upload

**Existing tools it wraps:**
- `publish_listings_tool.py` — Sheets queue + Etsy draft + image upload + PDF upload + digital delivery
- Token management — proactive refresh via `expires_at` tracking

**Trigger:** After QA Agent passes all listings

**Output:** Etsy draft IDs, upload confirmation

**Approval gate:** **Strictly gated.** Andy must approve each batch before drafts are created. Drafts remain in "draft" state — Andy clicks Publish in Etsy Shop Manager.

---

### 6. Analytics Agent

**Domain:** Performance monitoring + feedback loop

**Existing tools it wraps:**
- `etsy_analytics` workflow — daily shop stats, per-listing metrics
- `triage_listings_tool.py` — A/B/C tier scoring with action recommendations

**Trigger:** Scheduled (daily)

**Output:** Analytics dashboard in Google Sheets + triage recommendations

**Approval gate:** None for data collection. Triage actions (deactivate C-tier listings) require Andy's approval.

**Feedback loop:** Analytics → Research Agent (identifies underperforming niches → Research adjusts opportunity scoring)

---

## Data Flow Between Agents

```
Research Agent
    │
    ▼ opportunities (Sheets)
Listing Agent
    │
    ├─▶ listings + bundle_tags
    │
    ▼
Design Agent ◄─── listing content needed for image context
    │
    ▼ image_map + pdf_map
QA Agent ◄─── validates both content + images
    │
    ▼ approved listings
Publish Agent ──▶ Andy approves ──▶ Etsy drafts
    │
    ▼ live listings
Analytics Agent
    │
    ▼ performance data
Research Agent (feedback loop)
```

---

## Orchestrator Responsibilities

The Orchestrator sits above all agents and manages:

1. **Task scheduling** — which agents run when (cron-like or event-driven)
2. **Data routing** — passes outputs between agents (via Sheets or in-memory)
3. **Gate enforcement** — blocks downstream agents until approvals received
4. **Error handling** — retries failed agent runs, alerts Andy on repeated failures
5. **Logging** — all agent actions logged via ExecutionLogger for Brain analysis

**Implementation option:** Extend `SimpleOrchestrator` from `lib/orchestrator/` with agent-aware scheduling. Each agent is a workflow phase with its own tool + validator pair.

---

## Approval Model

| Action | Approval Required | Method |
|--------|-------------------|--------|
| Research data collection | No | Auto-run on schedule |
| Content generation | No | Auto-run, QA validates |
| Image creation | No | Auto-run, QA validates |
| Quality validation | No | Auto-run, flags issues |
| Create Etsy drafts | **Yes** | Andy reviews batch in Sheets → approves |
| Publish drafts to live | **Yes** | Andy clicks Publish in Etsy Shop Manager |
| Deactivate C-tier listings | **Yes** | Andy reviews triage report → approves |
| Apply Brain proposals | **Yes** | Andy reviews proposal → approves |

---

## Progressive Autonomy Roadmap

**Phase 1 (Now):** All agents gated. Andy runs pipeline manually, reviews everything.

**Phase 2 (After 50+ listings):** Research + Listing + Design + QA run automatically on schedule. Publish still gated.

**Phase 3 (After proven quality):** Auto-publish drafts that score 90+ (A-grade). Andy reviews B-grade. C-grade blocked.

**Phase 4 (Full autonomy):** End-to-end daily runs. Andy reviews weekly summary dashboard. Alerts only on anomalies.

---

## Implementation Priority

1. **Wire existing workflows as agents** — no new code, just scheduling + data routing
2. **Add approval gates** — Sheets-based queue with status column (PENDING → APPROVED → PUBLISHED)
3. **Build feedback loop** — Analytics → Research scoring weights
4. **Schedule automation** — cron or n8n triggers for daily/weekly runs
5. **Progressive autonomy controls** — config flags per agent for auto-approve thresholds

---

## Niche Expansion

Each agent works identically across niches. Config controls which niches are active:

```python
FOCUS_NICHE = "tattoo"
EXPANSION_NICHES = ["nail", "hair", "beauty", "spa"]
```

Research Agent runs once per niche. Listing Agent uses `NICHE_KEYWORD_STRATEGIES` per niche. Same tools, different config — zero new code needed.
