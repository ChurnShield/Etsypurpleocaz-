"""
Valid Dates Validator
=====================
Checks that filtered articles have valid publication dates.

Runs after FilterRecentTool to confirm the date filtering worked
correctly and we're not passing bad data to Airtable.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_validator import BaseValidator


class ValidDatesValidator(BaseValidator):
    """Validates that articles have parseable publication dates."""

    def validate(self, data, context=None) -> dict:
        """
        Check that each article's 'published' field is a valid date.

        Args:
            data: The tool result dict from FilterRecentTool.
                  Expected: {'success': True, 'data': [list of articles], ...}
            context: Optional extra context (unused here).

        Returns:
            Standard validator result dict.
        """
        issues = []

        # Handle tool result dict
        if isinstance(data, dict):
            articles = data.get('data', [])
        else:
            articles = data

        if not articles:
            # No articles to validate (this is OK - filter may have
            # removed everything if nothing was published recently)
            return {
                'passed': True,
                'issues': [],
                'needs_more': False,
                'validator_name': self.get_name(),
                'metadata': {'article_count': 0, 'valid_dates': 0}
            }

        valid_count = 0
        invalid_count = 0

        for i, article in enumerate(articles):
            published = article.get('published', '')

            if not published:
                issues.append(f"Article {i + 1} has no publication date")
                invalid_count += 1
                continue

            # Try to parse the date
            parsed = _try_parse(published)
            if parsed is None:
                issues.append(
                    f"Article {i + 1} has unparseable date: '{published}'"
                )
                invalid_count += 1
            else:
                valid_count += 1

        # We pass if at least some articles have valid dates
        # (a few bad dates among many good ones shouldn't block the workflow)
        passed = valid_count > 0 and invalid_count == 0

        return {
            'passed': passed,
            'issues': issues,
            'needs_more': not passed and valid_count == 0,
            'validator_name': self.get_name(),
            'metadata': {
                'article_count': len(articles),
                'valid_dates': valid_count,
                'invalid_dates': invalid_count,
            }
        }


def _try_parse(date_str):
    """Try to parse a date string. Returns datetime or None."""
    if not date_str:
        return None

    clean = date_str.replace('Z', '').strip()
    if len(clean) > 19 and ('+' in clean[19:] or clean[19:].startswith('-')):
        clean = clean[:19]

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue

    return None
