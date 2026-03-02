# =============================================================================
# svg_generator_tool.py
#
# BaseTool that generates all SVG files from the botanical design registry.
# Each SVG: viewBox 0 0 1000 1000, stroke-width 2, stroke #000, fill none.
# =============================================================================

import os
import svgwrite
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool
from .botanical_categories import get_all_designs, get_category_counts

# SVG canvas settings
VIEWBOX_W, VIEWBOX_H = 1000, 1000
DEFAULT_STROKE = "#000000"
DEFAULT_STROKE_W = 2


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
