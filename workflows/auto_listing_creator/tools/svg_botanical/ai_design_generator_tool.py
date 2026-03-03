# =============================================================================
# ai_design_generator_tool.py
#
# BaseTool that generates fine-line botanical tattoo designs using AI,
# then vectorizes the PNG output to clean SVG using potrace (potracer).
#
# Provider: SVG_IMAGE_PROVIDER env var → "gemini" (default) or "replicate" (FLUX.1)
# Flow: AI prompt → PNG (black on white) → potrace → SVG (black on transparent)
# =============================================================================

import os
import tempfile
from typing import Any, Dict, List

import numpy as np
from PIL import Image

from lib.orchestrator.base_tool import BaseTool
from config import SVG_IMAGE_PROVIDER

# Image generation — provider selected via SVG_IMAGE_PROVIDER env var
if SVG_IMAGE_PROVIDER == "replicate":
    from workflows.auto_listing_creator.tools.replicate_image_client import (
        generate_product_image,
    )
else:
    from workflows.auto_listing_creator.tools.gemini_image_client import (
        generate_product_image,
    )

# ── Style prompt: the "artist DNA" that keeps all designs consistent ─────────

STYLE_PROMPT = (
    "A single fine-line botanical tattoo design on a PURE WHITE background. "
    "Style: minimalist fine-line tattoo art, exactly like hand-drawn ink "
    "illustrations by a professional tattoo artist. "
    "RULES (critical for consistency): "
    "- BLACK ink lines ONLY on pure white (#FFFFFF) background. "
    "- Consistent thin line weight throughout (like a 0.3mm fineliner pen). "
    "- NO fill, NO shading, NO gradients, NO gray tones, NO color. "
    "- NO watercolor effects, NO splatter, NO texture in the lines. "
    "- Clean, precise, continuous lines with natural organic flow. "
    "- The design should be CENTERED with generous margin on all sides. "
    "- NO text, NO words, NO letters, NO numbers anywhere in the image. "
    "- NO background elements, NO frame, NO border — just the design floating "
    "on white space. "
    "- The line art should be suitable for a real tattoo stencil. "
    "Output: a crisp, high-contrast black-on-white line drawing."
)


# ── Design prompts per category ──────────────────────────────────────────────

DESIGN_PROMPTS = {
    # ── Roses ──
    "Rose-Open-Bloom": "A fully open rose seen from above, with layered petals spiraling outward from a tight center.",
    "Rose-Side-View": "A single rose viewed from the side, showing the cup shape of overlapping petals with a short stem and two small leaves.",
    "Rose-Bud-Stem": "A closed rosebud on a gently curved stem with two serrated leaves.",
    "Rose-Single-Long-Stem": "An elegant single open rose on a long curved stem with three leaves at different heights.",
    "Rose-Pair-Intertwined": "Two roses on intertwined curving stems, one fully open and one partially open, with scattered leaves.",
    "Rose-Climbing-Vine": "A climbing rose vine with 4 small roses at different bloom stages along a wavy stem with leaves and tiny thorns.",
    "Rose-Open-Bloom-Detailed": "A large detailed open rose with many layered petals, visible spiral center, and delicate vein lines on each petal.",
    "Rose-With-Crescent": "A crescent moon shape with an open rose blooming at one end and small leaves trailing along the curve.",
    "Rose-Geometric-Frame": "A single open rose centered inside a thin diamond geometric frame with small leaf sprigs at two corners.",
    "Rose-Three-Stages": "Three roses in a row showing bud, half-open, and fully open bloom stages, connected by a single stem.",
    "Rose-And-Snake": "A rose with a thin snake winding gracefully around its stem, both rendered in fine line art.",
    "Rose-Bouquet-Small": "A small tied bouquet of three roses with mixed foliage, wrapped with a simple ribbon at the stems.",

    # ── Wildflowers ──
    "Daisy-Single-Stem": "A single daisy flower on a thin stem with two small leaves. Elongated petals radiating evenly around a dotted center.",
    "Poppy-Open": "An open poppy flower with 4-5 large delicate petals and a detailed seed pod center, on a curved stem.",
    "Lavender-Sprig": "A single lavender sprig with tiny buds arranged along the top third of a gently curved stem, two narrow leaves at base.",
    "Chamomile-Cluster": "Three chamomile flowers at different heights on branching stems, each with many thin petals around a round center.",
    "Sunflower-Single": "A single sunflower with a large detailed seed center (crosshatch pattern) and two rings of pointed petals, on a thick stem with two large leaves.",
    "Cosmos-Flower": "A cosmos flower with 8 broad petals and a small center, on a delicate thin stem with feathery divided leaves.",
    "Wildflower-Spray": "A loose spray of mixed wildflowers: one daisy, one poppy, two small buds, and assorted leaves on branching stems.",
    "Forget-Me-Not-Branch": "A branch of tiny 5-petal forget-me-not flowers clustered together with small oval leaves.",
    "Poppy-Seed-Pod": "A poppy in three stages on one stem: one open bloom, one wilting, and one mature seed pod.",
    "Dandelion-Wishflower": "A dandelion seed head (puffball) with some seeds floating away in the wind, on a single stem.",
    "Bluebell-Trio": "Three bluebell flowers hanging from an arching stem, each bell-shaped with curled petal tips.",
    "Anemone-Single": "A single anemone flower with 6 rounded petals and a dark detailed center of stamens, on a straight stem.",
    "Wildflower-Meadow-Strip": "A horizontal strip of mixed wildflowers growing from a ground line: daisies, poppies, lavender, grasses.",
    "Sweet-Pea-Vine": "Sweet pea flowers on a curling vine with tendrils, 3-4 ruffled butterfly-shaped blooms.",
    "Thistle-Single": "A Scottish thistle with spiky leaves and a detailed round flower head with fine protruding filaments.",
    "Peony-Open": "A lush open peony with many layered ruffled petals, seen from a slight angle, with two leaves.",
    "Lily-Single": "A single lily flower with 6 pointed recurved petals, visible stamens, and spotted petal details.",

    # ── Birth Flowers (12 months) ──
    "Birth-01-Carnation": "A single carnation flower with ruffled layered petals on a straight stem with two narrow leaves. January birth flower.",
    "Birth-02-Violet": "A small cluster of violet flowers with heart-shaped leaves. Simple 5-petal blooms. February birth flower.",
    "Birth-03-Daffodil": "A single daffodil with 6 pointed petals and a trumpet-shaped corona in the center, on a straight stem. March birth flower.",
    "Birth-04-Sweet-Pea": "Two sweet pea flowers on a curling vine with tendrils and oval leaves. April birth flower.",
    "Birth-05-Lily-of-Valley": "A lily of the valley stem with 7 tiny bell-shaped flowers hanging from one side of an arching stem, two large leaves. May birth flower.",
    "Birth-06-Rose": "A classic single open rose on a stem with thorns and serrated leaves. June birth flower.",
    "Birth-07-Larkspur": "A tall larkspur spike with many small flowers arranged along the upper stem, decreasing in size toward the tip. July birth flower.",
    "Birth-08-Gladiolus": "A gladiolus stem with trumpet-shaped flowers opening progressively from bottom to top. August birth flower.",
    "Birth-09-Aster": "A single aster flower with many thin ray petals radiating from a round center, on a stem with narrow leaves. September birth flower.",
    "Birth-10-Marigold": "A single marigold with dense layers of rounded petals forming a pompom shape, on a sturdy stem. October birth flower.",
    "Birth-11-Chrysanthemum": "A single chrysanthemum with many long thin curving petals radiating outward from center. November birth flower.",
    "Birth-12-Narcissus": "A narcissus (paperwhite) with 6 pointed petals and a small cup-shaped corona, on a straight stem. December birth flower.",

    # ── Botanical Stems ──
    "Eucalyptus-Branch": "A eucalyptus branch with round coin-shaped leaves alternating along a gently curved stem.",
    "Eucalyptus-Long": "A long trailing eucalyptus branch with many small round leaves, suitable for a spine or arm tattoo.",
    "Fern-Frond": "A single fern frond with many small leaflets (pinnae) arranged symmetrically along a central stem, curling slightly at the tip.",
    "Fern-Fiddle-Head": "An unfurling fern fiddlehead (spiral shape) with tiny emerging leaflets.",
    "Olive-Branch": "An olive branch with narrow elongated leaves and a few small round olives.",
    "Olive-Branch-Peace": "A curved olive branch forming a partial wreath shape, symbol of peace.",
    "Monstera-Leaf": "A single monstera deliciosa leaf with characteristic splits and holes, on a straight stem.",
    "Palm-Leaf-Fan": "A fan palm leaf with multiple narrow fronds radiating from a single point.",
    "Ivy-Trailing": "A trailing ivy vine with heart-shaped leaves at regular intervals along a wavy stem.",
    "Bamboo-Stem": "Two bamboo stems with segmented joints and small clusters of narrow leaves.",
    "Willow-Branch": "A weeping willow branch with long thin drooping leaves cascading downward.",
    "Ginkgo-Leaf": "Three ginkgo biloba leaves on thin stems, showing the distinctive fan shape with central notch.",

    # ── Mini / Tiny (25) ──
    "Mini-Rose": "A very small simple rose, just 5 petals around a spiral center. Tiny tattoo size.",
    "Mini-Daisy": "A tiny simple daisy with 8 petals and a dot center. Finger tattoo size.",
    "Mini-Leaf": "A single tiny leaf with a central vein line. Behind-the-ear tattoo size.",
    "Mini-Tulip": "A tiny tulip with 3 overlapping petals on a short stem.",
    "Mini-Lavender": "A tiny lavender sprig, just 5-6 small buds on a short stem.",
    "Mini-Sunflower": "A tiny sunflower with a round center and short pointed petals.",
    "Mini-Cherry-Blossom": "A tiny cherry blossom with 5 round petals and visible stamens.",
    "Mini-Fern-Curl": "A tiny curled fern tendril (spiral) with 2-3 small leaflets.",
    "Mini-Heart-Leaf": "Two tiny leaves arranged to form a heart shape.",
    "Mini-Crescent-Flower": "A tiny crescent moon with one small flower at the tip.",
    "Mini-Star-Flower": "A tiny 5-pointed star-shaped flower with a dot center.",
    "Mini-Berry-Sprig": "A tiny sprig with 3 round berries and 2 small leaves.",
    "Mini-Olive-Branch": "A tiny olive branch with 4 narrow leaves.",
    "Mini-Eucalyptus": "A tiny eucalyptus sprig with 4 round leaves.",
    "Mini-Wildflower": "A tiny simple 6-petal wildflower on a short stem.",
    "Mini-Lotus": "A tiny lotus flower seen from front, petals opening upward.",
    "Mini-Poppy": "A tiny poppy with 4 round petals and a dot center.",
    "Mini-Vine": "A tiny wavy vine with 3 small leaves.",
    "Mini-Cosmos": "A tiny cosmos flower with 8 petals.",
    "Mini-Peony-Bud": "A tiny closed peony bud with layered petals.",
    "Mini-Dandelion-Puff": "A tiny dandelion seed puff (circle of seeds).",
    "Mini-Butterfly-Flower": "A tiny flower that looks like a butterfly with wing-shaped petals.",
    "Mini-Sprig": "A tiny botanical sprig with alternating small leaves.",
    "Mini-Moon-Phase": "A tiny crescent moon with small dots (stars) and a leaf.",
    "Mini-Arrow-Floral": "A tiny arrow with a small flower wrapped around the shaft.",

    # ── Wreaths & Frames (12) ──
    "Wreath-Circle-Mixed": "A circular wreath made of mixed leaves (eucalyptus, olive) with 3-4 small flowers evenly spaced.",
    "Wreath-Circle-Eucalyptus": "A full circular wreath made entirely of eucalyptus branches with round leaves.",
    "Wreath-Berry-Vine": "A circular wreath of thin vine with scattered berries and small leaves.",
    "Wreath-Half-Top": "A half wreath (top arc only) of mixed flowers and leaves, open at the bottom.",
    "Wreath-Half-Crescent": "A crescent-shaped half wreath with flowers concentrated at one end trailing into leaves.",
    "Frame-Corner-Botanical": "An L-shaped corner frame of leaves and small flowers, suitable for framing text.",
    "Frame-Corner-Vine": "An L-shaped corner made of trailing vine with small leaves and tendrils.",
    "Frame-Oval-Floral": "An oval frame made of intertwined flowers and leaves.",
    "Wreath-Lavender-Circle": "A circular wreath made entirely of lavender sprigs.",
    "Wreath-Minimal-Circle": "A very minimal circular wreath of just a few simple leaves with lots of open space.",
    "Frame-Rectangle-Botanical": "A rectangular border frame of vine and small flowers along all four edges.",
    "Wreath-Heart-Shape": "A heart-shaped wreath made of small flowers, leaves, and berries.",

    # ── Bouquets (15) ──
    "Bouquet-Rose-Classic": "A classic bouquet of 3 open roses tied with a ribbon, with eucalyptus filler and small leaves.",
    "Bouquet-Wildflower-Mixed": "A loose wildflower bouquet with daisies, lavender, poppy, and mixed grasses tied together.",
    "Bouquet-Large-Mixed": "A large lush bouquet with 5-7 different flowers (rose, peony, daisy, wildflowers) and abundant greenery.",
    "Bouquet-Minimal-Three": "Three simple stems tied together: one flower, one bud, and one leaf branch.",
    "Bouquet-Peony-Rose": "A bouquet combining two peonies and one rose with eucalyptus and fern filler.",
    "Bouquet-Daisy-Field": "A hand-picked bouquet of 5 daisies with long stems wrapped in twine.",
    "Bouquet-Lavender-Bundle": "A bundle of lavender sprigs tied with a simple bow.",
    "Bouquet-Sunflower-Mix": "A bouquet centered on one large sunflower with smaller wildflowers and leaves around it.",
    "Bouquet-Bridal-Style": "An elegant cascading bridal bouquet with roses, peonies, and trailing ivy.",
    "Bouquet-Mason-Jar": "A small bouquet of wildflowers arranged in a mason jar.",
    "Bouquet-Hand-Held": "A bouquet viewed as if someone is presenting it (stems pointing down, flowers up), no hands visible.",
    "Bouquet-Dried-Flowers": "A bouquet of dried flowers: cotton stems, dried roses, wheat stalks, and lunaria seed pods.",
    "Bouquet-Tropical": "A tropical bouquet with a bird of paradise, monstera leaf, and palm fronds.",
    "Bouquet-Herb-Garden": "A kitchen herb bouquet: rosemary, thyme, sage, and basil sprigs tied together.",
    "Bouquet-Cosmos-Anemone": "A delicate bouquet of cosmos and anemone flowers with feathery foliage.",

    # ── Decorative (14) ──
    "Leaf-Detailed-Large": "A single large leaf with detailed vein pattern, showing every branching vein line.",
    "Leaf-Pair-Symmetrical": "A symmetrical pair of leaves on a short shared stem, like butterfly wings.",
    "Leaf-Skeleton": "A leaf skeleton showing only the vein network, no outer membrane — just the branching structure.",
    "Berry-Branch-Cluster": "A branch with 3 clusters of small round berries and narrow leaves between them.",
    "Berry-Holly": "A holly branch with spiky leaves and clusters of round berries.",
    "Vine-Trailing-Long": "A long trailing vine with leaves and curling tendrils, suitable for a wrist or ankle wrap.",
    "Vine-With-Flowers": "A decorative vine with small flowers blooming along its length and spiral tendrils.",
    "Branch-Bare-Winter": "A bare winter branch with no leaves, just elegant forking twigs.",
    "Branch-Cherry-Blossom": "A cherry blossom branch with clusters of 5-petal flowers and a few buds.",
    "Feather-Botanical": "A decorative feather shape made entirely of tiny leaves and flowers instead of barbs.",
    "Infinity-Floral": "An infinity symbol made of intertwined flowers and vines.",
    "Botanical-Compass": "A compass rose design where the cardinal points are decorated with different botanical elements.",
    "Hourglass-Floral": "An hourglass shape with flowers growing out of the top and roots/vines at the bottom.",
    "Botanical-Letter-A": "The letter A formed from intertwined botanical elements — vines, leaves, and small flowers.",
}


# ── potrace settings for clean fine-line vectorization ────────────────────────

POTRACE_SETTINGS = {
    "turdsize": 4,          # suppress speckles up to this size (was filter_speckle)
    "alphamax": 1.0,        # corner threshold (0 = sharp corners, 1.334 = smooth)
    "opticurve": True,       # optimize Bezier curves
    "opttolerance": 0.2,    # curve optimization tolerance
}

# Threshold for binarizing Gemini output (0-255).  Pixels darker than this → black.
# Lowered from 128 to 100 to capture lighter gray anti-aliased lines from Gemini,
# preserving fine-line detail that was previously clipped.
BINARY_THRESHOLD = 100

SVG_VIEWBOX = 1000  # Normalize all output to 1000×1000 viewBox


class AiDesignGeneratorTool(BaseTool):
    """Generate botanical tattoo designs via Gemini AI + potrace vectorization."""

    def get_name(self) -> str:
        return "AiDesignGeneratorTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        api_key = (kwargs.get("image_api_key", "")
                   or kwargs.get("gemini_api_key", ""))
        output_dir = kwargs.get("output_dir", "")
        design_names = kwargs.get("design_names", [])
        category_filter = kwargs.get("category_filter", None)

        if not api_key:
            return self._error(
                "image_api_key (or gemini_api_key) is required")
        if not output_dir:
            return self._error("output_dir is required")

        try:
            import potrace
        except ImportError:
            return self._error("potrace not installed: pip install potracer")

        # Determine which designs to generate
        if design_names:
            prompts = {n: DESIGN_PROMPTS[n] for n in design_names
                       if n in DESIGN_PROMPTS}
        elif category_filter:
            prompts = {n: p for n, p in DESIGN_PROMPTS.items()
                       if n.startswith(category_filter)}
        else:
            prompts = dict(DESIGN_PROMPTS)

        if not prompts:
            return self._error("No matching designs found")

        svg_dir = os.path.join(output_dir, "svg")
        png_raw_dir = os.path.join(output_dir, "_raw_png")
        os.makedirs(svg_dir, exist_ok=True)
        os.makedirs(png_raw_dir, exist_ok=True)

        generated = []
        errors = []

        for name, design_prompt in prompts.items():
            category = _get_category(name)
            cat_svg_dir = os.path.join(svg_dir, category)
            os.makedirs(cat_svg_dir, exist_ok=True)

            try:
                # Step 1: Generate PNG via Gemini
                full_prompt = f"{STYLE_PROMPT}\n\nDesign: {design_prompt}"
                result = generate_product_image(
                    api_key=api_key,
                    prompt=full_prompt,
                    aspect_ratio="1:1",
                    image_size="1K",
                    max_retries=2,
                )

                if not result["success"]:
                    errors.append({"name": name, "step": "gemini",
                                   "error": result["error"]})
                    print(f"     FAIL [{name}]: {result['error'][:80]}")
                    continue

                # Save raw PNG
                png_path = os.path.join(png_raw_dir, f"{name}.png")
                with open(png_path, "wb") as f:
                    f.write(result["image_bytes"])

                # Step 2: Vectorize PNG → SVG via potrace
                svg_path = os.path.join(cat_svg_dir, f"{name}.svg")
                _vectorize_png_to_svg(png_path, svg_path)

                generated.append({
                    "name": name, "category": category,
                    "svg_path": svg_path, "png_path": png_path,
                })
                print(f"     OK   [{name}]")

            except Exception as e:
                errors.append({"name": name, "step": "pipeline",
                               "error": str(e)})
                print(f"     FAIL [{name}]: {e}")

        category_counts = {}
        for g in generated:
            cat = g["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "success": len(generated) > 0,
            "data": {
                "svg_dir": svg_dir,
                "generated_count": len(generated),
                "error_count": len(errors),
                "generated": generated,
                "errors": errors,
                "category_counts": category_counts,
            },
            "error": None if not errors else f"{len(errors)} designs failed",
            "tool_name": self.get_name(),
            "metadata": {
                "total_requested": len(prompts),
                "generated": len(generated),
                "failed": len(errors),
            },
        }

    def _error(self, msg):
        return {
            "success": False, "data": None, "error": msg,
            "tool_name": self.get_name(), "metadata": {},
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_category(name):
    """Derive category folder name from design name."""
    if name.startswith("Rose-"):
        return "Roses"
    if name.startswith("Birth-"):
        return "Birth-Flowers"
    if name.startswith("Mini-"):
        return "Mini"
    if name.startswith("Wreath-") or name.startswith("Frame-"):
        return "Wreaths-and-Frames"
    if name.startswith("Bouquet-"):
        return "Bouquets"
    if name.startswith("Leaf-") or name.startswith("Berry-") or \
       name.startswith("Vine-") or name.startswith("Branch-") or \
       name.startswith("Feather-") or name.startswith("Infinity-") or \
       name.startswith("Botanical-") or name.startswith("Hourglass-"):
        return "Decorative"
    stem_prefixes = ("Eucalyptus-", "Fern-", "Olive-", "Monstera-",
                     "Palm-", "Ivy-", "Bamboo-", "Willow-", "Ginkgo-")
    for pfx in stem_prefixes:
        if name.startswith(pfx):
            return "Botanical-Stems"
    return "Wildflowers"


def _vectorize_png_to_svg(png_path, svg_path):
    """Convert a black-on-white PNG to a clean stroke-only SVG using potrace.

    Steps:
    1. Load PNG → grayscale → binary bitmap
    2. Trace contours with potrace (Bezier splines)
    3. Scale paths to 1000×1000 viewBox
    4. Write SVG with stroke-only styling (no fill)
    """
    import potrace
    from PIL import ImageEnhance, ImageFilter

    img = Image.open(png_path).convert("L")
    w, h = img.size

    # Pre-process: sharpen + boost contrast to preserve fine lines before binarization
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(1.5)

    # Binary bitmap: True = white (background), False = black (traced)
    arr = np.array(img)
    bitmap_data = arr >= BINARY_THRESHOLD

    bmp = potrace.Bitmap(bitmap_data)
    path = bmp.trace(**POTRACE_SETTINGS)

    # Scale factor to normalize to SVG_VIEWBOX × SVG_VIEWBOX
    sx = SVG_VIEWBOX / w
    sy = SVG_VIEWBOX / h

    svg_path_strings = []
    for curve in path.curves:
        parts = []
        sp = curve.start_point
        parts.append(f"M {sp.x * sx:.2f},{sp.y * sy:.2f}")

        for seg in curve.segments:
            ep = seg.end_point
            if seg.is_corner:
                c = seg.c
                parts.append(
                    f"L {c.x * sx:.2f},{c.y * sy:.2f} "
                    f"L {ep.x * sx:.2f},{ep.y * sy:.2f}"
                )
            else:
                c1, c2 = seg.c1, seg.c2
                parts.append(
                    f"C {c1.x * sx:.2f},{c1.y * sy:.2f} "
                    f"{c2.x * sx:.2f},{c2.y * sy:.2f} "
                    f"{ep.x * sx:.2f},{ep.y * sy:.2f}"
                )
        parts.append("Z")
        svg_path_strings.append(" ".join(parts))

    all_paths = "\n    ".join(
        f'<path d="{d}" fill="none" stroke="#000000" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        for d in svg_path_strings
    )

    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_VIEWBOX} {SVG_VIEWBOX}" '
        f'width="{SVG_VIEWBOX}px" height="{SVG_VIEWBOX}px">\n'
        f'    {all_paths}\n'
        f'</svg>\n'
    )

    # Optimize SVG: remove redundant nodes, clean up paths, reduce file size
    try:
        from scour.scour import scourString
        from scour.scour import parse_args as scour_parse_args
        scour_options = scour_parse_args(["--enable-id-stripping",
                                          "--remove-metadata",
                                          "--strip-xml-prolog"])
        svg_content = scourString(svg_content, options=scour_options)
    except ImportError:
        pass  # scour not installed, skip optimization

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
