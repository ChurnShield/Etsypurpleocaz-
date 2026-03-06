# Validator Patterns

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers the BaseValidator contract and how to create new validators.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Tool patterns: [docs/architecture/03-tool-patterns.md](03-tool-patterns.md)
> - Orchestrator: [docs/architecture/02-orchestrator.md](02-orchestrator.md)
> - Brain: [docs/architecture/06-brain.md](06-brain.md)

## Table of Contents

1. [Overview](#overview)
2. [Pattern and Interface](#pattern-and-interface)
3. [Return Format](#return-format)
4. [Validator Categories](#validator-categories)
5. [Creating a New Validator](#creating-a-new-validator)
6. [Example Implementation](#example-implementation)
7. [Existing Validators](#existing-validators)

## Overview

Validators check tool output quality after each phase. They determine whether the Orchestrator should accept the result, retry, or fail.

### What it does

- Check tool output against quality thresholds
- Return structured results the Orchestrator uses for retry decisions
- Provide issue lists that get logged for SmallBrain analysis

### What it does NOT do

- Fix or transform data (tools do that)
- Retry operations (the Orchestrator decides retries based on `needs_more`)
- Log its own results (the Orchestrator logs validation events)

## Pattern and Interface

**Location**: `lib/orchestrator/base_validator.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
```

Key rules:
- `validate()` receives the tool's `data` field (not the full result dict)
- `context` is optional extra info (rarely used)
- `get_name()` returns the class name (used in logging and SmallBrain analytics)

## Return Format

Every validator must return this exact dict structure:

```python
{
    'passed': bool,             # True if quality is acceptable
    'issues': List[str],        # Human-readable problems found; [] if passed
    'needs_more': bool,         # True if retrying might help
    'validator_name': str,      # self.get_name()
    'metadata': dict            # Optional: scores, counts, thresholds
}
```

### How the Orchestrator uses this

- `passed=True` -> accept the result, move to next phase
- `passed=False, needs_more=True` -> retry (if attempts remain)
- `passed=False, needs_more=False` -> fail permanently (retrying won't help)

## Validator Categories

| Category | When to use | Example |
|----------|------------|---------|
| Data presence | Tool must return non-empty data | ArticlesFetchedValidator |
| Data quality | Data must meet thresholds (min count, score) | TagAnalysisValidator |
| Format check | Data must have required fields/structure | AnalysisValidator |
| Save confirmation | External write succeeded | GoogleSheetsSaveValidator |

## Creating a New Validator

1. Create file in `workflows/<your_workflow>/validators/<validator_name>.py`
2. Add path setup boilerplate (3 dirname calls to project root)
3. Import and extend `BaseValidator`
4. Implement `validate(data, context=None)` returning standard dict
5. Import in your workflow's `run.py`

## Example Implementation

From `templates/workflow_template/validators/example_validator.py`:

```python
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_template_root = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_template_root))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator

class ExampleValidator(BaseValidator):
    def validate(self, data, context=None):
        issues = []
        if not data:
            issues.append("No data returned from tool")
        elif not isinstance(data, dict):
            issues.append(f"Expected dict, got {type(data).__name__}")
        elif data.get("word_count", 0) < 1:
            issues.append("Word count is zero")

        passed = len(issues) == 0
        return {
            'passed': passed,
            'issues': issues,
            'needs_more': not passed,
            'validator_name': self.get_name(),
            'metadata': {'check_count': 3}
        }
```

## Existing Validators

| Workflow | Validator | What it checks |
|----------|-----------|---------------|
| ai_news_rss | ArticlesFetchedValidator | Articles list is non-empty |
| ai_news_rss | ValidDatesValidator | Articles have parseable dates |
| ai_news_rss | GoogleSheetsSaveValidator | Sheets write succeeded |
| etsy_analytics | ListingsFetchedValidator | Listings list is non-empty |
| etsy_analytics | AnalysisValidator | Analysis has snapshot + listings |
| etsy_analytics | AnalyticsSavedValidator | Sheets write succeeded |
| etsy_seo_optimizer | TagAnalysisValidator | Tag analysis has overview |
| etsy_seo_optimizer | TagsGeneratedValidator | Claude generated tags for listings |
| etsy_seo_optimizer | ReportSavedValidator | SEO report written to Sheets |
| tattoo_trend_monitor | TrendsFetchedValidator | Trend data is non-empty |
| tattoo_trend_monitor | OpportunitiesValidator | Opportunities were ranked |
| tattoo_trend_monitor | ReportSavedValidator | Report written to Sheets |
| auto_listing_creator | OpportunitiesLoadedValidator | Opportunities loaded from prior workflow |
| auto_listing_creator | ContentGeneratedValidator | Claude generated listing content |
| auto_listing_creator | ListingsPublishedValidator | Etsy drafts created or Sheets updated |
