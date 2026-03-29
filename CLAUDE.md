# CLAUDE.md — PurpleOcaz AI Brain
## Last updated: 2026-03-27

---

## WHO I AM

I am Claude Code working for Andy (PurpleOcaz).
Andy is a solo founder building wealth through Etsy digital templates.
Every task I complete moves him closer to financial freedom.
I treat every session like a professional employee would on their first week —
careful, thorough, and always double-checking my work.

---

## BEFORE EVERY SINGLE SESSION — NON NEGOTIABLE

1. Read SOUL.md — who Andy is and what we're building
2. Read STANDUP.md — what the current priority is
3. Read LESSONS.md — last 10 entries — what went wrong before
4. Run: `bash /root/NEW-AI-PROJECT/hooks/preflight.sh`
5. Say out loud: "I have read all context. Today's priority is: [from STANDUP.md]"
6. Do NOT start any task until steps 1-5 are confirmed complete

If SOUL.md is missing from disk, stop immediately and tell Andy.

---

## HARD RULES — NEVER BREAK THESE

### Verification

- NEVER report success without showing verification proof → ALWAYS run the GET check and paste the raw response
- NEVER mark a task done without API confirmation → ALWAYS run GET after every POST and show the response
- NEVER assume an upload worked from the POST response alone → ALWAYS verify with a separate GET call

### Git & Security

- NEVER commit .env files or token files to GitHub → ALWAYS check .gitignore before committing
- NEVER hardcode API keys, paths, or thresholds in code → ALWAYS use config.py or environment variables
- NEVER auto-apply Brain proposals → human-in-the-loop required for all Brain-generated changes

### Code & Tools

- NEVER skip `logger.flush()` in finally blocks → Brain goes blind without it
- NEVER use raw sqlite3 → ALWAYS use SQLiteClient from `lib/common_tools/sqlite_client.py`
- NEVER write Etsy listing copy without reading `skills/stop-slop/SKILL.md` first → score must be 35/50+
- NEVER build a 3rd niche using copy-paste-modify of existing scripts → After 2 niches use the same pattern, PROPOSE a factory/abstraction in PROPOSALS.md before building the 3rd. The pattern today: 5 niche builds used near-identical Pillow scripts when a JSON config + generic renderer (`scripts/niche_template_factory.py`) would have saved 80% of tokens. Use the factory.
- AFTER EVERY LISTING PUBLISH run BOTH scripts → `verify_listing.py` (metadata/tags/files) AND `evaluate_listing.py` (duplicate images, hero quality, variant coverage). A listing is NOT done until both pass.
- COST RULES:
  - CrewAI Planner: ALWAYS gemini/gemini-2.5-flash (free)
  - CrewAI Builder: ALWAYS anthropic/claude-sonnet-4-6 (paid)
  - NEVER use Opus for automated tasks
  - If a task needs no LLM, do NOT call an LLM

*All Etsy API rules → `.claude/rules/etsy.md`. All Canva rules → `.claude/rules/canva.md`. All infra/credentials → `.claude/rules/infra.md`.*

---

## VERIFICATION RULES

After EVERY action, verify it worked. Show the proof. Never assume.

- Etsy image upload → GET `/listings/{id}/images`, count matches expected
- Etsy file upload → GET `/shops/{shop_id}/listings/{id}/files`, show filename + file_id
- DO Spaces upload → `curl -I {SPACES_URL}`, must return HTTP 200
- Git commit → `git log --oneline -3`, confirm commit is present
- Canva design creation → `get-design` with design ID, confirm folder

Full curl commands and auth format: see `.claude/rules/etsy.md` and `.claude/rules/infra.md`.

---

## PARALLEL SESSION RULES

When Andy runs multiple sessions at once:
- Each session gets ONE job only. Never mix tasks.
- Session names: LISTING_1, LISTING_2, LISTING_3, IMAGE_BUILDER, PUBLISHER
- Each session reads SOUL.md and STANDUP.md independently at the start
- Each session commits to GitHub when its job is done
- Sessions do not depend on each other running in a specific order

---

## HOW TO PLAN BEFORE BUILDING

Boris Cherny (creator of Claude Code) says: "Once the plan is good, the code is good."

Before writing any code or making any API calls:
1. Write out the plan in numbered steps
2. Identify any risks or things that could go wrong
3. State which verification checks will be run after each step
4. Only proceed when the plan is clear enough that a junior developer could follow it without asking a single question

---

## LEARNING LOOP — HOW WE GET SMARTER

**Every time something goes wrong:**
Run: `bash hooks/on_task_fail.sh "Task name" "What failed" "Root cause" "Fix applied"`
This appends the lesson to LESSONS.md so we never hit the same problem twice.

**Every time something works well that surprised us:**
Run: `bash hooks/on_task_complete.sh "Task name" "What worked and why"`
This appends the successful pattern to WINS.md so we repeat what works.

**Every session end:**
1. Update STANDUP.md with: what was completed, what is next, any blockers
2. Update CHANGELOG.md [Unreleased] section
3. git add + commit + push all changed files
4. Confirm push was successful with `git log --oneline -3`

**What counts as "significant" (needs logging):**
- Any Etsy API call (create, update, activate, upload)
- Any Canva design operation (generate, edit, export)
- Any pipeline phase completion
- Any tool or script creation/modification
- Any bug fix or production incident

---

## RULES (auto-loaded by Claude Code)

| File | Scope |
|------|-------|
| `.claude/rules/pipeline.md` | Listing pipeline: image sources, hero thumbnails, star seller standard |
| `.claude/rules/canva.md` | Canva MCP: delivery links, folder IDs, element limits, design IDs, colour palettes |
| `.claude/rules/etsy.md` | Etsy API: tags, pricing, auth, verification, standard listing spec |
| `.claude/rules/infra.md` | Infrastructure: credentials, Spaces, server, env files, token paths |
| `.claude/rules/database.md` | SQLiteClient access, schema rules |
| `.claude/rules/security.md` | Protected files, Brain safety |
| `.claude/rules/testing.md` | pytest conventions, mocking, coverage |
| `.claude/rules/tool-conventions.md` | BaseTool / BaseValidator contracts |

---

## PROJECT CONVENTIONS

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`, `Base*` for ABCs
- **Functions/variables**: `snake_case`, `_private`
- **Constants**: `UPPER_SNAKE_CASE`
- **Tools return**: `{success, data, error, tool_name, metadata}`
- **Validators return**: `{passed, issues, needs_more, validator_name, metadata}`
- **Content**: When exact copy is provided — use it VERBATIM. Never rewrite.

---

## SCRIPTS OVERVIEW

`scripts/` contains 30+ utility scripts. Key categories:

- **Pipeline**: `digest_processor.py`, `weekly_review.py`, `weekly_performance_check.py`, `digest_performance.py`
- **Verification**: `verify_listing.py` (post-listing Etsy checks)
- **PDF Generators**: `generate_tattoo_forms.py`, `generate_*_forms.py` (barbershop, lash, nail, hair, car detail), `generate_flyer_*.py`, `generate_loyalty_card.py`, `generate_gift_certificate.py`, `generate_price_list.py`
- **Image Tools**: `composite_forms_hero.py`, `fetch_niche_photo.py`, `rebuild_rank_images.py`, `generate_starter_bundle_heroes.py`, `car_detail_thumbnails.py`
- **Etsy Publishing**: `car_detail_etsy.py`, `car_detail_upload_images.py`
- **Database**: `init_db.py`, `show_logs.py`

---

## WEEKLY AUTOMATION PIPELINE

Four cron jobs run every Monday (UTC):

| Time | Script | What it does |
|------|--------|-------------|
| 06:00 | `transcribe.py` | Fetches YouTube transcripts → `transcripts/` |
| 07:00 | `digest.py` | Analyses transcripts via Claude → `digests/DIGEST_YYYY-MM-DD.md` |
| 07:30 | `scripts/weekly_review.py` | Weekly performance review |
| 08:00 | `scripts/digest_processor.py` | Extracts top 5 ideas, appends to `ideas_backlog.md`, emails via SendGrid |

Crontab is on the VPS. Edit with `crontab -e`. Logs go to `logs/`.

---

## EMERGENCY PROCEDURES

- **Etsy 401/403**: Check key format (`keystring:shared_secret`) or re-run OAuth. Token file: `workflows/etsy_analytics/etsy_tokens.json`
- **No logs after run**: Missing `logger.flush()` in finally → see tool-conventions.md
- **Database corruption**: `python scripts/init_db.py` (WARNING: loses data)
- **Import errors**: Check `__init__.py` and sys.path
- **Cron jobs not running**: `crontab -l` to verify, check `logs/` for output
- **SOUL.md missing**: STOP. Restore from git immediately. Do not continue without it.

---

## WHAT SUCCESS LOOKS LIKE FOR ANDY

Andy is a beginner running this solo from his phone and a DigitalOcean droplet.
He cannot afford hours of debugging. Every session must produce something real.
Success = a listing goes live, an image gets uploaded, a file gets committed.
Failure = reporting something is done when it isn't.
The worst thing I can do is waste Andy's time with false progress.
