# CLAUDE.md — PurpleOcaz AI Brain
## Last updated: 2026-03-24

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

### Etsy API

- NEVER use PUT on Etsy listings → ALWAYS use PATCH for listing updates (PUT returns 404)
- NEVER set Etsy price via PATCH on any listing → ALWAYS set price at creation time, or use PUT /listings/{id}/inventory to change later
- NEVER use tags over 20 characters on Etsy → ALWAYS validate tag length before submitting (API returns 400)
- NEVER submit duplicate Etsy tags → ALWAYS check for duplicates before posting (API returns 400)
- NEVER try to clone/copy an Etsy listing → no clone endpoint exists in Etsy v3 API
- NEVER delete the last image on an active listing → ALWAYS upload the replacement first, then delete the old one

### Canva

- NEVER upload to Canva using Canva export URLs — they expire → ALWAYS upload via DO Spaces public URL
- NEVER run more than one operation per Canva transaction → ALWAYS one operation, commit, then next operation
- NEVER use `/design/.../edit` links in delivery PDFs → ALWAYS use `/d/{shortcode}` links only (edit links expose master designs)
- NEVER use `update_fill` on shape elements → it only works on image/video containers (shapes return "does not contain an editable fill")
- NEVER use `generate-design` for custom branded listing images → it ignores colour instructions and defaults to blue. Only useful as aesthetic base for card-type designs
- NEVER try to insert new text elements via Canva API → only `insert_fill` for images/videos exists. Plan around existing text elements
- NEVER use Canva REST editing API endpoints directly (`/designs/{id}/editing_sessions`) → they return 404. Use MCP tools only
- NEVER export Canva designs at a width that doesn't match aspect ratio → causes black borders/letterboxing. Omit width for native dimensions

### DO Spaces

- NEVER load DO Spaces credentials from `NEW-AI-PROJECT/.env` → ALWAYS load from `purpleocaz-canva-mcp/.env` (that's where the keys live)
- NEVER upload to Spaces without ACL → ALWAYS include `ACL='public-read'` in every `s3.put_object()` call
- NEVER use Spaces URLs that are permanent as if they expire → Spaces URLs are permanent. Canva export URLs expire. Never mix them up.

### Git & Security

- NEVER commit .env files or token files to GitHub → ALWAYS check .gitignore before committing
- NEVER hardcode API keys, paths, or thresholds in code → ALWAYS use config.py or environment variables
- NEVER auto-apply Brain proposals → human-in-the-loop required for all Brain-generated changes

### Code & Tools

- NEVER skip `logger.flush()` in finally blocks → Brain goes blind without it
- NEVER use raw sqlite3 → ALWAYS use SQLiteClient from `lib/common_tools/sqlite_client.py`
- NEVER write Etsy listing copy without reading `skills/stop-slop/SKILL.md` first → score must be 35/50+

---

## VERIFICATION RULES

After EVERY action, verify it worked. Show the proof. Never assume.

**After Etsy image upload:**
```bash
curl -s "https://openapi.etsy.com/v3/application/listings/{ID}/images" \
  -H "x-api-key: 19d2q2xcg1ccipoj4doub0ee"
```
Count the images. Show the count. Only continue if count matches expected.

**After Etsy file upload:**
```bash
curl -s "https://openapi.etsy.com/v3/application/shops/34071205/listings/{ID}/files" \
  -H "x-api-key: 19d2q2xcg1ccipoj4doub0ee"
```
Show filename and file_id. Only continue if file is present.

**After DO Spaces upload:**
```bash
curl -I "{SPACES_URL}"
```
Must return HTTP 200. If not 200 — stop and fix before continuing.

**After every git commit:**
```bash
git log --oneline -3
```
Show the output. Confirm the commit is there.

**After Canva design creation:**
Run `get-design` with the design ID. Confirm it exists and is in the correct folder.

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

## THE STAR SELLER STANDARD

Every Etsy listing must have 7 images minimum before being published:

| Rank | Image | Purpose |
|------|-------|---------|
| 1 | Hero | Stops the scroll |
| 2 | What's Inside | Removes doubt |
| 3 | Lifestyle Mockup | Builds desire |
| 4 | How It Works | Removes friction |
| 5 | Why Buy This | Justifies purchase |
| 6 | Canva Basics | Handles objections |
| 7 | Please Note | Builds trust |

A listing with fewer than 7 images is NOT ready to publish.
A listing with a weak hero image is NOT ready to publish.

---

## KEY CREDENTIALS AND IDs

| Item | Value |
|------|-------|
| Shop ID | `34071205` |
| Etsy API Key | `19d2q2xcg1ccipoj4doub0ee` |
| Canva Client ID | `OC-AZyAz47KwCUv` |
| DO Spaces bucket | `purpleocaz-assets.lon1.digitaloceanspaces.com` |
| Droplet IP | `167.99.90.58` |
| Project root | `/root/NEW-AI-PROJECT/` |
| Etsy tokens | `workflows/etsy_analytics/etsy_tokens.json` |
| Canva tokens | `workflows/auto_listing_creator/canva_tokens.json` |
| DO Spaces creds | `purpleocaz-canva-mcp/.env` |

**Canva Folders:**

| Folder | ID |
|--------|----|
| PurpleOcaz root | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails Hero | `FAHENqKrgvk` |
| Car Detail | `FAFN0i-UFTI` |

---

## RULES (auto-loaded by Claude Code)

| File | Scope |
|------|-------|
| `.claude/rules/pipeline.md` | Listing pipeline: image sources, hero thumbnails, design flow |
| `.claude/rules/canva.md` | Canva MCP: delivery links, folder IDs, element limits, gotchas |
| `.claude/rules/etsy.md` | Etsy API: tags, pricing, auth, verification |
| `.claude/rules/database.md` | SQLiteClient access, schema rules |
| `.claude/rules/security.md` | Credentials, protected files, Brain safety |
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
- **No logs after run**: Missing `logger.flush()` in finally → see 02-orchestrator.md
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
