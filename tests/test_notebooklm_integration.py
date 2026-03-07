"""Tests for NotebookLM integration components.

Tests the research tool, research validator, audio workflow tools,
and audio workflow validators.
"""
import pytest
import json
import os
import sys
import importlib.util
from unittest.mock import patch, MagicMock

# Ensure project root is on path
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)
sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool
from lib.orchestrator.base_validator import BaseValidator


def _load_module(module_name, file_path):
    """Load a module from an absolute file path without polluting sys.path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Pre-load all modules to avoid import conflicts
_auto_listing_tools = os.path.join(_project_root, "workflows", "auto_listing_creator", "tools")
_auto_listing_validators = os.path.join(_project_root, "workflows", "auto_listing_creator", "validators")
_audio_tools = os.path.join(_project_root, "workflows", "notebooklm_audio", "tools")
_audio_validators = os.path.join(_project_root, "workflows", "notebooklm_audio", "validators")

_research_tool_mod = _load_module(
    "notebooklm_research_tool",
    os.path.join(_auto_listing_tools, "notebooklm_research_tool.py"),
)
NotebookLmResearchTool = _research_tool_mod.NotebookLmResearchTool

_research_validator_mod = _load_module(
    "research_enriched_validator",
    os.path.join(_auto_listing_validators, "research_enriched_validator.py"),
)
ResearchEnrichedValidator = _research_validator_mod.ResearchEnrichedValidator

_source_curator_mod = _load_module(
    "source_curator_tool",
    os.path.join(_audio_tools, "source_curator_tool.py"),
)
SourceCuratorTool = _source_curator_mod.SourceCuratorTool

_audio_gen_mod = _load_module(
    "audio_generator_tool",
    os.path.join(_audio_tools, "audio_generator_tool.py"),
)
AudioGeneratorTool = _audio_gen_mod.AudioGeneratorTool

_audio_packager_mod = _load_module(
    "audio_product_packager_tool",
    os.path.join(_audio_tools, "audio_product_packager_tool.py"),
)
AudioProductPackagerTool = _audio_packager_mod.AudioProductPackagerTool

_audio_publisher_mod = _load_module(
    "audio_publisher_tool",
    os.path.join(_audio_tools, "audio_publisher_tool.py"),
)
AudioPublisherTool = _audio_publisher_mod.AudioPublisherTool

_sources_curated_mod = _load_module(
    "sources_curated_validator",
    os.path.join(_audio_validators, "sources_curated_validator.py"),
)
SourcesCuratedValidator = _sources_curated_mod.SourcesCuratedValidator

_audio_generated_mod = _load_module(
    "audio_generated_validator",
    os.path.join(_audio_validators, "audio_generated_validator.py"),
)
AudioGeneratedValidator = _audio_generated_mod.AudioGeneratedValidator

_audio_published_mod = _load_module(
    "audio_published_validator",
    os.path.join(_audio_validators, "audio_published_validator.py"),
)
AudioPublishedValidator = _audio_published_mod.AudioPublishedValidator

# GenerateListingContentTool needs sys.path for its own config import
sys.path.insert(0, os.path.join(_project_root, "workflows", "auto_listing_creator"))
from tools.generate_listing_content_tool import GenerateListingContentTool


# =============================================================================
# Test NotebookLmResearchTool
# =============================================================================

class TestNotebookLmResearchTool:
    """Tests for the research enrichment tool in the listing pipeline."""

    def test_extends_base_tool(self):
        assert isinstance(NotebookLmResearchTool(), BaseTool)

    def test_get_name(self):
        assert NotebookLmResearchTool().get_name() == "NotebookLmResearchTool"

    def test_returns_standard_dict_keys(self):
        result = NotebookLmResearchTool().execute(opportunities=[], enable_research=False)
        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert "tool_name" in result
        assert "metadata" in result

    def test_disabled_research_passes_through(self):
        opps = [{"product_title": "Test", "target_keywords": ["test"]}]
        result = NotebookLmResearchTool().execute(opportunities=opps, enable_research=False)
        assert result["success"] is True
        assert result["data"] == opps
        assert result["metadata"]["skipped"] is True

    def test_empty_opportunities_returns_error(self):
        result = NotebookLmResearchTool().execute(opportunities=[], enable_research=True)
        assert result["success"] is False
        assert "No opportunities" in result["error"]

    def test_nlm_not_available_graceful_degradation(self):
        """When nlm CLI is not installed, tool passes through unchanged."""
        tool = NotebookLmResearchTool()
        opps = [{"product_title": "Test Product", "target_keywords": ["test"]}]
        with patch.object(tool, "_check_nlm_available", return_value=False):
            result = tool.execute(
                opportunities=opps,
                notebook_ids={"tattoo": "abc123"},
                focus_niche="tattoo",
                enable_research=True,
            )
        assert result["success"] is True
        assert result["data"] == opps
        assert result["metadata"]["skipped"] is True

    def test_no_notebook_id_passes_through(self):
        """When no notebook ID is configured, tool passes through."""
        tool = NotebookLmResearchTool()
        opps = [{"product_title": "Test", "target_keywords": ["test"]}]
        with patch.object(tool, "_check_nlm_available", return_value=True):
            result = tool.execute(
                opportunities=opps,
                notebook_ids={},
                focus_niche="tattoo",
                enable_research=True,
            )
        assert result["success"] is True
        assert result["data"] == opps

    def test_successful_enrichment(self):
        """When nlm query succeeds, opportunities get enriched."""
        tool = NotebookLmResearchTool()
        opps = [{"product_title": "Tattoo Gift Certificate", "target_keywords": ["tattoo gift card"], "why": "High demand"}]

        research_result = {
            "insights": "Tattoo gift certificates are the #1 searched template.",
            "keywords": ["tattoo gift card", "ink studio voucher"],
            "positioning": "Premium design differentiator",
            "citations": ["Industry Report 2025"],
        }

        with patch.object(tool, "_check_nlm_available", return_value=True), \
             patch.object(tool, "_query_notebook", return_value=research_result):
            result = tool.execute(
                opportunities=opps,
                notebook_ids={"tattoo": "notebook123"},
                focus_niche="tattoo",
                enable_research=True,
            )

        assert result["success"] is True
        assert len(result["data"]) == 1
        enriched = result["data"][0]
        assert "research_context" in enriched
        assert enriched["research_context"]["insights"] != ""
        assert result["metadata"]["enriched_count"] == 1

    def test_build_research_query(self):
        tool = NotebookLmResearchTool()
        query = tool._build_research_query(
            "Tattoo Gift Certificate",
            ["tattoo gift card", "ink voucher"],
            "High search volume",
            "tattoo",
        )
        assert "Tattoo Gift Certificate" in query
        assert "tattoo" in query
        assert "tattoo gift card" in query

    def test_extract_keywords_from_insights(self):
        tool = NotebookLmResearchTool()
        insights = 'Popular keywords include "tattoo gift card" and "ink studio voucher" for search.'
        keywords = tool._extract_keywords_from_insights(insights)
        assert "tattoo gift card" in keywords
        assert "ink studio voucher" in keywords


# =============================================================================
# Test ResearchEnrichedValidator
# =============================================================================

class TestResearchEnrichedValidator:
    """Tests for the research enrichment validator."""

    def test_extends_base_validator(self):
        assert isinstance(ResearchEnrichedValidator(), BaseValidator)

    def test_returns_standard_dict_keys(self):
        result = ResearchEnrichedValidator().validate([])
        assert "passed" in result
        assert "issues" in result
        assert "needs_more" in result
        assert "validator_name" in result
        assert "metadata" in result

    def test_non_list_input(self):
        result = ResearchEnrichedValidator().validate("not a list")
        assert result["passed"] is False

    def test_empty_list(self):
        result = ResearchEnrichedValidator().validate([])
        assert result["passed"] is False

    def test_no_enrichment_passes_gracefully(self):
        """No enrichment is OK (graceful degradation)."""
        data = [{"product_title": "Test"}]
        result = ResearchEnrichedValidator().validate(data)
        assert result["passed"] is True
        assert result["metadata"]["enriched"] == 0

    def test_enriched_opportunities_pass(self):
        data = [
            {
                "product_title": "Test",
                "research_context": {
                    "insights": "Good market positioning",
                    "keywords": ["test keyword"],
                    "positioning": "Unique angle",
                    "citations": [],
                },
            }
        ]
        result = ResearchEnrichedValidator().validate(data)
        assert result["passed"] is True
        assert result["metadata"]["enriched"] == 1
        assert result["metadata"]["rate"] == 1.0

    def test_empty_insights_flagged(self):
        data = [
            {
                "product_title": "Test Product",
                "research_context": {"insights": "", "keywords": [], "positioning": "", "citations": []},
            }
        ]
        result = ResearchEnrichedValidator().validate(data)
        assert result["passed"] is False
        assert any("Empty insights" in i for i in result["issues"])


# =============================================================================
# Test Audio Workflow Tools
# =============================================================================

class TestSourceCuratorTool:
    def test_extends_base_tool(self):
        assert isinstance(SourceCuratorTool(), BaseTool)

    def test_returns_standard_dict(self):
        tool = SourceCuratorTool()
        with patch.object(tool, "_check_nlm_available", return_value=False):
            result = tool.execute(niches=["tattoo"], notebook_ids={})
        assert "success" in result
        assert "tool_name" in result

    def test_nlm_unavailable(self):
        tool = SourceCuratorTool()
        with patch.object(tool, "_check_nlm_available", return_value=False):
            result = tool.execute(niches=["tattoo"], notebook_ids={})
        assert result["success"] is False
        assert "not installed" in result["error"]


class TestAudioGeneratorTool:
    def test_extends_base_tool(self):
        assert isinstance(AudioGeneratorTool(), BaseTool)

    def test_no_notebooks_returns_error(self):
        result = AudioGeneratorTool().execute(notebooks=[], export_dir="/tmp")
        assert result["success"] is False
        assert "No notebooks" in result["error"]

    def test_no_export_dir_returns_error(self):
        result = AudioGeneratorTool().execute(notebooks=[{"notebook_id": "x"}], export_dir="")
        assert result["success"] is False


class TestAudioProductPackagerTool:
    def test_extends_base_tool(self):
        assert isinstance(AudioProductPackagerTool(), BaseTool)

    def test_no_products_returns_error(self):
        result = AudioProductPackagerTool().execute(audio_products=[])
        assert result["success"] is False

    def test_no_api_key_returns_error(self):
        result = AudioProductPackagerTool().execute(audio_products=[{"niche": "tattoo"}], anthropic_api_key="")
        assert result["success"] is False
        assert "api_key" in result["error"].lower()


class TestAudioPublisherTool:
    def test_extends_base_tool(self):
        assert isinstance(AudioPublisherTool(), BaseTool)

    def test_no_products_returns_error(self):
        result = AudioPublisherTool().execute(packaged_products=[])
        assert result["success"] is False


# =============================================================================
# Test Audio Workflow Validators
# =============================================================================

class TestSourcesCuratedValidator:
    def test_extends_base_validator(self):
        assert isinstance(SourcesCuratedValidator(), BaseValidator)

    def test_valid_data_passes(self):
        result = SourcesCuratedValidator().validate({
            "notebooks": [{"niche": "tattoo", "sources_added": 3}],
            "total_sources": 3,
        })
        assert result["passed"] is True

    def test_no_notebooks_fails(self):
        result = SourcesCuratedValidator().validate({"notebooks": [], "total_sources": 0})
        assert result["passed"] is False

    def test_empty_notebook_flagged(self):
        result = SourcesCuratedValidator().validate({
            "notebooks": [{"niche": "tattoo", "sources_added": 0}],
            "total_sources": 0,
        })
        assert result["passed"] is False


class TestAudioGeneratedValidator:
    def test_extends_base_validator(self):
        assert isinstance(AudioGeneratedValidator(), BaseValidator)

    def test_no_products_fails(self):
        result = AudioGeneratedValidator().validate({"audio_products": [], "stats": {}})
        assert result["passed"] is False


class TestAudioPublishedValidator:
    def test_extends_base_validator(self):
        assert isinstance(AudioPublishedValidator(), BaseValidator)

    def test_successful_publish(self):
        result = AudioPublishedValidator().validate({
            "queue_rows": 3,
            "drafts_created": 0,
            "draft_errors": 0,
            "total_products": 3,
        })
        assert result["passed"] is True

    def test_no_publish_fails(self):
        result = AudioPublishedValidator().validate({
            "queue_rows": 0,
            "drafts_created": 0,
            "draft_errors": 0,
            "total_products": 3,
        })
        assert result["passed"] is False


# =============================================================================
# Test GenerateListingContentTool research context integration
# =============================================================================

class TestGenerateListingContentResearchContext:
    """Test that research_context is properly injected into Claude prompts."""

    def test_prompt_without_research_context(self):
        tool = GenerateListingContentTool()
        opp = {"product_title": "Test", "target_keywords": ["test"], "suggested_price": 4.99, "priority": "HIGH", "why": "test"}
        prompt = tool._build_prompt(opp, "tattoo", "GBP", research_context=None)
        assert "MARKET RESEARCH" not in prompt
        assert "PurpleOcaz" in prompt

    def test_prompt_with_research_context(self):
        tool = GenerateListingContentTool()
        opp = {"product_title": "Test", "target_keywords": ["test"], "suggested_price": 4.99, "priority": "HIGH", "why": "test"}
        rc = {
            "insights": "This product has high demand in Q4",
            "keywords": ["gift card", "studio voucher"],
            "positioning": "Stand out with premium design",
            "citations": [],
        }
        prompt = tool._build_prompt(opp, "tattoo", "GBP", research_context=rc)
        assert "MARKET RESEARCH" in prompt
        assert "high demand in Q4" in prompt
        assert "gift card" in prompt
        assert "Stand out with premium design" in prompt

    def test_prompt_with_empty_research_context(self):
        tool = GenerateListingContentTool()
        opp = {"product_title": "Test", "target_keywords": ["test"], "suggested_price": 4.99, "priority": "HIGH", "why": "test"}
        rc = {"insights": "", "keywords": [], "positioning": "", "citations": []}
        prompt = tool._build_prompt(opp, "tattoo", "GBP", research_context=rc)
        assert "MARKET RESEARCH" not in prompt
