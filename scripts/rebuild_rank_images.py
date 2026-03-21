#!/usr/bin/env python3
"""Rebuild forms listing rank images 2,4,5,6,7 with content scaled up to fill 2000x2000."""

import os
import sys
import boto3
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

SZ = 2000

# Palette
DARK_RED = (139, 26, 26)
CREAM = (245, 240, 232)
GOLD = (201, 169, 110)
CHARCOAL = (26, 26, 26)
WHITE = (255, 255, 255)

# Fonts
_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fnt(size, path=_SANS_B):
    return ImageFont.truetype(path, size)


def center_text(draw, text, cx, y, f, fill):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, y), text, fill=fill, font=f)
    return bbox[3] - bbox[1]


def gold_line(draw, y, width=400, cx=SZ // 2):
    x0 = cx - width // 2
    draw.rectangle([(x0, y), (x0 + width, y + 3)], fill=GOLD)


def header_bar(img, draw, text, subtitle=None, bar_height=None):
    """Draw a dark red header bar at top with centered text, and a thin bottom bar."""
    f_title = fnt(62, _SERIF_B)
    title_h = draw.textbbox((0, 0), text, font=f_title)[3]

    if subtitle:
        f_sub = fnt(44, _SANS)
        sub_h = draw.textbbox((0, 0), subtitle, font=f_sub)[3]
        if bar_height is None:
            bar_height = title_h + sub_h + 90
        draw.rectangle([(0, 0), (SZ, bar_height)], fill=DARK_RED)
        center_text(draw, text, SZ // 2, 30, f_title, CREAM)
        center_text(draw, subtitle, SZ // 2, 30 + title_h + 15, f_sub, GOLD)
    else:
        if bar_height is None:
            bar_height = title_h + 65
        draw.rectangle([(0, 0), (SZ, bar_height)], fill=DARK_RED)
        center_text(draw, text, SZ // 2, 30, f_title, CREAM)

    # Thin bottom bar
    draw.rectangle([(0, SZ - 18), (SZ, SZ)], fill=DARK_RED)

    return bar_height


# ============================================================
# RANK 2 — What's Inside Your Bundle
# ============================================================
def build_rank2():
    img = Image.new("RGB", (SZ, SZ), CREAM)
    draw = ImageDraw.Draw(img)

    bar_h = header_bar(img, draw, "WHAT'S INSIDE YOUR BUNDLE")

    # Gold separator line below header
    gold_line(draw, bar_h + 25, width=1600)

    items = [
        ("1", "Client Consent Form"),
        ("2", "Client Intake Form"),
        ("3", "Aftercare Instructions"),
        ("4", "Invoice"),
        ("5", "Session Tracker"),
        ("6", "Photo Release"),
        ("7", "Cancellation Policy"),
        ("8", "Design Request Form"),
    ]

    f_num = fnt(36, _SANS_B)
    f_item = fnt(42, _SANS_B)

    # Layout: 2 columns, 4 rows, spread across canvas
    col_left_cx = SZ * 0.30
    col_right_cx = SZ * 0.72
    start_y = bar_h + 80
    # End before footer area
    footer_zone = 350
    available_h = SZ - 18 - start_y - footer_zone
    row_spacing = available_h / 4
    circle_r = 32

    for i, (num, label) in enumerate(items):
        col = i % 2
        row = i // 2
        cx = col_left_cx if col == 0 else col_right_cx
        y = start_y + row * row_spacing + row_spacing * 0.35

        # Dark red numbered circle
        draw.ellipse(
            [cx - 90 - circle_r, y - circle_r, cx - 90 + circle_r, y + circle_r],
            fill=DARK_RED,
        )
        nbbox = draw.textbbox((0, 0), num, font=f_num)
        nw = nbbox[2] - nbbox[0]
        nh = nbbox[3] - nbbox[1]
        draw.text(
            (cx - 90 - nw // 2, y - nh // 2 - 3), num, fill=WHITE, font=f_num
        )

        # Gold diamond above right column items
        if col == 1:
            diamond_y = y - circle_r - 22
            diamond_x = cx - 90
            ds = 6
            draw.polygon(
                [
                    (diamond_x, diamond_y - ds),
                    (diamond_x + ds, diamond_y),
                    (diamond_x, diamond_y + ds),
                    (diamond_x - ds, diamond_y),
                ],
                fill=GOLD,
            )

        # Item text
        draw.text((cx - 45, y - 18), label, fill=CHARCOAL, font=f_item)

    # Footer: gold separator + text
    footer_y = SZ - 18 - footer_zone + 40
    gold_line(draw, footer_y, width=1600)

    f_footer_title = fnt(44, _SANS_B)
    f_footer_sub = fnt(36, _SANS)
    center_text(draw, "8 Print-Ready PDF Templates", SZ // 2, footer_y + 55, f_footer_title, DARK_RED)
    center_text(draw, "Edit Free in Canva", SZ // 2, footer_y + 115, f_footer_sub, CHARCOAL)

    # Brand line at bottom
    f_brand = fnt(28, _SANS)
    center_text(draw, "PURPLEOCAZ", SZ // 2, SZ - 18 - 60, f_brand, GOLD)

    return img


# ============================================================
# RANK 4 — Edit in Minutes / 3 Simple Steps
# ============================================================
def build_rank4():
    img = Image.new("RGB", (SZ, SZ), CREAM)
    draw = ImageDraw.Draw(img)

    # Thin top accent bar
    draw.rectangle([(0, 0), (SZ, 15)], fill=DARK_RED)

    # Title — pushed up tight
    f_title = fnt(82, _SERIF_B)
    f_sub = fnt(54, _SANS)
    center_text(draw, "EDIT IN MINUTES", SZ // 2, 50, f_title, DARK_RED)
    center_text(draw, "3 SIMPLE STEPS", SZ // 2, 155, f_sub, GOLD)

    # Gold separator
    gold_line(draw, 235, width=1200)

    # Three steps with large circles + arrows
    steps = [
        ("1", "Download\ninstantly\nfrom Etsy"),
        ("2", "Open free\nin Canva"),
        ("3", "Add your logo\n& studio\ndetails"),
    ]

    circle_r = 125  # 250px diameter
    f_num = fnt(100, _SANS_B)
    f_desc = fnt(60, _SANS)
    desc_line_h = 85

    # Layout targets: title zone 0-235, content 280-1750, bottom bar 1982-2000
    # Content zone = 1470px. Divide into: circles+text (top 60%), gap, footer (bottom)
    step_cy = 620  # circle centers
    cols = [SZ * 0.20, SZ * 0.50, SZ * 0.80]

    for i, (num, desc) in enumerate(steps):
        cx = cols[i]

        # Dark red circle
        draw.ellipse(
            [cx - circle_r, step_cy - circle_r, cx + circle_r, step_cy + circle_r],
            fill=DARK_RED,
        )
        # Number in circle
        nbbox = draw.textbbox((0, 0), num, font=f_num)
        nw = nbbox[2] - nbbox[0]
        nh = nbbox[3] - nbbox[1]
        draw.text((cx - nw // 2, step_cy - nh // 2 - 5), num, fill=GOLD, font=f_num)

        # Arrow to next circle
        if i < 2:
            arrow_y = step_cy
            ax1 = cx + circle_r + 20
            ax2 = cols[i + 1] - circle_r - 20
            draw.line([(ax1, arrow_y), (ax2, arrow_y)], fill=GOLD, width=4)
            draw.polygon(
                [
                    (ax2, arrow_y),
                    (ax2 - 22, arrow_y - 12),
                    (ax2 - 22, arrow_y + 12),
                ],
                fill=GOLD,
            )

        # Description below circle
        desc_y = step_cy + circle_r + 60
        for line in desc.split("\n"):
            lbbox = draw.textbbox((0, 0), line, font=f_desc)
            lw = lbbox[2] - lbbox[0]
            draw.text((cx - lw // 2, desc_y), line, fill=CHARCOAL, font=f_desc)
            desc_y += desc_line_h

    # Decorative diamonds
    diamond_y = step_cy + circle_r + 60 + desc_line_h * 3 + 100
    for cx in cols:
        ds = 8
        draw.polygon(
            [(cx, diamond_y - ds), (cx + ds, diamond_y),
             (cx, diamond_y + ds), (cx - ds, diamond_y)],
            fill=GOLD,
        )

    # "Works with free Canva accounts" — centered in remaining space
    f_tag = fnt(44, _SERIF)
    center_text(draw, "Works with free Canva accounts", SZ // 2, diamond_y + 120, f_tag, GOLD)

    # Gold separator
    gold_line(draw, 1520, width=1200)

    # "No design skills needed"
    f_bottom = fnt(52, _SANS)
    center_text(draw, "No design skills needed", SZ // 2, 1590, f_bottom, CHARCOAL)

    # Secondary note
    f_note = fnt(36, _SANS)
    center_text(draw, "No software to install  \u00b7  Instant access after purchase", SZ // 2, 1680, f_note, GOLD)

    # Brand
    f_brand = fnt(28, _SANS)
    center_text(draw, "PURPLEOCAZ", SZ // 2, SZ - 70, f_brand, GOLD)

    # Bottom bar
    draw.rectangle([(0, SZ - 18), (SZ, SZ)], fill=DARK_RED)

    return img


# ============================================================
# RANK 5 — Made for Tattoo Studios & Solo Artists
# ============================================================
def build_rank5():
    img = Image.new("RGB", (SZ, SZ), CREAM)
    draw = ImageDraw.Draw(img)

    # Title (no bar, text directly on cream)
    f_title = fnt(62, _SERIF_B)
    f_sub = fnt(54, _SERIF_B)
    center_text(draw, "MADE FOR TATTOO STUDIOS", SZ // 2, 50, f_title, DARK_RED)
    center_text(draw, "& SOLO ARTISTS", SZ // 2, 130, f_sub, GOLD)

    # Gold separator
    gold_line(draw, 210, width=1200)

    # Load form preview image from Spaces (the consent form)
    # We'll download it and composite
    form_path = "/tmp/ranks/consent_form_preview.png"
    form_img = None
    try:
        s3 = _get_s3()
        resp = s3.get_object(
            Bucket=os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets"),
            Key="thumbnails/forms/01_Client_Consent_Form.png",
        )
        form_data = resp["Body"].read()
        form_img = Image.open(BytesIO(form_data)).convert("RGBA")
    except Exception as e:
        print(f"  Warning: could not load form preview: {e}")

    if form_img:
        # Scale form to fill more of the canvas - target ~950px wide
        target_w = 950
        ratio = target_w / form_img.width
        target_h = int(form_img.height * ratio)
        form_resized = form_img.resize((target_w, target_h), Image.LANCZOS)

        # Add subtle shadow
        shadow_pad = 30
        shadow = Image.new("RGBA", (target_w + shadow_pad * 2, target_h + shadow_pad * 2), (0, 0, 0, 0))
        shadow_inner = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 80))
        shadow.paste(shadow_inner, (shadow_pad + 12, shadow_pad + 12))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))

        # Position form: left-center area
        form_x = 80
        form_y = 280
        img.paste(Image.new("RGB", shadow.size, CREAM), (form_x - shadow_pad, form_y - shadow_pad))
        img_rgba = img.convert("RGBA")
        img_rgba.paste(shadow, (form_x - shadow_pad, form_y - shadow_pad), shadow)
        img_rgba.paste(form_resized, (form_x, form_y), form_resized)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)

        # Annotation arrows and labels on the right side
        f_arrow = fnt(38, _SANS_B)
        annotations = [
            (form_y + 40, "Add your logo here"),
            (form_y + target_h * 0.38, "Your studio name"),
            (form_y + target_h * 0.62, "Your contact details"),
        ]

        arrow_start_x = form_x + target_w + 30
        label_x = arrow_start_x + 100

        for ay, label in annotations:
            ay = int(ay)
            # Arrow line
            draw.line([(arrow_start_x, ay), (label_x - 10, ay)], fill=GOLD, width=3)
            # Arrowhead pointing left
            draw.polygon(
                [
                    (arrow_start_x, ay),
                    (arrow_start_x + 16, ay - 8),
                    (arrow_start_x + 16, ay + 8),
                ],
                fill=GOLD,
            )
            # Label
            draw.text((label_x, ay - 18), label, fill=CHARCOAL, font=f_arrow)
    else:
        # Fallback: just show a placeholder box
        draw.rectangle([(200, 300), (900, 1500)], outline=GOLD, width=3)
        f_placeholder = fnt(36, _SANS)
        center_text(draw, "[Form Preview]", SZ // 2, 850, f_placeholder, CHARCOAL)

    # Footer text
    f_footer = fnt(40, _SERIF)
    footer_y = SZ - 160
    gold_line(draw, footer_y - 30, width=1400)
    center_text(
        draw,
        "Fully customisable \u2014 looks professional from day one",
        SZ // 2,
        footer_y,
        f_footer,
        CHARCOAL,
    )

    # Bottom bar
    draw.rectangle([(0, SZ - 18), (SZ, SZ)], fill=DARK_RED)

    return img


# ============================================================
# RANK 6 — Everything Included
# ============================================================
def build_rank6():
    img = Image.new("RGB", (SZ, SZ), CREAM)
    draw = ImageDraw.Draw(img)

    # Thin top accent bar
    draw.rectangle([(0, 0), (SZ, 15)], fill=DARK_RED)

    # Title
    f_title = fnt(68, _SERIF_B)
    center_text(draw, "EVERYTHING INCLUDED", SZ // 2, 55, f_title, DARK_RED)

    # Gold separator
    gold_line(draw, 145, width=1400)

    items = [
        "8 Professional PDF Templates",
        "Instant Digital Download",
        "Edit Free in Canva",
        "Print at Home or Professionally",
        "A4 Size \u2014 Print Ready",
        "UK & US English Versions",
        "Lifetime Access to Updates",
    ]

    f_item = fnt(44, _SANS_B)

    # Spread items from below title to above badge
    start_y = 210
    badge_zone = 280
    available = SZ - 18 - start_y - badge_zone
    row_h = available / len(items)
    item_x = 200
    checkbox_size = 36

    for i, item in enumerate(items):
        y = start_y + i * row_h + row_h * 0.35

        # Gold checkbox icon (rounded square with inner square)
        cbx = item_x - 70
        cby = y - checkbox_size // 2
        draw.rounded_rectangle(
            [(cbx, cby), (cbx + checkbox_size, cby + checkbox_size)],
            radius=6,
            outline=GOLD,
            width=3,
        )
        # Inner filled square
        inner_margin = 8
        draw.rounded_rectangle(
            [
                (cbx + inner_margin, cby + inner_margin),
                (cbx + checkbox_size - inner_margin, cby + checkbox_size - inner_margin),
            ],
            radius=3,
            fill=GOLD,
        )

        # Item text
        draw.text((item_x, y - 18), item, fill=CHARCOAL, font=f_item)

    # "INSTANT DOWNLOAD" badge bottom-right
    badge_w, badge_h = 460, 80
    badge_x = SZ - badge_w - 80
    badge_y = SZ - 18 - badge_h - 60
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        radius=8,
        fill=DARK_RED,
    )
    f_badge = fnt(36, _SANS_B)
    bbox = draw.textbbox((0, 0), "INSTANT DOWNLOAD", font=f_badge)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (badge_x + (badge_w - tw) // 2, badge_y + (badge_h - th) // 2 - 2),
        "INSTANT DOWNLOAD",
        fill=WHITE,
        font=f_badge,
    )

    # Bottom bar
    draw.rectangle([(0, SZ - 18), (SZ, SZ)], fill=DARK_RED)

    return img


# ============================================================
# RANK 7 — Please Note / Digital Product
# ============================================================
def build_rank7():
    img = Image.new("RGB", (SZ, SZ), CREAM)
    draw = ImageDraw.Draw(img)

    bar_h = header_bar(img, draw, "PLEASE NOTE", subtitle="DIGITAL PRODUCT", bar_height=145)

    # Gold separator
    gold_line(draw, bar_h + 30, width=1400)

    items = [
        "This is a DIGITAL download \u2014 nothing is shipped",
        "You receive instant access via Etsy after purchase",
        "Editable in Canva (free account required)",
        "For personal or commercial studio use",
        "All sales final \u2014 no refunds on digital products",
    ]

    f_item = fnt(40, _SANS)
    bullet_r = 16

    # Spread items across the middle zone
    start_y = bar_h + 100
    # Reserve space for footer
    footer_zone = 400
    available = SZ - 18 - start_y - footer_zone
    row_h = available / len(items)
    item_x = 200

    for i, item in enumerate(items):
        y = start_y + i * row_h + row_h * 0.4

        # Dark red bullet circle
        draw.ellipse(
            [item_x - 60 - bullet_r, y - bullet_r, item_x - 60 + bullet_r, y + bullet_r],
            fill=DARK_RED,
        )

        # Item text
        draw.text((item_x, y - 16), item, fill=CHARCOAL, font=f_item)

    # Footer separator + thank you
    footer_sep_y = SZ - 18 - footer_zone + 50
    gold_line(draw, footer_sep_y, width=1400)

    f_thanks = fnt(40, _SANS)
    center_text(
        draw,
        "Thank you for supporting a small business!",
        SZ // 2,
        footer_sep_y + 70,
        f_thanks,
        CHARCOAL,
    )

    # Brand
    f_brand = fnt(28, _SANS)
    center_text(draw, "PURPLEOCAZ", SZ // 2, SZ - 18 - 70, f_brand, GOLD)

    return img


# ============================================================
# S3 / Upload
# ============================================================
def _get_s3():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["DO_SPACES_ENDPOINT"],
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
        region_name=os.environ["DO_SPACES_REGION"],
    )


def upload(img, key):
    s3 = _get_s3()
    buf = BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buf.read(),
        ContentType="image/png",
        ACL="public-read",
    )
    region = os.environ.get("DO_SPACES_REGION", "lon1")
    url = f"https://{bucket}.{region}.digitaloceanspaces.com/{key}"
    return url


# ============================================================
if __name__ == "__main__":
    # Load .env from purpleocaz-canva-mcp
    env_path = "/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v

    builds = {
        "thumbnails/forms_listing_rank2_whats_inside.png": ("Rank 2 — What's Inside", build_rank2),
        "thumbnails/forms_listing_rank4_how_to_edit.png": ("Rank 4 — Edit in Minutes", build_rank4),
        "thumbnails/forms_listing_rank5_customise.png": ("Rank 5 — Made for Tattoo Studios", build_rank5),
        "thumbnails/forms_listing_rank6_what_you_get.png": ("Rank 6 — Everything Included", build_rank6),
        "thumbnails/forms_listing_rank7_disclaimer.png": ("Rank 7 — Please Note", build_rank7),
    }

    urls = []
    for key, (label, builder) in builds.items():
        print(f"\nBuilding {label}...")
        img = builder()
        assert img.size == (SZ, SZ), f"Wrong size: {img.size}"
        # Save locally for preview
        local = f"/tmp/ranks/{key.split('/')[-1]}"
        img.save(local, quality=95)
        print(f"  Local: {local} ({os.path.getsize(local) // 1024}KB)")
        # Upload
        url = upload(img, key)
        print(f"  URL: {url}")
        urls.append((label, url))

    print("\n=== ALL DONE ===")
    for label, url in urls:
        print(f"  {label}: {url}")
