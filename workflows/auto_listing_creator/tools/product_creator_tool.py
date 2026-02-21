# =============================================================================
# workflows/auto_listing_creator/tools/product_creator_tool.py
#
# Phase 3: Programmatic product creation using templates + Playwright.
#
# Architecture:
#   1. Claude generates JSON content spec for each product
#   2. Python renders the content into pre-built HTML templates
#   3. Playwright captures each page as 2250x3000 PNG
#
# This approach is reliable because:
#   - HTML templates are pre-tested and guaranteed to fill the full canvas
#   - Claude focuses on content creation (what it's best at)
#   - Consistent professional output every time
# =============================================================================

import json
import time
import os
import sys
import html as html_module

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
EXPORT_DIR = os.path.join(_workflow, "exports")

PAGE_WIDTH = 2250
PAGE_HEIGHT = 3000
PAGES_PER_PRODUCT = 5

# Colour palettes for the 4 template variants
PALETTES = {
    "clean": {
        "bg": "#FAFAFA", "card_bg": "#FFFFFF", "accent": "#6B2189",
        "text": "#2D2D2D", "muted": "#888888", "border": "#E0D4E8",
        "header_bg": "#F5F0F8", "highlight": "#6B2189",
    },
    "bold": {
        "bg": "#1A1A2E", "card_bg": "#16213E", "accent": "#9B59B6",
        "text": "#FFFFFF", "muted": "#B0B0C0", "border": "#6B2189",
        "header_bg": "#0F3460", "highlight": "#E94560",
    },
    "vintage": {
        "bg": "#FDF5E6", "card_bg": "#FFFEF9", "accent": "#6B2189",
        "text": "#3C2415", "muted": "#8B7355", "border": "#C4A77D",
        "header_bg": "#F0E6D3", "highlight": "#8B4513",
    },
    "creative": {
        "bg": "#F8F0FF", "card_bg": "#FFFFFF", "accent": "#6B2189",
        "text": "#2D1B4E", "muted": "#7B6B8A", "border": "#D4B8E8",
        "header_bg": "linear-gradient(135deg, #F0E0FF 0%, #E8D0F0 50%, #F5E8FF 100%)",
        "highlight": "#9B59B6",
    },
}

VARIANT_NAMES = {2: "clean", 3: "bold", 4: "vintage", 5: "creative"}
VARIANT_LABELS = {
    2: "Clean & Minimal",
    3: "Bold & Modern",
    4: "Vintage & Classic",
    5: "Creative & Artistic",
}


class ProductCreatorTool(BaseTool):
    """Create digital product images using templates + Playwright rendering."""

    def execute(self, **kwargs) -> dict:
        listings      = kwargs.get("generated_listings", [])
        api_key       = kwargs.get("anthropic_api_key", "")
        model         = kwargs.get("model", "claude-sonnet-4-20250514")
        focus_niche   = kwargs.get("focus_niche", "tattoo")

        if not api_key:
            return {
                "success": False, "data": None,
                "error": "anthropic_api_key required",
                "tool_name": self.get_name(), "metadata": {},
            }
        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to create products for",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            from playwright.sync_api import sync_playwright

            os.makedirs(EXPORT_DIR, exist_ok=True)

            all_exports = []
            image_map = {}

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)

                for i, listing in enumerate(listings):
                    title = listing.get("title", "Untitled")[:60]
                    product_type = listing.get("product_type", "template")
                    print(f"     Creating product {i+1}/{len(listings)}: "
                          f"{title}...", flush=True)

                    # Step 1: Get content spec from Claude (single API call)
                    print(f"       Generating content spec...", flush=True)
                    try:
                        content_spec = self._generate_content_spec(
                            api_key, model, listing, focus_niche,
                        )
                    except Exception as spec_err:
                        print(f"       Content spec FAILED: {str(spec_err)[:80]}",
                              flush=True)
                        all_exports.append({
                            "listing_index": i, "title": title,
                            "product_type": product_type, "png_paths": [],
                            "page_count": 0, "status": "FAILED",
                        })
                        continue

                    # Step 2: Render all 5 pages from templates
                    png_paths = []

                    for page_num in range(1, PAGES_PER_PRODUCT + 1):
                        try:
                            if page_num == 1:
                                page_html = self._render_hero_template(
                                    listing, content_spec, focus_niche,
                                )
                            else:
                                variant = VARIANT_NAMES.get(page_num, "clean")
                                page_html = self._render_page_template(
                                    listing, content_spec, focus_niche,
                                    page_num, variant,
                                )

                            png_path = self._html_to_png(
                                browser, page_html, title, page_num,
                            )
                            png_paths.append(png_path)
                            size_kb = os.path.getsize(png_path) // 1024
                            print(f"       Page {page_num}/{PAGES_PER_PRODUCT}: "
                                  f"{os.path.basename(png_path)} ({size_kb}KB)",
                                  flush=True)

                        except Exception as page_err:
                            print(f"       Page {page_num} FAILED: "
                                  f"{str(page_err)[:80]}", flush=True)

                    export_result = {
                        "listing_index": i, "title": title,
                        "product_type": product_type,
                        "png_paths": png_paths,
                        "page_count": len(png_paths),
                        "status": "CREATED" if png_paths else "FAILED",
                    }
                    all_exports.append(export_result)

                    if png_paths:
                        image_map[i] = png_paths

                    print(f"       {len(png_paths)}/{PAGES_PER_PRODUCT} pages created",
                          flush=True)

                    if i < len(listings) - 1:
                        time.sleep(1)

                browser.close()

            created_count = sum(1 for e in all_exports if e["status"] == "CREATED")

            return {
                "success": True,
                "data": {
                    "exports": all_exports,
                    "image_map": image_map,
                    "created_count": created_count,
                    "total_listings": len(listings),
                    "export_dir": EXPORT_DIR,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"created": created_count, "total": len(listings)},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # =========================================================================
    # Claude content generation (JSON only — no HTML)
    # =========================================================================

    def _generate_content_spec(self, api_key, model, listing, focus_niche):
        """Ask Claude to generate content for all 5 pages as structured JSON."""
        import urllib.request

        title = listing.get("title", "")
        product_type = listing.get("product_type", "template")
        tags = listing.get("tags", [])

        prompt = f"""You are creating content for a digital product template bundle sold on Etsy by "PurpleOcaz" in the {focus_niche} industry.

PRODUCT: {title}
TYPE: {product_type}
KEYWORDS: {', '.join(tags[:8])}

Generate the content for a 5-page template bundle. Return ONLY valid JSON with this exact structure:

{{
  "hero": {{
    "headline": "Main product headline (short, impactful, max 40 chars)",
    "subheadline": "Professional subtitle (max 60 chars)",
    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
    "preview_labels": ["Preview 1 label", "Preview 2 label", "Preview 3 label", "Preview 4 label"]
  }},
  "template": {{
    "document_title": "Title shown on each template page (e.g., 'Tattoo Aftercare Guide')",
    "subtitle": "Subtitle for the template (e.g., 'Professional Care Instructions')",
    "sections": [
      {{
        "heading": "Section 1 heading",
        "items": ["Item/instruction 1", "Item/instruction 2", "Item/instruction 3", "Item/instruction 4"]
      }},
      {{
        "heading": "Section 2 heading",
        "items": ["Item 1", "Item 2", "Item 3", "Item 4"]
      }},
      {{
        "heading": "Section 3 heading",
        "items": ["Item 1", "Item 2", "Item 3"]
      }}
    ],
    "footer_note": "A professional closing note or disclaimer (1-2 sentences)",
    "fields": ["Field 1 label", "Field 2 label", "Field 3 label"]
  }}
}}

IMPORTANT:
- Content must be specific to a {product_type} for the {focus_niche} industry
- Each section should have 3-4 real, useful items (not placeholder text)
- Items should be actual instructions/content a {focus_niche} business would use
- Keep all text professional and industry-appropriate
- Return ONLY the JSON — no markdown, no explanations"""

        payload = json.dumps({
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(ANTHROPIC_API_URL, data=payload, method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("anthropic-version", "2023-06-01")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        content = data.get("content", [])
        for block in content:
            if block.get("type") == "text":
                text = block["text"].strip()
                # Extract JSON
                if text.startswith("```"):
                    lines = text.split("\n")
                    text = "\n".join(lines[1:])
                    if text.rstrip().endswith("```"):
                        text = text.rstrip()[:-3]
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])

        raise RuntimeError("Failed to parse content spec from Claude")

    # =========================================================================
    # HTML template rendering
    # =========================================================================

    def _render_hero_template(self, listing, spec, niche):
        """Render the hero/overview page (Page 1) from template."""
        hero = spec.get("hero", {})
        headline = _esc(hero.get("headline", listing.get("title", "Template Bundle")[:40]))
        subheadline = _esc(hero.get("subheadline", "Professional Digital Templates"))
        features = hero.get("features", ["Editable", "Print Ready", "Instant Download", "Commercial Use"])
        previews = hero.get("preview_labels", ["Design 1", "Design 2", "Design 3", "Design 4"])
        product_type = _esc(listing.get("product_type", "Template"))
        title_full = _esc(listing.get("title", ""))

        features_html = "".join(
            f'<div class="feature">✦ {_esc(f)}</div>' for f in features[:4]
        )
        previews_html = "".join(
            f'''<div class="preview-card">
                <div class="preview-inner">
                    <div class="preview-lines">
                        <div class="line w80"></div>
                        <div class="line w60"></div>
                        <div class="line w90"></div>
                        <div class="line w40"></div>
                        <div class="line w70"></div>
                    </div>
                    <div class="preview-label">{_esc(p)}</div>
                </div>
            </div>''' for p in previews[:4]
        )

        return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;600;700&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{PAGE_WIDTH}px; height:{PAGE_HEIGHT}px; overflow:hidden; }}
body {{
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(180deg, #0D0015 0%, #1A0030 30%, #12001E 70%, #0D0015 100%);
    color: #FFFFFF;
    display: grid;
    grid-template-rows: 120px 100px 650px 180px 900px 120px 500px 330px;
    padding: 0 100px;
}}
.top-bar {{
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 40px;
}}
.badge {{
    background: #6B2189; color: white; padding: 12px 28px;
    border-radius: 6px; font-size: 24px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
}}
.badge-outline {{
    border: 2px solid #6B2189; color: #C8A0E0; padding: 12px 28px;
    border-radius: 6px; font-size: 22px; letter-spacing: 1px;
}}
.type-label {{
    text-align: center; padding-top: 30px;
    font-size: 28px; letter-spacing: 8px; text-transform: uppercase;
    color: #9B6FBF;
}}
.title-section {{
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center;
}}
.title-section h1 {{
    font-family: 'Playfair Display', serif; font-size: 96px;
    font-weight: 900; line-height: 1.1; margin-bottom: 20px;
}}
.title-section h1 span {{ color: #B06FE0; }}
.title-section p {{
    font-size: 32px; color: #A890B8; font-weight: 300;
    letter-spacing: 2px;
}}
.divider {{
    display: flex; align-items: center; justify-content: center;
    gap: 20px; padding: 30px 0;
}}
.divider-line {{ width: 200px; height: 1px; background: #6B2189; }}
.divider-dot {{ color: #6B2189; font-size: 24px; }}
.previews {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 40px; padding: 20px 60px;
}}
.preview-card {{
    background: rgba(107,33,137,0.15); border: 2px solid rgba(107,33,137,0.4);
    border-radius: 16px; padding: 30px; display: flex;
    flex-direction: column; justify-content: space-between;
}}
.preview-inner {{ flex: 1; display: flex; flex-direction: column; justify-content: space-between; }}
.preview-lines {{ display: flex; flex-direction: column; gap: 16px; padding: 20px 0; }}
.line {{
    height: 10px; background: rgba(200,160,224,0.2); border-radius: 5px;
}}
.w80 {{ width: 80%; }} .w60 {{ width: 60%; }} .w90 {{ width: 90%; }}
.w40 {{ width: 40%; }} .w70 {{ width: 70%; }}
.preview-label {{
    font-size: 22px; color: #C8A0E0; text-align: center;
    padding-top: 15px; letter-spacing: 1px;
}}
.features {{
    display: flex; justify-content: center; gap: 60px;
    align-items: center; flex-wrap: wrap;
}}
.feature {{
    font-size: 26px; color: #D4B8E8; letter-spacing: 1px;
}}
.cta-section {{
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; gap: 30px; text-align: center;
}}
.cta-box {{
    background: linear-gradient(135deg, #6B2189, #9B59B6);
    padding: 30px 80px; border-radius: 12px;
    font-size: 32px; font-weight: 700; letter-spacing: 3px;
}}
.cta-sub {{ font-size: 26px; color: #A890B8; }}
.footer {{
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; gap: 15px; border-top: 1px solid rgba(107,33,137,0.3);
}}
.footer-brand {{
    font-family: 'Playfair Display', serif; font-size: 36px;
    color: #6B2189; letter-spacing: 4px;
}}
.footer-sub {{ font-size: 20px; color: #666; letter-spacing: 2px; }}
.corner {{ position:fixed; color: rgba(107,33,137,0.15); font-size: 80px; }}
.corner-tl {{ top:20px; left:30px; }} .corner-tr {{ top:20px; right:30px; }}
.corner-bl {{ bottom:20px; left:30px; }} .corner-br {{ bottom:20px; right:30px; }}
</style></head><body>
<div class="corner corner-tl">◆</div>
<div class="corner corner-tr">◆</div>
<div class="corner corner-bl">◆</div>
<div class="corner corner-br">◆</div>

<div class="top-bar">
    <div class="badge">✦ PurpleOcaz</div>
    <div class="badge">INSTANT DOWNLOAD</div>
    <div class="badge-outline">Editable in Canva</div>
</div>

<div class="type-label">✦ {niche.upper()} STUDIO COLLECTION ✦</div>

<div class="title-section">
    <h1>{headline.split()[0] if headline.split() else ""}<br>
    <span>{"&nbsp;".join(headline.split()[1:3]) if len(headline.split()) > 1 else ""}</span><br>
    {"&nbsp;".join(headline.split()[3:]) if len(headline.split()) > 3 else "Template Bundle"}</h1>
    <p>{subheadline}</p>
</div>

<div class="divider">
    <div class="divider-line"></div>
    <div class="divider-dot">◆ ✦ ◆</div>
    <div class="divider-line"></div>
</div>

<div class="previews">{previews_html}</div>

<div class="features">{features_html}</div>

<div class="cta-section">
    <div class="cta-box">✦ {PAGES_PER_PRODUCT} TEMPLATE DESIGNS INCLUDED ✦</div>
    <div class="cta-sub">Professional {product_type} Bundle • Print Ready • Fully Editable</div>
    <div class="divider">
        <div class="divider-line"></div>
        <div class="divider-dot">◈</div>
        <div class="divider-line"></div>
    </div>
</div>

<div class="footer">
    <div class="footer-brand">PurpleOcaz</div>
    <div class="footer-sub">PREMIUM DIGITAL TEMPLATES FOR {niche.upper()} PROFESSIONALS</div>
</div>
</body></html>'''

    def _render_page_template(self, listing, spec, niche, page_num, variant):
        """Render a template page (Pages 2-5) from template + palette."""
        pal = PALETTES.get(variant, PALETTES["clean"])
        tmpl = spec.get("template", {})

        doc_title = _esc(tmpl.get("document_title", listing.get("product_type", "Template")))
        subtitle = _esc(tmpl.get("subtitle", "Professional Template"))
        sections = tmpl.get("sections", [])
        footer_note = _esc(tmpl.get("footer_note", "Thank you for your business."))
        fields = tmpl.get("fields", ["Name", "Date", "Signature"])
        variant_label = VARIANT_LABELS.get(page_num, "Template")

        # Build sections HTML
        sections_html = ""
        for sec in sections[:3]:
            heading = _esc(sec.get("heading", "Section"))
            items = sec.get("items", [])
            items_html = "".join(
                f'<div class="item"><span class="bullet">◆</span> {_esc(item)}</div>'
                for item in items[:5]
            )
            sections_html += f'''
            <div class="section">
                <div class="section-heading">{heading}</div>
                <div class="section-items">{items_html}</div>
            </div>'''

        # Build fields HTML
        fields_html = "".join(
            f'''<div class="field">
                <div class="field-label">{_esc(f)}</div>
                <div class="field-line"></div>
            </div>''' for f in fields[:4]
        )

        # Determine if background is gradient or solid
        header_bg = pal["header_bg"]
        if "gradient" in header_bg:
            header_bg_css = f"background: {header_bg};"
        else:
            header_bg_css = f"background-color: {header_bg};"

        return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;600;700&family=Cormorant+Garamond:wght@400;600;700&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{PAGE_WIDTH}px; height:{PAGE_HEIGHT}px; overflow:hidden; }}
body {{
    font-family: 'Montserrat', sans-serif;
    background-color: {pal["bg"]};
    color: {pal["text"]};
    display: grid;
    grid-template-rows: 500px 80px 300px 60px 1200px 60px 400px 60px 340px;
}}
.header {{
    {header_bg_css}
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; padding: 40px 100px;
    border-bottom: 4px solid {pal["accent"]};
}}
.studio-name {{
    font-size: 28px; letter-spacing: 8px; text-transform: uppercase;
    color: {pal["muted"]}; margin-bottom: 15px;
}}
.doc-title {{
    font-family: 'Playfair Display', serif; font-size: 80px;
    font-weight: 700; color: {pal["text"]}; line-height: 1.15;
    margin-bottom: 15px;
}}
.doc-title span {{ color: {pal["accent"]}; }}
.doc-subtitle {{
    font-size: 30px; color: {pal["muted"]}; letter-spacing: 3px;
    font-weight: 300;
}}
.accent-bar {{
    background-color: {pal["accent"]}; display: flex;
    align-items: center; justify-content: center;
    color: white; font-size: 24px; letter-spacing: 6px;
    text-transform: uppercase; font-weight: 600;
}}
.intro-section {{
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; padding: 30px 120px;
}}
.intro-icon {{ font-size: 60px; color: {pal["accent"]}; margin-bottom: 15px; }}
.intro-text {{
    font-size: 28px; color: {pal["muted"]}; line-height: 1.6;
    max-width: 1800px;
}}
.divider {{
    display: flex; align-items: center; justify-content: center;
    gap: 20px;
}}
.divider-line {{ width: 300px; height: 1px; background: {pal["border"]}; }}
.divider-dot {{ color: {pal["accent"]}; font-size: 18px; }}
.sections {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
    gap: 40px; padding: 20px 100px; align-content: start;
}}
.section {{
    background: {pal["card_bg"]}; border: 2px solid {pal["border"]};
    border-radius: 16px; padding: 40px;
}}
.section-heading {{
    font-family: 'Playfair Display', serif; font-size: 36px;
    font-weight: 700; color: {pal["accent"]}; margin-bottom: 25px;
    padding-bottom: 15px; border-bottom: 2px solid {pal["border"]};
}}
.section-items {{ display: flex; flex-direction: column; gap: 18px; }}
.item {{
    font-size: 26px; line-height: 1.5; display: flex; gap: 15px;
    align-items: flex-start;
}}
.bullet {{ color: {pal["accent"]}; font-size: 16px; margin-top: 6px; flex-shrink: 0; }}
.fields-section {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 30px 60px; padding: 20px 100px; align-content: center;
}}
.field {{ display: flex; flex-direction: column; gap: 8px; }}
.field-label {{
    font-size: 22px; color: {pal["muted"]}; letter-spacing: 2px;
    text-transform: uppercase;
}}
.field-line {{
    height: 2px; background: {pal["border"]}; border-radius: 1px;
}}
.footer-note {{
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; padding: 20px 120px; gap: 20px;
}}
.footer-text {{
    font-size: 24px; color: {pal["muted"]}; font-style: italic;
    max-width: 1600px; line-height: 1.5;
}}
.footer-brand {{
    display: flex; gap: 30px; align-items: center; color: {pal["muted"]};
    font-size: 20px; letter-spacing: 3px;
}}
.footer-brand span {{ color: {pal["accent"]}; }}
.variant-tag {{
    position: fixed; bottom: 30px; right: 40px;
    font-size: 18px; color: {pal["muted"]}; letter-spacing: 2px;
    opacity: 0.6;
}}
.page-border {{
    position: fixed; top: 15px; left: 15px; right: 15px; bottom: 15px;
    border: 2px solid {pal["border"]}; pointer-events: none; border-radius: 8px;
}}
</style></head><body>
<div class="page-border"></div>

<div class="header">
    <div class="studio-name">✦ [ Your Studio Name ] ✦</div>
    <div class="doc-title">{doc_title.split()[0] if doc_title.split() else ""}<br>
    <span>{"&nbsp;".join(doc_title.split()[1:]) if len(doc_title.split()) > 1 else ""}</span></div>
    <div class="doc-subtitle">{subtitle}</div>
</div>

<div class="accent-bar">✦&nbsp;&nbsp;&nbsp;{niche.upper()} PROFESSIONAL TEMPLATE&nbsp;&nbsp;&nbsp;✦</div>

<div class="intro-section">
    <div class="intro-icon">◈</div>
    <div class="intro-text">{footer_note}</div>
</div>

<div class="divider">
    <div class="divider-line"></div>
    <div class="divider-dot">◆ ✦ ◆</div>
    <div class="divider-line"></div>
</div>

<div class="sections">{sections_html}</div>

<div class="divider">
    <div class="divider-line"></div>
    <div class="divider-dot">◈</div>
    <div class="divider-line"></div>
</div>

<div class="fields-section">{fields_html}</div>

<div class="divider">
    <div class="divider-line"></div>
    <div class="divider-dot">✦</div>
    <div class="divider-line"></div>
</div>

<div class="footer-note">
    <div class="footer-text">[ Your Studio Address ] &nbsp;•&nbsp; [ Phone Number ] &nbsp;•&nbsp; [ Email Address ]</div>
    <div class="footer-brand">
        <span>◆</span> PurpleOcaz Template <span>◆</span>
        {variant_label} Edition
        <span>◆</span> Template {page_num} of {PAGES_PER_PRODUCT} <span>◆</span>
    </div>
</div>

<div class="variant-tag">{variant_label} • Template {page_num}</div>
</body></html>'''

    # =========================================================================
    # Playwright rendering
    # =========================================================================

    def _html_to_png(self, browser, html_content, title, page_num):
        """Render HTML to a PNG file using Playwright."""
        page = browser.new_page(
            viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT},
            device_scale_factor=1,
        )
        page.set_content(html_content, wait_until="networkidle")
        page.wait_for_timeout(2000)

        safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title)
        safe_title = safe_title.strip()[:50]
        filename = f"{safe_title}_page{page_num}.png"
        filepath = os.path.join(EXPORT_DIR, filename)

        page.screenshot(
            path=filepath,
            clip={"x": 0, "y": 0, "width": PAGE_WIDTH, "height": PAGE_HEIGHT},
        )
        page.close()
        return filepath


def _esc(text):
    """HTML-escape text for safe template insertion."""
    return html_module.escape(str(text)) if text else ""
