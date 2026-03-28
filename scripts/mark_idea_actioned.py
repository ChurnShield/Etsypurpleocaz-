#!/usr/bin/env python3
"""
mark_idea_actioned.py — Update idea status in ideas_backlog.md.

Usage:
    # Mark matching NEW ideas as ACTIONED (keyword search, case-insensitive)
    python3 scripts/mark_idea_actioned.py --keyword "restaurant" --note "restaurant cafe niche built, listing #4479049403"

    # Mark as SKIPPED with reason
    python3 scripts/mark_idea_actioned.py --keyword "nano banana" --status SKIPPED --note "not relevant to our stack"

    # List all NEW ideas (no changes)
    python3 scripts/mark_idea_actioned.py --list

    # List top N NEW ideas prioritised by label
    python3 scripts/mark_idea_actioned.py --list --top 5

Called automatically by niche_template_factory.py after a successful build
to mark any backlog ideas that match the niche name.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

BACKLOG = Path(__file__).parent.parent / "ideas_backlog.md"

# Priority order for --list output: labels that matter most first
PRIORITY_LABELS = [
    "Etsy Keywords", "Etsy Trends", "Etsy SEO", "Etsy Strategy",
    "Keyword Research", "Trend Analysis", "Listing Optimization",
    "Template Creation", "Conversion", "Vision", "Pipeline",
    "Automation", "Architecture", "Agent Automation",
]


def load():
    return BACKLOG.read_text(encoding="utf-8")


def save(content: str):
    BACKLOG.write_text(content, encoding="utf-8")


def get_new_ideas(content: str) -> list[tuple[int, str]]:
    """Return list of (line_number, line_text) for all [NEW] lines."""
    results = []
    for i, line in enumerate(content.splitlines(), 1):
        if line.startswith("[NEW]"):
            results.append((i, line))
    return results


def priority_key(line: str) -> int:
    for i, label in enumerate(PRIORITY_LABELS):
        if label.lower() in line.lower():
            return i
    return len(PRIORITY_LABELS)


def cmd_list(top: int | None = None):
    content = load()
    ideas = get_new_ideas(content)
    ideas.sort(key=lambda x: priority_key(x[1]))
    if top:
        ideas = ideas[:top]
    print(f"[NEW] ideas in backlog ({len(get_new_ideas(content))} total):\n")
    for lineno, line in ideas:
        # Truncate long lines
        display = line[:120] + "…" if len(line) > 120 else line
        print(f"  L{lineno:>4}  {display}")


def cmd_mark(keyword: str, status: str, note: str | None):
    today = date.today().isoformat()
    content = load()
    lines = content.splitlines(keepends=True)
    matched = 0

    kw_lower = keyword.lower()
    for i, line in enumerate(lines):
        if not line.startswith("[NEW]"):
            continue
        if kw_lower not in line.lower():
            continue
        # Replace [NEW] with [STATUS: date]
        new_prefix = f"[{status}: {today}]"
        new_line = line.replace("[NEW]", new_prefix, 1)
        if note and status == "ACTIONED":
            # Append note before newline
            new_line = new_line.rstrip("\n") + f" — {note}\n"
        lines[i] = new_line
        matched += 1
        print(f"  Marked {status}: {line.strip()[:100]}")

    if matched == 0:
        print(f"  No [NEW] ideas matched keyword '{keyword}'. No changes made.")
        return

    save("".join(lines))
    print(f"\n  {matched} idea(s) marked [{status}: {today}] in {BACKLOG.name}")


def main():
    ap = argparse.ArgumentParser(description="Manage idea statuses in ideas_backlog.md")
    ap.add_argument("--keyword",  help="Keyword to search for in [NEW] ideas (case-insensitive)")
    ap.add_argument("--status",   default="ACTIONED", choices=["ACTIONED", "SKIPPED"],
                    help="New status to apply (default: ACTIONED)")
    ap.add_argument("--note",     help="Short note appended to matched lines (e.g. listing ID, reason)")
    ap.add_argument("--list",     action="store_true", help="List all [NEW] ideas and exit")
    ap.add_argument("--top",      type=int, default=None, help="With --list, show only top N ideas")
    args = ap.parse_args()

    if args.list:
        cmd_list(top=args.top)
        return

    if not args.keyword:
        ap.error("--keyword is required unless --list is used")

    cmd_mark(keyword=args.keyword, status=args.status, note=args.note)


if __name__ == "__main__":
    main()
