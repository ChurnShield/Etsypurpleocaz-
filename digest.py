"""
Weekly Digest Generator — Agentic AI Self-Improving Loop
=========================================================
Reads transcripts from the last 7 days, sends them to Claude,
and produces:
  1. A weekly digest with flagged ideas (DIGEST_YYYY-MM-DD.md)
  2. An updated ideas backlog (ideas_backlog.md)
  3. Pipeline improvement suggestions

Usage:
  python digest.py           # process last 7 days of transcripts
  python digest.py --all     # process ALL transcripts ever

Requires:
  pip install anthropic
  ANTHROPIC_API_KEY in your .env file
"""

import os
import sys
import argparse

# Force UTF-8 stdout on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
TRANSCRIPTS_DIR = SCRIPT_DIR / "transcripts"
DIGEST_DIR      = SCRIPT_DIR / "digests"
BACKLOG_FILE    = SCRIPT_DIR / "ideas_backlog.md"
DAYS_BACK       = 7

# ── Load API Key ──────────────────────────────────────────────────────────────

def load_api_key() -> str:
    """Load Anthropic API key from .env file or environment."""
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("[ERROR] ANTHROPIC_API_KEY not found in .env or environment.")
        print("   Add it to your .env file: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    return key


# ── Load Transcripts ──────────────────────────────────────────────────────────

def get_recent_transcripts(all_time: bool = False) -> list[dict]:
    """Return list of recent transcript dicts with metadata."""
    if not TRANSCRIPTS_DIR.exists():
        print("[ERROR] No transcripts/ folder found. Run transcribe.py first.")
        sys.exit(1)

    cutoff = datetime.min if all_time else datetime.now() - timedelta(days=DAYS_BACK)
    transcripts = []

    for f in sorted(TRANSCRIPTS_DIR.glob("*.md")):
        modified = datetime.fromtimestamp(f.stat().st_mtime)
        if modified >= cutoff:
            content = f.read_text(encoding="utf-8")
            # Extract tags from content
            tags = "#General"
            for line in content.splitlines():
                if line.startswith("**Tags:**"):
                    tags = line.replace("**Tags:**", "").strip()
                    break
            transcripts.append({
                "filename": f.name,
                "content": content,
                "tags": tags,
                "modified": modified.strftime("%Y-%m-%d"),
            })

    return transcripts


# ── Claude Analysis ───────────────────────────────────────────────────────────

def analyse_transcripts(transcripts: list[dict], api_key: str) -> dict:
    """Send transcripts to Claude for analysis and idea extraction."""
    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic package not found. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Build context from all transcripts
    transcript_context = ""
    for t in transcripts:
        transcript_context += f"\n\n---\nFILE: {t['filename']}\nTAGS: {t['tags']}\n\n{t['content'][:3000]}"

    system_prompt = """You are an intelligent business analyst and agentic AI assistant working with Andy, 
an entrepreneur building wealth through three ventures:

1. PurpleOcaz — Star Seller Etsy shop with 900+ digital template listings
2. ChurnShield — B2B SaaS churn reduction tool (building toward first paying customer)
3. Tails of Sinton Green — dog grooming business

Andy also runs an agentic AI pipeline using Claude Code, n8n, Lovable, and custom Python scripts.
His goal is to build passive income and wealth by automating and improving these businesses constantly.

Your job is to analyse YouTube transcripts Andy has collected and extract maximum value from them.
Be specific, actionable, and always tie ideas back to Andy's actual businesses and pipeline."""

    user_prompt = f"""Analyse these YouTube transcripts collected this week and produce a structured report.

TRANSCRIPTS:
{transcript_context}

Produce your response in this EXACT format:

## 🔥 TOP IDEAS THIS WEEK
List the 3-5 most impactful ideas from all transcripts. For each:
- **Idea:** [clear description]
- **Apply to:** [PurpleOcaz / ChurnShield / AgentPipeline / All]
- **Action:** [specific next step Andy can take]
- **Effort:** [Low / Medium / High]

## 💡 FULL IDEAS BACKLOG ENTRIES
List ALL actionable ideas extracted, even smaller ones. Format each as:
[ ] [Category] Idea description — Source: [video title]

## 🤖 PIPELINE IMPROVEMENT SUGGESTIONS
Specific suggestions to improve Andy's agentic AI pipeline based on what you learned:
- Any new tools, techniques, or workflows mentioned
- Ways to improve the transcription/digest loop itself
- Automations that could save time across PurpleOcaz or ChurnShield

## 📊 WEEKLY SUMMARY
2-3 sentences summarising what was learned this week and the single most important thing to action first.

## 🏷️ TRANSCRIPT BREAKDOWN
Brief one-liner on each transcript processed and its relevance score (1-10) for Andy's goals."""

    print("  ->Sending to Claude for analysis...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return {"analysis": response.content[0].text}


# ── Save Outputs ──────────────────────────────────────────────────────────────

def save_digest(analysis: str, transcript_count: int) -> Path:
    """Save the weekly digest as a markdown file."""
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    digest_path = DIGEST_DIR / f"DIGEST_{date_str}.md"

    content = f"""# Weekly Intelligence Digest — {date_str}

**Transcripts processed:** {transcript_count}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  

---

{analysis}

---
*Auto-generated by digest.py | Agentic AI Self-Improving Loop*
"""
    digest_path.write_text(content, encoding="utf-8")
    return digest_path


def update_backlog(analysis: str) -> None:
    """Extract backlog items from analysis and append to ideas_backlog.md."""
    # Pull out the backlog section
    lines = analysis.splitlines()
    in_backlog = False
    backlog_items = []

    for line in lines:
        if "FULL IDEAS BACKLOG" in line:
            in_backlog = True
            continue
        if in_backlog and line.startswith("## "):
            break
        if in_backlog and line.strip().startswith("[ ]"):
            backlog_items.append(line.strip())

    if not backlog_items:
        return

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Append to backlog file
    if not BACKLOG_FILE.exists():
        BACKLOG_FILE.write_text(
            "# Ideas Backlog\n\nAuto-populated from weekly YouTube digest.\n\n",
            encoding="utf-8"
        )

    existing = BACKLOG_FILE.read_text(encoding="utf-8")
    new_section = f"\n## Added {date_str}\n\n" + "\n".join(backlog_items) + "\n"
    BACKLOG_FILE.write_text(existing + new_section, encoding="utf-8")
    print(f"  ->Added {len(backlog_items)} items to ideas_backlog.md")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Weekly digest from YouTube transcripts")
    parser.add_argument("--all", action="store_true", help="Process all transcripts ever")
    args = parser.parse_args()

    print("\n[BRAIN] Weekly Digest Generator")
    print("=" * 45)

    api_key = load_api_key()
    transcripts = get_recent_transcripts(all_time=args.all)

    if not transcripts:
        period = "ever" if args.all else f"the last {DAYS_BACK} days"
        print(f"[INFO] No transcripts found from {period}.")
        print("   Run transcribe.py first to collect some videos.")
        sys.exit(0)

    print(f"[DOCS] Found {len(transcripts)} transcript(s) to analyse:")
    for t in transcripts:
        print(f"   {t['tags']} -- {t['filename']}")

    print("\n[AI] Analysing with Claude...")
    result = analyse_transcripts(transcripts, api_key)
    analysis = result["analysis"]

    # Save digest
    digest_path = save_digest(analysis, len(transcripts))
    print(f"\n[OK] Digest saved -> digests/{digest_path.name}")

    # Update backlog
    update_backlog(analysis)
    print(f"[OK] Backlog updated -> ideas_backlog.md")

    # Print summary to terminal
    print("\n" + "=" * 45)
    print("[PREVIEW] DIGEST PREVIEW:")
    print("=" * 45)
    # Show just the top ideas section
    lines = analysis.splitlines()
    preview_lines = []
    in_top = False
    for line in lines:
        if "TOP IDEAS" in line:
            in_top = True
        if in_top and line.startswith("## ") and "TOP IDEAS" not in line:
            break
        if in_top:
            preview_lines.append(line)
    print("\n".join(preview_lines[:30]))
    print(f"\n[FILE] Full digest: digests/{digest_path.name}")
    print("=" * 45)


if __name__ == "__main__":
    main()
