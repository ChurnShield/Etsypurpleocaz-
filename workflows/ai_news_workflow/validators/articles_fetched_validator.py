"""
Articles Fetched Validator
===========================
Checks that the RSS fetch actually returned articles.

Runs after FetchRSSTool to make sure we got real data before
continuing to the filter step.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_validator import BaseValidator


class ArticlesFetchedValidator(BaseValidator):
    """Validates that articles were actually fetched from the RSS feed."""

    def __init__(self, min_articles=1):
        """
        Args:
            min_articles (int): Minimum number of articles required.
                Default is 1 (at least one article must be returned).
        """
        self.min_articles = min_articles

    def validate(self, data, context=None) -> dict:
        """
        Check that the fetch result contains articles.

        Args:
            data: The tool result dict from FetchRSSTool.
                  Expected: {'success': True, 'data': [list of articles], ...}
            context: Optional extra context (unused here).

        Returns:
            Standard validator result dict.
        """
        issues = []

        # Handle tool result dict (data is nested under 'data' key)
        if isinstance(data, dict):
            articles = data.get('data', [])
        else:
            articles = data

        # Check 1: Is it None?
        if articles is None:
            issues.append("Fetch returned None (feed may be unreachable)")

        # Check 2: Is it a list?
        elif not isinstance(articles, list):
            issues.append(f"Expected a list of articles, got {type(articles).__name__}")

        # Check 3: Does it have enough articles?
        elif len(articles) < self.min_articles:
            issues.append(
                f"Only {len(articles)} article(s) fetched "
                f"(minimum: {self.min_articles})"
            )

        # Check 4: Do articles have the required fields?
        elif articles:
            first = articles[0]
            required_fields = ['title', 'url', 'published']
            missing = [f for f in required_fields if f not in first]
            if missing:
                issues.append(f"Articles missing fields: {', '.join(missing)}")

        passed = len(issues) == 0
        article_count = len(articles) if isinstance(articles, list) else 0

        return {
            'passed': passed,
            'issues': issues,
            'needs_more': not passed,
            'validator_name': self.get_name(),
            'metadata': {
                'article_count': article_count,
                'min_required': self.min_articles,
            }
        }
