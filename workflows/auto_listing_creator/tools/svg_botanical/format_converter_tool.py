# =============================================================================
# format_converter_tool.py
#
# BaseTool converting SVG files to PNG, DXF, PDF, and EPS formats.
#
# PNG  -> Playwright (SVG in HTML page, screenshot at 4096x4096)
# PDF  -> ReportLab (parse SVG paths, draw as vector PDF)
# DXF  -> ezdxf (SVG bezier paths to DXF SPLINE entities)
# EPS  -> Raw PostScript (SVG path commands map to PS commands)
# =============================================================================

import os
import re
import math
from typing import Any, Dict, List, Tuple

from lib.orchestrator.base_tool import BaseTool
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

PNG_SIZE = 4096
SVG_VIEWBOX = 1000  # Source SVG viewBox dimension


class FormatConverterTool(BaseTool):
    """Convert SVG botanical designs to PNG, DXF, PDF, and EPS."""

    def get_name(self) -> str:
        return "FormatConverterTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        svg_dir = kwargs.get("svg_dir", "")
        output_dir = kwargs.get("output_dir", "")
        formats = kwargs.get("formats", ["png", "dxf", "pdf", "eps"])
        if not svg_dir or not output_dir:
            return {
                "success": False, "data": None,
                "error": "svg_dir and output_dir are required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # Collect all SVG files
            svg_files = _collect_svg_files(svg_dir)
            if not svg_files:
                return {
                    "success": False, "data": None,
                    "error": f"No SVG files found in {svg_dir}",
                    "tool_name": self.get_name(), "metadata": {},
                }

            results = {"png": 0, "dxf": 0, "pdf": 0, "eps": 0}
            errors = []

            # PNG conversion (batch via Playwright)
            if "png" in formats:
                png_count, png_errors = _convert_all_png(
                    svg_files, output_dir)
                results["png"] = png_count
                errors.extend(png_errors)

            # DXF conversion
            if "dxf" in formats:
                dxf_count, dxf_errors = _convert_all_dxf(
                    svg_files, output_dir)
                results["dxf"] = dxf_count
                errors.extend(dxf_errors)

            # PDF conversion
            if "pdf" in formats:
                pdf_count, pdf_errors = _convert_all_pdf(
                    svg_files, output_dir)
                results["pdf"] = pdf_count
                errors.extend(pdf_errors)

            # EPS conversion
            if "eps" in formats:
                eps_count, eps_errors = _convert_all_eps(
                    svg_files, output_dir)
                results["eps"] = eps_count
                errors.extend(eps_errors)

            total_converted = sum(results.values())
            return {
                "success": total_converted > 0,
                "data": {
                    "output_dir": output_dir,
                    "conversions": results,
                    "total_converted": total_converted,
                    "error_count": len(errors),
                    "errors": errors[:20],  # Cap error list
                },
                "error": None if not errors else f"{len(errors)} conversion errors",
                "tool_name": self.get_name(),
                "metadata": {"svg_count": len(svg_files), **results},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }


# ── SVG File Collection ─────────────────────────────────────────────────────

def _collect_svg_files(svg_dir):
    """Collect all SVG files with their relative category paths."""
    files = []
    for root, _dirs, filenames in os.walk(svg_dir):
        for fn in filenames:
            if fn.lower().endswith(".svg"):
                full_path = os.path.join(root, fn)
                rel = os.path.relpath(full_path, svg_dir)
                files.append({"path": full_path, "rel": rel,
                              "name": fn[:-4]})
    return files


def _ensure_output_dir(output_dir, fmt, rel_path):
    """Ensure output directory exists for a format/category combo."""
    cat_dir = os.path.dirname(rel_path)
    out_dir = os.path.join(output_dir, fmt, cat_dir) if cat_dir else \
        os.path.join(output_dir, fmt)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


# ── PNG Conversion (Playwright) ──────────────────────────────────────────────

def _convert_all_png(svg_files, output_dir):
    """Convert all SVGs to PNG via Playwright."""
    count = 0
    errors = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return 0, [{"format": "png", "error": "playwright not installed"}]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": PNG_SIZE, "height": PNG_SIZE},
            device_scale_factor=1,
        )

        for sf in svg_files:
            try:
                out_dir = _ensure_output_dir(output_dir, "png", sf["rel"])
                out_path = os.path.join(out_dir, f"{sf['name']}.png")

                svg_content = _read_file(sf["path"])
                html = _png_html_template(svg_content)

                page.set_content(
                    html, wait_until="networkidle",
                    timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
                page.wait_for_timeout(500)
                page.screenshot(
                    path=out_path,
                    clip={"x": 0, "y": 0,
                          "width": PNG_SIZE, "height": PNG_SIZE},
                    omit_background=True,
                )
                count += 1
            except Exception as e:
                errors.append({
                    "format": "png", "name": sf["name"], "error": str(e)})

        page.close()
        browser.close()
    return count, errors


def _png_html_template(svg_content):
    """HTML wrapper for rendering SVG at PNG_SIZE with transparent bg."""
    return f"""<!DOCTYPE html>
<html><head><style>
html, body {{ margin:0; padding:0; width:{PNG_SIZE}px; height:{PNG_SIZE}px;
             background:transparent; overflow:hidden; }}
svg {{ width:{PNG_SIZE}px; height:{PNG_SIZE}px; }}
</style></head>
<body>{svg_content}</body></html>"""


# ── DXF Conversion (ezdxf) ──────────────────────────────────────────────────

def _convert_all_dxf(svg_files, output_dir):
    """Convert all SVGs to DXF format."""
    count = 0
    errors = []
    try:
        import ezdxf
    except ImportError:
        return 0, [{"format": "dxf", "error": "ezdxf not installed"}]

    for sf in svg_files:
        try:
            out_dir = _ensure_output_dir(output_dir, "dxf", sf["rel"])
            out_path = os.path.join(out_dir, f"{sf['name']}.dxf")

            svg_content = _read_file(sf["path"])
            paths = _extract_svg_paths(svg_content)

            doc = ezdxf.new("R2010")
            msp = doc.modelspace()

            for path_d in paths:
                segments = _parse_svg_path(path_d)
                _add_dxf_entities(msp, segments)

            doc.saveas(out_path)
            count += 1
        except Exception as e:
            errors.append({
                "format": "dxf", "name": sf["name"], "error": str(e)})

    return count, errors


def _add_dxf_entities(msp, segments):
    """Add parsed path segments as DXF entities."""
    for seg in segments:
        if seg["type"] == "line":
            msp.add_line(seg["start"], seg["end"])
        elif seg["type"] == "polyline" and len(seg["points"]) >= 2:
            msp.add_lwpolyline(seg["points"])
        elif seg["type"] == "spline" and len(seg["fit_points"]) >= 2:
            try:
                msp.add_spline(fit_points=seg["fit_points"])
            except Exception:
                # Fallback to polyline approximation
                if len(seg["fit_points"]) >= 2:
                    msp.add_lwpolyline(seg["fit_points"])


# ── PDF Conversion (ReportLab) ──────────────────────────────────────────────

def _convert_all_pdf(svg_files, output_dir):
    """Convert all SVGs to vector PDF format."""
    count = 0
    errors = []
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.units import inch
    except ImportError:
        return 0, [{"format": "pdf", "error": "reportlab not installed"}]

    # PDF page size: 8x8 inches (square, matching SVG aspect)
    page_w = 8 * inch
    page_h = 8 * inch
    scale = page_w / SVG_VIEWBOX

    for sf in svg_files:
        try:
            out_dir = _ensure_output_dir(output_dir, "pdf", sf["rel"])
            out_path = os.path.join(out_dir, f"{sf['name']}.pdf")

            svg_content = _read_file(sf["path"])
            paths = _extract_svg_paths(svg_content)

            c = rl_canvas.Canvas(out_path, pagesize=(page_w, page_h))
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(2 * scale)
            c.setLineCap(1)  # Round cap
            c.setLineJoin(1)  # Round join

            for path_d in paths:
                _draw_pdf_path(c, path_d, scale, page_h)

            c.save()
            count += 1
        except Exception as e:
            errors.append({
                "format": "pdf", "name": sf["name"], "error": str(e)})

    return count, errors


def _draw_pdf_path(c, path_d, scale, page_h):
    """Draw an SVG path string on a ReportLab canvas."""
    tokens = _tokenize_path(path_d)
    p = c.beginPath()
    cx, cy = 0.0, 0.0  # Current point

    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        i += 1

        if cmd == "M" and i + 1 < len(tokens):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            p.moveTo(cx * scale, page_h - cy * scale)
            i += 2
        elif cmd == "L" and i + 1 < len(tokens):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            p.lineTo(cx * scale, page_h - cy * scale)
            i += 2
        elif cmd == "C" and i + 5 < len(tokens):
            x1, y1 = float(tokens[i]), float(tokens[i + 1])
            x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
            cx, cy = float(tokens[i + 4]), float(tokens[i + 5])
            p.curveTo(
                x1 * scale, page_h - y1 * scale,
                x2 * scale, page_h - y2 * scale,
                cx * scale, page_h - cy * scale,
            )
            i += 6
        elif cmd == "Q" and i + 3 < len(tokens):
            # Quadratic -> cubic approximation
            qx, qy = float(tokens[i]), float(tokens[i + 1])
            ex, ey = float(tokens[i + 2]), float(tokens[i + 3])
            c1x = cx + (2 / 3) * (qx - cx)
            c1y = cy + (2 / 3) * (qy - cy)
            c2x = ex + (2 / 3) * (qx - ex)
            c2y = ey + (2 / 3) * (qy - ey)
            p.curveTo(
                c1x * scale, page_h - c1y * scale,
                c2x * scale, page_h - c2y * scale,
                ex * scale, page_h - ey * scale,
            )
            cx, cy = ex, ey
            i += 4
        elif cmd == "A" and i + 6 < len(tokens):
            # Arc: approximate with line to endpoint
            cx, cy = float(tokens[i + 5]), float(tokens[i + 6])
            p.lineTo(cx * scale, page_h - cy * scale)
            i += 7
        elif cmd == "Z":
            p.close()
        else:
            # Skip unknown tokens
            pass

    c.drawPath(p, stroke=1, fill=0)


# ── EPS Conversion (Raw PostScript) ─────────────────────────────────────────

def _convert_all_eps(svg_files, output_dir):
    """Convert all SVGs to EPS format."""
    count = 0
    errors = []
    # EPS page: 576x576 points (8 inches)
    page_size = 576
    scale = page_size / SVG_VIEWBOX

    for sf in svg_files:
        try:
            out_dir = _ensure_output_dir(output_dir, "eps", sf["rel"])
            out_path = os.path.join(out_dir, f"{sf['name']}.eps")

            svg_content = _read_file(sf["path"])
            paths = _extract_svg_paths(svg_content)

            eps_lines = [
                "%!PS-Adobe-3.0 EPSF-3.0",
                f"%%BoundingBox: 0 0 {page_size} {page_size}",
                f"%%Title: {sf['name']}",
                "%%Creator: PurpleOcaz Botanical Bundle Generator",
                "%%EndComments",
                f"{2 * scale:.4f} setlinewidth",
                "1 setlinecap",
                "1 setlinejoin",
                "0 0 0 setrgbcolor",
            ]

            for path_d in paths:
                eps_lines.extend(
                    _svg_path_to_ps(path_d, scale, page_size))

            eps_lines.append("%%EOF")
            _write_file(out_path, "\n".join(eps_lines))
            count += 1
        except Exception as e:
            errors.append({
                "format": "eps", "name": sf["name"], "error": str(e)})

    return count, errors


def _svg_path_to_ps(path_d, scale, page_h):
    """Convert SVG path to PostScript commands."""
    tokens = _tokenize_path(path_d)
    lines = ["newpath"]
    cx, cy = 0.0, 0.0

    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        i += 1

        if cmd == "M" and i + 1 < len(tokens):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            lines.append(
                f"{cx * scale:.2f} {page_h - cy * scale:.2f} moveto")
            i += 2
        elif cmd == "L" and i + 1 < len(tokens):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            lines.append(
                f"{cx * scale:.2f} {page_h - cy * scale:.2f} lineto")
            i += 2
        elif cmd == "C" and i + 5 < len(tokens):
            x1, y1 = float(tokens[i]), float(tokens[i + 1])
            x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
            cx, cy = float(tokens[i + 4]), float(tokens[i + 5])
            lines.append(
                f"{x1 * scale:.2f} {page_h - y1 * scale:.2f} "
                f"{x2 * scale:.2f} {page_h - y2 * scale:.2f} "
                f"{cx * scale:.2f} {page_h - cy * scale:.2f} curveto")
            i += 6
        elif cmd == "Q" and i + 3 < len(tokens):
            qx, qy = float(tokens[i]), float(tokens[i + 1])
            ex, ey = float(tokens[i + 2]), float(tokens[i + 3])
            c1x = cx + (2 / 3) * (qx - cx)
            c1y = cy + (2 / 3) * (qy - cy)
            c2x = ex + (2 / 3) * (qx - ex)
            c2y = ey + (2 / 3) * (qy - ey)
            lines.append(
                f"{c1x * scale:.2f} {page_h - c1y * scale:.2f} "
                f"{c2x * scale:.2f} {page_h - c2y * scale:.2f} "
                f"{ex * scale:.2f} {page_h - ey * scale:.2f} curveto")
            cx, cy = ex, ey
            i += 4
        elif cmd == "A" and i + 6 < len(tokens):
            cx, cy = float(tokens[i + 5]), float(tokens[i + 6])
            lines.append(
                f"{cx * scale:.2f} {page_h - cy * scale:.2f} lineto")
            i += 7
        elif cmd == "Z":
            lines.append("closepath")
        else:
            pass

    lines.append("stroke")
    return lines


# ── SVG Path Parsing Utilities ───────────────────────────────────────────────

def _read_file(path):
    """Read file contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_file(path, content):
    """Write content to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _extract_svg_paths(svg_content):
    """Extract all 'd' attributes from <path> elements."""
    return re.findall(r'd="([^"]+)"', svg_content)


def _tokenize_path(d):
    """Split SVG path 'd' attribute into command/number tokens."""
    # Insert spaces before letters (commands), then split
    spaced = re.sub(r'([MLCQAZmlcqaz])', r' \1 ', d)
    spaced = spaced.replace(",", " ")
    return [t for t in spaced.split() if t.strip()]


def _parse_svg_path(path_d):
    """Parse SVG path into segments for DXF conversion."""
    tokens = _tokenize_path(path_d)
    segments = []
    cx, cy = 0.0, 0.0
    i = 0

    while i < len(tokens):
        cmd = tokens[i]
        i += 1

        if cmd == "M" and i + 1 < len(tokens):
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            i += 2
        elif cmd == "L" and i + 1 < len(tokens):
            ex, ey = float(tokens[i]), float(tokens[i + 1])
            segments.append({
                "type": "line",
                "start": (cx, -cy),  # Flip Y for DXF
                "end": (ex, -ey),
            })
            cx, cy = ex, ey
            i += 2
        elif cmd == "C" and i + 5 < len(tokens):
            x1, y1 = float(tokens[i]), float(tokens[i + 1])
            x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
            ex, ey = float(tokens[i + 4]), float(tokens[i + 5])
            # Approximate cubic bezier with fit points
            points = _cubic_bezier_points(
                cx, cy, x1, y1, x2, y2, ex, ey, steps=8)
            segments.append({
                "type": "spline",
                "fit_points": [(p[0], -p[1]) for p in points],
            })
            cx, cy = ex, ey
            i += 6
        elif cmd == "Q" and i + 3 < len(tokens):
            qx, qy = float(tokens[i]), float(tokens[i + 1])
            ex, ey = float(tokens[i + 2]), float(tokens[i + 3])
            points = _quad_bezier_points(cx, cy, qx, qy, ex, ey, steps=6)
            segments.append({
                "type": "spline",
                "fit_points": [(p[0], -p[1]) for p in points],
            })
            cx, cy = ex, ey
            i += 4
        elif cmd == "A" and i + 6 < len(tokens):
            ex, ey = float(tokens[i + 5]), float(tokens[i + 6])
            segments.append({
                "type": "line",
                "start": (cx, -cy),
                "end": (ex, -ey),
            })
            cx, cy = ex, ey
            i += 7
        elif cmd == "Z":
            pass
        else:
            pass

    return segments


def _cubic_bezier_points(x0, y0, x1, y1, x2, y2, x3, y3, steps=8):
    """Sample points along a cubic bezier curve."""
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = (u ** 3 * x0 + 3 * u ** 2 * t * x1
             + 3 * u * t ** 2 * x2 + t ** 3 * x3)
        y = (u ** 3 * y0 + 3 * u ** 2 * t * y1
             + 3 * u * t ** 2 * y2 + t ** 3 * y3)
        points.append((x, y))
    return points


def _quad_bezier_points(x0, y0, x1, y1, x2, y2, steps=6):
    """Sample points along a quadratic bezier curve."""
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u ** 2 * x0 + 2 * u * t * x1 + t ** 2 * x2
        y = u ** 2 * y0 + 2 * u * t * y1 + t ** 2 * y2
        points.append((x, y))
    return points
