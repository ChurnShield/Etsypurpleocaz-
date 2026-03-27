#!/usr/bin/env python3
"""
Niche Template Factory
======================
One script renders any niche bundle from a JSON config.
No more copy-paste-modify per niche.

Usage:
    python3 scripts/niche_template_factory.py configs/niches/dog_walking.json
    python3 scripts/niche_template_factory.py configs/niches/dog_walking.json --skip-etsy
    python3 scripts/niche_template_factory.py configs/niches/dog_walking.json --only-pdf

Config schema: see configs/niches/sample_niche.json

Template types supported:
    business_card, appointment_card, loyalty_card, referral_card, thank_you_card
    gift_certificate, welcome_sign, opening_hours_sign
    flyer_a4, price_list, form_a4, invoice, booking_confirmation
    social_1080, certificate
"""
import argparse, io, json, math, os, sys, uuid, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib import colors
from dotenv import load_dotenv

PROJECT = Path(__file__).parent.parent
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

A4_SIZE       = (2480, 3508)
A4_LAND       = (3508, 2480)
BCARD         = (1050, 600)
GIFT_CERT     = (2550, 1800)
SOCIAL        = (1080, 1080)
LISTING_IMG   = (3000, 3000)


# ── Font helpers ──────────────────────────────────────────────────────────────

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REGULAR, size)


# ── Generic drawing primitives ────────────────────────────────────────────────

def centred(draw, y, text, fill, f, canvas_w):
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text(((canvas_w - tw) // 2, y), text, fill=fill, font=f)


def right_align(draw, x_right, y, text, fill, f):
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text((x_right - tw, y), text, fill=fill, font=f)


def hline(draw, y, x0, x1, fill, thickness=6):
    draw.rectangle([x0, y, x1, y + thickness], fill=fill)


def vline(draw, x, y0, y1, fill, thickness=4):
    draw.rectangle([x, y0, x + thickness, y1], fill=fill)


def bar(draw, x0, y, x1, h, fill):
    draw.rectangle([x0, y, x1, y + h], fill=fill)


def paw_print(draw, cx, cy, size=60, fill=(201, 169, 110)):
    pw = int(size * 1.0); ph = int(size * 1.15)
    draw.ellipse([cx - pw, cy - ph // 2, cx + pw, cy + ph + ph // 2], fill=fill)
    tr = int(size * 0.38)
    toe_y = int(size * 1.55)
    for tx, ty in [
        (cx - int(size * 0.95), cy - toe_y + int(tr * 0.3)),
        (cx - int(size * 0.38), cy - toe_y - int(tr * 0.4)),
        (cx + int(size * 0.38), cy - toe_y - int(tr * 0.4)),
        (cx + int(size * 0.95), cy - toe_y + int(tr * 0.3)),
    ]:
        draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=fill)


def camera_icon(draw, cx, cy, size=60, fill=(201, 169, 110)):
    bw = int(size * 2.0); bh = int(size * 1.4)
    draw.rectangle([cx - bw, cy - bh // 2, cx + bw, cy + bh // 2], fill=fill)
    lr = int(size * 0.75)
    draw.ellipse([cx - lr, cy - lr, cx + lr, cy + lr], fill=fill)
    lr2 = int(size * 0.45)
    bg = tuple(max(0, c - 40) for c in fill) if isinstance(fill, tuple) else fill
    draw.ellipse([cx - lr2, cy - lr2, cx + lr2, cy + lr2], fill=bg)
    nw = int(size * 0.7); nh = int(size * 0.45)
    draw.rectangle([cx - bw + 4, cy - bh // 2 - nh, cx - bw + 4 + nw, cy - bh // 2], fill=fill)


def scissors_icon(draw, cx, cy, size=50, fill=(201, 169, 110)):
    # Simple scissors: two diagonal lines + circles
    s = size
    draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=fill, width=max(4, s // 8))
    draw.line([(cx + s, cy - s), (cx - s, cy + s)], fill=fill, width=max(4, s // 8))
    r = s // 3
    for bx, by in [(cx - s, cy - s), (cx + s, cy - s)]:
        draw.ellipse([bx - r, by - r, bx + r, by + r], outline=fill, width=max(3, s // 12))


def niche_icon(draw, cx, cy, size, fill, icon_type):
    """Dispatch to the right icon based on niche icon_type."""
    if icon_type == "paw":
        paw_print(draw, cx, cy, size, fill)
    elif icon_type == "camera":
        camera_icon(draw, cx, cy, size, fill)
    elif icon_type == "scissors":
        scissors_icon(draw, cx, cy, size, fill)
    else:
        paw_print(draw, cx, cy, size, fill)  # default


# ── Palette helper ────────────────────────────────────────────────────────────

def p(cfg, key):
    """Return palette colour as tuple from config."""
    v = cfg["palette"][key]
    return tuple(v)


# ── A4 shared header / footer ─────────────────────────────────────────────────

def a4_header(img, draw, cfg, title):
    W = img.width
    PRIMARY = p(cfg, "primary")
    GOLD    = p(cfg, "gold")
    CREAM   = p(cfg, "cream")
    WHITE   = (255, 255, 255)
    brand   = cfg.get("brand", {})
    icon    = cfg.get("icon", "paw")

    bar(draw, 0, 0, W, 420, PRIMARY)
    niche_icon(draw, 180, 210, size=80, fill=GOLD, icon_type=icon)
    draw.text((300, 80),  brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD,  font=font(56, bold=True))
    draw.text((300, 155), brand.get("subtitle", ""), fill=CREAM, font=font(38))
    centred(draw, 255, title, WHITE, font(66, bold=True), canvas_w=W)
    hline(draw, 420, 0, W, GOLD, thickness=8)
    return 460


def a4_footer(draw, W, H, cfg):
    PRIMARY = p(cfg, "primary")
    GOLD    = p(cfg, "gold")
    CREAM   = p(cfg, "cream")
    bar(draw, 0, H - 100, W, 100, PRIMARY)
    hline(draw, H - 100, 0, W, GOLD, thickness=6)
    centred(draw, H - 76, "© PurpleOcaz — purpleocaz.etsy.com",
            CREAM, font(30), canvas_w=W)


# ── Field drawing helpers ─────────────────────────────────────────────────────

def field_line(draw, x, y, label, width, cfg, font_size=36):
    PRIMARY  = p(cfg, "primary")
    CHARCOAL = p(cfg, "charcoal")
    draw.text((x, y), label, fill=CHARCOAL, font=font(font_size, bold=True))
    y += 58
    draw.rectangle([x, y, x + width, y + 3], fill=PRIMARY)
    return y + 52


def field_pair(draw, x, y, label1, label2, total_w, cfg, font_size=36):
    PRIMARY  = p(cfg, "primary")
    CHARCOAL = p(cfg, "charcoal")
    half = (total_w - 60) // 2
    draw.text((x, y),           label1, fill=CHARCOAL, font=font(font_size, bold=True))
    draw.text((x + half + 60, y), label2, fill=CHARCOAL, font=font(font_size, bold=True))
    y2 = y + 58
    draw.rectangle([x,           y2, x + half,       y2 + 3], fill=PRIMARY)
    draw.rectangle([x + half + 60, y2, x + total_w,  y2 + 3], fill=PRIMARY)
    return y2 + 52


def field_triple(draw, x, y, labels, total_w, cfg, font_size=34):
    PRIMARY  = p(cfg, "primary")
    CHARCOAL = p(cfg, "charcoal")
    w3 = (total_w - 80) // 3
    for i, lbl in enumerate(labels[:3]):
        xoff = x + i * (w3 + 40)
        draw.text((xoff, y), lbl, fill=CHARCOAL, font=font(font_size, bold=True))
        y2 = y + 54
        draw.rectangle([xoff, y2, xoff + w3, y2 + 3], fill=PRIMARY)
    return y + 54 + 50


def checkbox(draw, x, y, label, cfg, font_size=34):
    PRIMARY  = p(cfg, "primary")
    CHARCOAL = p(cfg, "charcoal")
    draw.rectangle([x, y + 4, x + 36, y + 40], outline=PRIMARY, width=3)
    draw.text((x + 52, y + 4), label, fill=CHARCOAL, font=font(font_size))
    return y + 50


def section_head(draw, x, y, text, width, cfg):
    PRIMARY = p(cfg, "primary")
    WHITE   = (255, 255, 255)
    draw.rectangle([x, y, x + width, y + 72], fill=PRIMARY)
    draw.text((x + 24, y + 14), text, fill=WHITE, font=font(42, bold=True))
    return y + 72


def table_row(draw, x, y, cols, widths, cfg, row_h=60, alt=False, header=False):
    PRIMARY   = p(cfg, "primary")
    GOLD      = p(cfg, "gold")
    CREAM_ALT = p(cfg, "cream_alt")
    CHARCOAL  = p(cfg, "charcoal")
    WHITE     = (255, 255, 255)
    bg = PRIMARY if header else (CREAM_ALT if alt else WHITE)
    fg = WHITE   if header else CHARCOAL
    total_w = sum(widths)
    draw.rectangle([x, y, x + total_w, y + row_h], fill=bg)
    draw.rectangle([x, y, x + total_w, y + row_h], outline=GOLD, width=1)
    cx = x
    for i, (col, w) in enumerate(zip(cols, widths)):
        draw.text((cx + 12, y + 12), str(col), fill=fg,
                  font=font(34 if not header else 36, bold=header))
        if i < len(cols) - 1:
            draw.line([(cx + w, y), (cx + w, y + row_h)], fill=GOLD, width=1)
        cx += w
    return y + row_h


# ── Row renderer dispatcher ───────────────────────────────────────────────────

def render_rows(draw, x, y, rows, margin_w, cfg):
    """Render a list of row specs onto an A4 draw context. Returns final y."""
    W_content = margin_w  # total usable width

    for row in rows:
        rt = row.get("type")
        y += row.get("gap_before", 0)

        if rt == "section_header":
            y = section_head(draw, x, y, row["text"], W_content, cfg)

        elif rt == "field_single":
            y = field_line(draw, x, y, row["label"], W_content, cfg,
                           font_size=row.get("font_size", 36))

        elif rt == "field_pair":
            y = field_pair(draw, x, y, row["labels"][0], row["labels"][1],
                           W_content, cfg, font_size=row.get("font_size", 36))

        elif rt == "field_triple":
            y = field_triple(draw, x, y, row["labels"], W_content, cfg,
                             font_size=row.get("font_size", 34))

        elif rt == "checkbox_group":
            cols = row.get("cols", 1)
            items = row["items"]
            if cols == 1:
                for item in items:
                    y = checkbox(draw, x, y, item, cfg,
                                 font_size=row.get("font_size", 34))
            else:
                col_w = W_content // cols
                for i in range(0, len(items), cols):
                    row_items = items[i:i + cols]
                    base_y = y
                    for j, item in enumerate(row_items):
                        checkbox(draw, x + j * col_w, base_y, item, cfg,
                                 font_size=row.get("font_size", 34))
                    y = base_y + 50

        elif rt == "table":
            headers = row["headers"]
            n_data_rows = row.get("n_rows", 5)
            total_w = W_content
            n_cols = len(headers)
            # Column widths: first col wider if "description" style
            if row.get("col_widths"):
                widths = [int(total_w * w) for w in row["col_widths"]]
                # Adjust last col to fill
                widths[-1] = total_w - sum(widths[:-1])
            else:
                widths = [total_w // n_cols] * n_cols
                widths[-1] = total_w - sum(widths[:-1])

            y = table_row(draw, x, y, headers, widths, cfg, header=True)
            for i in range(n_data_rows):
                y = table_row(draw, x, y, [""] * n_cols, widths, cfg,
                              alt=(i % 2 == 1))

        elif rt == "text_block":
            CHARCOAL = p(cfg, "charcoal")
            lines = row.get("lines", [row.get("text", "")])
            fs = row.get("font_size", 36)
            bold = row.get("bold", False)
            for line in lines:
                draw.text((x, y), line, fill=CHARCOAL, font=font(fs, bold=bold))
                y += fs + 12

        elif rt == "spacer":
            y += row.get("height", 40)

        y += row.get("gap_after", 0)

    return y


# ── Template renderers ────────────────────────────────────────────────────────

def render_business_card(tmpl, cfg, out_path):
    W, H = BCARD
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    if variant == "dark":
        bg, fg, accent = PRIMARY, WHITE, GOLD
    else:
        bg, fg, accent = CREAM, CHARCOAL, PRIMARY

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Top accent rule
    hline(draw, 0, 0, W, GOLD, thickness=10)
    # Bottom accent rule
    hline(draw, H - 10, 0, W, GOLD, thickness=10)

    # Icon (left side)
    niche_icon(draw, 90, H // 2, size=55, fill=GOLD, icon_type=icon)

    # Business name
    draw.text((170, 80), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=accent, font=font(52, bold=True))
    # Subtitle
    draw.text((170, 150), brand.get("subtitle", ""), fill=fg, font=font(34))

    # Divider
    hline(draw, 210, 170, W - 60, GOLD, thickness=3)

    # Contact placeholders
    for i, line in enumerate([
        "📍  123 Example Street, Town",
        "📞  07700 000000",
        "✉   hello@yourbusiness.com",
    ]):
        draw.text((170, 250 + i * 68), line, fill=fg, font=font(30))

    img.save(str(out_path), "PNG")
    img.close()


def render_appointment_card(tmpl, cfg, out_path):
    W, H = BCARD
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    hline(draw, 0, 0, W, GOLD, thickness=10)
    hline(draw, H - 10, 0, W, GOLD, thickness=10)

    draw.text((60, 50), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD, font=font(44, bold=True))
    hline(draw, 115, 60, W - 60, GOLD, thickness=3)

    centred(draw, 135, "APPOINTMENT CARD", fg, font(40, bold=True), canvas_w=W)

    fields = [("Date:", 210), ("Time:", 290), ("Service:", 370), ("With:", 450)]
    for label, fy in fields:
        draw.text((60, fy), label, fill=GOLD, font=font(32, bold=True))
        hline(draw, fy + 44, 200, W - 60, GOLD if variant == "dark" else PRIMARY, thickness=2)

    img.save(str(out_path), "PNG")
    img.close()


def render_loyalty_card(tmpl, cfg, out_path):
    W, H = BCARD
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    n_stamps = tmpl.get("stamps", 10)

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    hline(draw, 0, 0, W, GOLD, thickness=10)
    hline(draw, H - 10, 0, W, GOLD, thickness=10)

    draw.text((60, 50), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD, font=font(44, bold=True))
    centred(draw, 130, "LOYALTY CARD", fg, font(40, bold=True), canvas_w=W)
    hline(draw, 190, 60, W - 60, GOLD, thickness=3)

    # Stamp circles
    cols = 5; rows = math.ceil(n_stamps / cols)
    r = 45; spacing_x = (W - 120) // cols; spacing_y = 110
    for i in range(n_stamps):
        col = i % cols; row = i // cols
        cx = 90 + col * spacing_x + spacing_x // 2
        cy = 230 + row * spacing_y
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=4)
        if i == 0:
            draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], fill=GOLD)

    # Footer text
    reward = tmpl.get("reward", "Buy 5, Get 1 FREE")
    centred(draw, H - 75, reward, GOLD, font(32, bold=True), canvas_w=W)

    img.save(str(out_path), "PNG")
    img.close()


def render_card_simple(tmpl, cfg, out_path):
    """Generic small card — thank you, referral, etc."""
    W, H = BCARD
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    hline(draw, 0, 0, W, GOLD, thickness=10)
    hline(draw, H - 10, 0, W, GOLD, thickness=10)
    vline(draw, 0, 0, H, GOLD, thickness=10)
    vline(draw, W - 10, 0, H, GOLD, thickness=10)

    niche_icon(draw, W // 2, 130, size=60, fill=GOLD, icon_type=icon)

    title = tmpl.get("card_title", tmpl.get("title", "THANK YOU"))
    centred(draw, 240, title.upper(), fg, font(64, bold=True), canvas_w=W)
    hline(draw, 330, 100, W - 100, GOLD, thickness=4)

    body_lines = tmpl.get("body_lines", [brand.get("subtitle", "")])
    for i, line in enumerate(body_lines):
        centred(draw, 360 + i * 60, line, GOLD if variant == "dark" else PRIMARY,
                font(36), canvas_w=W)

    draw.text((60, H - 95), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD, font=font(32, bold=True))

    img.save(str(out_path), "PNG")
    img.close()


def render_gift_certificate(tmpl, cfg, out_path):
    W, H = GIFT_CERT
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Border
    for t in range(3):
        draw.rectangle([20 + t * 12, 20 + t * 12, W - 20 - t * 12, H - 20 - t * 12],
                       outline=GOLD, width=4)

    # Header
    niche_icon(draw, 140, H // 2, size=70, fill=GOLD, icon_type=icon)
    draw.text((250, 80), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD, font=font(60, bold=True))
    draw.text((250, 160), brand.get("subtitle", ""), fill=fg, font=font(42))
    hline(draw, 240, 250, W - 100, GOLD, thickness=4)
    centred(draw, 290, "GIFT CERTIFICATE", GOLD, font(100, bold=True, serifbold=True), canvas_w=W)
    hline(draw, 430, 100, W - 100, GOLD, thickness=4)

    # Fields
    fields = tmpl.get("fields", [
        ("Gift For:", ""),
        ("Gift From:", ""),
        ("Amount / Service:", ""),
        ("Valid Until:", ""),
    ])
    fy = 500
    for label, _ in fields:
        draw.text((120, fy), label, fill=GOLD, font=font(44, bold=True))
        hline(draw, fy + 58, 120 + 380, W - 120, fg if variant == "dark" else PRIMARY, thickness=2)
        fy += 130

    # Signature area
    hline(draw, H - 200, 120, 700, fg if variant == "dark" else PRIMARY, thickness=2)
    draw.text((120, H - 170), "Signature", fill=fg, font=font(36))

    img.save(str(out_path), "PNG")
    img.close()


def render_welcome_sign(tmpl, cfg, out_path):
    W, H = A4_SIZE
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")
    variant  = tmpl.get("variant", "dark")

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    for t in range(3):
        draw.rectangle([30 + t * 16, 30 + t * 16, W - 30 - t * 16, H - 30 - t * 16],
                       outline=GOLD, width=5)

    niche_icon(draw, W // 2, 400, size=120, fill=GOLD, icon_type=icon)
    centred(draw, 580, "WELCOME TO", fg, font(80), canvas_w=W)
    centred(draw, 700, brand.get("name_placeholder", "YOUR BUSINESS NAME"),
            GOLD, font(110, bold=True), canvas_w=W)
    hline(draw, 880, 150, W - 150, GOLD, thickness=8)
    centred(draw, 940, brand.get("subtitle", ""), fg, font(60), canvas_w=W)

    body_lines = tmpl.get("body_lines", [
        "We are so glad you're here.",
        "Please make yourself comfortable.",
        "We will be right with you!",
    ])
    for i, line in enumerate(body_lines):
        centred(draw, 1100 + i * 120, line, GOLD if variant == "dark" else PRIMARY,
                font(50), canvas_w=W)

    hline(draw, H - 400, 150, W - 150, GOLD, thickness=8)
    centred(draw, H - 350, brand.get("contact_line", "📞 07700 000000"),
            fg, font(50), canvas_w=W)
    centred(draw, H - 270, brand.get("email_line", "✉ hello@yourbusiness.com"),
            fg, font(50), canvas_w=W)

    img.save(str(out_path), "PNG")
    img.close()


def render_flyer_a4(tmpl, cfg, out_path):
    W, H = A4_SIZE
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")
    variant  = tmpl.get("variant", "dark")

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Header band
    bar(draw, 0, 0, W, 360, p(cfg, "primary_dark") if "primary_dark" in cfg["palette"] else PRIMARY)
    niche_icon(draw, 180, 180, size=80, fill=GOLD, icon_type=icon)
    draw.text((300, 80), brand.get("name_placeholder", "YOUR BUSINESS NAME"),
              fill=GOLD, font=font(56, bold=True))
    draw.text((300, 155), brand.get("subtitle", ""), fill=CREAM, font=font(38))
    hline(draw, 360, 0, W, GOLD, thickness=8)

    # Hero title
    title = tmpl.get("title", "SPECIAL OFFER")
    centred(draw, 420, title.upper(), GOLD, font(100, bold=True), canvas_w=W)
    hline(draw, 570, 120, W - 120, GOLD, thickness=4)

    # Body lines
    body_lines = tmpl.get("body_lines", [
        "Lorem ipsum service description",
        "All breeds welcome",
        "",
        "📞  Call to book your appointment",
    ])
    y = 620
    for line in body_lines:
        if line == "":
            y += 40
        else:
            centred(draw, y, line, fg, font(52), canvas_w=W)
            y += 80

    # CTA box
    cta = tmpl.get("cta", "CALL NOW TO BOOK")
    draw.rectangle([200, H - 500, W - 200, H - 350], fill=GOLD)
    centred(draw, H - 470, cta, PRIMARY, font(62, bold=True), canvas_w=W)

    # Footer
    bar(draw, 0, H - 280, W, 280, PRIMARY)
    hline(draw, H - 280, 0, W, GOLD, thickness=6)
    centred(draw, H - 250, brand.get("contact_line", "📞 07700 000000"),
            fg, font(48), canvas_w=W)
    centred(draw, H - 175, brand.get("email_line", "✉ hello@yourbusiness.com"),
            fg, font(48), canvas_w=W)
    centred(draw, H - 90, "© PurpleOcaz — purpleocaz.etsy.com",
            CREAM, font(30), canvas_w=W)

    img.save(str(out_path), "PNG")
    img.close()


def render_price_list(tmpl, cfg, out_path):
    W, H = A4_SIZE
    M = 120  # margin
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)

    img  = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    y    = a4_header(img, draw, cfg, tmpl.get("title", "PRICE LIST"))

    services = tmpl.get("services", [
        {"category": "BASIC SERVICES", "items": [
            {"name": "Service 1", "price": "£XX"},
            {"name": "Service 2", "price": "£XX"},
        ]},
        {"category": "PREMIUM SERVICES", "items": [
            {"name": "Service 3", "price": "£XX"},
        ]},
    ])

    for section in services:
        y += 30
        y = section_head(draw, M, y, section["category"], W - M * 2, cfg)
        y += 10
        for i, item in enumerate(section["items"]):
            alt = (i % 2 == 1)
            row_bg = p(cfg, "cream_alt") if alt else WHITE
            draw.rectangle([M, y, W - M, y + 70], fill=row_bg)
            draw.text((M + 20, y + 18), item["name"], fill=CHARCOAL, font=font(38))
            right_align(draw, W - M - 20, y + 18, item["price"], CHARCOAL, font(38, bold=True))
            hline(draw, y + 70, M, W - M, GOLD, thickness=1)
            y += 70

    a4_footer(draw, W, H, cfg)
    img.save(str(out_path), "PNG")
    img.close()


def render_form_a4(tmpl, cfg, out_path):
    W, H = A4_SIZE
    M = 120  # left/right margin
    content_w = W - M * 2

    img  = Image.new("RGB", (W, H), p(cfg, "cream"))
    draw = ImageDraw.Draw(img)
    y    = a4_header(img, draw, cfg, tmpl.get("title", "CLIENT FORM"))

    y += 20
    rows = tmpl.get("rows", [
        {"type": "field_single",  "label": "Full Name"},
        {"type": "field_pair",    "labels": ["Date", "Time"]},
        {"type": "section_header","text":  "DETAILS"},
        {"type": "field_single",  "label": "Notes"},
    ])
    y = render_rows(draw, M, y, rows, content_w, cfg)

    a4_footer(draw, W, H, cfg)
    img.save(str(out_path), "PNG")
    img.close()


def render_invoice(tmpl, cfg, out_path):
    W, H = A4_SIZE
    M = 120
    content_w = W - M * 2
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    img  = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    y    = a4_header(img, draw, cfg, "INVOICE")

    y += 20
    # Invoice meta
    rows_meta = [
        {"type": "field_pair", "labels": ["Invoice No:", "Date:"]},
        {"type": "field_pair", "labels": ["Client Name:", "Email:"]},
        {"type": "field_single", "label": "Address:"},
    ]
    y = render_rows(draw, M, y, rows_meta, content_w, cfg)
    y += 20

    # Services table
    n_rows = tmpl.get("n_rows", 8)
    y = section_head(draw, M, y, "SERVICES", content_w, cfg)
    widths = [int(content_w * 0.5), int(content_w * 0.15),
              int(content_w * 0.175), int(content_w * 0.175)]
    widths[-1] = content_w - sum(widths[:-1])
    y = table_row(draw, M, y, ["Description", "Qty", "Unit Price", "Total"],
                  widths, cfg, header=True)
    for i in range(n_rows):
        y = table_row(draw, M, y, ["", "", "", ""], widths, cfg, alt=(i % 2 == 1))

    y += 20
    # Totals
    total_x = M + int(content_w * 0.65)
    total_w = content_w - int(content_w * 0.65)
    for label in ["Subtotal:", "Tax/VAT:", "TOTAL DUE:"]:
        bold = "TOTAL" in label
        draw.text((total_x, y), label, fill=CHARCOAL,
                  font=font(38, bold=bold))
        hline(draw, y + 50, total_x + 220, total_x + total_w, GOLD, thickness=2)
        y += 72

    y += 30
    rows_footer = [
        {"type": "field_pair", "labels": ["Payment Method:", "Payment Date:"]},
        {"type": "text_block", "lines": ["Thank you for your business!"],
         "font_size": 40, "bold": True},
    ]
    render_rows(draw, M, y, rows_footer, content_w, cfg)

    a4_footer(draw, W, H, cfg)
    img.save(str(out_path), "PNG")
    img.close()


def render_booking_confirmation(tmpl, cfg, out_path):
    W, H = A4_SIZE
    M = 120
    content_w = W - M * 2

    img  = Image.new("RGB", (W, H), p(cfg, "cream"))
    draw = ImageDraw.Draw(img)
    y    = a4_header(img, draw, cfg, "BOOKING CONFIRMATION")

    rows = [
        {"type": "field_pair",   "labels": ["Client Name:", "Phone:"]},
        {"type": "field_pair",   "labels": ["Date:", "Time:"]},
        {"type": "field_single", "label": "Service(s) Booked:"},
        {"type": "section_header", "text": "APPOINTMENT DETAILS", "gap_before": 20},
        {"type": "field_single", "label": "Staff Member:"},
        {"type": "field_pair",   "labels": ["Duration:", "Total Price:"]},
        {"type": "section_header", "text": "NOTES", "gap_before": 20},
        {"type": "field_single", "label": ""},
        {"type": "field_single", "label": ""},
        {"type": "section_header", "text": "CANCELLATION POLICY", "gap_before": 20},
        {"type": "text_block",
         "lines": ["Please give 24 hours notice to cancel or reschedule.",
                   "Late cancellations may incur a fee."],
         "font_size": 36, "gap_before": 16},
    ]
    render_rows(draw, M, y + 20, rows, content_w, cfg)

    a4_footer(draw, W, H, cfg)
    img.save(str(out_path), "PNG")
    img.close()


def render_social_1080(tmpl, cfg, out_path):
    W = H = 1080
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    bg = PRIMARY if variant == "dark" else CREAM
    fg = WHITE   if variant == "dark" else CHARCOAL

    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Corner accents
    for x0, y0, x1, y1 in [(0, 0, 120, 16), (0, 0, 16, 120),
                             (W - 120, 0, W, 16), (W - 16, 0, W, 120),
                             (0, H - 16, 120, H), (0, H - 120, 16, H),
                             (W - 120, H - 16, W, H), (W - 16, H - 120, W, H)]:
        draw.rectangle([x0, y0, x1, y1], fill=GOLD)

    niche_icon(draw, W // 2, 220, size=80, fill=GOLD, icon_type=icon)

    title = tmpl.get("title", "NEW POST")
    centred(draw, 360, title.upper(), fg, font(82, bold=True), canvas_w=W)
    hline(draw, 480, 80, W - 80, GOLD, thickness=4)

    body_lines = tmpl.get("body_lines", [brand.get("subtitle", ""), "Add your text here"])
    y = 520
    for line in body_lines:
        centred(draw, y, line, GOLD if variant == "dark" else PRIMARY,
                font(48), canvas_w=W)
        y += 80

    hline(draw, H - 130, 80, W - 80, GOLD, thickness=4)
    centred(draw, H - 110, brand.get("name_placeholder", "YOUR BUSINESS NAME"),
            fg, font(40, bold=True), canvas_w=W)

    img.save(str(out_path), "PNG")
    img.close()


def render_certificate(tmpl, cfg, out_path):
    W, H = A4_SIZE
    variant = tmpl.get("variant", "dark")
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    CHARCOAL = p(cfg, "charcoal")
    WHITE    = (255, 255, 255)
    brand    = cfg.get("brand", {})
    icon     = cfg.get("icon", "paw")

    bg = CREAM if variant == "light" else WHITE
    img  = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Decorative border
    for t in range(3):
        draw.rectangle([30 + t * 18, 30 + t * 18, W - 30 - t * 18, H - 30 - t * 18],
                       outline=GOLD, width=5)

    # Top header band
    bar(draw, 0, 0, W, 300, PRIMARY)
    niche_icon(draw, W // 2, 150, size=100, fill=GOLD, icon_type=icon)

    hline(draw, 300, 0, W, GOLD, thickness=8)

    centred(draw, 380, "CERTIFICATE OF COMPLETION", GOLD,
            font(82, bold=True, serifbold=True), canvas_w=W)
    hline(draw, 510, 150, W - 150, GOLD, thickness=4)

    program = tmpl.get("program_name", brand.get("subtitle", "Training Programme"))
    centred(draw, 560, program, PRIMARY, font(58, bold=True), canvas_w=W)

    centred(draw, 680, "This certifies that", CHARCOAL, font(48), canvas_w=W)

    # Name line
    hline(draw, 820, 300, W - 300, PRIMARY, thickness=3)
    centred(draw, 840, "OWNER / PET NAME", CHARCOAL, font(40), canvas_w=W)

    centred(draw, 940, "has successfully completed the above programme", CHARCOAL,
            font(46), canvas_w=W)

    # Date + Signature
    y = 1100
    draw.text((300, y), "Date:", fill=CHARCOAL, font=font(40, bold=True))
    hline(draw, y + 56, 300, 900, PRIMARY, thickness=2)
    right_align(draw, W - 300, y, "Trainer Signature:", CHARCOAL, font(40, bold=True))
    hline(draw, y + 56, W - 900, W - 300, PRIMARY, thickness=2)

    # Footer
    bar(draw, 0, H - 200, W, 200, PRIMARY)
    hline(draw, H - 200, 0, W, GOLD, thickness=6)
    centred(draw, H - 170, brand.get("name_placeholder", "YOUR BUSINESS NAME"),
            GOLD, font(48, bold=True), canvas_w=W)
    centred(draw, H - 110, "© PurpleOcaz — purpleocaz.etsy.com",
            CREAM, font(30), canvas_w=W)

    img.save(str(out_path), "PNG")
    img.close()


def render_income_tracker(tmpl, cfg, out_path):
    W, H = A4_SIZE
    M = 120; content_w = W - M * 2

    img  = Image.new("RGB", (W, H), p(cfg, "cream"))
    draw = ImageDraw.Draw(img)
    y    = a4_header(img, draw, cfg, tmpl.get("title", "INCOME TRACKER"))
    y += 20

    col_spec = tmpl.get("columns", ["Date", "Client", "Service", "Amount", "Notes"])
    n_rows   = tmpl.get("n_rows", 25)
    n_cols   = len(col_spec)
    widths   = [content_w // n_cols] * n_cols
    widths[-1] = content_w - sum(widths[:-1])

    y = table_row(draw, M, y, col_spec, widths, cfg, header=True)
    for i in range(n_rows):
        y = table_row(draw, M, y, [""] * n_cols, widths, cfg, alt=(i % 2 == 1))

    # Totals row
    y = table_row(draw, M, y, ["TOTAL"] + [""] * (n_cols - 2) + ["£"], widths, cfg, header=True)

    a4_footer(draw, W, H, cfg)
    img.save(str(out_path), "PNG")
    img.close()


# ── Template type dispatcher ──────────────────────────────────────────────────

RENDERERS = {
    "business_card":       render_business_card,
    "appointment_card":    render_appointment_card,
    "loyalty_card":        render_loyalty_card,
    "referral_card":       render_card_simple,
    "thank_you_card":      render_card_simple,
    "gift_certificate":    render_gift_certificate,
    "welcome_sign":        render_welcome_sign,
    "opening_hours_sign":  render_welcome_sign,   # same layout, different title
    "flyer_a4":            render_flyer_a4,
    "price_list":          render_price_list,
    "form_a4":             render_form_a4,
    "invoice":             render_invoice,
    "booking_confirmation":render_booking_confirmation,
    "social_1080":         render_social_1080,
    "certificate":         render_certificate,
    "income_tracker":      render_income_tracker,
    "expenses_tracker":    render_income_tracker,   # same layout, different title
}


# ── Spaces upload ─────────────────────────────────────────────────────────────

def upload_to_spaces(local_path, spaces_key, content_type="image/png"):
    s3 = boto3.client(
        "s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
    )
    s3.upload_file(str(local_path), "purpleocaz-assets", spaces_key,
                   ExtraArgs={"ACL": "public-read", "ContentType": content_type})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    with urllib.request.urlopen(url) as r:
        assert r.status == 200, f"Spaces verify failed: {url}"
    print(f"  ↑ {spaces_key} → HTTP 200")
    return url


# ── Delivery PDF ──────────────────────────────────────────────────────────────

def build_delivery_pdf(cfg, template_urls, out_path):
    """Build delivery PDF listing all templates with CDN URLs."""
    from reportlab.pdfgen import canvas as rc
    from reportlab.lib.pagesizes import A4 as RA4
    from reportlab.lib import colors as rlc

    niche_name = cfg["niche"]["name"]
    PRIMARY    = tuple(c / 255 for c in cfg["palette"]["primary"])
    GOLD_RL    = tuple(c / 255 for c in cfg["palette"]["gold"])

    c = rc.Canvas(str(out_path), pagesize=RA4)
    W, H = RA4

    # Cover page
    c.setFillColorRGB(*PRIMARY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*GOLD_RL)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H - 100, niche_name.upper())
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 140, "MEGA BUNDLE — DELIVERY LINKS")
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H - 180,
                        "Click each link to open your Canva template. Duplicate to edit.")
    c.showPage()

    # One page: list all templates
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*PRIMARY)
    c.rect(0, H - 80, W, 80, fill=1, stroke=0)
    c.setFillColorRGB(*GOLD_RL)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 52, "ALL TEMPLATES")

    y = H - 110
    c.setFont("Helvetica", 11)
    for tmpl_name, url in template_urls:
        if y < 60:
            c.showPage()
            c.setFillColorRGB(1, 1, 1)
            c.rect(0, 0, W, H, fill=1, stroke=0)
            y = H - 60
        c.setFillColorRGB(*tuple(c2 / 255 for c2 in (26, 26, 26)))
        c.drawString(40, y, f"• {tmpl_name}")
        c.setFillColorRGB(*PRIMARY)
        c.drawRightString(W - 40, y, url)
        y -= 22

    c.setFillColorRGB(*PRIMARY)
    c.rect(0, 0, W, 50, fill=1, stroke=0)
    c.setFillColorRGB(*GOLD_RL)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, 18, "© PurpleOcaz — purpleocaz.etsy.com")
    c.save()
    print(f"  PDF saved → {out_path}")


# ── Etsy helpers ──────────────────────────────────────────────────────────────

def get_etsy_headers():
    tokens = json.loads((PROJECT / "workflows/etsy_analytics/etsy_tokens.json").read_text())
    return {
        "x-api-key": "19d2q2xcg1ccipoj4doub0ee:rj7ou7mzjq",
        "Authorization": f"Bearer {tokens['access_token']}",
    }


def etsy_request(method, path, body=None):
    url = "https://openapi.etsy.com/v3/application" + path
    headers = get_etsy_headers()
    if body:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body.encode() if body else None,
                                  headers=headers, method=method)
    with urllib.request.urlopen(req) as r:
        raw = r.read()
        return json.loads(raw) if raw.strip() else {}


def upload_image_to_etsy(listing_id, img_path, rank):
    boundary = uuid.uuid4().hex
    img_data = open(img_path, "rb").read()
    fn = Path(img_path).name
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n{rank}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
            f"filename=\"{fn}\"\r\nContent-Type: image/png\r\n\r\n").encode() \
           + img_data + f"\r\n--{boundary}--\r\n".encode()
    headers = get_etsy_headers()
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(
        f"https://openapi.etsy.com/v3/application/shops/34071205/listings/{listing_id}/images",
        data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def upload_file_to_etsy(listing_id, pdf_path):
    boundary = uuid.uuid4().hex
    pdf_data = open(pdf_path, "rb").read()
    fn = Path(pdf_path).name
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{fn}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            f"filename=\"{fn}\"\r\nContent-Type: application/pdf\r\n\r\n").encode() \
           + pdf_data + f"\r\n--{boundary}--\r\n".encode()
    headers = get_etsy_headers()
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(
        f"https://openapi.etsy.com/v3/application/shops/34071205/listings/{listing_id}/files",
        data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ── Listing image builder ─────────────────────────────────────────────────────

def build_listing_images(cfg, out_dir, template_pngs):
    """Build 7 standard listing images from template PNGs."""
    PRIMARY  = p(cfg, "primary")
    GOLD     = p(cfg, "gold")
    CREAM    = p(cfg, "cream")
    WHITE    = (255, 255, 255)
    W = H    = 3000
    niche    = cfg["niche"]
    brand    = cfg.get("brand", {})
    slug     = niche["slug"]
    count    = len(cfg["templates"])
    icon     = cfg.get("icon", "paw")
    listing_imgs = []

    def listing_img(filename, bg, draw_fn):
        path = out_dir / filename
        img  = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(img)
        draw_fn(img, draw)
        img.save(str(path), "PNG")
        img.close()
        listing_imgs.append(path)
        print(f"  Saved {filename}")

    # Image 1: Hero
    def draw_hero(img, draw):
        bar(draw, 0, H - 700, W, 700, PRIMARY)
        hline(draw, H - 700, 0, W, GOLD, thickness=10)
        centred(draw, 80, niche["name"].upper(), PRIMARY, font(100, bold=True), canvas_w=W)
        hline(draw, 220, 100, W - 100, GOLD, thickness=6)
        centred(draw, 280, "MEGA BUNDLE", GOLD, font(80, bold=True), canvas_w=W)
        centred(draw, 400, f"{count} CANVA TEMPLATES", PRIMARY, font(60), canvas_w=W)
        niche_icon(draw, W // 2, 600, size=120, fill=PRIMARY, icon_type=icon)
        centred(draw, H - 620, "FULLY EDITABLE IN CANVA FREE PLAN", WHITE,
                font(64, bold=True), canvas_w=W)
        centred(draw, H - 520, "INSTANT DIGITAL DOWNLOAD", GOLD, font(54), canvas_w=W)
        centred(draw, H - 420, "© PurpleOcaz", WHITE, font(40), canvas_w=W)
    listing_img(f"{slug}_listing_01_hero.png", CREAM, draw_hero)

    # Image 2: What's Inside
    def draw_inside(img, draw):
        bar(draw, 0, 0, W, 300, PRIMARY)
        hline(draw, 300, 0, W, GOLD, thickness=8)
        centred(draw, 100, "WHAT'S INSIDE", WHITE, font(100, bold=True), canvas_w=W)
        categories = {}
        for t in cfg["templates"]:
            cat = t.get("category", "Templates")
            categories.setdefault(cat, []).append(t.get("title", t["filename"]))
        y = 360
        for cat, items in categories.items():
            draw.rectangle([80, y, W - 80, y + 80], fill=PRIMARY)
            draw.text((120, y + 18), cat.upper(), fill=GOLD, font=font(48, bold=True))
            draw.text((W - 200, y + 18), f"{len(items)}", fill=WHITE, font=font(48, bold=True))
            y += 80
            for item in items[:6]:
                draw.text((120, y + 14), f"  ✓  {item}", fill=(26, 26, 26), font=font(44))
                y += 68
            if len(items) > 6:
                draw.text((120, y + 14), f"  + {len(items) - 6} more...",
                          fill=p(cfg, "primary"), font=font(44))
                y += 68
            y += 20
    listing_img(f"{slug}_listing_02_whats_inside.png", CREAM, draw_inside)

    # Image 3: Lifestyle / preview collage (tiled templates)
    def draw_lifestyle(img, draw):
        bar(draw, 0, 0, W, 200, PRIMARY)
        hline(draw, 200, 0, W, GOLD, thickness=6)
        centred(draw, 60, "PREVIEW", WHITE, font(90, bold=True), canvas_w=W)
        tile_size = 700; cols = 4; x0 = 0; y0 = 220
        for i, tp in enumerate(template_pngs[:8]):
            col = i % cols; row = i // cols
            try:
                thumb = Image.open(str(tp)).convert("RGB")
                thumb = thumb.resize((tile_size, tile_size), Image.LANCZOS)
                img.paste(thumb, (x0 + col * tile_size, y0 + row * tile_size))
                thumb.close()
            except Exception:
                pass
    listing_img(f"{slug}_listing_03_lifestyle.png", CREAM, draw_lifestyle)

    # Image 4: How It Works
    def draw_how(img, draw):
        bar(draw, 0, 0, W, 300, PRIMARY)
        hline(draw, 300, 0, W, GOLD, thickness=8)
        centred(draw, 100, "HOW IT WORKS", WHITE, font(100, bold=True), canvas_w=W)
        steps = [
            ("1", "PURCHASE", "Buy once, yours forever"),
            ("2", "DOWNLOAD", "PDF delivered instantly"),
            ("3", "CLICK LINK", "Open template in Canva"),
            ("4", "CUSTOMISE", "Add your brand & details"),
            ("5", "PRINT / SHARE", "Ready in minutes"),
        ]
        y = 380
        for num, title, sub in steps:
            draw.ellipse([120, y, 240, y + 120], fill=GOLD)
            centred_x = 180
            bb = draw.textbbox((0, 0), num, font=font(72, bold=True))
            draw.text((centred_x - (bb[2] - bb[0]) // 2, y + 20), num,
                      fill=PRIMARY, font=font(72, bold=True))
            draw.text((300, y + 10), title, fill=PRIMARY, font=font(70, bold=True))
            draw.text((300, y + 88), sub, fill=(80, 80, 80), font=font(48))
            y += 180
    listing_img(f"{slug}_listing_04_how_it_works.png", CREAM, draw_how)

    # Image 5: Why Buy
    def draw_why(img, draw):
        bar(draw, 0, 0, W, 300, PRIMARY)
        hline(draw, 300, 0, W, GOLD, thickness=8)
        centred(draw, 100, "WHY BUY THIS", WHITE, font(100, bold=True), canvas_w=W)
        reasons = [
            "Save hours of design time",
            "Professional, print-ready templates",
            "Fully editable — any colours, any fonts",
            "Works with Canva FREE plan",
            "Instant download — no waiting",
            f"Everything in one bundle — {count} templates",
            "Designed for your niche, not generic",
        ]
        y = 380
        for reason in reasons:
            niche_icon(draw, 120, y + 40, size=35, fill=GOLD, icon_type=icon)
            draw.text((200, y + 5), reason, fill=(26, 26, 26), font=font(58))
            y += 170
    listing_img(f"{slug}_listing_05_why_buy.png", CREAM, draw_why)

    # Image 6: Canva Basics
    def draw_canva(img, draw):
        bar(draw, 0, 0, W, 300, PRIMARY)
        hline(draw, 300, 0, W, GOLD, thickness=8)
        centred(draw, 100, "USING CANVA", WHITE, font(100, bold=True), canvas_w=W)
        draw.rectangle([120, 360, W - 120, 760], fill=p(cfg, "primary"))
        centred(draw, 380, "FREE CANVA ACCOUNT WORKS",
                GOLD, font(64, bold=True), canvas_w=W)
        centred(draw, 470, "You do NOT need Canva Pro to use these templates.",
                WHITE, font(48), canvas_w=W)
        centred(draw, 560, "A free account is all you need.",
                WHITE, font(48), canvas_w=W)
        tips = [
            "Open the link in your delivery PDF",
            "Click 'Use Template' to make your copy",
            "Edit text, colours and images",
            "Download as PDF (Print) or PNG",
        ]
        y = 820
        for tip in tips:
            draw.text((160, y), f"▸  {tip}", fill=(26, 26, 26), font=font(56))
            y += 140
    listing_img(f"{slug}_listing_06_canva_basics.png", CREAM, draw_canva)

    # Image 7: Please Note
    def draw_note(img, draw):
        bar(draw, 0, 0, W, 300, PRIMARY)
        hline(draw, 300, 0, W, GOLD, thickness=8)
        centred(draw, 100, "PLEASE NOTE", WHITE, font(100, bold=True), canvas_w=W)
        notes = [
            "This is a DIGITAL DOWNLOAD — nothing physical is posted.",
            "Templates are for your own business use only.",
            "Reselling or redistributing is not permitted.",
            "Colours may vary slightly between screens and printers.",
            "Questions? Message us on Etsy — reply within 24 hours.",
        ]
        y = 400
        for note in notes:
            draw.rectangle([80, y, W - 80, y + 4], fill=GOLD)
            y += 30
            draw.text((120, y), note, fill=(26, 26, 26), font=font(52))
            y += 170
    listing_img(f"{slug}_listing_07_please_note.png", CREAM, draw_note)

    return listing_imgs


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main(config_path, skip_etsy=False, only_pdf=False):
    print(f"\n{'='*60}")
    print(f"NICHE TEMPLATE FACTORY")
    print(f"Config: {config_path}")
    print(f"{'='*60}\n")

    cfg = json.loads(Path(config_path).read_text())

    niche     = cfg["niche"]
    slug      = niche["slug"]
    prefix    = cfg.get("spaces", {}).get("prefix", f"templates/{slug}")
    out_base  = PROJECT / "outputs" / slug
    tmpl_dir  = out_base / "templates"
    list_dir  = out_base / "listing"
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    list_dir.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: Build templates ──────────────────────────────────────────────
    print("=== Phase 1: Building templates ===")
    template_urls  = []
    template_paths = []

    for tmpl in cfg["templates"]:
        t_type    = tmpl["type"]
        filename  = tmpl["filename"]
        out_path  = tmpl_dir / filename
        renderer  = RENDERERS.get(t_type)

        if renderer is None:
            print(f"  SKIP (unknown type): {t_type} — {filename}")
            continue

        renderer(tmpl, cfg, out_path)

        # Sub-folder based on category
        cat = tmpl.get("category", "misc").lower().replace(" ", "_").replace("/", "_")
        spaces_key = f"{prefix}/{cat}/{filename}"
        url = upload_to_spaces(out_path, spaces_key)
        template_urls.append((tmpl.get("title", filename), url))
        template_paths.append(out_path)
        print(f"  ✓  {filename}")

    print(f"\n  {len(template_paths)} templates built and uploaded.\n")

    # ── Phase 2: Delivery PDF ─────────────────────────────────────────────────
    print("=== Phase 2: Delivery PDF ===")
    prefix_upper = slug.upper().replace("-", "_")
    pdf_filename = f"{prefix_upper}_Mega_Bundle_DELIVERY.pdf"
    pdf_path     = list_dir / pdf_filename
    build_delivery_pdf(cfg, template_urls, pdf_path)

    pdf_spaces_key = f"{prefix}/{pdf_filename}"
    pdf_url = upload_to_spaces(pdf_path, pdf_spaces_key, content_type="application/pdf")
    print(f"  PDF on Spaces: {pdf_url}\n")

    if only_pdf:
        print("--only-pdf flag set. Stopping after PDF.")
        return

    # ── Phase 3: Listing images ───────────────────────────────────────────────
    print("=== Phase 3: Listing images ===")
    listing_imgs = build_listing_images(cfg, list_dir, template_paths)
    print()

    if skip_etsy:
        print("--skip-etsy flag set. Done.")
        return

    # ── Phase 4: Etsy draft ───────────────────────────────────────────────────
    print("=== Phase 4: Creating Etsy draft ===")
    etsy_cfg = niche.get("etsy", {})
    tags = etsy_cfg.get("tags", [])
    for tag in tags:
        assert len(tag) <= 20, f"Tag too long: '{tag}' ({len(tag)})"
    assert len(tags) == len(set(tags)), "Duplicate tags detected"

    body = urllib.parse.urlencode({
        "title":       etsy_cfg.get("title", niche["name"]),
        "description": etsy_cfg.get("description", niche["name"]),
        "price":       str(etsy_cfg.get("price", "39.99")),
        "quantity":    "999",
        "who_made":    "i_did",
        "when_made":   "2020_2025",
        "taxonomy_id": "1874",
        "type":        "download",
        "is_supply":   "false",
        "tags":        ",".join(tags),
        "state":       "draft",
    })
    result = etsy_request("POST", "/shops/34071205/listings", body)
    listing_id = result["listing_id"]
    print(f"  Draft created: #{listing_id}")

    # ── Phase 5: Upload listing images ────────────────────────────────────────
    print("\n=== Phase 5: Uploading listing images ===")
    for rank, img_path in enumerate(listing_imgs, 1):
        res = upload_image_to_etsy(listing_id, img_path, rank)
        print(f"  rank {rank} — {img_path.name}")

    check = etsy_request("GET", f"/listings/{listing_id}/images")
    print(f"  GET images count: {check['count']}")

    # ── Phase 6: Attach PDF ───────────────────────────────────────────────────
    print("\n=== Phase 6: Attaching PDF ===")
    fr = upload_file_to_etsy(listing_id, pdf_path)
    print(f"  File: {fr.get('filename')} | ID {fr.get('listing_file_id')}")
    files = etsy_request("GET", f"/shops/34071205/listings/{listing_id}/files")
    print(f"  GET files count: {files['count']}")

    print(f"\n{'='*60}")
    print(f"COMPLETE — Draft #{listing_id}")
    print(f"https://www.etsy.com/listing/{listing_id}")
    print(f"{'='*60}")

    return listing_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Niche Template Factory")
    parser.add_argument("config", help="Path to niche JSON config")
    parser.add_argument("--skip-etsy", action="store_true",
                        help="Build templates + PDF only, skip Etsy")
    parser.add_argument("--only-pdf", action="store_true",
                        help="Build templates + PDF only, skip listing images + Etsy")
    args = parser.parse_args()
    main(args.config, skip_etsy=args.skip_etsy, only_pdf=args.only_pdf)
