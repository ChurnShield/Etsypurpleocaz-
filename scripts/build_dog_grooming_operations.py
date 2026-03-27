#!/usr/bin/env python3
"""
Dog Grooming — Operations Templates (6 A4 templates)
1. Daily Appointment Schedule
2. Cleaning Checklist
3. Tool Sanitisation Log
4. Flea Policy Notice
5. Expenses Tracker
6. Income Tracker
"""
import sys
from pathlib import Path

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
from dog_grooming_design_system import (
    TEAL, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT,
    A4, font, centred, right, gold_rule, section_head,
    field_line, field_pair, checkbox, table_row,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)
from PIL import Image, ImageDraw

OUTPUT = PROJECT / "outputs" / "dog-grooming" / "operations"
OUTPUT.mkdir(parents=True, exist_ok=True)

MARGIN = 120
FIELD_W = A4[0] - MARGIN * 2


def _blank_a4(title: str):
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, title)
    return img, draw, y


# ── 1. Daily Appointment Schedule ────────────────────────────────────────────

def _daily_schedule():
    img, draw, y = _blank_a4("DAILY APPOINTMENT SCHEDULE")

    y = section_head(draw, MARGIN, y, "DATE / GROOMER", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Date:", "Groomer on duty:", total_w=FIELD_W)
    y += 20

    y = section_head(draw, MARGIN, y, "APPOINTMENTS", width=FIELD_W)
    cols = ["Time", "Dog's name", "Breed", "Service", "Owner phone", "Notes", "Done"]
    widths_raw = [180, 320, 280, 360, 280, 460, 120]
    total = sum(widths_raw)
    scale = FIELD_W / total
    widths = [int(w * scale) for w in widths_raw]
    widths[-1] = FIELD_W - sum(widths[:-1])  # absorb rounding

    y = table_row(draw, MARGIN, y, cols, widths, row_h=70, header=True)

    time_slots = ["8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30",
                  "12:00", "12:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30",
                  "4:00", "4:30", "5:00", "5:30"]
    for i, t in enumerate(time_slots):
        y = table_row(draw, MARGIN, y,
                      [t, "", "", "", "", "", "□"],
                      widths, row_h=58, alt=(i % 2 == 1))

    y += 18
    y = section_head(draw, MARGIN, y, "END OF DAY NOTES", width=FIELD_W)
    for _ in range(3):
        y = field_line(draw, MARGIN, y + 18, "", width=FIELD_W, font_size=10)

    a4_footer(draw, *A4)
    return img


# ── 2. Cleaning Checklist ─────────────────────────────────────────────────────

def _cleaning_checklist():
    img, draw, y = _blank_a4("CLEANING CHECKLIST")

    y = section_head(draw, MARGIN, y, "DATE & COMPLETED BY", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Date:", "Completed by:", total_w=FIELD_W)
    y += 20

    sections = [
        ("BETWEEN EVERY DOG", [
            "Clean and disinfect grooming table",
            "Brush/vacuum table and floor area",
            "Rinse and sanitise bath/tub",
            "Replace towels with fresh ones",
            "Disinfect brush, comb, scissors used",
            "Dispose of loose hair and waste",
        ]),
        ("START OF DAY", [
            "Check and restock shampoos / conditioners",
            "Clean and dry all tools from previous day",
            "Mop salon floor",
            "Clean windows and mirrors",
            "Empty and clean waste bins",
            "Check dryer filters and clean if needed",
        ]),
        ("END OF DAY", [
            "Full floor mop and sweep",
            "Disinfect all work surfaces",
            "Sterilise scissors and blades (Barbicide / UV)",
            "Clean and dry all cages / kennels",
            "Empty all bins and replace liners",
            "Wipe down dryers and clippers",
            "Secure all products and equipment",
            "Lock up and set alarm",
        ]),
        ("WEEKLY DEEP CLEAN", [
            "Clean grooming table legs and hydraulics",
            "Descale bath/tub and showerhead",
            "Clean fridge (if applicable)",
            "Wash all towels and laundrettes",
            "Check stock levels and reorder as needed",
            "Inspect equipment for wear or damage",
        ]),
    ]

    for sec_title, items in sections:
        if y > A4[1] - 400:
            break
        y = section_head(draw, MARGIN, y, sec_title, width=FIELD_W)
        y += 12
        for item in items:
            draw.rectangle([MARGIN, y, MARGIN + 50, y + 50], outline=TEAL, width=3)
            draw.text((MARGIN + 66, y + 8), item, fill=CHARCOAL, font=font(34))
            y += 62
        y += 8

    a4_footer(draw, *A4)
    return img


# ── 3. Tool Sanitisation Log ──────────────────────────────────────────────────

def _tool_log():
    img, draw, y = _blank_a4("TOOL SANITISATION LOG")

    y = section_head(draw, MARGIN, y, "MONTH / GROOMER", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Month / Year:", "Groomer name:", total_w=FIELD_W)
    y += 16

    y = section_head(draw, MARGIN, y, "SANITISATION METHODS USED", width=FIELD_W)
    y += 16
    methods = [
        ("B", "Barbicide soak (minimum 10 minutes)"),
        ("UV", "UV sterilisation cabinet"),
        ("A", "Autoclave / steam sterilisation"),
        ("W", "Wipe down with disinfectant spray"),
    ]
    for code, desc in methods:
        draw.rectangle([MARGIN, y, MARGIN + 70, y + 52], fill=TEAL)
        centred(draw, y + 8, code, WHITE, font(36, bold=True), canvas_w=70)
        draw.text((MARGIN + 86, y + 12), f"= {desc}", fill=CHARCOAL, font=font(34))
        y += 64
    y += 12

    # Log table
    y = section_head(draw, MARGIN, y, "DAILY LOG", width=FIELD_W)
    cols = ["Date", "Scissors", "Blades", "Combs/Brushes", "Dryer nozzles", "Method", "Sign"]
    widths_raw = [200, 240, 200, 320, 280, 200, 200]
    total = sum(widths_raw)
    scale = FIELD_W / total
    widths = [int(w * scale) for w in widths_raw]
    widths[-1] = FIELD_W - sum(widths[:-1])

    y = table_row(draw, MARGIN, y, cols, widths, row_h=68, header=True)
    for i in range(22):
        y = table_row(draw, MARGIN, y, [""] * len(cols), widths,
                      row_h=56, alt=(i % 2 == 1))

    a4_footer(draw, *A4)
    return img


# ── 4. Flea Policy Notice ──────────────────────────────────────────────────────

def _flea_policy():
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 500], fill=TEAL)
    paw_print(draw, 200, 250, size=88, fill=GOLD)
    paw_print(draw, W - 200, 250, size=88, fill=GOLD)
    centred(draw, 60, "⚠  FLEA POLICY  ⚠", GOLD, font(120, bold=True), canvas_w=W)
    centred(draw, 222, "Please read before your dog's appointment", WHITE, font(52), canvas_w=W)
    centred(draw, 310, "YOUR SALON NAME", WHITE, font(56, bold=True), canvas_w=W)
    centred(draw, 390, "Professional Dog Grooming", GOLD, font(44), canvas_w=W)
    gold_rule(draw, 500, thickness=10, canvas_w=W)

    sections = [
        ("WHAT TO DO IF YOUR DOG HAS FLEAS", [
            "Please inform us BEFORE your appointment — there is no shame, it's very common.",
            "Treat your dog with a vet-recommended flea treatment at least 24 hours before.",
            "Treat your home (carpets, bedding, furniture) at the same time.",
            "Inform your vet if the infestation is severe.",
        ]),
        ("OUR SALON POLICY", [
            "If we discover fleas during a groom, we will stop the service immediately.",
            "We will contact you to collect your dog as soon as possible.",
            "A flea surcharge of £15 will be applied for decontamination of the salon.",
            "We reserve the right to refuse future bookings for untreated repeat cases.",
            "Any costs incurred treating other dogs affected will be passed to the owner.",
        ]),
        ("WHY THIS MATTERS", [
            "Fleas can spread to other dogs and pets in the salon within minutes.",
            "Our staff health and other clients' pets depend on strict hygiene.",
            "We decontaminate the entire salon when fleas are found — this takes 2+ hours.",
            "By booking with us you agree to notify us of any known flea infestations.",
        ]),
    ]

    y = 540
    for sec_title, items in sections:
        y = section_head(draw, MARGIN, y, sec_title, width=FIELD_W)
        y += 16
        for item in items:
            paw_print(draw, MARGIN + 22, y + 20, size=14, fill=TEAL)
            draw.text((MARGIN + 52, y + 4), item, fill=CHARCOAL, font=font(36))
            y += 68
        y += 12

    gold_rule(draw, y + 20, x0=MARGIN, x1=W - MARGIN, thickness=6)
    centred(draw, y + 48, "Thank you for your cooperation in keeping all our dogs safe 🐾",
            TEAL, font(40, bold=True), canvas_w=W)
    centred(draw, y + 102, "Any questions? Call us on 07700 000000", CHARCOAL, font(36), canvas_w=W)

    a4_footer(draw, W, H)
    return img


# ── 5. Expenses Tracker ───────────────────────────────────────────────────────

def _expenses_tracker():
    img, draw, y = _blank_a4("MONTHLY EXPENSES TRACKER")

    y = section_head(draw, MARGIN, y, "PERIOD", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Month / Year:", "Business name:", total_w=FIELD_W)
    y += 20

    y = section_head(draw, MARGIN, y, "EXPENSE LOG", width=FIELD_W)
    cols = ["Date", "Description / Supplier", "Category", "Amount (£)", "Receipt?", "Notes"]
    widths_raw = [200, 580, 340, 240, 180, 460 + (FIELD_W - 200 - 580 - 340 - 240 - 180 - 460)]
    widths = widths_raw[:5] + [FIELD_W - sum(widths_raw[:5])]
    y = table_row(draw, MARGIN, y, cols, widths, row_h=68, header=True)
    for i in range(22):
        y = table_row(draw, MARGIN, y, ["", "", "", "", "□ Yes  □ No", ""],
                      widths, row_h=56, alt=(i % 2 == 1))

    # Totals
    y += 20
    y = section_head(draw, MARGIN, y, "CATEGORY TOTALS", width=FIELD_W)
    cats = ["Products & supplies", "Equipment", "Rent / utilities", "Insurance",
            "Marketing", "Training / CPD", "Other"]
    cols2 = ["Category", "Total (£)", "Category", "Total (£)"]
    hw = FIELD_W // 2
    for i in range(0, len(cats), 2):
        left  = cats[i]  if i < len(cats) else ""
        right_ = cats[i + 1] if i + 1 < len(cats) else ""
        bg = CREAM_ALT if (i // 2) % 2 else CREAM
        draw.rectangle([MARGIN, y, A4[0] - MARGIN, y + 66], fill=bg)
        gold_rule(draw, y + 64, x0=MARGIN, x1=A4[0] - MARGIN, thickness=1)
        draw.text((MARGIN + 16, y + 14), left, fill=CHARCOAL, font=font(36))
        draw.text((MARGIN + hw // 2 + 100, y + 14), "£", fill=TEAL, font=font(36, bold=True))
        if right_:
            draw.text((MARGIN + hw + 16, y + 14), right_, fill=CHARCOAL, font=font(36))
            draw.text((MARGIN + hw * 3 // 2 + 100, y + 14), "£", fill=TEAL, font=font(36, bold=True))
        y += 66

    y += 12
    draw.rectangle([MARGIN, y, A4[0] - MARGIN, y + 78], fill=TEAL)
    draw.text((MARGIN + 20, y + 18), "TOTAL EXPENSES THIS MONTH:", fill=WHITE, font=font(44, bold=True))
    right(draw, A4[0] - MARGIN - 20, y + 18, "£ ________________", fill=GOLD, f=font(44, bold=True))

    a4_footer(draw, *A4)
    return img


# ── 6. Income Tracker ─────────────────────────────────────────────────────────

def _income_tracker():
    img, draw, y = _blank_a4("MONTHLY INCOME TRACKER")

    y = section_head(draw, MARGIN, y, "PERIOD", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Month / Year:", "Business name:", total_w=FIELD_W)
    y += 20

    y = section_head(draw, MARGIN, y, "INCOME LOG", width=FIELD_W)
    cols = ["Date", "Client / Dog name", "Service", "Amount (£)", "Payment", "Notes"]
    widths_raw = [200, 480, 440, 240, 280, 560 + (FIELD_W - 200 - 480 - 440 - 240 - 280 - 560)]
    widths = widths_raw[:5] + [FIELD_W - sum(widths_raw[:5])]
    y = table_row(draw, MARGIN, y, cols, widths, row_h=68, header=True)
    for i in range(22):
        y = table_row(draw, MARGIN, y,
                      ["", "", "", "", "□ Cash  □ Card  □ Bank", ""],
                      widths, row_h=56, alt=(i % 2 == 1))

    # Summary
    y += 20
    y = section_head(draw, MARGIN, y, "MONTHLY SUMMARY", width=FIELD_W)
    summaries = [
        ("Total grooms this month:",     "£"),
        ("Add-ons / extras income:",     "£"),
        ("Product sales:",               "£"),
        ("Gift certificates redeemed:",  "£"),
        ("Total income this month:",     "£"),
    ]
    for i, (label, val) in enumerate(summaries):
        bold = "Total income" in label
        bg = TEAL if bold else (CREAM_ALT if i % 2 else CREAM)
        fg = WHITE if bold else CHARCOAL
        draw.rectangle([MARGIN, y, A4[0] - MARGIN, y + 72], fill=bg)
        gold_rule(draw, y + 70, x0=MARGIN, x1=A4[0] - MARGIN, thickness=2)
        draw.text((MARGIN + 20, y + 16), label, fill=fg, font=font(40, bold=bold))
        right(draw, A4[0] - MARGIN - 20, y + 16, f"{val} ________________",
              fill=GOLD if bold else TEAL, f=font(40, bold=bold))
        y += 72

    y += 12
    draw.text((MARGIN, y + 10), "* Keep receipts and records for 6 years for tax purposes.",
              fill=TEAL, font=font(34, bold=True))

    a4_footer(draw, *A4)
    return img


# ── Build & upload ────────────────────────────────────────────────────────────

TEMPLATES = {
    "DG_Daily_Schedule.png":        (_daily_schedule,  "operations"),
    "DG_Cleaning_Checklist.png":    (_cleaning_checklist,"operations"),
    "DG_Tool_Sanitisation_Log.png": (_tool_log,        "operations"),
    "DG_Flea_Policy.png":           (_flea_policy,     "operations"),
    "DG_Expenses_Tracker.png":      (_expenses_tracker,"operations"),
    "DG_Income_Tracker.png":        (_income_tracker,  "operations"),
}


def build_all() -> dict:
    urls = {}
    print(f"\n{'='*60}")
    print("DOG GROOMING — OPERATIONS TEMPLATES (6 templates)")
    print(f"{'='*60}")
    for filename, (build_fn, category) in TEMPLATES.items():
        print(f"\n  Building {filename}...")
        img = build_fn()
        local = OUTPUT / filename
        img.save(local, "PNG", dpi=(300, 300))
        key = f"templates/dog-grooming/{category}/{filename}"
        url = upload_to_spaces(local, key)
        urls[filename] = url
    print(f"\n  ✓ Operations templates complete — {len(urls)} uploaded")
    return urls


if __name__ == "__main__":
    result = build_all()
    for name, url in result.items():
        print(f"  {name}: {url}")
