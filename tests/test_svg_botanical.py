# =============================================================================
# tests/test_svg_botanical.py
#
# Tests for the fine-line botanical SVG/PNG bundle pipeline.
# =============================================================================

import os
import sys
import tempfile
import shutil

import pytest

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)

from workflows.auto_listing_creator.tools.svg_botanical import (
    botanical_primitives as bp,
    botanical_compositions as comp,
    botanical_categories as cats,
)
from workflows.auto_listing_creator.tools.svg_botanical.svg_generator_tool import (
    SvgGeneratorTool,
)
from workflows.auto_listing_creator.tools.svg_botanical.format_converter_tool import (
    FormatConverterTool,
    _extract_svg_paths,
    _tokenize_path,
    _parse_svg_path,
    _cubic_bezier_points,
    _quad_bezier_points,
)
from workflows.auto_listing_creator.tools.svg_botanical.bundle_packager_tool import (
    BundlePackagerTool,
)


# ── Primitives ───────────────────────────────────────────────────────────────

class TestBotanicalPrimitives:
    """Tests for low-level SVG path primitives."""

    def test_petal_teardrop_returns_valid_path(self):
        d = bp.petal_teardrop(length=40, width=15)
        assert d.startswith("M ")
        assert "C " in d

    def test_petal_round_returns_closed_path(self):
        d = bp.petal_round(radius=20)
        assert d.startswith("M ")
        assert d.count("C ") == 4  # Circle approximation has 4 curves

    def test_petal_elongated_returns_path(self):
        d = bp.petal_elongated(length=50, width=12)
        assert "M " in d
        assert "C " in d

    def test_petal_pointed_returns_path(self):
        d = bp.petal_pointed(length=45, width=18)
        assert "M " in d
        assert "L " in d

    def test_petal_tulip_returns_path(self):
        d = bp.petal_tulip(length=40, width=22)
        assert "M " in d
        assert "C " in d

    def test_leaf_simple_returns_outline_and_vein(self):
        outline, vein = bp.leaf_simple(length=60, width=20)
        assert "M " in outline
        assert "C " in outline
        assert vein.startswith("M ")
        assert "L " in vein

    def test_leaf_round_returns_outline_and_vein(self):
        outline, vein = bp.leaf_round(length=35, width=25)
        assert "M " in outline
        assert "M " in vein

    def test_leaf_fern_segment_returns_path(self):
        d = bp.leaf_fern_segment(length=25, width=8)
        assert "M " in d

    def test_leaf_monstera_returns_three_parts(self):
        outline, holes, vein = bp.leaf_monstera(radius=80)
        assert "M " in outline
        assert "M " in holes  # At least one hole
        assert "M " in vein

    def test_leaf_palm_returns_fronds(self):
        fronds = bp.leaf_palm(length=120, fronds=7)
        assert len(fronds) == 7
        for f in fronds:
            assert "M " in f
            assert "Q " in f

    def test_leaf_olive_returns_path(self):
        d = bp.leaf_olive(length=30, width=8)
        assert "M " in d

    def test_stem_straight_returns_line(self):
        d = bp.stem_straight(length=200)
        assert d.startswith("M ")
        assert "L " in d

    def test_stem_curved_returns_curve(self):
        d = bp.stem_curved(length=200, curve=40)
        assert "C " in d

    def test_stem_branch_returns_paths(self):
        paths = bp.stem_branch(length=180, branch_count=3)
        assert len(paths) == 4  # main + 3 branches
        assert all("M " in p for p in paths)

    def test_stem_vine_returns_wavy_path(self):
        d = bp.stem_vine(length=250, waves=4, amplitude=30)
        assert "Q " in d

    def test_center_circle_returns_path(self):
        d = bp.center_circle(radius=8)
        assert d.count("C ") == 4

    def test_center_dots_returns_path(self):
        d = bp.center_dots(count=5, spread=10)
        assert d.count("M ") == 5

    def test_center_spiral_returns_path(self):
        d = bp.center_spiral(turns=2.5, max_radius=12)
        assert "M " in d
        assert "L " in d

    def test_berry_cluster_returns_path(self):
        d = bp.berry_cluster(count=5, spread=15)
        assert d.count("M ") == 5

    def test_vine_tendril_returns_path(self):
        d = bp.vine_tendril(length=40, coils=1.5)
        assert "M " in d

    def test_thorn_returns_path(self):
        d = bp.thorn(size=8)
        assert "M " in d
        assert "L " in d

    def test_leaf_vein_lines_returns_list(self):
        veins = bp.leaf_vein_lines(length=50, vein_count=4)
        assert len(veins) == 9  # 1 center + 4*2 sides

    def test_stamen_returns_line_and_head(self):
        line, head = bp.stamen(length=30, head_radius=3)
        assert "M " in line
        assert "M " in head

    def test_arrange_radial_correct_count(self):
        items = bp.arrange_radial("M 0,0", count=5, radius=50)
        assert len(items) == 5

    def test_arrange_along_stem_returns_items(self):
        items = bp.arrange_along_stem("M 0,0", stem_length=200, count=5)
        assert len(items) > 0


# ── Categories ───────────────────────────────────────────────────────────────

class TestBotanicalCategories:
    """Tests for the design registry."""

    def test_registry_has_designs(self):
        designs = cats.get_all_designs()
        assert len(designs) >= 120

    def test_all_categories_present(self):
        counts = cats.get_category_counts()
        for cat in cats.ALL_CATEGORIES:
            assert cat in counts, f"Missing category: {cat}"
            assert counts[cat] > 0

    def test_registry_entries_have_required_fields(self):
        for d in cats.get_all_designs():
            assert "name" in d
            assert "category" in d
            assert "fn" in d
            assert callable(d["fn"])
            assert "description" in d

    def test_category_counts_match_total(self):
        counts = cats.get_category_counts()
        total = sum(counts.values())
        assert total == cats.get_design_count()

    def test_design_names_unique(self):
        names = [d["name"] for d in cats.get_all_designs()]
        assert len(names) == len(set(names)), "Duplicate design names found"

    def test_roses_category_count(self):
        roses = cats.get_designs_by_category(cats.CAT_ROSES)
        assert len(roses) == 12

    def test_birth_flowers_category_count(self):
        birth = cats.get_designs_by_category(cats.CAT_BIRTH)
        assert len(birth) == 12

    def test_mini_category_count(self):
        mini = cats.get_designs_by_category(cats.CAT_MINI)
        assert len(mini) == 25


# ── SVG Generator Tool ──────────────────────────────────────────────────────

class TestSvgGeneratorTool:
    """Tests for SVG generation BaseTool."""

    def test_returns_standard_dict(self):
        tool = SvgGeneratorTool()
        result = tool.execute()  # No output_dir -> error
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert "tool_name" in result
        assert "metadata" in result

    def test_get_name(self):
        assert SvgGeneratorTool().get_name() == "SvgGeneratorTool"

    def test_missing_output_dir_returns_error(self):
        result = SvgGeneratorTool().execute()
        assert result["success"] is False
        assert "output_dir" in result["error"]

    def test_generates_svg_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = SvgGeneratorTool().execute(output_dir=tmpdir)
            assert result["success"] is True
            data = result["data"]
            assert data["generated_count"] >= 120
            # Verify actual SVG files exist
            svg_dir = data["svg_dir"]
            svg_count = 0
            for root, _dirs, files in os.walk(svg_dir):
                svg_count += sum(1 for f in files if f.endswith(".svg"))
            assert svg_count == data["generated_count"]

    def test_svg_files_have_correct_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = SvgGeneratorTool().execute(output_dir=tmpdir)
            first_svg = result["data"]["generated"][0]["path"]
            with open(first_svg, "r", encoding="utf-8") as f:
                content = f.read()
            assert 'viewBox="0 0 1000 1000"' in content
            assert "<path" in content
            assert 'stroke="#000000"' in content


# ── Format Converter Utilities ───────────────────────────────────────────────

class TestFormatConverterUtils:
    """Tests for SVG path parsing utilities."""

    def test_extract_svg_paths(self):
        svg = '<path d="M 0,0 L 10,10"/><path d="M 5,5 C 1,2 3,4 5,6"/>'
        paths = _extract_svg_paths(svg)
        assert len(paths) == 2
        assert paths[0] == "M 0,0 L 10,10"

    def test_tokenize_path(self):
        tokens = _tokenize_path("M 0,0 L 10,10 Z")
        assert "M" in tokens
        assert "L" in tokens
        assert "Z" in tokens

    def test_cubic_bezier_points_count(self):
        points = _cubic_bezier_points(0, 0, 1, 2, 3, 4, 5, 6, steps=8)
        assert len(points) == 9  # steps + 1

    def test_cubic_bezier_endpoints(self):
        points = _cubic_bezier_points(0, 0, 1, 1, 2, 2, 3, 3, steps=10)
        assert points[0] == (0, 0)
        assert abs(points[-1][0] - 3) < 0.01
        assert abs(points[-1][1] - 3) < 0.01

    def test_quad_bezier_points_count(self):
        points = _quad_bezier_points(0, 0, 1, 1, 2, 0, steps=6)
        assert len(points) == 7

    def test_parse_svg_path_line(self):
        segments = _parse_svg_path("M 0,0 L 10,20")
        assert len(segments) == 1
        assert segments[0]["type"] == "line"

    def test_parse_svg_path_curve(self):
        segments = _parse_svg_path("M 0,0 C 1,2 3,4 5,6")
        assert len(segments) == 1
        assert segments[0]["type"] == "spline"


class TestFormatConverterTool:
    """Tests for the format converter BaseTool."""

    def test_get_name(self):
        assert FormatConverterTool().get_name() == "FormatConverterTool"

    def test_missing_params_returns_error(self):
        result = FormatConverterTool().execute()
        assert result["success"] is False

    def test_empty_svg_dir_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = FormatConverterTool().execute(
                svg_dir=os.path.join(tmpdir, "nonexistent"),
                output_dir=tmpdir,
            )
            assert result["success"] is False

    def test_dxf_conversion_produces_files(self):
        """Test DXF conversion on generated SVGs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate SVGs first
            gen = SvgGeneratorTool().execute(output_dir=tmpdir)
            assert gen["success"]
            svg_dir = gen["data"]["svg_dir"]

            # Convert to DXF only (no Playwright needed)
            result = FormatConverterTool().execute(
                svg_dir=svg_dir, output_dir=tmpdir,
                formats=["dxf"],
            )
            assert result["success"] is True
            assert result["data"]["conversions"]["dxf"] > 0

    def test_eps_conversion_produces_files(self):
        """Test EPS conversion on generated SVGs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SvgGeneratorTool().execute(output_dir=tmpdir)
            assert gen["success"]
            svg_dir = gen["data"]["svg_dir"]

            result = FormatConverterTool().execute(
                svg_dir=svg_dir, output_dir=tmpdir,
                formats=["eps"],
            )
            assert result["success"] is True
            assert result["data"]["conversions"]["eps"] > 0

    def test_pdf_conversion_produces_files(self):
        """Test PDF conversion on generated SVGs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SvgGeneratorTool().execute(output_dir=tmpdir)
            assert gen["success"]
            svg_dir = gen["data"]["svg_dir"]

            result = FormatConverterTool().execute(
                svg_dir=svg_dir, output_dir=tmpdir,
                formats=["pdf"],
            )
            assert result["success"] is True
            assert result["data"]["conversions"]["pdf"] > 0


# ── Bundle Packager Tool ─────────────────────────────────────────────────────

class TestBundlePackagerTool:
    """Tests for ZIP bundle creation."""

    def test_get_name(self):
        assert BundlePackagerTool().get_name() == "BundlePackagerTool"

    def test_missing_output_dir_returns_error(self):
        result = BundlePackagerTool().execute()
        assert result["success"] is False

    def test_creates_zip_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate SVGs and convert to at least one format
            gen = SvgGeneratorTool().execute(output_dir=tmpdir)
            assert gen["success"]

            result = BundlePackagerTool().execute(
                output_dir=tmpdir,
                design_count=gen["data"]["generated_count"],
                category_counts=gen["data"]["category_counts"],
            )
            assert result["success"] is True
            assert os.path.exists(result["data"]["zip_path"])
            assert result["data"]["zip_size_mb"] > 0

    def test_zip_contains_license_and_readme(self):
        import zipfile
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SvgGeneratorTool().execute(output_dir=tmpdir)
            pkg = BundlePackagerTool().execute(
                output_dir=tmpdir,
                design_count=gen["data"]["generated_count"],
                category_counts=gen["data"]["category_counts"],
            )
            with zipfile.ZipFile(pkg["data"]["zip_path"], "r") as zf:
                names = zf.namelist()
                has_license = any("LICENSE.txt" in n for n in names)
                has_readme = any("README.txt" in n for n in names)
                assert has_license, "Missing LICENSE.txt in ZIP"
                assert has_readme, "Missing README.txt in ZIP"


# ── Compositions ─────────────────────────────────────────────────────────────

class TestCompositions:
    """Test that all composition functions produce valid SVG."""

    def _make_dwg(self):
        import svgwrite
        return svgwrite.Drawing(size=("1000px", "1000px"),
                                viewBox="0 0 1000 1000")

    def test_rose_open_adds_elements(self):
        dwg = self._make_dwg()
        comp.rose_open(dwg)
        xml = dwg.tostring()
        assert "<path" in xml

    def test_daisy_adds_elements(self):
        dwg = self._make_dwg()
        comp.daisy(dwg)
        xml = dwg.tostring()
        assert "<path" in xml

    def test_wreath_circle_adds_elements(self):
        dwg = self._make_dwg()
        comp.wreath_circle(dwg)
        xml = dwg.tostring()
        assert "<path" in xml

    def test_bouquet_roses_adds_elements(self):
        dwg = self._make_dwg()
        comp.bouquet_roses(dwg)
        xml = dwg.tostring()
        assert "<path" in xml

    def test_all_registry_designs_render(self):
        """Every registered design should produce valid SVG without errors."""
        import svgwrite
        for design in cats.get_all_designs():
            dwg = svgwrite.Drawing(
                size=("1000px", "1000px"),
                viewBox="0 0 1000 1000")
            extra = dict(design.get("extra_kwargs", {}))
            try:
                design["fn"](dwg, cx=500, cy=500, **extra)
            except Exception as e:
                pytest.fail(
                    f"Design '{design['name']}' failed to render: {e}")
            xml = dwg.tostring()
            assert "<path" in xml, \
                f"Design '{design['name']}' produced no paths"
