# =============================================================================
# tests/test_thumbnail_pipeline.py
#
# Tests for ThumbnailPipelineTool: registry lookup, shadow compositing,
# and full execute flow with mocked Canva API.
# =============================================================================

import io
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)
sys.path.insert(1, os.path.join(
    _project_root, "workflows", "auto_listing_creator",
))

from workflows.auto_listing_creator.tools.thumbnail_pipeline_tool import (
    ThumbnailPipelineTool,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_REGISTRY = {
    "version": 1,
    "designs": {
        "tattoo": {
            "business_card": {
                "base_design_id": "DAFx_dsWpTA",
                "base_design_title": "Etsy Listing - Business Card Purple",
                "page_count": 5,
                "pages": {
                    "1": {
                        "width": 3000,
                        "height": 2250,
                        "card_slots": {
                            "front_card": {
                                "element_id": "PBYdP0fP9tx4c7Hw-LBStl4Tz3Wf18JQg",
                                "original_asset_id": "MAFx_hPfdk0",
                                "width": 1425,
                                "height": 814,
                                "top": 197,
                                "left": 353,
                                "confirmed_unlocked": True,
                                "confirmed_date": "2026-03-16",
                            },
                            "back_card": {
                                "element_id": "PBYdP0fP9tx4c7Hw-LBYSdstM3fGX4Vqg",
                                "original_asset_id": "MAFx_sdcedo",
                                "width": 1451,
                                "height": 829,
                                "top": 743,
                                "left": 936,
                                "confirmed_unlocked": True,
                                "confirmed_date": "2026-03-16",
                            },
                        },
                        "text_elements": {
                            "title": {
                                "element_id": "PBYdP0fP9tx4c7Hw-LBxKw3mlnn9fvQtq",
                                "default_text": "Tattoo Studio\nBusiness Card",
                            },
                            "subtitle": {
                                "element_id": "PBYdP0fP9tx4c7Hw-LBMzzm2JK93kPpr8",
                                "default_text": "MAKE A MEMORABLE IMPRESSION",
                            },
                        },
                    }
                },
                "card_designs": {
                    "dark": {
                        "design_id": "DAHD07F9MsY",
                        "canva_asset_id": "MAHEHX1itYY",
                        "export_page": 1,
                        "export_width": 2100,
                    },
                    "light": {
                        "design_id": "DAHD15IcxRs",
                        "canva_asset_id": "MAHEHd3QNt0",
                        "export_page": 1,
                        "export_width": 2100,
                    },
                },
            }
        }
    },
    "shadow_preset": {
        "shadow_color": [0, 0, 0],
        "shadow_opacity": 0.75,
        "shadow_blur": 12,
        "shadow_offset_x": 15,
        "shadow_offset_y": 15,
        "padding": 40,
        "extra_right_padding": 80,
        "extra_bottom_padding": 40,
    },
    "spaces": {
        "bucket": "purpleocaz-assets",
        "region": "lon1",
        "endpoint": "https://lon1.digitaloceanspaces.com",
        "cdn_base": "https://purpleocaz-assets.lon1.digitaloceanspaces.com",
        "thumbnail_prefix": "thumbnails",
    },
}

SHADOW_PRESET = SAMPLE_REGISTRY["shadow_preset"]


def _make_test_png(width=100, height=50, color=(255, 0, 0, 255)):
    """Create a small test PNG in memory."""
    img = Image.new("RGBA", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture
def tool():
    return ThumbnailPipelineTool()


@pytest.fixture
def registry_file():
    """Write sample registry to a temp file and return path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(SAMPLE_REGISTRY, f)
        return f.name


# ── Registry Lookup Tests ───────────────────────────────────────────────────

class TestRegistryLookup:

    def test_lookup_existing_niche_product(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "tattoo", "business_card")
        assert result is not None
        assert result["base_design_id"] == "DAFx_dsWpTA"
        assert result["page_count"] == 5

    def test_lookup_returns_card_slots(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "tattoo", "business_card")
        page1 = result["pages"]["1"]
        slots = page1["card_slots"]
        assert "front_card" in slots
        assert "back_card" in slots
        assert slots["front_card"]["confirmed_unlocked"] is True
        assert slots["back_card"]["confirmed_unlocked"] is True

    def test_lookup_returns_card_designs(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "tattoo", "business_card")
        cards = result["card_designs"]
        assert cards["dark"]["canva_asset_id"] == "MAHEHX1itYY"
        assert cards["light"]["canva_asset_id"] == "MAHEHd3QNt0"

    def test_lookup_returns_text_elements(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "tattoo", "business_card")
        texts = result["pages"]["1"]["text_elements"]
        assert "title" in texts
        assert "subtitle" in texts
        assert texts["title"]["element_id"] == "PBYdP0fP9tx4c7Hw-LBxKw3mlnn9fvQtq"

    def test_lookup_missing_niche_returns_none(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "nonexistent", "business_card")
        assert result is None

    def test_lookup_missing_product_type_returns_none(self, tool):
        result = tool._lookup_design(SAMPLE_REGISTRY, "tattoo", "nonexistent")
        assert result is None

    def test_lookup_empty_registry_returns_none(self, tool):
        result = tool._lookup_design({}, "tattoo", "business_card")
        assert result is None

    def test_load_registry_from_file(self, tool, registry_file):
        result = tool._load_registry(registry_file)
        assert result is not None
        assert result["version"] == 1
        os.unlink(registry_file)

    def test_load_registry_missing_file(self, tool):
        result = tool._load_registry("/nonexistent/path.json")
        assert result is None


# ── Shadow Compositing Tests ────────────────────────────────────────────────

class TestShadowCompositing:

    def test_shadow_output_is_valid_png(self, tool):
        input_bytes = _make_test_png(100, 50)
        output_bytes = tool._apply_shadow(input_bytes, SHADOW_PRESET)
        img = Image.open(io.BytesIO(output_bytes))
        assert img.format == "PNG"

    def test_shadow_output_is_larger_due_to_padding(self, tool):
        input_bytes = _make_test_png(100, 50)
        output_bytes = tool._apply_shadow(input_bytes, SHADOW_PRESET)
        img = Image.open(io.BytesIO(output_bytes))
        # Expected: pad_l=40, pad_r=120, pad_t=40, pad_b=80
        assert img.width == 40 + 100 + 120  # 260
        assert img.height == 40 + 50 + 80   # 170

    def test_shadow_output_is_rgba(self, tool):
        input_bytes = _make_test_png(100, 50)
        output_bytes = tool._apply_shadow(input_bytes, SHADOW_PRESET)
        img = Image.open(io.BytesIO(output_bytes))
        assert img.mode == "RGBA"

    def test_shadow_has_white_background(self, tool):
        """Corners should be white (flattened onto white background)."""
        input_bytes = _make_test_png(100, 50)
        output_bytes = tool._apply_shadow(input_bytes, SHADOW_PRESET)
        img = Image.open(io.BytesIO(output_bytes))
        corner = img.getpixel((0, 0))
        assert corner == (255, 255, 255, 255)

    def test_shadow_preserves_original_area(self, tool):
        """The original image area should contain the card pixels."""
        input_bytes = _make_test_png(100, 50, (255, 0, 0, 255))
        output_bytes = tool._apply_shadow(input_bytes, SHADOW_PRESET)
        img = Image.open(io.BytesIO(output_bytes))
        # Sample pixel at original position (pad_l, pad_t) = (40, 40)
        pixel = img.getpixel((40, 40))
        assert pixel[0] == 255  # Red channel preserved
        assert pixel[3] == 255  # Fully opaque

    def test_shadow_with_custom_preset(self, tool):
        preset = {
            "shadow_color": [0, 0, 0],
            "shadow_opacity": 0.5,
            "shadow_blur": 5,
            "shadow_offset_x": 10,
            "shadow_offset_y": 10,
            "padding": 20,
            "extra_right_padding": 0,
            "extra_bottom_padding": 0,
        }
        input_bytes = _make_test_png(200, 100)
        output_bytes = tool._apply_shadow(input_bytes, preset)
        img = Image.open(io.BytesIO(output_bytes))
        assert img.width == 20 + 200 + 20   # 240
        assert img.height == 20 + 100 + 20  # 140


# ── Execute Integration Tests (mocked APIs) ─────────────────────────────────

class TestExecuteMocked:

    @patch.object(ThumbnailPipelineTool, "_upload_to_spaces")
    @patch.object(ThumbnailPipelineTool, "_download_bytes")
    @patch.object(ThumbnailPipelineTool, "_export_pages")
    @patch.object(ThumbnailPipelineTool, "_swap_element")
    @patch("workflows.auto_listing_creator.tools.thumbnail_pipeline_tool.get_valid_token")
    @patch.object(ThumbnailPipelineTool, "_load_registry")
    def test_execute_success(self, mock_registry, mock_token,
                             mock_swap, mock_export, mock_download,
                             mock_upload, tool):
        mock_registry.return_value = SAMPLE_REGISTRY
        mock_token.return_value = "fake-token"
        mock_swap.return_value = (True, None)
        mock_export.return_value = ["https://export.canva.com/fake.png"]
        mock_download.return_value = _make_test_png(3000, 2250)
        mock_upload.return_value = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/thumbnails/test.png"

        result = tool.execute(
            niche="tattoo",
            product_type="business_card",
        )

        assert result["success"] is True
        assert result["data"]["base_design_id"] == "DAFx_dsWpTA"
        assert len(result["data"]["pages"]) == 1
        assert "spaces_url" in result["data"]["pages"][0]
        assert mock_swap.call_count == 2  # front + back

    @patch.object(ThumbnailPipelineTool, "_load_registry")
    def test_execute_missing_registry(self, mock_registry, tool):
        mock_registry.return_value = None
        result = tool.execute(niche="tattoo", product_type="business_card")
        assert result["success"] is False
        assert "registry" in result["error"].lower()

    @patch("workflows.auto_listing_creator.tools.thumbnail_pipeline_tool.get_valid_token")
    @patch.object(ThumbnailPipelineTool, "_load_registry")
    def test_execute_missing_niche(self, mock_registry, mock_token, tool):
        mock_registry.return_value = SAMPLE_REGISTRY
        mock_token.return_value = "fake-token"
        result = tool.execute(niche="nonexistent", product_type="business_card")
        assert result["success"] is False
        assert "not registered" in result["error"].lower() or "no design" in result["error"].lower()

    @patch("workflows.auto_listing_creator.tools.thumbnail_pipeline_tool.get_valid_token")
    @patch.object(ThumbnailPipelineTool, "_load_registry")
    def test_execute_no_canva_token(self, mock_registry, mock_token, tool):
        mock_registry.return_value = SAMPLE_REGISTRY
        mock_token.return_value = ""
        result = tool.execute(niche="tattoo", product_type="business_card")
        assert result["success"] is False
        assert "token" in result["error"].lower()

    @patch.object(ThumbnailPipelineTool, "_swap_element")
    @patch("workflows.auto_listing_creator.tools.thumbnail_pipeline_tool.get_valid_token")
    @patch.object(ThumbnailPipelineTool, "_load_registry")
    def test_execute_swap_failure(self, mock_registry, mock_token,
                                  mock_swap, tool):
        mock_registry.return_value = SAMPLE_REGISTRY
        mock_token.return_value = "fake-token"
        mock_swap.return_value = (False, "API error 500")
        result = tool.execute(niche="tattoo", product_type="business_card")
        assert result["success"] is False
        assert "swap failed" in result["error"].lower()

    def test_execute_returns_standard_shape(self, tool):
        """Every return must have success, data, error, tool_name, metadata."""
        with patch.object(tool, "_load_registry", return_value=None):
            result = tool.execute()
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert "tool_name" in result
        assert "metadata" in result
        assert result["tool_name"] == "ThumbnailPipelineTool"
