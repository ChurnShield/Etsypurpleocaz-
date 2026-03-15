#!/usr/bin/env python3
# =============================================================================
# workflows/auto_listing_creator/create_etsy_listing.py
#
# Offline listing generator: reads a niche JSON config and prints a full
# Etsy listing preview (title, description, tags, price).
# No API calls — pure template-based generation.
#
# Usage:
#   python create_etsy_listing.py niches/tattoo_business_card.json
# =============================================================================

import json
import sys
import os
import textwrap


def load_niche_config(path):
    """Load and validate a niche JSON config file."""
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required = [
        "niche_name", "niche_display", "niche_keywords", "target_audience",
        "use_cases", "tags", "price_gbp", "card_size", "file_format",
    ]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"Error: missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return config


def generate_title(config):
    """Generate an SEO title: primary keyword in first 50 chars, under 15 words."""
    display = config["niche_display"]
    # Primary keyword phrase front-loaded
    title = (
        f"{display} Business Card Template, Editable Canva Design, "
        f"Printable {display} Card"
    )
    # Enforce under 15 words — trim from end if needed
    words = title.split()
    if len(words) > 15:
        title = " ".join(words[:15])
    return title


def generate_description(config):
    """Generate a full Etsy listing description from the niche config."""
    niche = config["niche_display"]
    audience = config["target_audience"]
    use_cases = config["use_cases"]
    card_size = config["card_size"]
    file_format = config["file_format"]
    colours = config.get("attributes", {})
    primary_colour = colours.get("primary_colour", "dark")
    secondary_colour = colours.get("secondary_colour", "light")
    keywords = config.get("niche_keywords", [])
    keyword_list = ", ".join(keywords[:4])

    description = textwrap.dedent(f"""\
        Looking for a professional, eye-catching business card for your {niche.lower()} studio? Stand out from the crowd with this beautifully designed, fully editable Canva template — ready to customise and print in minutes.

        ═══════════════════════════════
        WHAT'S INCLUDED
        ═══════════════════════════════
        - 2 editable business card designs (front & back)
        - {card_size} standard size
        - {primary_colour.title()} & {secondary_colour} colour scheme
        - {file_format}
        - Instant download after purchase

        ═══════════════════════════════
        HOW TO EDIT
        ═══════════════════════════════
        1. Purchase and download the PDF
        2. Click the Canva link inside
        3. Edit text, colours, fonts, and images to match your brand
        4. Download as PDF or PNG and print at home or at any print shop

        No Canva Pro required — works with the free version!

        ═══════════════════════════════
        FEATURES
        ═══════════════════════════════
        - Professionally designed for {keyword_list}
        - Fully customisable — change every element
        - Print-ready at {card_size} with bleed
        - High-resolution 300 DPI output
        - Works on desktop and mobile Canva

        ═══════════════════════════════
        PERFECT FOR
        ═══════════════════════════════
        - {niche} professionals building their brand
        - New studios and shops needing instant branding
        - {use_cases.title()}
        - Gift for a {niche.lower()} apprentice or artist

        ═══════════════════════════════
        FAQ
        ═══════════════════════════════
        Q: Do I need Canva Pro?
        A: No! This template works with the free version of Canva.

        Q: Can I change the colours and fonts?
        A: Absolutely — every element is fully editable.

        Q: How do I print these?
        A: Download as PDF and print at home, at a local shop, or via an online print service like Vistaprint.

        ═══════════════════════════════
        PLEASE NOTE
        ═══════════════════════════════
        This is a DIGITAL product — no physical item will be shipped. You will receive a PDF with a link to edit in Canva. Colours may vary slightly depending on your screen and printer settings.

        Perfect for: {audience}""")

    return description


def print_listing_preview(config, title, description):
    """Print the full listing preview to screen."""
    tags = config["tags"]
    price = config["price_gbp"]
    niche = config["niche_display"]

    separator = "=" * 60

    print(f"\n{separator}")
    print(f"  ETSY LISTING PREVIEW — {niche} Business Card")
    print(separator)

    print(f"\n{'TITLE':}")
    print(f"  {title}")
    print(f"  ({len(title)} chars, {len(title.split())} words)")

    # Check primary keyword in first 50 chars
    first_50 = title[:50].lower()
    primary_kw = config["niche_keywords"][0] if config["niche_keywords"] else ""
    kw_check = "YES" if primary_kw.lower() in first_50 else "NO"
    print(f"  Primary keyword '{primary_kw}' in first 50 chars: {kw_check}")

    print(f"\n{'PRICE':}")
    print(f"  £{price:.2f} GBP")

    print(f"\n{'TAGS':} ({len(tags)}/13)")
    for i, tag in enumerate(tags, 1):
        length_warn = " [!>20]" if len(tag) > 20 else ""
        print(f"  {i:2d}. {tag}{length_warn}")

    print(f"\n{'DESCRIPTION':}")
    print("-" * 60)
    print(description)
    print("-" * 60)

    # Summary stats
    print(f"\n{'LISTING STATS':}")
    print(f"  Title length:    {len(title)} / 140 chars")
    print(f"  Title words:     {len(title.split())} / 15 max")
    print(f"  Tags count:      {len(tags)} / 13")
    over_20 = [t for t in tags if len(t) > 20]
    if over_20:
        print(f"  Tags over 20ch:  {len(over_20)} — {over_20}")
    else:
        print(f"  Tags over 20ch:  0 (all valid)")
    print(f"  Price:           £{price:.2f}")
    print(f"  File format:     {config['file_format']}")
    print(f"  Card size:       {config['card_size']}")
    print(separator)
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_etsy_listing.py <niche_config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_niche_config(config_path)

    title = generate_title(config)
    description = generate_description(config)

    print_listing_preview(config, title, description)


if __name__ == "__main__":
    main()
