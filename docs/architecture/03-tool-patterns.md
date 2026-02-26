# Tool Patterns

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers the BaseTool contract and how to create new tools.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Orchestrator: [docs/architecture/02-orchestrator.md](02-orchestrator.md)
> - Validator patterns: [docs/architecture/04-validator-patterns.md](04-validator-patterns.md)
> - Workflows: [docs/architecture/07-workflows.md](07-workflows.md)

## Table of Contents

1. [Overview](#overview)
2. [Pattern and Interface](#pattern-and-interface)
3. [Return Format](#return-format)
4. [Creating a New Tool](#creating-a-new-tool)
5. [Example Implementation](#example-implementation)
6. [Existing Tools](#existing-tools)
7. [Testing Tools](#testing-tools)

## Overview

Every tool in the system extends `BaseTool` and returns a standardized dict. This enables the Orchestrator to treat all tools uniformly and SmallBrain to analyze any tool's performance.

### What it does

- Define reusable operations (fetch data, transform, save results)
- Return structured results that the Orchestrator and Brain can parse
- Catch all exceptions internally (never raise from execute())

### What it does NOT do

- Log its own execution (the Orchestrator handles logging)
- Retry on failure (the Orchestrator handles retries)
- Validate its own output (validators handle that)

## Pattern and Interface

**Location**: `lib/orchestrator/base_tool.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
```

Key rules:
- `execute()` receives all params as keyword arguments
- `get_name()` returns the class name (used in logging and SmallBrain analytics)
- Never raise exceptions from `execute()` -- catch and return error dict

## Return Format

Every tool must return this exact dict structure:

```python
{
    'success': bool,        # True if tool completed without error
    'data': Any,            # The result payload; None if success=False
    'error': str | None,    # Error message; None if success=True
    'tool_name': str,       # self.get_name() -- used for analytics grouping
    'metadata': dict        # Optional: timing, counts, debug info
}
```

**Why this matters**: SmallBrain queries `execution_logs` and expects `tool_result` events to have `success` and `tool_name` fields. Inconsistent return formats break pattern analysis.

## Creating a New Tool

1. Create file in `workflows/<your_workflow>/tools/<tool_name>.py`
2. Add path setup boilerplate (3 dirname calls to reach project root)
3. Import and extend `BaseTool`
4. Implement `execute(**kwargs)` with try/except returning standard dict
5. Add `__init__.py` entry if needed
6. Import in your workflow's `run.py`

## Example Implementation

From `templates/workflow_template/tools/example_tool.py`:

```python
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_template_root = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_template_root))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

class ExampleTool(BaseTool):
    def execute(self, **kwargs) -> dict:
        try:
            text = kwargs.get("text", "")
            result = {
                "original": text,
                "upper": text.upper(),
                "word_count": len(text.split()),
            }
            return {
                'success': True,
                'data': result,
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {'char_count': len(text)}
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'tool_name': self.get_name(),
                'metadata': {'exception_type': type(e).__name__}
            }
```

## Existing Tools

| Workflow | Tool | Purpose |
|----------|------|---------|
| ai_news_rss | FetchRSSTool | Fetch articles from RSS feed URLs |
| ai_news_rss | FilterRecentTool | Filter articles to last N hours |
| ai_news_rss | SaveToGoogleSheetsTool | Write articles to Google Sheets |
| etsy_analytics | FetchEtsyDataTool | Fetch all listings + shop stats from Etsy API |
| etsy_analytics | AnalyzePerformanceTool | Compute metrics, top performers, tag analysis |
| etsy_analytics | SaveAnalyticsTool | Write analytics to Google Sheets (3 tabs) |
| etsy_analytics | TriageListingsTool | Score and prioritize listings for action |
| etsy_seo_optimizer | AnalyzeTagsTool | Scan all listing tags, score SEO quality |
| etsy_seo_optimizer | GenerateTagsTool | Use Claude to generate optimized tags |
| etsy_seo_optimizer | SaveSeoReportTool | Write SEO report to Google Sheets |
| tattoo_trend_monitor | FetchTrendsTool | Google Trends + Etsy competitor search |
| tattoo_trend_monitor | AnalyseOpportunitiesTool | Gap analysis + AI opportunity ranking |
| tattoo_trend_monitor | SaveTrendsReportTool | Write trend report to Google Sheets |
| auto_listing_creator | LoadOpportunitiesTool | Load opportunities from trend monitor output |
| auto_listing_creator | GenerateListingContentTool | Claude generates titles, descriptions, tags |
| auto_listing_creator | ProductCreatorTool | HTML templates + Playwright -> PNG images |
| auto_listing_creator | CanvaExportTool | Canva API export (deprecated, use ProductCreatorTool) |
| auto_listing_creator | PublishListingsTool | Create Etsy drafts + upload images |

## Testing Tools

Test tools in isolation by calling `execute()` directly:

```python
def test_example_tool():
    tool = ExampleTool()
    result = tool.execute(text="hello world")
    assert result["success"] is True
    assert result["data"]["word_count"] == 2
    assert result["tool_name"] == "ExampleTool"
    assert "error" in result
    assert "metadata" in result
```

See `tests/test_base_classes.py` for the reference test pattern.
