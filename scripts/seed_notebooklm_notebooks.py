#!/usr/bin/env python3
# =============================================================================
# scripts/seed_notebooklm_notebooks.py
#
# One-time setup script to create and seed NotebookLM notebooks per niche.
# Creates a notebook for each configured niche and populates it with
# foundational business expertise content.
#
# Usage:
#   python scripts/seed_notebooklm_notebooks.py
#
# Prerequisites:
#   - notebooklm-mcp-cli installed: pip install notebooklm-mcp-cli
#   - Authenticated: nlm login
#
# After running, set the notebook IDs in your .env file:
#   NOTEBOOKLM_NOTEBOOK_TATTOO=<id>
#   NOTEBOOKLM_NOTEBOOK_NAIL=<id>
#   etc.
# =============================================================================

import json
import subprocess
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)
sys.path.insert(0, _project_root)


NICHES = {
    "tattoo": {
        "name": "tattoo-business-expertise",
        "sources": [
            {
                "title": "Tattoo Studio Business Fundamentals",
                "content": (
                    "Complete guide to running a professional tattoo studio.\n\n"
                    "ESSENTIAL BUSINESS DOCUMENTS:\n"
                    "- Appointment cards: Professional scheduling cards with studio name, date, time\n"
                    "- Gift certificates: Revenue driver (30% average markup), great for holidays\n"
                    "- Price lists/service menus: Clear pricing builds trust and reduces enquiries\n"
                    "- Consent forms: Legal requirement in most jurisdictions\n"
                    "- Aftercare cards: Reduces complications, improves reviews, shows professionalism\n"
                    "- Business cards: First impression piece for networking and client referrals\n"
                    "- Intake forms: Streamlines client onboarding, captures allergies/medical info\n\n"
                    "INDUSTRY KEYWORDS (what buyers search):\n"
                    "- 'tattoo gift card template', 'ink studio voucher'\n"
                    "- 'tattoo consent form printable', 'aftercare card editable'\n"
                    "- 'tattoo price list canva', 'tattoo appointment card'\n"
                    "- 'tattoo business card template', 'tattoo studio branding kit'\n\n"
                    "BUYER PSYCHOLOGY:\n"
                    "- Tattoo studio owners want to look professional but lack design skills\n"
                    "- They search for 'editable' and 'instant download' because they need it NOW\n"
                    "- Bundles are attractive because they solve multiple problems at once\n"
                    "- Price sensitivity: willing to pay £3-8 for individual templates, £15-25 for bundles\n"
                ),
            },
            {
                "title": "Tattoo Industry Trends 2025-2026",
                "content": (
                    "Current trends in the tattoo industry:\n\n"
                    "- Fine-line and minimalist tattoos: Growing 40% YoY, driving new studio openings\n"
                    "- Digital-first branding: Studios expected to have professional online presence\n"
                    "- Gift certificate demand: Peaks in December (holiday season) and February (Valentine's)\n"
                    "- Mobile booking: 70% of appointments now booked online\n"
                    "- Instagram marketing: Primary client acquisition channel for studios\n"
                    "- Health regulations: Increasing documentation requirements (consent, aftercare)\n"
                    "- Studio specialization: Niche studios (watercolor, geometric, botanical) growing\n"
                    "- Sustainability: Eco-friendly inks and practices becoming a selling point\n"
                ),
            },
        ],
    },
    "nail": {
        "name": "nail-salon-expertise",
        "sources": [
            {
                "title": "Nail Salon Business Fundamentals",
                "content": (
                    "Guide to professional nail salon management and branding.\n\n"
                    "ESSENTIAL DOCUMENTS:\n"
                    "- Service menus with clear pricing tiers\n"
                    "- Gift certificates (drive 25-40% of new client visits)\n"
                    "- Appointment cards for repeat booking\n"
                    "- Business cards for networking\n"
                    "- Social media templates for Instagram marketing\n\n"
                    "BUYER KEYWORDS:\n"
                    "- 'nail salon gift card', 'nail tech business card'\n"
                    "- 'nail price list template', 'nail salon branding'\n"
                    "- 'manicure gift certificate', 'nail art price list'\n"
                ),
            },
        ],
    },
    "hair": {
        "name": "hair-salon-expertise",
        "sources": [
            {
                "title": "Hair Salon & Barber Business Fundamentals",
                "content": (
                    "Guide to hair salon and barber shop branding.\n\n"
                    "ESSENTIAL DOCUMENTS:\n"
                    "- Service menus (cuts, color, treatments, packages)\n"
                    "- Gift certificates (top seller during holidays)\n"
                    "- Appointment cards and consultation forms\n"
                    "- Business cards and referral cards\n\n"
                    "BUYER KEYWORDS:\n"
                    "- 'hair salon gift card', 'barber price list'\n"
                    "- 'salon service menu template', 'hair stylist branding'\n"
                ),
            },
        ],
    },
    "beauty": {
        "name": "beauty-spa-expertise",
        "sources": [
            {
                "title": "Beauty & Spa Business Fundamentals",
                "content": (
                    "Guide to beauty and spa business branding.\n\n"
                    "ESSENTIAL DOCUMENTS:\n"
                    "- Service menus (facials, waxing, lash, massage)\n"
                    "- Gift certificates and vouchers\n"
                    "- Consent forms (especially for treatments)\n"
                    "- Aftercare cards (for lash, wax, facial treatments)\n\n"
                    "BUYER KEYWORDS:\n"
                    "- 'spa gift certificate', 'beauty salon voucher'\n"
                    "- 'esthetician price list', 'lash tech business card'\n"
                ),
            },
        ],
    },
}


def check_nlm_available():
    """Check if nlm CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["nlm", "login", "--check"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def create_notebook(name):
    """Create a NotebookLM notebook and return its ID."""
    try:
        result = subprocess.run(
            ["nlm", "notebook", "create", name, "--format", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("id", data.get("notebook_id", ""))
        print(f"  Error creating notebook: {result.stderr}")
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"  Error: {e}")
        return None


def add_source(notebook_id, title, content):
    """Add a text source to a notebook."""
    try:
        result = subprocess.run(
            ["nlm", "source", "add", notebook_id,
             "--type", "text", "--title", title,
             "--content", content[:50000]],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main():
    print("=" * 60)
    print("  NotebookLM Knowledge Base Seeding Script")
    print("=" * 60)

    if not check_nlm_available():
        print("\nERROR: nlm CLI is not installed or not authenticated.")
        print("Install: pip install notebooklm-mcp-cli")
        print("Auth:    nlm login")
        return

    env_lines = []

    for niche, config in NICHES.items():
        print(f"\n--- {niche.upper()} ---")

        # Create notebook
        notebook_id = create_notebook(config["name"])
        if not notebook_id:
            print(f"  FAILED to create notebook for {niche}")
            continue

        print(f"  Created notebook: {notebook_id}")
        env_var = f"NOTEBOOKLM_NOTEBOOK_{niche.upper()}"
        env_lines.append(f"{env_var}={notebook_id}")

        # Add sources
        for source in config["sources"]:
            success = add_source(notebook_id, source["title"], source["content"])
            status = "OK" if success else "FAILED"
            print(f"  Source '{source['title']}': {status}")

    if env_lines:
        print(f"\n{'=' * 60}")
        print("  Add these to your .env file:")
        print("=" * 60)
        for line in env_lines:
            print(f"  {line}")
        print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
