#!/usr/bin/env python3
"""
Digest the latest weekly performance report into PERFORMANCE_INSIGHTS.md.
Runs Monday 8:30am after weekly_performance_check.py (8:00am).

Reads the newest JSON from reports/, extracts:
- Top 5 performers with winning-pattern analysis
- Underperformers to consider updating or deleting
- Correlations between niches, price points, tag counts and views
"""
import glob
import json
import os
import re
import statistics
import sys
from collections import Counter
from datetime import datetime

REPORT_DIR = "/root/NEW-AI-PROJECT/reports"
OUTPUT_FILE = "/root/NEW-AI-PROJECT/PERFORMANCE_INSIGHTS.md"


def find_latest_report():
    """Return the path to the most recent performance JSON."""
    pattern = os.path.join(REPORT_DIR, "performance_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    return files[-1]


def extract_niche(title):
    """Extract a rough niche keyword from a listing title."""
    title_lower = title.lower()
    # Common niche keywords in tattoo/digital template space
    niches = [
        "tattoo", "appointment", "consent", "aftercare", "invoice",
        "business card", "template", "planner", "tracker", "bundle",
        "floral", "botanical", "minimalist", "gothic", "watercolor",
        "geometric", "mandala", "tribal", "traditional", "fine line",
    ]
    found = [n for n in niches if n in title_lower]
    return found[0] if found else "other"


def analyze_correlations(listings):
    """Analyze what correlates with high views."""
    if not listings:
        return {}

    views = [l["views"] for l in listings]
    if not views:
        return {}

    median_views = statistics.median(views)

    high = [l for l in listings if l["views"] >= median_views]
    low = [l for l in listings if l["views"] < median_views]

    def avg(items, key):
        vals = [i[key] for i in items if i.get(key) is not None]
        return round(sum(vals) / len(vals), 2) if vals else 0

    # Price correlation
    high_avg_price = avg(high, "price")
    low_avg_price = avg(low, "price")

    # Tag count correlation
    high_avg_tags = avg(high, "tags")
    low_avg_tags = avg(low, "tags")

    # Niche breakdown for top performers
    niche_views = Counter()
    niche_counts = Counter()
    for l in listings:
        niche = extract_niche(l["title"])
        niche_views[niche] += l["views"]
        niche_counts[niche] += 1

    niche_avg = {}
    for niche in niche_counts:
        niche_avg[niche] = round(niche_views[niche] / niche_counts[niche], 1)

    top_niches = sorted(niche_avg.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "median_views": median_views,
        "high_performers": {
            "count": len(high),
            "avg_price": high_avg_price,
            "avg_tags": high_avg_tags,
        },
        "low_performers": {
            "count": len(low),
            "avg_price": low_avg_price,
            "avg_tags": low_avg_tags,
        },
        "top_niches": top_niches,
    }


def format_insights(report, correlations):
    """Build the markdown insights document."""
    generated = report.get("generated", "unknown")
    summary = report.get("summary", {})
    top5 = report.get("top_5", [])
    under = report.get("underperformers", [])

    lines = [
        f"# Performance Insights",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Source report:** {generated}  ",
        f"**Total listings:** {summary.get('total_listings', 0)}  ",
        f"**Total views:** {summary.get('total_views', 0):,}  ",
        f"**Total sales:** {summary.get('total_sales', 0):,}  ",
        f"**Total revenue:** {summary.get('total_revenue', 0):,.2f} GBP",
        f"",
        f"---",
        f"",
        f"## Winning Patterns",
        f"",
    ]

    # Correlation insights
    if correlations:
        hp = correlations.get("high_performers", {})
        lp = correlations.get("low_performers", {})
        median = correlations.get("median_views", 0)

        lines.append(f"**Median views:** {median:,}")
        lines.append(f"")
        lines.append(f"| Metric | Above median | Below median |")
        lines.append(f"|--------|-------------|-------------|")
        lines.append(
            f"| Avg price | {hp.get('avg_price', 0):.2f} | "
            f"{lp.get('avg_price', 0):.2f} |"
        )
        lines.append(
            f"| Avg tag count | {hp.get('avg_tags', 0):.1f} | "
            f"{lp.get('avg_tags', 0):.1f} |"
        )
        lines.append(f"| Listing count | {hp.get('count', 0)} | {lp.get('count', 0)} |")
        lines.append(f"")

        top_niches = correlations.get("top_niches", [])
        if top_niches:
            lines.append(f"### Top niches by avg views")
            lines.append(f"")
            lines.append(f"| Niche | Avg views |")
            lines.append(f"|-------|-----------|")
            for niche, avg_v in top_niches:
                lines.append(f"| {niche} | {avg_v:,.1f} |")
            lines.append(f"")

    # Top 5
    lines.append(f"## Top 5 Performers")
    lines.append(f"")
    lines.append(f"| # | Views | Favs | Sales | Price | Title |")
    lines.append(f"|---|-------|------|-------|-------|-------|")
    for i, item in enumerate(top5, 1):
        lines.append(
            f"| {i} | {item['views']:,} | {item['favorites']} | "
            f"{item['sales']} | {item['price']:.2f} | {item['title']} |"
        )
    lines.append(f"")

    # Underperformers
    lines.append(f"## Underperformers ({len(under)} listings with <10 views)")
    lines.append(f"")
    if under:
        lines.append(f"Consider updating tags/titles or deleting these listings:")
        lines.append(f"")
        lines.append(f"| Views | Favs | Sales | Tags | Title | Action |")
        lines.append(f"|-------|------|-------|------|-------|--------|")
        for item in under:
            action = "DELETE" if item["views"] == 0 and item["sales"] == 0 else "UPDATE"
            lines.append(
                f"| {item['views']} | {item['favorites']} | {item['sales']} | "
                f"{item['tags']} | {item['title']} | {action} |"
            )
    else:
        lines.append(f"No underperformers found.")
    lines.append(f"")

    return "\n".join(lines)


def main():
    print(f"\nDigest Performance — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    report_path = find_latest_report()
    if not report_path:
        print(f"No reports found in {REPORT_DIR}")
        sys.exit(1)

    print(f"Reading: {report_path}")
    with open(report_path) as f:
        report = json.load(f)

    all_listings = report.get("all_listings", [])
    print(f"Listings in report: {len(all_listings)}")

    correlations = analyze_correlations(all_listings)
    md = format_insights(report, correlations)

    with open(OUTPUT_FILE, "w") as f:
        f.write(md)

    print(f"Insights written to: {OUTPUT_FILE}")
    print(f"Top 5 + {len(report.get('underperformers', []))} underperformers analyzed")


if __name__ == "__main__":
    main()
