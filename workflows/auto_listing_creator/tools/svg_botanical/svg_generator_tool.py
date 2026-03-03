# =============================================================================
# svg_generator_tool.py
#
# BaseTool that generates all SVG files from the botanical design registry.
# Each SVG: viewBox 0 0 1000 1000, stroke-width 2, stroke #000, fill none.
# =============================================================================

import math
import os
import re
import xml.etree.ElementTree as ET
import svgwrite
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool
from .botanical_categories import get_all_designs, get_category_counts

# SVG canvas settings
VIEWBOX_W, VIEWBOX_H = 1000, 1000
DEFAULT_STROKE = "#000000"
DEFAULT_STROKE_W = 2

# Padding ratio for auto-cropped viewBox (fraction of design size)
VIEWBOX_PADDING = 0.12


# ── Affine matrix helpers ([a, b, c, d, tx, ty]) ────────────────────────────

def _mat_identity():
    return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def _mat_multiply(a, b):
    return [
        a[0]*b[0] + a[2]*b[1],  a[1]*b[0] + a[3]*b[1],
        a[0]*b[2] + a[2]*b[3],  a[1]*b[2] + a[3]*b[3],
        a[0]*b[4] + a[2]*b[5] + a[4],
        a[1]*b[4] + a[3]*b[5] + a[5],
    ]


def _mat_apply(m, x, y):
    return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])


def _parse_transform(s):
    """Parse an SVG transform attribute into an affine matrix."""
    if not s:
        return _mat_identity()
    mat = _mat_identity()
    for m in re.finditer(r'(\w+)\(([^)]+)\)', s):
        kind = m.group(1)
        args = [float(v) for v in re.findall(r'[-+]?\d*\.?\d+', m.group(2))]
        if kind == 'translate':
            tx = args[0] if args else 0
            ty = args[1] if len(args) > 1 else 0
            mat = _mat_multiply(mat, [1, 0, 0, 1, tx, ty])
        elif kind == 'rotate' and args:
            a = math.radians(args[0])
            c, s_ = math.cos(a), math.sin(a)
            if len(args) == 3:
                cx, cy = args[1], args[2]
                mat = _mat_multiply(mat, [1, 0, 0, 1, cx, cy])
                mat = _mat_multiply(mat, [c, s_, -s_, c, 0, 0])
                mat = _mat_multiply(mat, [1, 0, 0, 1, -cx, -cy])
            else:
                mat = _mat_multiply(mat, [c, s_, -s_, c, 0, 0])
        elif kind == 'scale':
            sx = args[0] if args else 1
            sy = args[1] if len(args) > 1 else sx
            mat = _mat_multiply(mat, [sx, 0, 0, sy, 0, 0])
    return mat


# ── Auto-crop viewBox ────────────────────────────────────────────────────────

def _auto_crop_viewbox(svg_path):
    """Rewrite the SVG file's viewBox to tightly fit the drawing content.

    Uses XML parsing to walk the element tree, accumulating transform
    matrices (translate, rotate, scale) so that path coordinates are
    mapped to their actual rendered positions before computing the
    bounding box.
    """
    with open(svg_path, "r") as f:
        content = f.read()

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return

    all_x, all_y = [], []

    def _walk(elem, parent_mat):
        t = elem.get('transform', '')
        mat = _mat_multiply(parent_mat, _parse_transform(t))

        d = elem.get('d', '')
        if d:
            nums = re.findall(r'[-+]?\d*\.?\d+', d)
            for i in range(0, len(nums) - 1, 2):
                try:
                    lx, ly = float(nums[i]), float(nums[i + 1])
                    gx, gy = _mat_apply(mat, lx, ly)
                    all_x.append(gx)
                    all_y.append(gy)
                except (ValueError, IndexError):
                    pass

        for child in elem:
            _walk(child, mat)

    _walk(root, _mat_identity())

    if not all_x or not all_y:
        return  # nothing to crop

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    w = max_x - min_x
    h = max_y - min_y

    if w < 1 or h < 1:
        return

    pad = max(w, h) * VIEWBOX_PADDING
    vb_x = min_x - pad
    vb_y = min_y - pad
    vb_w = w + 2 * pad
    vb_h = h + 2 * pad

    # Replace viewBox
    content = re.sub(
        r'viewBox="[^"]*"',
        f'viewBox="{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}"',
        content,
    )
    # Keep size at 1000px for consistency
    content = re.sub(r'width="\d+px"', 'width="1000px"', content)
    content = re.sub(r'height="\d+px"', 'height="1000px"', content)

    with open(svg_path, "w") as f:
        f.write(content)


class SvgGeneratorTool(BaseTool):
    """Generate fine-line botanical SVG files from the design registry."""

    def get_name(self) -> str:
        return "SvgGeneratorTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        output_dir = kwargs.get("output_dir", "")
        if not output_dir:
            return {
                "success": False, "data": None,
                "error": "output_dir is required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            svg_dir = os.path.join(output_dir, "svg")
            designs = get_all_designs()
            generated = []
            errors = []

            # Create category subdirectories
            categories_seen = set()
            for design in designs:
                cat = design["category"]
                if cat not in categories_seen:
                    os.makedirs(os.path.join(svg_dir, cat), exist_ok=True)
                    categories_seen.add(cat)

            for design in designs:
                name = design["name"]
                category = design["category"]
                fn = design["fn"]
                extra = dict(design.get("extra_kwargs", {}))

                try:
                    svg_path = os.path.join(
                        svg_dir, category, f"{name}.svg")
                    dwg = svgwrite.Drawing(
                        svg_path,
                        size=("1000px", "1000px"),
                        viewBox=f"0 0 {VIEWBOX_W} {VIEWBOX_H}",
                    )
                    # Transparent background (no rect)
                    fn(dwg, cx=VIEWBOX_W // 2, cy=VIEWBOX_H // 2, **extra)
                    dwg.save()
                    _auto_crop_viewbox(svg_path)
                    generated.append({
                        "name": name,
                        "category": category,
                        "path": svg_path,
                    })
                except Exception as e:
                    errors.append({"name": name, "error": str(e)})

            return {
                "success": len(generated) > 0,
                "data": {
                    "svg_dir": svg_dir,
                    "generated_count": len(generated),
                    "error_count": len(errors),
                    "generated": generated,
                    "errors": errors,
                    "category_counts": get_category_counts(),
                },
                "error": None if not errors else f"{len(errors)} designs failed",
                "tool_name": self.get_name(),
                "metadata": {
                    "total_designs": len(designs),
                    "generated": len(generated),
                    "failed": len(errors),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }
