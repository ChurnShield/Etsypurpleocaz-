# =============================================================================
# workflows/auto_listing_creator/tools/ideogram_image_client.py
#
# Nano Banana Pro -- Ideogram v3 image generation client.
# Replaces gemini_image_client.py. Superior typography rendering.
# =============================================================================

import io
import json
import math
import os
import time
import urllib.request
import urllib.error

IDEOGRAM_API_URL = "https://api.ideogram.ai/v1/ideogram-v3/generate"

PROMPT_TEMPLATES = {
    "appointment card": {
        "raw_prompt": (
            "Two business cards overlapping at a natural angle on a light grey "
            "linen textured surface. Front card: black background, gold script "
            "heading Book Appointment, fine-line gold rose illustration, small "
            "circular logo placeholder top right. Back card: white background, "
            "script heading Appointment Card, clean horizontal form lines, "
            "7 small black rounded pill shapes in a row at bottom. Green plant "
            "top left, latte coffee cup bottom left, glasses top right. Bright "
            "clean studio lighting, professional product photography, no people, "
            "no text banners, no bottom strip."
        ),
        "full_composite": True,
    },
    "gift certificate": {
        "card_description": (
            "One elegant gift certificate card. Bold black background with "
            "a niche-appropriate ornamental divider. Script heading "
            "Gift Certificate. Fields for TO:, FROM:, AMOUNT:, EXPIRES: "
            "each with thin underlines. Studio name at top, contact footer."
        ),
        "card_count": "one card",
    },
    "gift voucher": {
        "card_description": (
            "One elegant gift voucher card. Bold black background with "
            "ornamental divider. Script heading Gift Voucher. Fields for "
            "RECIPIENT:, AMOUNT:, FROM:, VALID UNTIL: with thin underlines. "
            "Studio name at top, contact details footer."
        ),
        "card_count": "one card",
    },
    "price list": {
        "card_description": (
            "One price list card, larger format A5 size. Bold black "
            "background with ornamental dividers between sections. Script "
            "heading Price List. Service categories and prices in clean "
            "columns. Studio name at top, contact footer."
        ),
        "card_count": "one card",
    },
    "service menu": {
        "card_description": (
            "One service menu card, larger format. Bold black background "
            "with ornamental dividers. Script heading Service Menu. "
            "Tiered pricing sections. Studio name at top, contact footer."
        ),
        "card_count": "one card",
    },
    "business card": {
        "card_description": (
            "Two overlapping business cards front and back. Both use the "
            "SAME elegant script font. Front: bold black background, "
            "ornamental divider, studio name in script, contact details. "
            "Back: bold black background, large LOGO placeholder, tagline."
        ),
        "card_count": "two cards",
    },
    "aftercare card": {
        "card_description": (
            "One aftercare instruction card. Bold black background with "
            "ornamental divider. Script heading Aftercare Instructions. "
            "Numbered care steps in clean white text. Studio name and contact footer."
        ),
        "card_count": "one card",
    },
    "branding bundle": {
        "card_description": (
            "Multiple matching stationery pieces fanned out: business card, "
            "appointment card, gift certificate, and letterhead. All share "
            "bold black backgrounds with matching ornamental design elements."
        ),
        "card_count": "multiple cards fanned out",
    },
    "consent form": {
        "card_description": (
            "One consent waiver form. Bold black header with ornamental "
            "divider. Script heading Consent Form. Fields for CLIENT NAME:, "
            "DATE:, SIGNATURE: with thin underlines. Studio name at top."
        ),
        "card_count": "one form",
    },
    "social media": {
        "card_description": (
            "One social media post template square format. Bold black "
            "background with ornamental accents. Large script heading with "
            "promotional text. Studio name and logo placeholder."
        ),
        "card_count": "one template",
    },
}

_DEFAULT_PROMPT_PARTS = {
    "card_description": (
        "One professional editable template card. Bold black background with "
        "ornamental divider. Elegant script heading. Clean white placeholder "
        "fields for NAME:, DATE:, PHONE:, EMAIL: with thin underlines. "
        "Studio name at top, contact footer."
    ),
    "card_count": "one card",
}

NICHE_PROP_SETS = {
    "tattoo": (
        "TOP-LEFT: two small black tattoo ink bottles and dark eucalyptus leaves. "
        "LEFT: a rotary tattoo machine resting flat. "
        "TOP-RIGHT: tattoo flash art and stencil paper with line art designs. "
        "BOTTOM-RIGHT: a few tattoo needles and black nitrile gloves folded neatly."
    ),
    "nail": (
        "TOP-LEFT: three bottles of nail polish pink red nude. "
        "LEFT: professional nail tools on a small white towel. "
        "TOP-RIGHT: scattered nail art gems and a nail art brush. "
        "BOTTOM-RIGHT: a small potted succulent and dried flowers."
    ),
    "hair": (
        "TOP-LEFT: hair styling scissors and a fine-tooth comb on a white towel. "
        "LEFT: a round hair brush and bobby pins scattered. "
        "TOP-RIGHT: a small amber bottle of hair serum. "
        "BOTTOM-RIGHT: a sprig of eucalyptus and a hair clip."
    ),
    "barber": (
        "TOP-LEFT: a classic straight razor and leather strop with eucalyptus. "
        "LEFT: a shaving brush in a small bowl. "
        "TOP-RIGHT: a vintage barber comb and small scissors. "
        "BOTTOM-RIGHT: a small jar of pomade or beard oil."
    ),
    "beauty": (
        "TOP-LEFT: a compact mirror and gold lipstick tube. "
        "LEFT: a makeup brush set fanned out. "
        "TOP-RIGHT: a small potted succulent and dried lavender. "
        "BOTTOM-RIGHT: a perfume bottle and a silk scrunchie."
    ),
    "spa": (
        "TOP-LEFT: a lit white candle in a ceramic holder and eucalyptus. "
        "LEFT: two rolled white towels stacked neatly. "
        "TOP-RIGHT: a bowl of bath salts and a wooden scoop. "
        "BOTTOM-RIGHT: smooth massage stones and a small succulent."
    ),
    "lash": (
        "TOP-LEFT: false lash strips and a lash applicator tool. "
        "LEFT: a small bottle of lash adhesive and micro brushes. "
        "TOP-RIGHT: a lash wand spoolie and a compact mirror. "
        "BOTTOM-RIGHT: dried flowers and a silk eye mask."
    ),
    "piercing": (
        "TOP-LEFT: a small velvet jewelry box open with stud earrings and eucalyptus. "
        "LEFT: sterile piercing needles in sealed packets. "
        "TOP-RIGHT: a small mirror and antiseptic spray bottle. "
        "BOTTOM-RIGHT: scattered small jewelry pieces hoops and studs."
    ),
}

_DEFAULT_PROPS = (
    "TOP-LEFT: a small potted succulent and eucalyptus leaves. "
    "LEFT: a white ceramic coffee cup with latte art. "
    "TOP-RIGHT: tortoiseshell reading glasses arms open. "
    "BOTTOM-RIGHT: a stylish pen and a small notebook."
)


def build_product_prompt(product_type, niche, theme, hero_title=None, tagline=None):
    pt_lower = product_type.lower().strip()
    parts = _DEFAULT_PROMPT_PARTS
    for key, template_parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            parts = template_parts
            break
    # If template provides a raw prompt, use it directly (no wrapper)
    if "raw_prompt" in parts:
        return parts["raw_prompt"]
    if not hero_title:
        hero_title = f"{niche.title()} Studio {product_type.title()}"
    if not tagline:
        tagline = "EDITABLE CANVA TEMPLATE | INSTANT DOWNLOAD"
    niche_accent = NICHE_PROP_SETS.get(niche.lower(), _DEFAULT_PROPS)
    return (
        f"A styled overhead flat-lay product photograph shot from directly above, "
        f"as seen on a premium Etsy digital product listing. "
        f"This must look like a real photograph NOT a graphic design or poster. "
        f"IMAGE LAYOUT: TOP 70% is the product photography scene on a warm "
        f"beige cream textured kraft paper surface with visible grain and fibres. "
        f"BOTTOM 30% is a solid black footer banner. "
        f"CENTER OF SCENE: {parts['card_description']} "
        f"The {parts['card_count']} are placed centrally, slightly overlapping "
        f"at a casual angle as if placed by hand. "
        f"This is a {niche} studio template product. "
        f"TYPOGRAPHY CRITICAL: ALL text on cards must be PERFECTLY SHARP, "
        f"CORRECTLY SPELLED, and LEGIBLE. Title text in elegant script calligraphy. "
        f"Form field labels in clean UPPERCASE sans-serif. Each field is LABEL: "
        f"followed by a thin horizontal line. ALL horizontal lines on each card "
        f"must be the SAME length ending at the SAME right margin. "
        f"No garbled duplicated or overlapping text. No checkboxes. "
        f"PROPS niche-specific partially cropped at frame edges: {niche_accent} "
        f"CARD STYLE: pure WHITE card backgrounds. Fine-line ornamental "
        f"dividers appropriate for {niche} mandala lines geometric dot-work "
        f"dagger arrow line art filigree. ALL cards use the SAME script font "
        f"family at the SAME size for titles. "
        f"FOOTER BANNER: solid black background spanning full width. "
        f"Sharp clean edge where black meets the beige scene above. "
        f"Centered text Line 1 large: {hero_title} in bold WHITE serif font. "
        f"Line 2 small: {tagline} in uppercase WHITE sans-serif. "
        f"BOTTOM-RIGHT: small circular EDIT IN CANVA badge. "
        f"LIGHTING: soft diffused natural daylight from top-left. Gentle shadows "
        f"for depth. Warm inviting professionally styled mood. "
        f"No human hands or body parts. No real brand names or logos. "
        f"No phones tablets or device screens. "
        f"High-resolution photorealistic 300 DPI quality."
    )


def needs_composite_banner(product_type):
    """Check if this product type needs a Pillow-composited banner."""
    pt_lower = product_type.lower().strip()
    for key, parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            return parts.get("composite_banner", False)
    return False


def needs_composite_card_title(product_type):
    """Check if this product type needs a Pillow card title overlay."""
    pt_lower = product_type.lower().strip()
    for key, parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            return parts.get("composite_card_title", False)
    return False


def needs_composite_day_buttons(product_type):
    """Check if this product type needs Pillow-drawn day buttons."""
    pt_lower = product_type.lower().strip()
    for key, parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            return parts.get("composite_day_buttons", False)
    return False


def needs_full_composite(product_type):
    """Check if this product type uses full Pillow composite (bg only from Ideogram)."""
    pt_lower = product_type.lower().strip()
    for key, parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            return parts.get("full_composite", False)
    return False


# =============================================================================
# Font loader (shared across composite functions)
# =============================================================================

_FONT_DIRS = ["/usr/share/fonts/truetype/", "/usr/share/fonts/opentype/"]

def _load_font(names, size):
    """Try to load a named font at given size; fall back to Pillow default."""
    from PIL import ImageFont
    for name in names:
        for prefix in _FONT_DIRS:
            for root_dir, _dirs, files in os.walk(prefix):
                for f in files:
                    if name.lower() in f.lower():
                        try:
                            return ImageFont.truetype(os.path.join(root_dir, f), size)
                        except Exception:
                            pass
    return ImageFont.load_default(size=size)


# =============================================================================
# Full composite: appointment card hero image
# =============================================================================

def composite_appointment_card(
    bg_image_bytes,
    banner_title="Tattoo Studio Appointment Card",
    banner_subtitle="KEEP YOUR CLIENTS ORGANISED AND ON TIME",
    front_heading="Book\nAppointment",
    back_heading="Appointment Card",
    back_fields=("NAME:", "DATE:", "TIME:", "YOUR ARTIST:"),
    day_labels=("MON", "TUE", "WED", "THU", "FRI", "SAT"),
    banner_color=(242, 196, 206),   # #F2C4CE blush pink
    strip_color=(80, 80, 80),
    badge_color=(80, 80, 80),
):
    """Build a complete appointment card hero image.

    Two-step process:
      Step 1 (Ideogram): flatlay photo of two cards with props, NO text banner.
      Step 2 (Pillow):   composite crisp text — blush pink banner, dark strip,
                         badge circle. All typography rendered by Pillow.
    """
    from PIL import Image, ImageDraw, ImageFont

    bg = Image.open(io.BytesIO(bg_image_bytes)).convert("RGB")
    bg_w, bg_h = bg.size

    # -- Layout: photo top 70%, banner+strip bottom 30% --
    photo_h = bg_h
    banner_h = int(photo_h * 0.30 * 0.75)   # ~22.5% of photo
    strip_h = int(photo_h * 0.30 * 0.25)     # ~7.5% of photo
    canvas_h = photo_h + banner_h + strip_h
    canvas = Image.new("RGB", (bg_w, canvas_h), (255, 255, 255))
    canvas.paste(bg, (0, 0))
    bg.close()

    # -- Card dimensions: 85x55mm business card ratio --
    card_w = int(bg_w * 0.58)
    card_h = int(card_w * 55 / 85)   # 85:55 landscape
    card_radius = int(card_w * 0.03)
    gold = (210, 175, 90)

    # =====================================================================
    # FRONT CARD (black) — drawn on transparent layer, then rotated
    # =====================================================================
    front_img = _draw_front_card(
        card_w, card_h, card_radius, gold, front_heading,
    )
    # Rotate -5 degrees (slight clockwise tilt)
    front_rot = front_img.rotate(5, expand=True, resample=Image.BICUBIC)
    front_img.close()

    # Position: upper-left area, centred vertically in top 70%
    front_paste_x = int(bg_w * 0.02)
    front_paste_y = int(photo_h * 0.12)
    canvas.paste(front_rot, (front_paste_x, front_paste_y), front_rot)
    front_rot.close()

    # =====================================================================
    # BACK CARD (white) — drawn on transparent layer, then rotated
    # =====================================================================
    back_img = _draw_back_card(
        card_w, card_h, card_radius, back_heading, back_fields, day_labels,
    )
    # Rotate +4 degrees (slight counter-clockwise tilt)
    back_rot = back_img.rotate(-4, expand=True, resample=Image.BICUBIC)
    back_img.close()

    # Position: lower-right, overlapping front card in the middle
    back_paste_x = int(bg_w * 0.30)
    back_paste_y = int(photo_h * 0.38)
    canvas.paste(back_rot, (back_paste_x, back_paste_y), back_rot)
    back_rot.close()

    # =====================================================================
    # BANNER (blush pink) — bottom 30%
    # =====================================================================
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        [(0, photo_h), (bg_w, photo_h + banner_h)],
        fill=banner_color,
    )

    # Auto-size banner title
    max_title_w = int(bg_w * 0.90)
    title_size = int(banner_h * 0.38)
    title_font = _load_font(["DejaVuSerif-Bold", "LiberationSerif-Bold"], title_size)
    tb = draw.textbbox((0, 0), banner_title, font=title_font)
    while (tb[2] - tb[0]) > max_title_w and title_size > 16:
        title_size -= 2
        title_font = _load_font(["DejaVuSerif-Bold", "LiberationSerif-Bold"], title_size)
        tb = draw.textbbox((0, 0), banner_title, font=title_font)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    draw.text(
        ((bg_w - tw) // 2, photo_h + (banner_h - th) // 2),
        banner_title, fill=(0, 0, 0), font=title_font,
    )

    # =====================================================================
    # STRIP (dark grey)
    # =====================================================================
    draw.rectangle(
        [(0, bg_h + banner_h), (bg_w, canvas_h)],
        fill=strip_color,
    )
    sub_font = _load_font(["DejaVuSans", "LiberationSans"], int(strip_h * 0.45))
    sb = draw.textbbox((0, 0), banner_subtitle, font=sub_font)
    sw = sb[2] - sb[0]
    sh = sb[3] - sb[1]
    draw.text(
        ((bg_w - sw) // 2, bg_h + banner_h + (strip_h - sh) // 2),
        banner_subtitle, fill=(255, 255, 255), font=sub_font,
    )

    # =====================================================================
    # BADGE (dark grey circle, top-right)
    # =====================================================================
    # =====================================================================
    # STRIP (dark grey)
    # =====================================================================
    draw.rectangle(
        [(0, photo_h + banner_h), (bg_w, canvas_h)],
        fill=strip_color,
    )
    # Auto-size subtitle to fit strip
    sub_size = int(strip_h * 0.45)
    sub_font = _load_font(["DejaVuSans", "LiberationSans"], sub_size)
    sb = draw.textbbox((0, 0), banner_subtitle, font=sub_font)
    max_sub_w = int(bg_w * 0.92)
    while (sb[2] - sb[0]) > max_sub_w and sub_size > 10:
        sub_size -= 1
        sub_font = _load_font(["DejaVuSans", "LiberationSans"], sub_size)
        sb = draw.textbbox((0, 0), banner_subtitle, font=sub_font)
    sw = sb[2] - sb[0]
    sh = sb[3] - sb[1]
    draw.text(
        ((bg_w - sw) // 2, photo_h + banner_h + (strip_h - sh) // 2),
        banner_subtitle, fill=(255, 255, 255), font=sub_font,
    )

    # =====================================================================
    # BADGE (dark grey circle, top-right of photo)
    # =====================================================================
    badge_r = int(bg_w * 0.055)
    badge_cx = bg_w - badge_r - int(bg_w * 0.03)
    badge_cy = badge_r + int(photo_h * 0.03)
    draw.ellipse(
        [(badge_cx - badge_r, badge_cy - badge_r),
         (badge_cx + badge_r, badge_cy + badge_r)],
        fill=badge_color,
    )
    badge_font = _load_font(["DejaVuSans-Bold", "LiberationSans-Bold"], int(badge_r * 0.42))
    for i, line in enumerate(["EDIT IN", "CANVA"]):
        lbb = draw.textbbox((0, 0), line, font=badge_font)
        lw = lbb[2] - lbb[0]
        lh = lbb[3] - lbb[1]
        draw.text(
            (badge_cx - lw // 2,
             badge_cy - lh + (i * (lh + 2)) - int(lh * 0.1)),
            line, fill=(255, 255, 255), font=badge_font,
        )

    # -- Save --
    buf = io.BytesIO()
    canvas.save(buf, format="PNG", quality=95)
    canvas.close()
    return buf.getvalue()


# =============================================================================
# Card drawing helpers (each returns an RGBA Image)
# =============================================================================

def _draw_front_card(card_w, card_h, radius, gold, heading_text):
    """Draw the black front card with gold text on a transparent RGBA image."""
    from PIL import Image, ImageDraw

    pad = 20  # padding around card for anti-aliased edges
    img = Image.new("RGBA", (card_w + pad * 2, card_h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Card body
    d.rounded_rectangle(
        [(pad, pad), (pad + card_w, pad + card_h)],
        radius=radius, fill=(20, 20, 20, 255),
    )
    # Gold border
    d.rounded_rectangle(
        [(pad + 3, pad + 3), (pad + card_w - 3, pad + card_h - 3)],
        radius=radius, outline=gold + (255,), width=2,
    )

    # Heading
    heading_size = int(card_h * 0.24)
    heading_font = _load_font(
        ["FreeSerifBoldItalic", "DejaVuSerif-Bold", "LiberationSerif-Bold"],
        heading_size,
    )
    lines = heading_text.split("\n")
    line_y = pad + int(card_h * 0.10)
    for line in lines:
        hb = d.textbbox((0, 0), line, font=heading_font)
        hw, hh = hb[2] - hb[0], hb[3] - hb[1]
        d.text(
            (pad + (card_w - hw) // 2, line_y),
            line, fill=gold + (255,), font=heading_font,
        )
        line_y += hh + int(card_h * 0.02)

    # Ornamental divider
    div_y = line_y + int(card_h * 0.02)
    div_margin = int(card_w * 0.18)
    d.line(
        [(pad + div_margin, div_y), (pad + card_w - div_margin, div_y)],
        fill=gold + (255,), width=2,
    )
    dm_cx = pad + card_w // 2
    dm_s = 5
    d.polygon(
        [(dm_cx, div_y - dm_s), (dm_cx + dm_s, div_y),
         (dm_cx, div_y + dm_s), (dm_cx - dm_s, div_y)],
        fill=gold + (255,),
    )

    # Rose
    rose_cx = pad + card_w // 2
    rose_cy = div_y + int(card_h * 0.16)
    _draw_simple_rose(d, rose_cx, rose_cy, int(card_h * 0.14), gold + (255,))

    # Logo circle
    logo_r = int(card_w * 0.04)
    logo_cx = pad + card_w - int(card_w * 0.08)
    logo_cy = pad + int(card_h * 0.12)
    d.ellipse(
        [(logo_cx - logo_r, logo_cy - logo_r),
         (logo_cx + logo_r, logo_cy + logo_r)],
        outline=gold + (255,), width=2,
    )
    logo_font = _load_font(["DejaVuSans"], int(logo_r * 0.7))
    lb = d.textbbox((0, 0), "LOGO", font=logo_font)
    d.text(
        (logo_cx - (lb[2] - lb[0]) // 2, logo_cy - (lb[3] - lb[1]) // 2),
        "LOGO", fill=(120, 100, 60, 255), font=logo_font,
    )

    return img


def _draw_back_card(card_w, card_h, radius, heading, fields, day_labels):
    """Draw the white back card with form fields on a transparent RGBA image."""
    from PIL import Image, ImageDraw

    pad = 20
    img = Image.new("RGBA", (card_w + pad * 2, card_h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Shadow
    d.rounded_rectangle(
        [(pad + 5, pad + 5), (pad + card_w + 5, pad + card_h + 5)],
        radius=radius, fill=(160, 160, 160, 120),
    )
    # Card body
    d.rounded_rectangle(
        [(pad, pad), (pad + card_w, pad + card_h)],
        radius=radius, fill=(255, 255, 255, 255),
    )
    d.rounded_rectangle(
        [(pad, pad), (pad + card_w, pad + card_h)],
        radius=radius, outline=(220, 220, 220, 255), width=1,
    )

    # Heading
    h_size = int(card_h * 0.12)
    h_font = _load_font(
        ["FreeSerifBoldItalic", "DejaVuSerif", "LiberationSerif"], h_size,
    )
    hb = d.textbbox((0, 0), heading, font=h_font)
    hw = hb[2] - hb[0]
    d.text(
        (pad + (card_w - hw) // 2, pad + int(card_h * 0.06)),
        heading, fill=(40, 40, 40, 255), font=h_font,
    )

    # Divider
    hdiv_y = pad + int(card_h * 0.22)
    hdiv_m = int(card_w * 0.22)
    d.line(
        [(pad + hdiv_m, hdiv_y), (pad + card_w - hdiv_m, hdiv_y)],
        fill=(200, 200, 200, 255), width=1,
    )

    # Fields
    f_size = int(card_h * 0.06)
    f_font = _load_font(["DejaVuSans", "LiberationSans"], f_size)
    f_left = pad + int(card_w * 0.08)
    f_right = pad + card_w - int(card_w * 0.08)
    f_y = hdiv_y + int(card_h * 0.06)
    f_gap = int(card_h * 0.105)

    for label in fields:
        d.text((f_left, f_y), label, fill=(100, 100, 100, 255), font=f_font)
        ul_y = f_y + f_size + 4
        d.line([(f_left, ul_y), (f_right, ul_y)], fill=(200, 200, 200, 255), width=1)
        f_y += f_gap

    # Day buttons
    btn_fs = int(card_h * 0.045)
    btn_font = _load_font(["DejaVuSans-Bold", "LiberationSans-Bold"], btn_fs)
    btn_h = int(card_h * 0.07)
    btn_w = int(card_w * 0.11)
    btn_gap = int(card_w * 0.018)
    btn_r = btn_h // 3
    total_w = len(day_labels) * btn_w + (len(day_labels) - 1) * btn_gap
    bx_start = pad + (card_w - total_w) // 2
    by = pad + card_h - int(card_h * 0.12)

    for idx, label in enumerate(day_labels):
        bx = bx_start + idx * (btn_w + btn_gap)
        d.rounded_rectangle(
            [(bx, by), (bx + btn_w, by + btn_h)],
            radius=btn_r, fill=(30, 30, 30, 255),
        )
        lb = d.textbbox((0, 0), label, font=btn_font)
        lw, lh = lb[2] - lb[0], lb[3] - lb[1]
        d.text(
            (bx + (btn_w - lw) // 2, by + (btn_h - lh) // 2 - 1),
            label, fill=(255, 255, 255, 255), font=btn_font,
        )

    return img


def _draw_simple_rose(draw, cx, cy, size, color):
    """Draw a stylised line-art rose at (cx, cy)."""
    import math as _math
    # Concentric arcs to suggest petals
    for i, (start_deg, span, r_frac) in enumerate([
        (200, 160, 0.9), (30, 150, 0.75), (180, 140, 0.55),
        (350, 130, 0.4), (150, 120, 0.25),
    ]):
        r = int(size * r_frac * 0.5)
        bbox = [(cx - r, cy - r), (cx + r, cy + r)]
        draw.arc(bbox, start_deg, start_deg + span, fill=color, width=2)
    # Stem
    stem_top = cy + int(size * 0.35)
    stem_bottom = cy + int(size * 0.55)
    draw.line([(cx, stem_top), (cx, stem_bottom)], fill=color, width=2)
    # Small leaf
    leaf_cx = cx + int(size * 0.1)
    leaf_cy = stem_top + int(size * 0.12)
    leaf_s = int(size * 0.08)
    draw.ellipse(
        [(leaf_cx - leaf_s, leaf_cy - leaf_s // 2),
         (leaf_cx + leaf_s, leaf_cy + leaf_s // 2)],
        outline=color, width=1,
    )


def composite_hero_banner(
    image_bytes,
    title="Tattoo Studio Appointment Card",
    subtitle="KEEP YOUR CLIENTS ORGANISED AND ON TIME",
    badge_text="EDIT IN\nCANVA",
    card_title=None,
    day_buttons=None,
    banner_color=(242, 196, 206),   # blush pink #F2C4CE
    strip_color=(80, 80, 80),       # dark grey
    badge_color=(80, 80, 80),       # dark grey
):
    """Composite a text banner onto the bottom of an Ideogram-generated image.

    Step 2 of the two-step process: Ideogram generates the flatlay photo,
    then Pillow adds crisp text overlays (banner, strip, badge).

    If card_title is provided, it is rendered as serif text onto the white
    card area of the photo (upper-centre region of the image).
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    photo_w, photo_h = img.size

    # Target final aspect ratio ~3:4 (Etsy listing).
    # Photo takes top ~70%, banner+strip take bottom ~30%.
    banner_h = int(photo_h * 0.25)
    strip_h = int(photo_h * 0.07)
    total_h = photo_h + banner_h + strip_h

    canvas = Image.new("RGB", (photo_w, total_h), (255, 255, 255))
    canvas.paste(img, (0, 0))
    img.close()

    draw = ImageDraw.Draw(canvas)

    # -- Detect white card region (used by card title + day buttons) --
    card_top = None
    card_bottom = None
    card_cx = photo_w // 2
    if card_title or day_buttons:
        photo_pixels = canvas.load()
        search_start = int(photo_h * 0.20)
        search_end = int(photo_h * 0.85)
        sample_x_start = int(photo_w * 0.3)
        sample_x_end = int(photo_w * 0.9)
        sample_step = max(1, (sample_x_end - sample_x_start) // 20)

        for r in range(search_start, search_end):
            bright_count = 0
            samples = 0
            for cx in range(sample_x_start, sample_x_end, sample_step):
                px = photo_pixels[cx, r]
                if px[0] > 200 and px[1] > 200 and px[2] > 200:
                    bright_count += 1
                samples += 1
            if samples > 0 and bright_count / samples > 0.6:
                card_top = r
                break

        if card_top is not None:
            card_cx = (sample_x_start + sample_x_end) // 2
            # Find card bottom by scanning upward from search_end
            for r in range(search_end, card_top, -1):
                bright_count = 0
                samples = 0
                for cx in range(sample_x_start, sample_x_end, sample_step):
                    px = photo_pixels[cx, r]
                    if px[0] > 200 and px[1] > 200 and px[2] > 200:
                        bright_count += 1
                    samples += 1
                if samples > 0 and bright_count / samples > 0.5:
                    card_bottom = r
                    break

    # -- Card title overlay --
    if card_title and card_top is not None:
        card_title_size = int(photo_h * 0.04)
        card_title_font = _load_font(
            ["DejaVuSerif", "LiberationSerif", "Georgia"], card_title_size,
        )
        ct_bbox = draw.textbbox((0, 0), card_title, font=card_title_font)
        ct_w = ct_bbox[2] - ct_bbox[0]
        ct_x = card_cx - ct_w // 2
        ct_y = card_top + int(photo_h * 0.015)
        draw.text((ct_x, ct_y), card_title, fill=(40, 40, 40), font=card_title_font)

    # -- Day buttons (small rounded rectangles with day labels) --
    if day_buttons and card_top is not None and card_bottom is not None:
        btn_labels = day_buttons if isinstance(day_buttons, list) else [
            "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN",
        ]
        btn_font_size = int(photo_h * 0.016)
        btn_font = _load_font(["DejaVuSans-Bold", "LiberationSans-Bold", "Arial"], btn_font_size)
        btn_h = int(photo_h * 0.028)
        btn_w = int(photo_w * 0.055)
        btn_gap = int(photo_w * 0.012)
        btn_radius = btn_h // 3
        total_btn_w = len(btn_labels) * btn_w + (len(btn_labels) - 1) * btn_gap
        btn_start_x = card_cx - total_btn_w // 2
        btn_y = card_bottom - int(photo_h * 0.05)

        for idx, label in enumerate(btn_labels):
            bx = btn_start_x + idx * (btn_w + btn_gap)
            draw.rounded_rectangle(
                [(bx, btn_y), (bx + btn_w, btn_y + btn_h)],
                radius=btn_radius,
                fill=(30, 30, 30),
            )
            lb = draw.textbbox((0, 0), label, font=btn_font)
            lw = lb[2] - lb[0]
            lh = lb[3] - lb[1]
            draw.text(
                (bx + (btn_w - lw) // 2, btn_y + (btn_h - lh) // 2 - 1),
                label, fill=(255, 255, 255), font=btn_font,
            )

    # -- Banner (blush pink #F4B8C1) --
    draw.rectangle(
        [(0, photo_h), (photo_w, photo_h + banner_h)],
        fill=banner_color,
    )

    # -- Strip (dark grey) --
    draw.rectangle(
        [(0, photo_h + banner_h), (photo_w, total_h)],
        fill=strip_color,
    )

    # Auto-size title font to fit within banner with padding
    max_title_w = int(photo_w * 0.90)
    title_size = int(banner_h * 0.35)
    title_font = _load_font(["DejaVuSerif-Bold", "LiberationSerif-Bold", "Georgia"], title_size)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    while (title_bbox[2] - title_bbox[0]) > max_title_w and title_size > 16:
        title_size -= 2
        title_font = _load_font(["DejaVuSerif-Bold", "LiberationSerif-Bold", "Georgia"], title_size)
        title_bbox = draw.textbbox((0, 0), title, font=title_font)

    subtitle_font = _load_font(["DejaVuSans", "LiberationSans", "Arial"], int(strip_h * 0.45))
    badge_font = _load_font(["DejaVuSans-Bold", "LiberationSans-Bold", "Arial"], int(photo_w * 0.018))

    # -- Draw title text centred on banner --
    title_tw = title_bbox[2] - title_bbox[0]
    title_th = title_bbox[3] - title_bbox[1]
    title_x = (photo_w - title_tw) // 2
    title_y = photo_h + (banner_h - title_th) // 2
    draw.text((title_x, title_y), title, fill=(0, 0, 0), font=title_font)

    # -- Draw subtitle text centred on strip --
    sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_tw = sub_bbox[2] - sub_bbox[0]
    sub_th = sub_bbox[3] - sub_bbox[1]
    sub_x = (photo_w - sub_tw) // 2
    sub_y = photo_h + banner_h + (strip_h - sub_th) // 2
    draw.text((sub_x, sub_y), subtitle, fill=(255, 255, 255), font=subtitle_font)

    # -- Draw badge circle (top-right of photo area) --
    badge_r = int(photo_w * 0.06)
    badge_cx = photo_w - badge_r - int(photo_w * 0.04)
    badge_cy = badge_r + int(photo_h * 0.03)
    draw.ellipse(
        [(badge_cx - badge_r, badge_cy - badge_r),
         (badge_cx + badge_r, badge_cy + badge_r)],
        fill=badge_color,
    )
    # Badge text (two lines)
    for i, line in enumerate(badge_text.split("\n")):
        line_bbox = draw.textbbox((0, 0), line, font=badge_font)
        lw = line_bbox[2] - line_bbox[0]
        lh = line_bbox[3] - line_bbox[1]
        lx = badge_cx - lw // 2
        ly = badge_cy - lh + (i * lh) - int(lh * 0.15)
        draw.text((lx, ly), line, fill=(255, 255, 255), font=badge_font)

    # -- Save to bytes --
    buf = io.BytesIO()
    canvas.save(buf, format="PNG", quality=95)
    canvas.close()
    return buf.getvalue()


def generate_product_image(api_key, prompt, aspect_ratio="3:4", image_size="2K", max_retries=2):
    last_error = None
    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait = min(2 ** attempt, 10)
            print(f"       Ideogram retry {attempt}/{max_retries} (waiting {wait}s)...", flush=True)
            time.sleep(wait)
        result = _call_ideogram_api(api_key, prompt, aspect_ratio)
        if result["success"]:
            return result
        last_error = result["error"]
        if not _is_retryable(last_error):
            return result
    return {"success": False, "image_bytes": None, "mime_type": None,
            "error": f"Failed after {max_retries + 1} attempts: {last_error}"}


def _call_ideogram_api(api_key, prompt, aspect_ratio):
    ratio_map = {
        "3:4": "960x1280",   # not valid — use closest
        "4:3": "1280x960",   # not valid — use closest
        "1:1": "1024x1024",
        "9:16": "704x1280",  # closest to 720x1280
        "16:9": "1280x704",  # closest to 1280x720
        "2:3": "832x1248",
        "3:2": "1248x832",
    }
    # Validate against known resolutions; fall back to closest match
    valid_resolutions = {
        "512x1536", "576x1408", "576x1472", "576x1536",
        "640x1344", "640x1408", "640x1472", "640x1536",
        "704x1152", "704x1216", "704x1280", "704x1344", "704x1408", "704x1472",
        "736x1312", "768x1088", "768x1216", "768x1280", "768x1344",
        "800x1280", "832x960", "832x1024", "832x1088", "832x1152", "832x1216", "832x1248",
        "864x1152", "896x960", "896x1024", "896x1088", "896x1120", "896x1152",
        "960x832", "960x896", "960x1024", "960x1088",
        "1024x832", "1024x896", "1024x960", "1024x1024",
        "1088x768", "1088x832", "1088x896", "1088x960",
        "1120x896", "1152x704", "1152x832", "1152x864", "1152x896",
        "1216x704", "1216x768", "1216x832", "1248x832",
        "1280x704", "1280x768", "1280x800",
        "1312x736", "1344x640", "1344x704", "1344x768",
        "1408x576", "1408x640", "1408x704",
        "1472x576", "1472x640", "1472x704",
        "1536x512", "1536x576", "1536x640",
    }
    resolution = ratio_map.get(aspect_ratio, "768x1024")
    if resolution not in valid_resolutions:
        # Find closest valid resolution by aspect ratio
        target_w, target_h = (int(x) for x in resolution.split("x"))
        target_ratio = target_w / target_h
        resolution = min(
            valid_resolutions,
            key=lambda r: abs((int(r.split("x")[0]) / int(r.split("x")[1])) - target_ratio),
        )
    payload = {
        "prompt": prompt,
        "magic_prompt": "OFF",
        "resolution": resolution,
        "rendering_speed": "QUALITY",
        "num_images": 1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(IDEOGRAM_API_URL, data=data, method="POST")
    req.add_header("Api-Key", api_key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        images = body.get("data", [])
        if not images:
            return {"success": False, "image_bytes": None, "mime_type": None,
                    "error": "No images in Ideogram response"}
        image_url = images[0].get("url")
        if not image_url:
            return {"success": False, "image_bytes": None, "mime_type": None,
                    "error": "No URL in Ideogram response"}
        with urllib.request.urlopen(image_url, timeout=60) as img_resp:
            image_bytes = img_resp.read()
        return {"success": True, "image_bytes": image_bytes, "mime_type": "image/jpeg", "error": None}
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        return {"success": False, "image_bytes": None, "mime_type": None,
                "error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"success": False, "image_bytes": None, "mime_type": None,
                "error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"success": False, "image_bytes": None, "mime_type": None,
                "error": f"{type(e).__name__}: {str(e)[:200]}"}


def _is_retryable(error_str):
    if not error_str:
        return False
    return any(code in error_str for code in ("429", "500", "502", "503", "504"))
