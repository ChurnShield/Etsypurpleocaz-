"""
Filter Recent Articles Tool
=============================
Takes a list of articles and keeps only those published within the last N hours.

This runs AFTER FetchRSSTool. It receives the full list of articles and
returns only the recent ones.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_tool import BaseTool


class FilterRecentTool(BaseTool):
    """Filters articles to only include those from the last N hours."""

    def execute(self, **kwargs) -> dict:
        """
        Filter articles by publication date.

        Args:
            articles (list): List of article dicts from FetchRSSTool.
                Each article must have a 'published' key with a date string.
            hours (int): How many hours back to look. Default: 24.

        Returns:
            Standard tool result dict. On success, 'data' contains the
            filtered list of articles.
        """
        try:
            articles = kwargs.get('articles', [])
            hours = kwargs.get('hours', 24)

            if not articles:
                return {
                    'success': True,
                    'data': [],
                    'error': None,
                    'tool_name': self.get_name(),
                    'metadata': {
                        'input_count': 0,
                        'output_count': 0,
                        'hours_filter': hours,
                        'reason': 'empty_input'
                    }
                }

            # Calculate the cutoff time (now minus N hours)
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            recent = []
            skipped = 0

            for article in articles:
                published_str = article.get('published', '')

                # Try to parse the date string
                pub_date = _parse_iso_date(published_str)

                if pub_date is None:
                    # If we can't parse the date, skip the article
                    # (we don't want articles with unknown dates)
                    skipped += 1
                    continue

                if pub_date >= cutoff:
                    # Article is recent enough - keep it
                    recent.append(article)

            return {
                'success': True,
                'data': recent,
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {
                    'input_count': len(articles),
                    'output_count': len(recent),
                    'skipped_bad_date': skipped,
                    'hours_filter': hours,
                    'cutoff_time': cutoff.isoformat(),
                }
            }

        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'tool_name': self.get_name(),
                'metadata': {'exception_type': type(e).__name__}
            }


def _parse_iso_date(date_str):
    """
    Try to parse a date string into a datetime object.

    Handles common formats from RSS feeds:
        - ISO 8601: "2025-01-15T14:30:00"
        - With timezone: "2025-01-15T14:30:00+00:00"
        - Date only: "2025-01-15"

    Returns None if the date can't be parsed.
    """
    if not date_str:
        return None

    # Strip timezone info for simple comparison (we compare in UTC)
    # Remove trailing Z, +00:00, -05:00, etc.
    clean = date_str.replace('Z', '').strip()
    # Remove timezone offset like +00:00 or -05:00
    if len(clean) > 19 and ('+' in clean[19:] or clean[19:].startswith('-')):
        clean = clean[:19]

    # Try common formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",    # 2025-01-15T14:30:00
        "%Y-%m-%d %H:%M:%S",    # 2025-01-15 14:30:00
        "%Y-%m-%d",              # 2025-01-15
    ]

    for fmt in formats:
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue

    return None
