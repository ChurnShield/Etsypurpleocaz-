# =============================================================================
# bundle_packager_tool.py
#
# BaseTool that packages all converted files into a ZIP bundle for Etsy.
# Includes LICENSE.txt, README.txt, and Getting Started guide PDF.
# =============================================================================

import os
import zipfile
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool

BUNDLE_NAME = "PurpleOcaz-Fine-Line-Botanical-Bundle"

LICENSE_TEXT = """LICENSE — Personal & Commercial Use

Thank you for purchasing from PurpleOcaz!

WHAT YOU CAN DO:
- Use designs for personal tattoos, stickers, prints, and crafts
- Use in commercial products (t-shirts, mugs, tote bags, stickers, etc.)
- Use with cutting machines (Cricut, Silhouette, etc.)
- Resize and modify designs for your projects
- Use in unlimited personal and commercial projects

WHAT YOU CANNOT DO:
- Resell or redistribute the original digital files
- Share files with others (each user needs their own license)
- Claim the designs as your own original artwork
- Use in print-on-demand as-is without modification

For questions: purpleocaz@gmail.com

(c) PurpleOcaz. All rights reserved.
"""

README_TEXT = """FINE-LINE BOTANICAL TATTOO BUNDLE
by PurpleOcaz

Thank you for your purchase!

WHAT'S INCLUDED:
- {design_count} unique fine-line botanical tattoo designs
- Each design in 5 formats: SVG, PNG, DXF, PDF, EPS

FORMATS:
- SVG: Scalable vector, works with Cricut/Silhouette and design software
- PNG: 4096x4096 transparent background, high resolution
- DXF: Compatible with AutoCAD and cutting machines
- PDF: Vector format, perfect for printing at any size
- EPS: Professional vector format for design software

CATEGORIES:
{category_list}

HOW TO USE:
1. Choose your design from the categorized folders
2. Pick the format that works for your project
3. Import into your design software or cutting machine

TIPS:
- SVG is best for cutting machines (Cricut, Silhouette)
- PNG is best for digital use, social media, and web
- PDF is best for printing
- DXF is best for CAD software and laser cutters
- EPS is best for professional design software (Illustrator)

NEED HELP?
Email: purpleocaz@gmail.com

Enjoy your designs!
- The PurpleOcaz Team
"""


class BundlePackagerTool(BaseTool):
    """Package botanical designs into a ZIP bundle for Etsy."""

    def get_name(self) -> str:
        return "BundlePackagerTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        output_dir = kwargs.get("output_dir", "")
        design_count = kwargs.get("design_count", 0)
        category_counts = kwargs.get("category_counts", {})

        if not output_dir:
            return {
                "success": False, "data": None,
                "error": "output_dir is required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            zip_path = os.path.join(output_dir, f"{BUNDLE_NAME}.zip")
            formats = ["svg", "png", "dxf", "pdf", "eps"]
            files_added = 0

            with zipfile.ZipFile(zip_path, "w",
                                 zipfile.ZIP_DEFLATED) as zf:
                # Add format directories
                for fmt in formats:
                    fmt_dir = os.path.join(output_dir, fmt)
                    if not os.path.isdir(fmt_dir):
                        continue
                    for root, _dirs, filenames in os.walk(fmt_dir):
                        for fn in filenames:
                            full = os.path.join(root, fn)
                            rel = os.path.relpath(full, output_dir)
                            arc = os.path.join(
                                BUNDLE_NAME,
                                rel.replace("\\", "/").upper()
                                if fmt != "svg" else rel.replace("\\", "/"),
                            )
                            # Normalize: keep SVG paths as-is, upper format dirs
                            arc = os.path.join(
                                BUNDLE_NAME, rel.replace("\\", "/"))
                            zf.write(full, arc)
                            files_added += 1

                # Add LICENSE.txt
                zf.writestr(
                    f"{BUNDLE_NAME}/LICENSE.txt", LICENSE_TEXT.strip())
                files_added += 1

                # Add README.txt
                cat_list = "\n".join(
                    f"- {cat}: {cnt} designs"
                    for cat, cnt in sorted(category_counts.items())
                )
                readme = README_TEXT.format(
                    design_count=design_count,
                    category_list=cat_list,
                )
                zf.writestr(
                    f"{BUNDLE_NAME}/README.txt", readme.strip())
                files_added += 1

                # Add Getting Started guide PDF
                guide_path = _generate_guide_pdf(output_dir, design_count)
                if guide_path and os.path.exists(guide_path):
                    zf.write(
                        guide_path,
                        f"{BUNDLE_NAME}/Getting-Started-Guide.pdf")
                    files_added += 1

            zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)

            return {
                "success": True,
                "data": {
                    "zip_path": zip_path,
                    "zip_size_mb": round(zip_size_mb, 2),
                    "files_added": files_added,
                    "bundle_name": BUNDLE_NAME,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"files_added": files_added,
                              "zip_size_mb": round(zip_size_mb, 2)},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }


def _generate_guide_pdf(output_dir, design_count):
    """Generate a Getting Started guide PDF using ReportLab."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import Color
        from reportlab.lib.units import inch
    except ImportError:
        return None

    guide_path = os.path.join(output_dir, "Getting-Started-Guide.pdf")
    W, H = 595.27, 841.89  # A4

    PURPLE = Color(0.420, 0.243, 0.620)
    DARK = Color(0.05, 0.05, 0.05)
    WHITE = Color(1, 1, 1)
    LIGHT_GRAY = Color(0.96, 0.96, 0.96)

    c = canvas.Canvas(guide_path, pagesize=(W, H))

    # ── Page 1: Welcome ──
    # Purple header
    c.setFillColor(PURPLE)
    c.rect(0, H - 120, W, 120, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H - 60, "Fine-Line Botanical Tattoo Bundle")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H - 90, "Getting Started Guide")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 108, f"{design_count} Designs | 5 Formats | Personal & Commercial Use")

    # Thank you section
    y = H - 170
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Thank You!")
    y -= 30
    c.setFont("Helvetica", 11)
    for line in [
        "Thank you for purchasing the Fine-Line Botanical Tattoo Bundle",
        "from PurpleOcaz! This guide will help you get the most out of",
        "your new designs.",
    ]:
        c.drawString(50, y, line)
        y -= 18

    # What's included
    y -= 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "What's Included")
    y -= 8
    c.setFillColor(PURPLE)
    c.rect(50, y, 100, 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    y -= 25

    items = [
        f"{design_count} unique fine-line botanical designs",
        "Each design in SVG, PNG, DXF, PDF, and EPS formats",
        "Personal and commercial use license",
        "This Getting Started guide",
    ]
    c.setFont("Helvetica", 11)
    for item in items:
        c.drawString(70, y, f"\u2022  {item}")
        y -= 20

    # Format guide
    y -= 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Format Guide")
    y -= 8
    c.setFillColor(PURPLE)
    c.rect(50, y, 100, 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    y -= 25

    format_info = [
        ("SVG", "Scalable vector graphics. Best for Cricut, Silhouette,",
         "and design software like Adobe Illustrator."),
        ("PNG", "High-res 4096x4096 transparent images. Best for",
         "digital use, social media, and web projects."),
        ("DXF", "AutoCAD-compatible format. Best for laser cutters,",
         "CNC machines, and CAD software."),
        ("PDF", "Vector PDF files. Best for printing at any size",
         "without losing quality."),
        ("EPS", "Encapsulated PostScript. Best for professional",
         "design software and print shops."),
    ]
    c.setFont("Helvetica", 10)
    for name, desc1, desc2 in format_info:
        # Card background
        c.setFillColor(LIGHT_GRAY)
        c.roundRect(50, y - 8, W - 100, 48, 5, fill=1, stroke=0)
        c.setFillColor(PURPLE)
        c.rect(50, y - 8, 4, 48, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(65, y + 26, name)
        c.setFont("Helvetica", 10)
        c.drawString(65, y + 12, desc1)
        c.drawString(65, y, desc2)
        y -= 58

    # Footer
    c.setFillColor(PURPLE)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, 30, "PurpleOcaz  |  purpleocaz@gmail.com")

    # ── Page 2: Tips & Support ──
    c.showPage()
    c.setFillColor(PURPLE)
    c.rect(0, H - 80, W, 80, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 50, "Tips & Support")

    y = H - 130
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Using with Cutting Machines")
    y -= 8
    c.setFillColor(PURPLE)
    c.rect(50, y, 100, 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    y -= 25

    steps = [
        "Open Cricut Design Space or Silhouette Studio",
        "Upload the SVG file for your chosen design",
        "Resize to your desired dimensions",
        "Select your material and follow cutting instructions",
    ]
    c.setFont("Helvetica", 11)
    for idx, step in enumerate(steps, 1):
        # Numbered circle
        c.setFillColor(PURPLE)
        c.circle(65, y + 4, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(65, y, str(idx))
        c.setFillColor(DARK)
        c.setFont("Helvetica", 11)
        c.drawString(85, y, step)
        y -= 28

    # Tattoo stencil section
    y -= 15
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Creating Tattoo Stencils")
    y -= 8
    c.setFillColor(PURPLE)
    c.rect(50, y, 100, 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    y -= 25

    stencil_steps = [
        "Print the PNG or PDF at desired size on stencil paper",
        "You can also use a thermal copier with the design",
        "Apply to clean, dry skin using standard stencil methods",
        "Fine-line designs work best with thin liner needles (3RL-7RL)",
    ]
    c.setFont("Helvetica", 11)
    for idx, step in enumerate(stencil_steps, 1):
        c.setFillColor(PURPLE)
        c.circle(65, y + 4, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(65, y, str(idx))
        c.setFillColor(DARK)
        c.setFont("Helvetica", 11)
        c.drawString(85, y, step)
        y -= 28

    # Support section
    y -= 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Need Help?")
    y -= 8
    c.setFillColor(PURPLE)
    c.rect(50, y, 100, 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    y -= 25

    c.setFont("Helvetica", 11)
    for line in [
        "Email us: purpleocaz@gmail.com",
        "Visit our Etsy shop for more designs",
        "",
        "If you love your designs, we'd really appreciate a",
        "5-star review on Etsy! It helps us create more",
        "amazing designs for you.",
    ]:
        c.drawString(50, y, line)
        y -= 18

    # Review CTA box
    y -= 10
    c.setFillColor(PURPLE)
    c.roundRect(50, y - 10, W - 100, 45, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, y + 14, "Leave a Review on Etsy!")
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, y, "Your feedback means the world to us")

    # Footer
    c.setFillColor(PURPLE)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, 30, "PurpleOcaz  |  purpleocaz@gmail.com")

    c.save()
    return guide_path
