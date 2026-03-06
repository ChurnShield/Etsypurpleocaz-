# =============================================================================
# workflows/ai_news_rss/tools/fetch_rss_tool.py
#
# FetchRSSTool — Phase 1
#
# Downloads one or more RSS/Atom feeds and parses them into article dicts.
# Uses only Python built-in libraries (no feedparser dependency).
#
# Accepts either:
#   rss_url  : str        A single feed URL (backward-compatible).
#   rss_urls : list[str]  Multiple feed URLs — results are combined and
#                         deduplicated by URL so duplicates across feeds
#                         are automatically removed.
#
# Supported feed formats:
#   RSS 2.0  — standard format used by TechCrunch, The Verge, VentureBeat,
#               HackerNews (hnrss.org).
#   Atom     — used by Reddit (/r/subreddit/new/.rss returns Atom XML despite
#               the .rss extension).
#
# Output format (stored in result["data"]):
#   {
#       "articles": [
#           {
#               "title":       str,   # Article headline
#               "url":         str,   # Link to the full article
#               "pub_date":    str,   # Raw date string from the feed
#               "description": str,   # Summary text, HTML stripped
#               "source":      str,   # Feed channel title
#           },
#           ...
#       ]
#   }
# =============================================================================

import sys
import os
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# fetch_rss_tool.py lives at: workflows/ai_news_rss/tools/fetch_rss_tool.py
#   dirname(_here)                    → workflows/ai_news_rss
#   dirname(dirname(_here))           → workflows
#   dirname(dirname(dirname(_here)))  → project root  ✅
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


# Atom namespace — Reddit and some other feeds use this format.
ATOM_NS = "http://www.w3.org/2005/Atom"


class FetchRSSTool(BaseTool):
    """
    Downloads and parses one or more RSS 2.0 or Atom feeds.

    Why urllib instead of feedparser?
    ----------------------------------
    feedparser is the easiest library for this, but we avoid adding
    dependencies without approval (see CLAUDE.md).  urllib + ElementTree
    are built into Python and handle both RSS 2.0 and Atom feeds correctly.
    """

    # Some RSS servers block requests with no User-Agent header.
    USER_AGENT = "ai-news-workflow/1.0 (Python)"

    def execute(self, **kwargs) -> dict:
        """
        Parameters
        ----------
        rss_urls : list[str]   One or more RSS feed URLs to fetch.
        rss_url  : str         Single URL (backward-compatible fallback).

        Returns
        -------
        Standard tool dict.  result["data"]["articles"] is the combined list,
        deduplicated by URL across all feeds.
        """
        # Accept a list (rss_urls) or fall back to a single URL (rss_url).
        rss_urls = kwargs.get("rss_urls") or []
        if not rss_urls:
            single = kwargs.get("rss_url", "")
            if single:
                rss_urls = [single]

        try:
            if not rss_urls:
                raise ValueError("rss_urls (list) or rss_url (str) parameter is required")

            all_articles = []
            seen_urls    = set()
            errors       = []

            for url in rss_urls:
                try:
                    xml_bytes = self._download(url)
                    articles  = self._parse(xml_bytes)
                    for article in articles:
                        # Deduplicate by article URL across feeds.
                        article_url = article.get("url", "")
                        if article_url and article_url in seen_urls:
                            continue
                        if article_url:
                            seen_urls.add(article_url)
                        all_articles.append(article)
                except Exception as feed_err:
                    errors.append(f"{url}: {feed_err}")

            # Only fail if ALL feeds errored out.
            if errors and not all_articles:
                raise RuntimeError(
                    f"All {len(rss_urls)} feed(s) failed:\n" + "\n".join(errors)
                )

            return {
                "success": True,
                "data": {"articles": all_articles},
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "article_count": len(all_articles),
                    "feeds_fetched": len(rss_urls) - len(errors),
                    "feeds_failed":  len(errors),
                    "feed_errors":   errors,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _download(self, url: str) -> bytes:
        """Fetch the URL and return the raw bytes."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": self.USER_AGENT},
        )
        # create_default_context() uses the system's trusted CA certificates.
        # If you get SSL errors, you can pass ssl._create_unverified_context()
        # as a temporary workaround (not recommended for production).
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return resp.read()

    def _parse(self, xml_bytes: bytes) -> list:
        """
        Auto-detect RSS 2.0 or Atom format and parse into article dicts.

        RSS 2.0 structure:
            <rss>
              <channel>
                <title>Feed Name</title>
                <item>
                  <title>Article Title</title>
                  <link>https://...</link>
                  <pubDate>Wed, 19 Feb 2026 12:00:00 +0000</pubDate>
                  <description>Summary text...</description>
                </item>
              </channel>
            </rss>

        Atom structure (used by Reddit):
            <feed xmlns="http://www.w3.org/2005/Atom">
              <title>r/subreddit</title>
              <entry>
                <title>Post title</title>
                <link href="https://..." rel="alternate"/>
                <updated>2026-02-19T13:00:00+00:00</updated>
                <summary type="html">Post text...</summary>
              </entry>
            </feed>
        """
        root    = ET.fromstring(xml_bytes)
        channel = root.find("channel")

        if channel is not None:
            # Standard RSS 2.0
            return self._parse_rss(channel)

        # Atom — root tag is <feed> with or without the namespace.
        return self._parse_atom(root)

    def _parse_rss(self, channel) -> list:
        """Parse a standard RSS 2.0 <channel> element."""
        source_name = (channel.findtext("title") or "Unknown Source").strip()
        articles = []

        for item in channel.findall("item"):
            title       = (item.findtext("title")       or "").strip()
            url         = (item.findtext("link")        or "").strip()
            pub_date    = (item.findtext("pubDate")     or "").strip()
            description = (item.findtext("description") or "").strip()

            description = self._strip_html(description)
            if len(description) > 500:
                description = description[:497] + "..."

            if not title and not url:
                continue

            articles.append({
                "title":       title,
                "url":         url,
                "pub_date":    pub_date,
                "description": description,
                "source":      source_name,
            })

        return articles

    def _parse_atom(self, root) -> list:
        """
        Parse an Atom <feed> element (used by Reddit and some other sources).

        Atom uses XML namespaces, so every tag must be prefixed with the
        namespace URI: {http://www.w3.org/2005/Atom}tagname
        """
        ns          = ATOM_NS
        source_name = (root.findtext(f"{{{ns}}}title") or "Unknown Source").strip()
        articles    = []

        for entry in root.findall(f"{{{ns}}}entry"):
            title = (entry.findtext(f"{{{ns}}}title") or "").strip()

            # Atom <link> is an element with an href attribute, not text.
            link_el = entry.find(f"{{{ns}}}link[@rel='alternate']") \
                      or entry.find(f"{{{ns}}}link")
            url = (link_el.get("href", "") if link_el is not None else "").strip()

            # Use <updated> or <published> as the publication date.
            pub_date = (
                entry.findtext(f"{{{ns}}}published")
                or entry.findtext(f"{{{ns}}}updated")
                or ""
            ).strip()

            # Reddit puts the post body in <content> or <summary>.
            description = (
                entry.findtext(f"{{{ns}}}content")
                or entry.findtext(f"{{{ns}}}summary")
                or ""
            ).strip()

            description = self._strip_html(description)
            if len(description) > 500:
                description = description[:497] + "..."

            if not title and not url:
                continue

            articles.append({
                "title":       title,
                "url":         url,
                "pub_date":    pub_date,
                "description": description,
                "source":      source_name,
            })

        return articles

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags and decode common HTML entities."""
        # Remove tags
        text = re.sub(r"<[^>]+>", "", text)
        # Decode common entities
        text = (text
                .replace("&amp;",  "&")
                .replace("&lt;",   "<")
                .replace("&gt;",   ">")
                .replace("&quot;", '"')
                .replace("&#39;",  "'")
                .replace("&nbsp;", " "))
        # Collapse whitespace
        return " ".join(text.split())
