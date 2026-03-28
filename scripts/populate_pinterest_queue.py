#!/usr/bin/env python3
"""
populate_pinterest_queue.py — Build pinterest_queue.json from Spaces-hosted pins.

Scans all known Spaces CDN pins across all niches.
Adds any pin not already in the queue, spaced 1 per day across 3 daily slots.
Auto-generates titles and descriptions from niche + pin type.

Usage:
    python3 scripts/populate_pinterest_queue.py [--preview]
"""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

PROJECT    = Path(__file__).parent.parent
QUEUE_FILE = PROJECT / "configs" / "pinterest_queue.json"

# ── Niche pin catalogue ───────────────────────────────────────────────────────
# All Spaces-hosted pins. Add new niches here as they are built.

SPACES = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/pinterest"

NICHE_PINS = [
    # ── Car Detailing ─────────────────────────────────────────────────────────
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "hero_overview",
        "image_url":  f"{SPACES}/car-detail-pin-1.png",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "50+ Car Detailing Canva Templates | Complete Business Kit",
        "description": (
            "Everything a car detailing business needs in one Canva bundle. "
            "Business cards, job forms, vehicle condition reports, social media posts, "
            "flyers, and more. Instant download — fully editable in Canva Free. "
            "Professional templates designed for mobile detailers and detailing studios. "
            "#CarDetailing #SmallBusinessTemplates #CanvaTemplates #CarDetailingBusiness"
        ),
    },
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "business_cards",
        "image_url":  f"{SPACES}/car-detail-pin-2.png",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "Car Detailing Business Cards | Dark & Light Canva Templates",
        "description": (
            "Professional business card templates for car detailers. "
            "Two variants (dark and light) fully editable in Canva Free. "
            "Add your logo, phone, social handles and you're done. Instant download. "
            "#CarDetailingBusinessCard #CanvaTemplates #MobileDetailing"
        ),
    },
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "client_forms",
        "image_url":  f"{SPACES}/car-detail-pin-3.png",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "Car Detailing Client Forms | Vehicle Condition Report + Checklist",
        "description": (
            "Protect your business with professional car detailing forms. "
            "Includes vehicle condition report, pre-service checklist, and client intake form. "
            "Editable in Canva Free — print or use digitally. Instant download. "
            "#CarDetailingForms #VehicleConditionReport #DetailingBusiness"
        ),
    },
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "marketing",
        "image_url":  f"{SPACES}/car-detail-pin-4.png",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "Car Detailing Marketing Pack | Instagram Posts + Flyers | Canva",
        "description": (
            "Grow your detailing business with ready-made marketing materials. "
            "Includes Instagram posts, promo flyers, and before/after templates. "
            "All editable in Canva Free. Designed for mobile and studio detailers. "
            "#CarDetailingMarketing #DetailingInstagram #SmallBusinessCanva"
        ),
    },
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "bundle_cta",
        "image_url":  f"{SPACES}/car-detail-pin-5.png",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "Car Detailing Business Bundle | 50+ Canva Templates | £39.99",
        "description": (
            "The complete car detailing business template bundle. "
            "50+ Canva templates covering branding, forms, social media, and marketing. "
            "One purchase, instant download, edit in Canva Free. "
            "Trusted by detailers across the UK. "
            "#CarDetailingBusiness #CanvaBundle #DetailingTemplates"
        ),
    },
    {
        "niche":      "car-detail",
        "board":      "Car Detailing Business Ideas",
        "pin_type":   "video",
        "image_url":  f"{SPACES}/car-detail-video-pin.mp4",
        "link":       "https://www.etsy.com/listing/4476909005",
        "title":      "Car Detailing Canva Templates | See What's Inside",
        "description": (
            "Watch what's inside the complete car detailing business bundle. "
            "50+ professional Canva templates — business cards, forms, social posts, flyers. "
            "Instant download. Edit in Canva Free. "
            "#CarDetailingTemplates #CanvaTemplates #DetailingBusiness"
        ),
    },

    # ── Restaurant / Cafe ─────────────────────────────────────────────────────
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "hero_overview",
        "image_url":  f"{SPACES}/restaurant-cafe-pin-1.png",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Restaurant & Cafe Canva Templates | Complete Business Bundle",
        "description": (
            "Everything a restaurant or café needs to look professional — in one Canva bundle. "
            "Menus, social media posts, loyalty cards, staff forms, and more. "
            "Instant download, editable in Canva Free. "
            "#RestaurantTemplates #CafeMarketing #CanvaTemplates #SmallBusinessOwner"
        ),
    },
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "menu_branding",
        "image_url":  f"{SPACES}/restaurant-cafe-pin-2.png",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Restaurant Menu Templates | A4 + Digital | Canva Editable",
        "description": (
            "Beautifully designed restaurant and café menu templates. "
            "A4 print-ready and digital format — swap your dishes and brand colours in minutes. "
            "Editable in Canva Free. Instant download. "
            "#RestaurantMenu #CafeMenu #CanvaMenuTemplate #FoodBusiness"
        ),
    },
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "social_media",
        "image_url":  f"{SPACES}/restaurant-cafe-pin-3.png",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Cafe Instagram Templates | 20 Social Media Posts | Canva",
        "description": (
            "Keep your café Instagram looking consistent and professional. "
            "20 ready-made social media post templates — daily specials, seasonal offers, "
            "and more. Editable in Canva Free. Instant download. "
            "#CafeInstagram #RestaurantSocialMedia #CanvaSocialTemplates"
        ),
    },
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "forms_ops",
        "image_url":  f"{SPACES}/restaurant-cafe-pin-4.png",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Restaurant Staff Forms & Operations Templates | Canva",
        "description": (
            "Run your restaurant or café more smoothly with professional operational templates. "
            "Staff rota, opening checklist, incident report, food safety log, and more. "
            "Editable in Canva Free. Instant download. "
            "#RestaurantManagement #CafeOperations #HospitalityTemplates"
        ),
    },
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "bundle_cta",
        "image_url":  f"{SPACES}/restaurant-cafe-pin-5.png",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Restaurant & Cafe Business Bundle | 32 Canva Templates | £39.99",
        "description": (
            "The complete restaurant and café business template bundle. "
            "32 Canva templates — menus, social posts, loyalty cards, staff forms, flyers. "
            "One purchase, instant download, edit in Canva Free. "
            "#RestaurantBusiness #CafeBusiness #CanvaBundle #HospitalityMarketing"
        ),
    },
    {
        "niche":      "restaurant-cafe",
        "board":      "Restaurant & Cafe Business Ideas",
        "pin_type":   "video",
        "image_url":  f"{SPACES}/restaurant-cafe-video-pin.mp4",
        "link":       "https://www.etsy.com/listing/4479049403",
        "title":      "Restaurant Canva Templates | See What's Inside the Bundle",
        "description": (
            "Watch what's inside the complete restaurant & café business bundle. "
            "32 professional Canva templates — menus, social posts, loyalty cards, and forms. "
            "Instant download. Edit in Canva Free. "
            "#RestaurantTemplates #CafeTemplates #CanvaTemplates"
        ),
    },
]


# ── Scheduling logic ──────────────────────────────────────────────────────────

def next_available_slot(queue: list[dict]) -> date:
    """Return the next date with fewer than 3 pins scheduled."""
    # Find the latest scheduled date in the queue
    booked: dict[str, int] = {}
    for p in queue:
        d = p.get("scheduled_date", "")
        if d:
            booked[d] = booked.get(d, 0) + 1

    # Start from tomorrow (don't backfill today — scheduler handles today)
    cursor = date.today() + timedelta(days=1)
    while True:
        key = cursor.isoformat()
        if booked.get(key, 0) < 3:
            booked[key] = booked.get(key, 0) + 1
            return cursor
        cursor += timedelta(days=1)


def already_queued(queue: list[dict], image_url: str) -> bool:
    return any(p.get("image_url") == image_url for p in queue)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Populate pinterest_queue.json")
    ap.add_argument("--preview", action="store_true", help="Print what would be added without writing")
    args = ap.parse_args()

    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    queue: list[dict] = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else []

    added = 0
    for pin in NICHE_PINS:
        if already_queued(queue, pin["image_url"]):
            print(f"  [skip] Already queued: {pin['image_url'].split('/')[-1]}")
            continue

        slot = next_available_slot(queue)
        entry = {
            "status":         "pending",
            "niche":          pin["niche"],
            "board":          pin["board"],
            "pin_type":       pin["pin_type"],
            "title":          pin["title"],
            "description":    pin["description"],
            "image_url":      pin["image_url"],
            "link":           pin["link"],
            "scheduled_date": slot.isoformat(),
        }

        if args.preview:
            print(f"  [ADD] {slot.isoformat()} | {pin['niche']} | {pin['pin_type']} | {pin['title'][:60]}")
        else:
            queue.append(entry)
            print(f"  Queued: {slot.isoformat()} — {pin['title'][:60]}")
        added += 1

    if not args.preview and added:
        save_fn = lambda: QUEUE_FILE.write_text(json.dumps(queue, indent=2))
        save_fn()
        print(f"\n  {added} pin(s) added to queue → {QUEUE_FILE}")
    elif not added:
        print("  Queue is already up to date — nothing to add.")
    else:
        print(f"\n  [PREVIEW] {added} pin(s) would be added (use without --preview to write)")


if __name__ == "__main__":
    main()
