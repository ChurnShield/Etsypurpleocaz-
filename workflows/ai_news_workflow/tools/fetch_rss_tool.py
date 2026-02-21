"""
Fetch RSS Tool
===============
Downloads and parses articles from an RSS feed.

Uses the 'feedparser' library to handle all the different RSS/Atom formats.
Returns a list of articles, each with: title, url, published, description, source.

INSTALL FIRST:
    pip install feedparser
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.orchestrator.base_tool import BaseTool


class FetchRSSTool(BaseTool):
    """Fetches articles from an RSS feed URL."""

    def execute(self, **kwargs) -> dict:
        """
        Fetch and parse an RSS feed.

        Args:
            feed_url (str): The URL of the RSS feed to fetch.

        Returns:
            Standard tool result dict. On success, 'data' contains a list of
            article dicts, each with keys:
                - title: Article headline
                - url: Link to the full article
                - published: Publication date as a string (ISO format when possible)
                - description: Summary/snippet text
                - source: Name of the feed
        """
        try:
            import feedparser
        except ImportError:
            return {
                'success': False,
                'data': None,
                'error': (
                    "feedparser is not installed. "
                    "Run: pip install feedparser"
                ),
                'tool_name': self.get_name(),
                'metadata': {'reason': 'missing_dependency'}
            }

        try:
            feed_url = kwargs.get('feed_url', '')

            if not feed_url or feed_url == "YOUR_RSS_FEED_URL_HERE":
                return {
                    'success': False,
                    'data': None,
                    'error': (
                        "No RSS feed URL configured. "
                        "Set RSS_FEED_URL in your .env file or in "
                        "workflows/ai_news_workflow/config.py"
                    ),
                    'tool_name': self.get_name(),
                    'metadata': {'reason': 'missing_config'}
                }

            # feedparser handles RSS 2.0, Atom, RSS 1.0, etc.
            feed = feedparser.parse(feed_url)

            # Check if the feed parsed successfully
            if feed.bozo and not feed.entries:
                # 'bozo' means feedparser found problems with the feed
                error_msg = str(feed.bozo_exception) if feed.bozo_exception else "Unknown parse error"
                return {
                    'success': False,
                    'data': None,
                    'error': f"Failed to parse RSS feed: {error_msg}",
                    'tool_name': self.get_name(),
                    'metadata': {'feed_url': feed_url, 'reason': 'parse_error'}
                }

            # Get the feed's title (used as the "source" name)
            source_name = feed.feed.get('title', 'Unknown Source')

            # Extract articles into our standard format
            articles = []
            for entry in feed.entries:
                # Try to get the published date in a standard format
                # feedparser normalizes dates into 'published_parsed' (a time tuple)
                published_str = _parse_date(entry)

                # Get the description/summary (some feeds use 'summary', others 'description')
                description = entry.get('summary', entry.get('description', ''))

                # Strip HTML tags from the description (feeds often include HTML)
                description = _strip_html(description)

                # Truncate very long descriptions
                if len(description) > 500:
                    description = description[:497] + "..."

                articles.append({
                    'title': entry.get('title', 'No title'),
                    'url': entry.get('link', ''),
                    'published': published_str,
                    'description': description,
                    'source': source_name,
                })

            return {
                'success': True,
                'data': articles,
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {
                    'feed_url': feed_url,
                    'source_name': source_name,
                    'articles_found': len(articles),
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


def _parse_date(entry):
    """
    Extract a publication date from a feedparser entry.

    feedparser normalizes dates into a time.struct_time at 'published_parsed'.
    We convert that to an ISO 8601 string. If that's not available, we fall
    back to the raw string.
    """
    from datetime import datetime

    # Best case: feedparser already parsed the date
    parsed = entry.get('published_parsed')
    if parsed:
        try:
            dt = datetime(*parsed[:6])
            return dt.isoformat()
        except (ValueError, TypeError):
            pass

    # Fallback: use the raw date string
    return entry.get('published', entry.get('updated', ''))


def _strip_html(text):
    """
    Remove HTML tags from text.

    RSS feed descriptions often contain HTML like <p>, <a href>, <img>, etc.
    We strip all tags to get plain text for storage in Airtable.
    """
    import re
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean
