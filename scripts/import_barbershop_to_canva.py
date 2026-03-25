#!/usr/bin/env python3
"""
Import 26 barbershop PNG files from DO Spaces into Canva.
For each file:
1. Upload PNG as Canva asset (asset-uploads)
2. Create a Canva design from that asset (with folder_id FAHE94J3odE)
3. Record design_id and view_url

Outputs JSON results for design_registry.json injection.
"""

import json
import time
import sys
import requests

# Load token from file
TOKEN_FILE = "/root/NEW-AI-PROJECT/workflows/auto_listing_creator/canva_tokens.json"
CANVA_API = "https://api.canva.com/rest/v1"
FOLDER_ID = "FAHE94J3odE"
POLL_INTERVAL = 2
MAX_POLLS = 30

with open(TOKEN_FILE) as f:
    tokens = json.load(f)

ACCESS_TOKEN = tokens["access_token"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

DESIGNS = [
    # PRINT (5)
    {
        "category": "print",
        "key": "business_card_front",
        "title": "Barbershop - Business Card Front",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/print/barber_print_01a_business_card_front.png",
    },
    {
        "category": "print",
        "key": "business_card_back",
        "title": "Barbershop - Business Card Back",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/print/barber_print_01b_business_card_back.png",
    },
    {
        "category": "print",
        "key": "appointment_card",
        "title": "Barbershop - Appointment Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/print/barber_print_02_appointment_card.png",
    },
    {
        "category": "print",
        "key": "thank_you_card",
        "title": "Barbershop - Thank You Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/print/barber_print_03_thank_you.png",
    },
    {
        "category": "print",
        "key": "refer_a_friend",
        "title": "Barbershop - Refer a Friend Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/print/barber_print_04_refer_a_friend.png",
    },
    # INSTAGRAM (12)
    {
        "category": "instagram",
        "key": "brand_welcome",
        "title": "Barbershop - IG Brand Welcome",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_01_brand_welcome.png",
    },
    {
        "category": "instagram",
        "key": "services_menu",
        "title": "Barbershop - IG Services Menu",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_02_services_menu.png",
    },
    {
        "category": "instagram",
        "key": "book_now",
        "title": "Barbershop - IG Book Now",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_03_book_now.png",
    },
    {
        "category": "instagram",
        "key": "new_client_offer",
        "title": "Barbershop - IG New Client Offer",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_04_new_client_offer.png",
    },
    {
        "category": "instagram",
        "key": "testimonial",
        "title": "Barbershop - IG Testimonial",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_05_testimonial.png",
    },
    {
        "category": "instagram",
        "key": "tip_of_week",
        "title": "Barbershop - IG Tip of the Week",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_06_tip_of_the_week.png",
    },
    {
        "category": "instagram",
        "key": "before_after",
        "title": "Barbershop - IG Before and After",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_07_before_after.png",
    },
    {
        "category": "instagram",
        "key": "meet_the_barber",
        "title": "Barbershop - IG Meet the Barber",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_08_meet_the_barber.png",
    },
    {
        "category": "instagram",
        "key": "opening_hours",
        "title": "Barbershop - IG Opening Hours",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_09_opening_hours.png",
    },
    {
        "category": "instagram",
        "key": "loyalty_program",
        "title": "Barbershop - IG Loyalty Program",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_10_loyalty_program.png",
    },
    {
        "category": "instagram",
        "key": "referral",
        "title": "Barbershop - IG Referral",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_11_referral.png",
    },
    {
        "category": "instagram",
        "key": "seasonal_promo",
        "title": "Barbershop - IG Seasonal Promo",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/barber_ig_12_seasonal_promo.png",
    },
    # STORIES (6)
    {
        "category": "stories",
        "key": "book_now",
        "title": "Barbershop - Story Book Now",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_01_book_now.png",
    },
    {
        "category": "stories",
        "key": "availability",
        "title": "Barbershop - Story Availability",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_02_availability.png",
    },
    {
        "category": "stories",
        "key": "flash_deal",
        "title": "Barbershop - Story Flash Deal",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_03_flash_deal.png",
    },
    {
        "category": "stories",
        "key": "tip_of_day",
        "title": "Barbershop - Story Tip of Day",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_04_tip_of_day.png",
    },
    {
        "category": "stories",
        "key": "client_shoutout",
        "title": "Barbershop - Story Client Shoutout",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_05_shoutout.png",
    },
    {
        "category": "stories",
        "key": "weekend_special",
        "title": "Barbershop - Story Weekend Special",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/barber_story_06_weekend_special.png",
    },
    # UTILITY (4)
    {
        "category": "utility",
        "key": "google_review",
        "title": "Barbershop - Google Review Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/utility/barber_util_01_google_review.png",
    },
    {
        "category": "utility",
        "key": "tip_guide",
        "title": "Barbershop - Grooming Tip Guide",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/utility/barber_util_02_tip_guide.png",
    },
    {
        "category": "utility",
        "key": "price_list",
        "title": "Barbershop - Price List Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/utility/barber_util_03_price_list.png",
    },
    {
        "category": "utility",
        "key": "aftercare",
        "title": "Barbershop - Aftercare Advice Card",
        "url": "https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/utility/barber_util_04_aftercare.png",
    },
]


def get_image_dimensions(png_bytes: bytes):
    """Extract width and height from PNG header bytes."""
    if png_bytes[1:4] == b"PNG" and len(png_bytes) >= 24:
        import struct
        w = struct.unpack(">I", png_bytes[16:20])[0]
        h = struct.unpack(">I", png_bytes[20:24])[0]
        return w, h
    return 1080, 1080  # fallback


def upload_asset(title: str, image_bytes: bytes) -> str:
    """Upload PNG bytes as Canva asset, poll until done. Returns asset_id."""
    import base64
    name_b64 = base64.b64encode(title.encode()).decode()
    metadata = json.dumps({"name_base64": name_b64})

    resp = requests.post(
        f"{CANVA_API}/asset-uploads",
        data=image_bytes,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
            "Asset-Upload-Metadata": metadata,
        },
    )
    resp.raise_for_status()
    job_id = resp.json()["job"]["id"]

    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        status_resp = requests.get(
            f"{CANVA_API}/asset-uploads/{job_id}",
            headers=HEADERS,
        )
        status_resp.raise_for_status()
        job = status_resp.json()["job"]
        if job["status"] == "success":
            return job["asset"]["id"]
        elif job["status"] == "failed":
            raise RuntimeError(f"Asset upload failed: {job.get('error')}")
        print(f"    Polling asset upload... ({i+1}/{MAX_POLLS})")

    raise RuntimeError("Asset upload timed out")


def create_design(title: str, width: int, height: int, asset_id: str) -> dict:
    """Create a Canva design with the given asset, in target folder. Returns design dict."""
    resp = requests.post(
        f"{CANVA_API}/designs",
        headers=HEADERS,
        json={
            "design_type": {"type": "custom", "width": width, "height": height},
            "title": title,
            "asset_id": asset_id,
            "folder_id": FOLDER_ID,
        },
    )
    resp.raise_for_status()
    return resp.json()["design"]


def get_design(design_id: str) -> dict:
    """Get design details, returns the design dict with urls."""
    resp = requests.get(
        f"{CANVA_API}/designs/{design_id}",
        headers=HEADERS,
    )
    resp.raise_for_status()
    return resp.json()["design"]


def build_view_url(design_id: str) -> str:
    """Build stable Canva view URL from design_id."""
    return f"https://www.canva.com/design/{design_id}/view"


results = {}  # category -> key -> {design_id, view_url, title}

for i, item in enumerate(DESIGNS, 1):
    cat = item["category"]
    key = item["key"]
    title = item["title"]
    spaces_url = item["url"]

    print(f"\n[{i}/26] {title}")
    print(f"  URL: {spaces_url}")

    # Step 1: Download PNG from DO Spaces
    print("  Step 1: Downloading PNG from Spaces...")
    dl_resp = requests.get(spaces_url)
    if dl_resp.status_code != 200:
        print(f"  ERROR: HTTP {dl_resp.status_code} — skipping")
        continue
    png_bytes = dl_resp.content
    width, height = get_image_dimensions(png_bytes)
    print(f"  Downloaded {len(png_bytes)//1024}KB, dimensions: {width}x{height}")

    # Step 2: Upload as Canva asset
    print("  Step 2: Uploading as Canva asset...")
    asset_id = upload_asset(title, png_bytes)
    print(f"  Asset ID: {asset_id}")

    # Step 3: Create Canva design from asset (with folder_id)
    print("  Step 3: Creating Canva design in folder FAHE94J3odE...")
    design = create_design(title, width, height, asset_id)
    design_id = design["id"]
    print(f"  Design ID: {design_id}")

    # Step 4: Get design to confirm and retrieve URL
    print("  Step 4: Verifying design via GET...")
    verified = get_design(design_id)
    view_url = build_view_url(design_id)
    print(f"  Verified: {verified['title']}")
    print(f"  View URL: {view_url}")

    # Record result
    if cat not in results:
        results[cat] = {}
    results[cat][key] = {
        "design_id": design_id,
        "view_url": view_url,
        "title": title,
    }

    print(f"  [OK] {title} -> {design_id}")

# Output final results as JSON
print("\n\n=== FINAL RESULTS ===")
print(json.dumps(results, indent=2))

# Save results to temp file for registry injection
with open("/tmp/barbershop_canva_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nResults saved to /tmp/barbershop_canva_results.json")
