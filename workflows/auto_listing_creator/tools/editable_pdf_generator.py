# =============================================================================
# workflows/auto_listing_creator/tools/editable_pdf_generator.py
#
# Creates editable (AcroForm) PDFs for Tier 1 products.
# Uses Nano Banana image as full-page background with overlaid text fields
# that buyers can type into directly in any PDF reader.
# =============================================================================

import os

from tools.design_constants import EXPORT_DIR, BRAND_PURPLE, safe_filename

# ---- Page sizes in points (72 points per inch) -----------------------------
A4_W, A4_H = 595.27, 841.89
LETTER_W, LETTER_H = 612.0, 792.0

# ---- Brand purple as 0-1 RGB tuple for ReportLab --------------------------
_BRAND_RGB = (0.420, 0.129, 0.537)  # #6B2189

# ---- Field layout definitions per product type -----------------------------
# Each field: name, label, x, y (from bottom-left), width, height
# Coordinates are for A4; Letter variants are auto-scaled.

FIELD_LAYOUTS = {
    "appointment card": {
        "page_title": "Appointment Card",
        "fields": [
            {"name": "name", "label": "Name",
             "x": 72, "y": 660, "w": 400, "h": 22},
            {"name": "date", "label": "Date",
             "x": 72, "y": 610, "w": 400, "h": 22},
            {"name": "time", "label": "Time",
             "x": 72, "y": 560, "w": 400, "h": 22},
            {"name": "day", "label": "Day",
             "x": 72, "y": 510, "w": 400, "h": 22},
        ],
    },
    "gift certificate": {
        "page_title": "Gift Certificate",
        "fields": [
            {"name": "studio_name", "label": "Studio Name",
             "x": 72, "y": 680, "w": 448, "h": 22},
            {"name": "recipient", "label": "Recipient",
             "x": 72, "y": 610, "w": 250, "h": 22},
            {"name": "amount", "label": "Amount",
             "x": 340, "y": 610, "w": 180, "h": 22},
            {"name": "from_name", "label": "From",
             "x": 72, "y": 560, "w": 250, "h": 22},
            {"name": "valid_until", "label": "Valid Until",
             "x": 340, "y": 560, "w": 180, "h": 22},
            {"name": "message", "label": "Personal Message",
             "x": 72, "y": 490, "w": 448, "h": 50},
        ],
    },
    "price list": {
        "page_title": "Service Menu",
        "fields": [
            {"name": "studio_name", "label": "Studio Name",
             "x": 72, "y": 700, "w": 448, "h": 22},
            {"name": "service_1", "label": "Service 1",
             "x": 72, "y": 640, "w": 300, "h": 22},
            {"name": "price_1", "label": "Price",
             "x": 390, "y": 640, "w": 130, "h": 22},
            {"name": "service_2", "label": "Service 2",
             "x": 72, "y": 600, "w": 300, "h": 22},
            {"name": "price_2", "label": "Price",
             "x": 390, "y": 600, "w": 130, "h": 22},
            {"name": "service_3", "label": "Service 3",
             "x": 72, "y": 560, "w": 300, "h": 22},
            {"name": "price_3", "label": "Price",
             "x": 390, "y": 560, "w": 130, "h": 22},
            {"name": "service_4", "label": "Service 4",
             "x": 72, "y": 520, "w": 300, "h": 22},
            {"name": "price_4", "label": "Price",
             "x": 390, "y": 520, "w": 130, "h": 22},
            {"name": "service_5", "label": "Service 5",
             "x": 72, "y": 480, "w": 300, "h": 22},
            {"name": "price_5", "label": "Price",
             "x": 390, "y": 480, "w": 130, "h": 22},
            {"name": "phone", "label": "Phone",
             "x": 72, "y": 420, "w": 200, "h": 22},
            {"name": "website", "label": "Website",
             "x": 290, "y": 420, "w": 230, "h": 22},
        ],
    },
    "business card": {
        "page_title": "Business Card",
        "fields": [
            {"name": "name", "label": "Your Name",
             "x": 72, "y": 660, "w": 250, "h": 22},
            {"name": "title", "label": "Title / Role",
             "x": 340, "y": 660, "w": 180, "h": 22},
            {"name": "phone", "label": "Phone",
             "x": 72, "y": 610, "w": 250, "h": 22},
            {"name": "email", "label": "Email",
             "x": 340, "y": 610, "w": 180, "h": 22},
            {"name": "website", "label": "Website",
             "x": 72, "y": 560, "w": 250, "h": 22},
            {"name": "address", "label": "Address",
             "x": 340, "y": 560, "w": 180, "h": 22},
        ],
    },
    "branding bundle": {
        "page_title": "Branding Bundle",
        "fields": [
            {"name": "studio_name", "label": "Studio Name",
             "x": 72, "y": 680, "w": 448, "h": 22},
            {"name": "tagline", "label": "Tagline",
             "x": 72, "y": 630, "w": 448, "h": 22},
            {"name": "phone", "label": "Phone",
             "x": 72, "y": 580, "w": 200, "h": 22},
            {"name": "email", "label": "Email",
             "x": 290, "y": 580, "w": 230, "h": 22},
            {"name": "website", "label": "Website",
             "x": 72, "y": 530, "w": 200, "h": 22},
            {"name": "address", "label": "Address",
             "x": 290, "y": 530, "w": 230, "h": 22},
        ],
    },
}

_DEFAULT_LAYOUT = {
    "page_title": "Template",
    "fields": [
        {"name": "name", "label": "Name",
         "x": 72, "y": 660, "w": 448, "h": 22},
        {"name": "date", "label": "Date",
         "x": 72, "y": 610, "w": 200, "h": 22},
        {"name": "phone", "label": "Phone",
         "x": 290, "y": 610, "w": 230, "h": 22},
        {"name": "email", "label": "Email",
         "x": 72, "y": 560, "w": 448, "h": 22},
        {"name": "details", "label": "Details",
         "x": 72, "y": 490, "w": 448, "h": 50},
    ],
}


def create_editable_pdf(listing, product_type, background_image_path,
                        output_dir=None, gemini_api_key=None):
    """Create an editable PDF with AcroForm fields.

    Generates a 6-page PDF:
      Page 1: Front card (business card size) — AI-generated design
      Page 2: Back card (business card size) — AI-generated design
      Page 3: Front print layout — US Letter (8 cards per page)
      Page 4: Front print layout — A4 (8 cards per page)
      Page 5: Back print layout — US Letter (8 cards per page)
      Page 6: Back print layout — A4 (8 cards per page)

    The card pages use Gemini-generated card images as backgrounds
    with invisible editable text fields overlaid, so the PDF looks
    identical to the hero image aesthetic while being fillable.

    Returns:
        {"success": bool, "pdf_path": str|None, "error": str|None}
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import Color

        out_dir = output_dir or EXPORT_DIR
        title = listing.get("title", "Template")
        safe_title = safe_filename(title)
        front_layout = _get_field_layout(product_type)
        back_layout = _get_back_layout(product_type)
        output_path = os.path.join(out_dir, f"{safe_title}_editable.pdf")

        # Generate card-only images via Gemini for PDF backgrounds
        front_img = None
        back_img = None
        if gemini_api_key:
            print("       Generating card designs for PDF...", flush=True)
            front_img, back_img = _generate_card_images(
                gemini_api_key, product_type,
                listing.get("focus_niche", "tattoo"),
                front_layout, back_layout, safe_title, out_dir,
            )

        c = canvas.Canvas(output_path)

        # Page 1: Front card — business card size with AI design
        _render_card_page(c, front_layout, "front", front_img)

        # Page 2: Back card — business card size with AI design
        c.showPage()
        _render_card_page(c, back_layout, "back", back_img)

        # Page 3: Front print layout — US Letter (8 cards per page)
        c.showPage()
        _render_print_sheet(c, front_img, front_layout,
                            LETTER_W, LETTER_H, "US Letter", "FRONT")

        # Page 4: Front print layout — A4 (8 cards per page)
        c.showPage()
        _render_print_sheet(c, front_img, front_layout,
                            A4_W, A4_H, "A4", "FRONT")

        # Page 5: Back print layout — US Letter (8 cards per page)
        c.showPage()
        _render_print_sheet(c, back_img, back_layout,
                            LETTER_W, LETTER_H, "US Letter", "BACK")

        # Page 6: Back print layout — A4 (8 cards per page)
        c.showPage()
        _render_print_sheet(c, back_img, back_layout,
                            A4_W, A4_H, "A4", "BACK")

        c.save()

        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) // 1024
            print(f"       Editable PDF: {os.path.basename(output_path)} "
                  f"({size_kb}KB, 6 pages)", flush=True)
            return {"success": True, "pdf_path": output_path, "error": None}

        return {"success": False, "pdf_path": None,
                "error": "PDF file not created"}

    except ImportError:
        return {"success": False, "pdf_path": None,
                "error": "reportlab not installed (pip install reportlab)"}
    except Exception as e:
        return {"success": False, "pdf_path": None,
                "error": f"{type(e).__name__}: {str(e)[:200]}"}


# ---- Back card field layouts ------------------------------------------------
BACK_LAYOUTS = {
    "appointment card": {
        "page_title": "Book Appointment",
        "fields": [
            {"name": "email", "label": "Email",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "phone", "label": "Phone",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "website", "label": "Website",
             "x": 0, "y": 0, "w": 0, "h": 0},
        ],
        "has_logo": True,
    },
    "gift certificate": {
        "page_title": "Gift Certificate",
        "fields": [
            {"name": "studio_name", "label": "Studio Name",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "phone", "label": "Phone",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "email", "label": "Email",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "website", "label": "Website",
             "x": 0, "y": 0, "w": 0, "h": 0},
        ],
    },
    "business card": {
        "page_title": "Contact Details",
        "fields": [
            {"name": "phone_back", "label": "Phone",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "email_back", "label": "Email",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "website_back", "label": "Website",
             "x": 0, "y": 0, "w": 0, "h": 0},
            {"name": "address_back", "label": "Address",
             "x": 0, "y": 0, "w": 0, "h": 0},
        ],
    },
}

_DEFAULT_BACK = {
    "page_title": "Contact Details",
    "fields": [
        {"name": "email_back", "label": "Email",
         "x": 0, "y": 0, "w": 0, "h": 0},
        {"name": "phone_back", "label": "Phone",
         "x": 0, "y": 0, "w": 0, "h": 0},
        {"name": "website_back", "label": "Website",
         "x": 0, "y": 0, "w": 0, "h": 0},
    ],
}

# ---- Business card dimensions in points (3.5" x 2") -------------------------
CARD_W = 252.0   # 3.5 inches * 72
CARD_H = 144.0   # 2.0 inches * 72


def _generate_card_images(api_key, product_type, niche,
                          front_layout, back_layout, safe_title, out_dir):
    """Generate front and back card images via Gemini for PDF backgrounds.

    These are clean card-only designs (no flat-lay, no props) that match
    the hero image card aesthetic — white card, script heading, ornamental
    divider, form fields with underlines.

    Returns (front_path, back_path) or (None, None) on failure.
    """
    from tools.gemini_image_client import generate_product_image

    niche_divider = {
        "tattoo": "fine-line tattoo-style ornamental divider (mandala, "
                  "dagger, or geometric dot-work)",
        "nail": "delicate floral swirl divider",
        "hair": "elegant scissors-and-comb line art divider",
        "barber": "classic straight razor line art divider",
        "beauty": "delicate rose and vine divider",
        "spa": "zen lotus flower line art divider",
    }
    divider = niche_divider.get(niche.lower(),
                                "elegant ornamental line divider")

    front_fields = "  ".join(
        f["label"].upper() + ": _______________"
        for f in front_layout["fields"]
    )

    back_fields = "  ".join(
        f["label"].upper() + ": _______________"
        for f in back_layout["fields"]
    )

    front_fields = ", ".join(
        f["label"].upper() for f in front_layout["fields"])
    back_fields = ", ".join(
        f["label"].upper() for f in back_layout["fields"])

    # --- Front card prompt ---
    front_prompt = (
        f"A single professional printed business card, viewed perfectly "
        f"straight-on (flat, no perspective, no angle, no shadow). "
        f"JUST the card on a pure white (#FFFFFF) background — nothing else. "
        f"Card design: clean WHITE card with a thin subtle double-line "
        f"grey border around the edge. "
        f"At the top centre: '{front_layout['page_title']}' in large, "
        f"elegant black script/calligraphy font (like Great Vibes). "
        f"Below the title: a {divider} centred on the card. "
        f"Below the divider, exactly {len(front_layout['fields'])} form "
        f"fields stacked vertically, left-aligned: "
        + " then ".join(
            f"'{f['label'].upper()}:' followed by a thin black horizontal line"
            for f in front_layout["fields"]
        )
        + f". ALL horizontal lines MUST be the same length and end at the "
        f"same right margin — perfectly aligned, creating a clean uniform "
        f"column. "
        f"This card must look IDENTICAL in style to the cards shown in "
        f"a premium Etsy flat-lay product photo — polished, professional, "
        f"print-ready. Clean sans-serif for field labels, elegant script "
        f"for the title. "
        f"Do NOT include any props, hands, shadows, background scene, or "
        f"mockup staging. Output the card ONLY. "
        f"High resolution, crisp sharp text, 300 DPI quality."
    )

    front_path = None
    result = generate_product_image(api_key, front_prompt,
                                    aspect_ratio="16:9", image_size="2K")
    if result["success"]:
        front_path = os.path.join(out_dir, f"{safe_title}_card_front.png")
        with open(front_path, "wb") as f:
            f.write(result["image_bytes"])
        print(f"       Card front saved ({len(result['image_bytes']) // 1024}KB)",
              flush=True)

    # --- Back card prompt ---
    has_logo = back_layout.get("has_logo", False)
    logo_instruction = (
        "In the top-right corner of the card, draw a small circle "
        "with the word 'LOGO' inside it (placeholder for the customer's "
        "logo). " if has_logo else ""
    )

    back_prompt = (
        f"A single professional printed business card, viewed perfectly "
        f"straight-on (flat, no perspective, no angle, no shadow). "
        f"JUST the card on a pure white (#FFFFFF) background — nothing else. "
        f"Card design: clean WHITE card with a thin subtle double-line "
        f"grey border around the edge — SAME style as the front card. "
        f"At the top centre: '{back_layout['page_title']}' in the SAME "
        f"large elegant black script/calligraphy font as the front card "
        f"(same size, same style — consistency is critical). "
        f"{logo_instruction}"
        f"Below the title: a {divider} centred on the card — SAME style "
        f"as the front card divider. "
        f"Below the divider, exactly {len(back_layout['fields'])} form "
        f"fields stacked vertically, left-aligned: "
        + " then ".join(
            f"'{f['label'].upper()}:' followed by a thin black horizontal line"
            for f in back_layout["fields"]
        )
        + f". ALL lines same length, same right margin — matching the front. "
        f"Below the fields, centred on the card, a small subtle "
        f"{niche}-themed line art icon (e.g. a fine-line rose, dagger, "
        f"or mandala — small and decorative, not overpowering). "
        f"Do NOT include any props, hands, shadows, background scene, or "
        f"mockup staging. Output the card ONLY. "
        f"High resolution, crisp sharp text, 300 DPI quality."
    )

    back_path = None
    result = generate_product_image(api_key, back_prompt,
                                    aspect_ratio="16:9", image_size="2K")
    if result["success"]:
        back_path = os.path.join(out_dir, f"{safe_title}_card_back.png")
        with open(back_path, "wb") as f:
            f.write(result["image_bytes"])
        print(f"       Card back saved ({len(result['image_bytes']) // 1024}KB)",
              flush=True)

    return front_path, back_path


def _get_back_layout(product_type):
    """Look up back card layout for a product type."""
    pt_lower = product_type.lower().strip()
    for key, layout in BACK_LAYOUTS.items():
        if key in pt_lower:
            return layout
    return _DEFAULT_BACK


def _render_card_page(canvas_obj, layout, suffix, card_image_path=None):
    """Render a single business-card-sized page.

    If a Gemini-generated card image is provided, it's used as the
    full-bleed background with invisible editable fields on top —
    giving the PDF the same polished aesthetic as the hero image.

    Falls back to basic ReportLab rendering if no image is available.
    """
    from reportlab.lib.colors import Color

    c = canvas_obj
    c.setPageSize((CARD_W, CARD_H))

    fields = layout["fields"]

    # Use Gemini card image as background if available
    if card_image_path and os.path.exists(card_image_path):
        c.drawImage(
            card_image_path, 0, 0,
            width=CARD_W, height=CARD_H,
            preserveAspectRatio=False,
        )

        # Overlay invisible editable fields positioned over the
        # form area (bottom portion of the card, below the divider).
        # Positions calibrated from Gemini card image analysis:
        #   Front lines at RL y: 65, 56, 46, 37 (spacing ~9.4pt)
        #   Back lines at RL y: 62, 53, 44 (spacing ~9pt)
        field_left = 55  # after the label text in the image
        line_right = CARD_W - 16
        field_start_y = CARD_H * 0.455  # ~65pt for front, ~62pt for back
        field_spacing = CARD_H * 0.065  # ~9.4pt between lines

        for i, field in enumerate(fields):
            fy = field_start_y - (i * field_spacing)
            if fy < 8:
                break

            field_name = f"{field['name']}_{suffix}"
            fw = line_right - field_left
            c.acroForm.textfield(
                name=field_name,
                tooltip=field["label"],
                x=field_left, y=fy - 2, width=fw, height=12,
                borderWidth=0,
                borderColor=Color(1, 1, 1, alpha=0),
                fillColor=Color(1, 1, 1, alpha=0),
                textColor=Color(0.1, 0.1, 0.1),
                fontSize=8,
                fontName="Helvetica",
            )
        return

    # Fallback: basic ReportLab rendering (no Gemini image)
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)

    c.setStrokeColor(Color(0.85, 0.85, 0.85))
    c.setLineWidth(0.5)
    c.rect(2, 2, CARD_W - 4, CARD_H - 4, fill=0, stroke=1)

    page_title = layout["page_title"]
    card_centre_x = CARD_W / 2

    title_y = CARD_H - 28
    c.setFont("Helvetica-BoldOblique", 14)
    c.setFillColor(Color(0.15, 0.15, 0.15))
    c.drawCentredString(card_centre_x, title_y, page_title)

    divider_y = title_y - 10
    c.setStrokeColor(Color(0.4, 0.4, 0.4))
    c.setLineWidth(0.5)
    c.line(card_centre_x - 40, divider_y, card_centre_x + 40, divider_y)

    field_left = 16
    line_right = CARD_W - 16
    field_start_y = divider_y - 22
    field_spacing = 20

    for i, field in enumerate(fields):
        fy = field_start_y - (i * field_spacing)
        if fy < 12:
            break

        label = field["label"].upper() + ":"
        label_w = c.stringWidth(label, "Helvetica-Bold", 7) + 4

        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawString(field_left, fy + 2, label)

        line_start = field_left + label_w
        c.setStrokeColor(Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.4)
        c.line(line_start, fy, line_right, fy)

        field_name = f"{field['name']}_{suffix}"
        fw = line_right - line_start
        c.acroForm.textfield(
            name=field_name,
            tooltip=field["label"],
            x=line_start, y=fy - 2, width=fw, height=12,
            borderWidth=0,
            borderColor=Color(1, 1, 1, alpha=0),
            fillColor=Color(1, 1, 1, alpha=0),
            textColor=Color(0.1, 0.1, 0.1),
            fontSize=8,
            fontName="Helvetica",
        )


def _render_page(canvas_obj, bg_image_path, layout, page_w, page_h, suffix):
    """Render one page of the editable PDF as a professional card template.

    The page shows a clean white card design matching the hero image
    aesthetic — script heading, ornamental divider, form fields with
    underlines. No background photo — this IS the product the customer
    fills in and prints.
    """
    from reportlab.lib.colors import Color

    c = canvas_obj
    c.setPageSize((page_w, page_h))

    # White page background
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    fields = layout["fields"]
    page_title = layout["page_title"]

    # Scale coordinates for Letter if needed (fields defined for A4)
    scale_x = page_w / A4_W
    scale_y = page_h / A4_H

    # --- Card area: centred rounded rectangle with thin border ---
    card_margin_x = 50 * scale_x
    card_margin_top = 120 * scale_y
    card_margin_bottom = 80 * scale_y
    card_x = card_margin_x
    card_y = card_margin_bottom
    card_w = page_w - (2 * card_margin_x)
    card_h = page_h - card_margin_top - card_margin_bottom

    # Card background (pure white with thin grey border)
    c.setFillColor(Color(1, 1, 1))
    c.setStrokeColor(Color(0.8, 0.8, 0.8))
    c.setLineWidth(1)
    c.roundRect(card_x, card_y, card_w, card_h, 8, fill=1, stroke=1)

    # --- Card title (script-style heading) ---
    card_centre_x = page_w / 2
    title_y = card_y + card_h - 60 * scale_y

    # Use Helvetica-BoldOblique as a stand-in for script fonts
    # (ReportLab core fonts — no custom font install needed)
    c.setFont("Helvetica-BoldOblique", 28)
    c.setFillColor(Color(0.15, 0.15, 0.15))
    c.drawCentredString(card_centre_x, title_y, page_title)

    # --- Ornamental divider line under title ---
    divider_y = title_y - 18
    div_half_w = 80 * scale_x
    c.setStrokeColor(Color(0.4, 0.4, 0.4))
    c.setLineWidth(0.75)
    c.line(card_centre_x - div_half_w, divider_y,
           card_centre_x + div_half_w, divider_y)

    # Small diamond in the centre of the divider
    d = 4
    c.setFillColor(Color(0.4, 0.4, 0.4))
    path = c.beginPath()
    path.moveTo(card_centre_x, divider_y + d)
    path.lineTo(card_centre_x + d, divider_y)
    path.lineTo(card_centre_x, divider_y - d)
    path.lineTo(card_centre_x - d, divider_y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    # --- Form fields ---
    field_start_y = divider_y - 50 * scale_y
    field_left = card_x + 40 * scale_x
    field_right = card_x + card_w - 40 * scale_x
    line_right = field_right  # all underlines end at the same point
    field_spacing = 40 * scale_y

    for i, field in enumerate(fields):
        fy = field_start_y - (i * field_spacing)

        if fy < card_y + 40:
            break  # don't overflow the card

        label = field["label"].upper() + ":"
        label_w = c.stringWidth(label, "Helvetica-Bold", 10) + 8

        # Label text
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawString(field_left, fy + 4, label)

        # Underline from after label to right edge (all aligned)
        line_start = field_left + label_w
        c.setStrokeColor(Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.5)
        c.line(line_start, fy, line_right, fy)

        # Unique field name per page size
        field_name = f"{field['name']}_{suffix}"

        # Invisible editable text field over the underline area
        fw = line_right - line_start
        c.acroForm.textfield(
            name=field_name,
            tooltip=field["label"],
            x=line_start, y=fy - 2, width=fw, height=18,
            borderWidth=0,
            borderColor=Color(1, 1, 1, alpha=0),
            fillColor=Color(1, 1, 1, alpha=0),
            textColor=Color(0.1, 0.1, 0.1),
            fontSize=11,
            fontName="Helvetica",
        )

    # --- Footer branding ---
    c.setFont("Helvetica", 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawCentredString(page_w / 2, 20,
                        "PurpleOcaz — Premium Digital Templates")

    # Size label in bottom-right
    size_label = "A4" if suffix == "a4" else "US Letter"
    c.drawRightString(page_w - 30, 20, size_label)


def _render_print_sheet(canvas_obj, bg_image_path, layout,
                        page_w, page_h, size_label, side="FRONT"):
    """Render a print layout sheet with 8 cards per page (2 columns x 4 rows).

    Each card is a placeholder rectangle with thin crop marks at the
    corners. The card mockup image is scaled and tiled into each slot.
    ``side`` is 'FRONT' or 'BACK' — shown in the page title.
    """
    from reportlab.lib.colors import Color

    c = canvas_obj
    c.setPageSize((page_w, page_h))

    # White background
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Page margins
    margin_x = 36  # 0.5 inch
    margin_top = 50
    margin_bottom = 60

    # Grid: 2 columns x 4 rows
    cols, rows = 2, 4
    gap = 8  # gap between cards

    usable_w = page_w - (2 * margin_x) - ((cols - 1) * gap)
    usable_h = page_h - margin_top - margin_bottom - ((rows - 1) * gap)

    card_w = usable_w / cols
    card_h = usable_h / rows

    # Standard business card aspect ratio is ~3.5:2 (1.75:1)
    # Constrain card_h to maintain reasonable proportions
    max_card_h = card_w / 1.6
    if card_h > max_card_h:
        card_h = max_card_h

    # Title at top
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(Color(0.1, 0.1, 0.1))
    c.drawCentredString(page_w / 2, page_h - 35,
                        f"PRINT AT HOME — 8 CARDS PER PAGE ({side} / {size_label})")

    # Draw 8 card slots
    crop_len = 8  # crop mark length in points

    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (card_w + gap)
            y = page_h - margin_top - (row + 1) * card_h - row * gap

            # Draw card outline (thin grey border)
            c.setStrokeColor(Color(0.75, 0.75, 0.75))
            c.setLineWidth(0.5)
            c.rect(x, y, card_w, card_h, fill=0, stroke=1)

            # Draw the card mockup image inside the slot if available
            if bg_image_path and os.path.exists(bg_image_path):
                try:
                    c.drawImage(
                        bg_image_path, x + 2, y + 2,
                        width=card_w - 4, height=card_h - 4,
                        preserveAspectRatio=True, anchor="c",
                    )
                except Exception:
                    pass  # Skip if image can't be drawn

            # Crop marks at corners (dark grey)
            c.setStrokeColor(Color(0.3, 0.3, 0.3))
            c.setLineWidth(0.25)

            # Top-left
            c.line(x - crop_len, y + card_h, x - 2, y + card_h)
            c.line(x, y + card_h + 2, x, y + card_h + crop_len)
            # Top-right
            c.line(x + card_w + 2, y + card_h, x + card_w + crop_len, y + card_h)
            c.line(x + card_w, y + card_h + 2, x + card_w, y + card_h + crop_len)
            # Bottom-left
            c.line(x - crop_len, y, x - 2, y)
            c.line(x, y - 2, x, y - crop_len)
            # Bottom-right
            c.line(x + card_w + 2, y, x + card_w + crop_len, y)
            c.line(x + card_w, y - 2, x + card_w, y - crop_len)

    # Footer
    c.setFont("Helvetica", 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawCentredString(page_w / 2, 20,
                        "PurpleOcaz — Premium Digital Templates")
    c.drawRightString(page_w - 30, 20, size_label)


def _get_field_layout(product_type):
    """Look up field layout for a product type.

    Falls back to a generic layout if no specific one exists.
    """
    pt_lower = product_type.lower().strip()
    for key, layout in FIELD_LAYOUTS.items():
        if key in pt_lower:
            return layout
    return _DEFAULT_LAYOUT
