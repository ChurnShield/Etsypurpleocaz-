
---

## Obsidian + Zettelkasten AI Brain

**Priority: MEDIUM — revisit after first Etsy listing ships**

### What it is
Obsidian is a local markdown knowledge base. Files live as plain .md files.
Zettelkasten is a note-linking methodology — every piece of information gets
an atomic note that links to related notes, building a web of interconnected
knowledge over time.

### Why it fits our pipeline
Our current CHANGELOG.md / LESSONS.md / SESSION_START.md system is a
primitive Zettelkasten. Obsidian formalises this into something browsable,
searchable and linkable — with Claude Code writing to it autonomously.

### Proposed vault structure
```
PurpleOcaz/
├── niches/
│   ├── barbershop.md         ← niche research, trends, Etsy keywords
│   ├── tattoo.md
│   ├── dog-grooming.md
│   └── _template.md          ← standard niche note template
├── products/
│   ├── appointment-cards.md  ← what works, Canva IDs, pipeline notes
│   ├── business-cards.md
│   └── _template.md
├── pipeline/
│   ├── canva-mcp.md          ← everything learned, asset IDs, flow
│   ├── icon-library.md       ← GitHub paths, Canva asset IDs per niche
│   ├── etsy-api.md
│   └── prompt-library.md     ← proven Canva generation prompts per niche
├── intelligence/
│   ├── youtube-digests/      ← auto-populated by YouTube feed cron
│   ├── etsy-trends/          ← Claude Code web fetches → stored here
│   └── competitor-notes/
├── agents/
│   ├── big-brain.md          ← Big Brain architecture and rules
│   ├── small-brain.md
│   └── canva-agent.md        ← Canva MCP agent spec
└── sessions/
    ├── 2026-03-12.md         ← daily session notes auto-generated
    └── _template.md
```

### Claude Code integration (autonomous)
- Web fetch trending Etsy searches → store as niche/etsy-trends/ notes
- Pull YouTube digest summaries → store as intelligence/youtube-digests/ notes
- Update product notes when new listing goes live
- Cross-link notes automatically (barbershop.md ↔ appointment-cards.md ↔ canva-mcp.md)
- Daily session note auto-generated at session start

### How it feeds the pipeline
Obsidian vault (brain)
        ↓
Niche research notes → feeds Big Brain prompt selection
Competitor analysis → informs design direction
YouTube digests → stored as intelligence notes
Etsy trend data → Claude Code web fetches → stored as notes
        ↓
Big Brain reads vault → generates design briefs
        ↓
Canva MCP → generates cards → injects niche icons → QR code
        ↓
Etsy API → live listing

### Why Obsidian specifically
- Plain .md files — Claude Code can read/write natively
- Graph view — visualise how niches, products and agents connect
- Works offline and on mobile (Obsidian mobile app)
- Sync via Git (already have GitHub set up)
- No lock-in — just markdown files

### Implementation steps (when ready)
1. Install Obsidian on desktop
2. Point vault at ~/Etsypurpleocaz- (repo is already .md based)
3. Install Git sync plugin → auto-syncs with GitHub
4. Create note templates for niches, products, sessions
5. Wire Claude Code to auto-populate intelligence/ folder
6. Build Big Brain prompt that reads vault before making decisions

### Related
- Links to: Big Brain architecture, YouTube Intelligence Feed, Canva MCP pipeline
- Flagged: 2026-03-12 session
