import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure project root is first on sys.path, then workflow dir
# (root config.py must take priority over workflow config.py)
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)
_workflow_dir = os.path.join(
    _project_root, "workflows", "auto_listing_creator",
)
# Insert workflow dir first, then project root (so root ends up at index 0)
for p in (_workflow_dir, _project_root):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

from workflows.auto_listing_creator.tools.hero_generator import HeroGeneratorTool


SAMPLE_LISTING = {
    "title": "Tattoo Gift Certificate Editable Template",
    "product_type": "Gift Certificate",
}


def test_hero_generator_is_base_tool():
    """HeroGeneratorTool extends BaseTool."""
    from lib.orchestrator.base_tool import BaseTool
    tool = HeroGeneratorTool()
    assert isinstance(tool, BaseTool)


def test_hero_generator_tool_name():
    tool = HeroGeneratorTool()
    assert tool.get_name() == "HeroGeneratorTool"


def test_no_listing_returns_error():
    """Returns error dict when no listing is provided."""
    tool = HeroGeneratorTool()
    result = tool.execute()

    assert result["success"] is False
    assert result["error"] == "No listing provided"
    assert result["tool_name"] == "HeroGeneratorTool"
    assert result["data"] is None
    assert isinstance(result["metadata"], dict)


def test_no_listing_explicit_none():
    tool = HeroGeneratorTool()
    result = tool.execute(listing=None)

    assert result["success"] is False
    assert "No listing" in result["error"]


def test_derive_hero_title():
    tool = HeroGeneratorTool()
    title = tool._derive_hero_title(
        "Tattoo Gift Certificate Editable Template, Instant Download",
        "Gift Certificate",
        "tattoo",
    )
    # "Editable", "Template", "Instant", "Download" are skip words
    assert "Editable" not in title
    assert "Template" not in title
    assert "Tattoo" in title
    assert "Gift" in title


def test_derive_hero_title_short():
    tool = HeroGeneratorTool()
    title = tool._derive_hero_title("Simple Card", "Gift Certificate", "tattoo")
    assert title == "Simple Card"


def test_derive_hero_title_long_truncates():
    tool = HeroGeneratorTool()
    title = tool._derive_hero_title(
        "One Two Three Four Five Six Seven",
        "Gift Certificate",
        "tattoo",
    )
    words = title.split()
    assert len(words) <= 5


def test_derive_tagline_known_type():
    tool = HeroGeneratorTool()
    tagline = tool._derive_tagline("Gift Certificate", "tattoo")
    assert tagline == "MAKE EXTRA INCOME SELLING GIFT CERTIFICATES"


def test_derive_tagline_unknown_type():
    tool = HeroGeneratorTool()
    tagline = tool._derive_tagline("Unknown Widget", "tattoo")
    assert tagline == "PROFESSIONAL TATTOO TEMPLATES"


def test_derive_tagline_price_list():
    tool = HeroGeneratorTool()
    tagline = tool._derive_tagline("Price List", "nail")
    assert "SERVICES" in tagline


def test_no_browser_no_playwright_returns_error():
    """Returns error when no browser provided and Playwright unavailable."""
    try:
        import playwright
        pytest.skip("Playwright is installed — cannot test unavailable path")
    except ImportError:
        pass

    tool = HeroGeneratorTool()
    result = tool.execute(listing=SAMPLE_LISTING, focus_niche="tattoo")

    assert result["success"] is False
    assert "Playwright unavailable" in result["error"]


def test_return_structure_on_error():
    """Error results follow the standard tool return format."""
    tool = HeroGeneratorTool()
    result = tool.execute()

    assert "success" in result
    assert "data" in result
    assert "error" in result
    assert "tool_name" in result
    assert "metadata" in result
