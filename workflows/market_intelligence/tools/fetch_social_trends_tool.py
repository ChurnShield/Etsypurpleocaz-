# =============================================================================
# workflows/market_intelligence/tools/fetch_social_trends_tool.py
#
# Phase 1: Gathers trend signals from two ToS-safe non-Etsy sources:
#   a) Enhanced Google Trends (interest + related queries + rising topics)
#   b) Reddit public JSON API (trending posts in niche subreddits)
#
# Each source is independently try/excepted so one failure does not block.
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import sys
import os
from datetime import datetime, timezone, timedelta

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class FetchSocialTrendsTool(BaseTool):
    """Fetch trend signals from Google Trends (enhanced) + Reddit public API."""

    def execute(self, **kwargs) -> dict:
        trend_keywords    = kwargs.get("trend_keywords", [])
        subreddits        = kwargs.get("subreddits", [])
        reddit_post_limit = kwargs.get("reddit_post_limit", 50)
        reddit_lookback   = kwargs.get("reddit_lookback_days", 30)
        trends_geo        = kwargs.get("trends_geo", "")
        trends_timeframe  = kwargs.get("trends_timeframe", "today 12-m")
        focus_niche       = kwargs.get("focus_niche", "tattoo")

        try:
            google_signals = []
            reddit_signals = []
            sources_summary = {}

            # ---- A) Enhanced Google Trends ----
            print("     [1a] Fetching enhanced Google Trends data...", flush=True)
            try:
                google_raw = self._fetch_enhanced_google_trends(
                    trend_keywords, trends_geo, trends_timeframe
                )
                google_signals = self._extract_google_signals(
                    google_raw, focus_niche
                )
                sources_summary["google_trends"] = len(google_signals)
                print(f"          {len(google_signals)} signals from Google Trends", flush=True)
            except Exception as e:
                print(f"          WARNING: Google Trends failed: {str(e)[:80]}", flush=True)
                sources_summary["google_trends_error"] = str(e)[:100]

            # ---- B) Reddit Public JSON API ----
            print("     [1b] Fetching Reddit trend signals...", flush=True)
            try:
                reddit_raw = self._fetch_reddit_trends(
                    subreddits, reddit_post_limit, reddit_lookback
                )
                reddit_signals = self._extract_reddit_signals(
                    reddit_raw, focus_niche
                )
                sources_summary["reddit"] = len(reddit_signals)
                print(f"          {len(reddit_signals)} signals from Reddit", flush=True)
            except Exception as e:
                print(f"          WARNING: Reddit failed: {str(e)[:80]}", flush=True)
                sources_summary["reddit_error"] = str(e)[:100]

            # ---- Merge and deduplicate ----
            all_signals = google_signals + reddit_signals

            if not all_signals:
                return {
                    "success": False, "data": None,
                    "error": "No trend signals collected from any source",
                    "tool_name": self.get_name(),
                    "metadata": {"sources_summary": sources_summary},
                }

            trend_signals = self._deduplicate_signals(all_signals)
            trend_signals.sort(key=lambda s: s.get("signal_score", 0), reverse=True)

            return {
                "success": True,
                "data": {
                    "trend_signals": trend_signals,
                    "sources_summary": sources_summary,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "total_signals": len(trend_signals),
                    "google_count": len(google_signals),
                    "reddit_count": len(reddit_signals),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # =========================================================================
    # A) Enhanced Google Trends
    # =========================================================================

    def _fetch_enhanced_google_trends(self, keywords, geo, timeframe):
        """Fetch interest-over-time + related queries (rising/top) from pytrends.

        Same batch-of-5 pattern as fetch_trends_tool.py but additionally
        calls related_queries() for rising/top related terms.
        """
        try:
            from pytrends.request import TrendReq
        except ImportError:
            print("          WARNING: pytrends not installed, skipping", flush=True)
            return {"interest": [], "related": []}

        pytrends = TrendReq(hl="en-US", tz=0)
        interest_results = []
        related_results = []

        for i in range(0, len(keywords), 5):
            group = keywords[i:i + 5]
            try:
                pytrends.build_payload(group, timeframe=timeframe, geo=geo)

                # Interest over time (same as existing pattern)
                interest = pytrends.interest_over_time()
                if not interest.empty:
                    for kw in group:
                        if kw not in interest.columns:
                            interest_results.append(self._empty_interest(kw))
                            continue

                        series = interest[kw]
                        current = int(series.iloc[-1]) if len(series) > 0 else 0
                        avg_val = round(float(series.mean()), 1)
                        peak = int(series.max())

                        if len(series) >= 12:
                            recent = float(series.iloc[-13:].mean())
                            earlier = float(series.iloc[:13].mean())
                        elif len(series) >= 4:
                            mid = len(series) // 2
                            recent = float(series.iloc[mid:].mean())
                            earlier = float(series.iloc[:mid].mean())
                        else:
                            recent = current
                            earlier = avg_val

                        if earlier > 0:
                            growth = round((recent - earlier) / earlier * 100, 1)
                        else:
                            growth = 100.0 if recent > 0 else 0.0

                        if growth > 15:
                            direction = "rising"
                        elif growth < -15:
                            direction = "declining"
                        else:
                            direction = "stable"

                        interest_results.append({
                            "keyword": kw,
                            "current_interest": current,
                            "avg_interest": avg_val,
                            "peak_interest": peak,
                            "trend_direction": direction,
                            "growth_pct": growth,
                        })
                else:
                    for kw in group:
                        interest_results.append(self._empty_interest(kw))

                # Related queries (NEW - not in existing fetch_trends_tool)
                try:
                    related = pytrends.related_queries()
                    for kw in group:
                        kw_data = related.get(kw, {})
                        for query_type in ("rising", "top"):
                            df = kw_data.get(query_type)
                            if df is not None and not df.empty:
                                for _, row in df.head(5).iterrows():
                                    related_results.append({
                                        "parent_keyword": kw,
                                        "related_query": row.get("query", ""),
                                        "value": int(row.get("value", 0)),
                                        "type": query_type,
                                    })
                except Exception:
                    pass  # Related queries are a bonus, not critical

                time.sleep(2)

            except Exception as e:
                for kw in group:
                    interest_results.append(self._empty_interest(kw, error=str(e)[:50]))
                time.sleep(5)

        return {"interest": interest_results, "related": related_results}

    def _empty_interest(self, keyword, error=None):
        return {
            "keyword": keyword,
            "current_interest": 0,
            "avg_interest": 0,
            "peak_interest": 0,
            "trend_direction": f"error: {error}" if error else "no data",
            "growth_pct": 0,
        }

    def _extract_google_signals(self, google_raw, niche):
        """Convert raw Google Trends data into unified signal format."""
        signals = []

        # Interest-over-time signals
        for item in google_raw.get("interest", []):
            if item["current_interest"] == 0 and item["avg_interest"] == 0:
                continue
            score = min(100, item["current_interest"])
            signals.append({
                "source": "google_trends",
                "keyword": item["keyword"],
                "signal_score": score,
                "context": f"Interest: {item['current_interest']}, "
                           f"Growth: {item['growth_pct']}%",
                "raw_metric": item["current_interest"],
                "direction": item["trend_direction"],
                "niche": niche,
            })

        # Related/rising query signals
        for item in google_raw.get("related", []):
            query = item.get("related_query", "")
            if not query:
                continue
            value = item.get("value", 0)
            score = min(100, value) if item["type"] == "rising" else min(50, value)
            signals.append({
                "source": "google_related",
                "keyword": query,
                "signal_score": score,
                "context": f"Rising related query for: {item['parent_keyword']}",
                "raw_metric": value,
                "direction": "rising" if item["type"] == "rising" else "stable",
                "niche": niche,
            })

        return signals

    # =========================================================================
    # B) Reddit Public JSON API
    # =========================================================================

    def _fetch_reddit_trends(self, subreddits, post_limit, lookback_days):
        """Fetch trending posts from Reddit subreddits via public JSON API.

        Reddit exposes JSON at any URL by appending .json. No auth needed
        for public subreddits. User-Agent header is required.
        """
        posts = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        cutoff_ts = cutoff.timestamp()

        for sub in subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit={post_limit}"
                req = urllib.request.Request(url)
                req.add_header("User-Agent", "MarketIntelligence/1.0 (Etsy trend research)")
                req.add_header("Accept", "application/json")

                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                children = data.get("data", {}).get("children", [])
                for child in children:
                    post = child.get("data", {})
                    created = post.get("created_utc", 0)

                    if created < cutoff_ts:
                        continue

                    # Skip stickied/mod posts
                    if post.get("stickied", False):
                        continue

                    posts.append({
                        "subreddit": sub,
                        "title": post.get("title", ""),
                        "text_snippet": (post.get("selftext", "") or "")[:200],
                        "score": post.get("score", 0),
                        "comments": post.get("num_comments", 0),
                        "created_utc": created,
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                    })

                time.sleep(1)  # Rate limit for Reddit

            except Exception as e:
                print(f"          WARNING: r/{sub} failed: {str(e)[:60]}", flush=True)
                time.sleep(2)

        return posts

    def _extract_reddit_signals(self, reddit_posts, niche):
        """Convert raw Reddit posts into unified signal format."""
        if not reddit_posts:
            return []

        # Find max engagement for normalisation
        max_engagement = max(
            p["score"] + p["comments"] * 2
            for p in reddit_posts
        ) or 1

        signals = []
        for post in reddit_posts:
            engagement = post["score"] + post["comments"] * 2
            score = min(100, round(engagement / max_engagement * 100))

            if score < 5:
                continue  # Skip very low engagement posts

            # Extract key phrases from title for keyword
            title = post["title"]
            keyword = self._extract_keyword_from_title(title, niche)
            if not keyword:
                continue

            signals.append({
                "source": "reddit",
                "keyword": keyword,
                "signal_score": score,
                "context": f"r/{post['subreddit']}: {title[:80]}",
                "raw_metric": engagement,
                "direction": "unknown",
                "niche": niche,
            })

        return signals

    def _extract_keyword_from_title(self, title, niche):
        """Extract a meaningful keyword phrase from a Reddit post title.

        Looks for product-related terms that could map to Etsy listings.
        """
        title_lower = title.lower()

        # Product-related terms that suggest digital product opportunities
        product_indicators = [
            "template", "printable", "design", "card", "form", "certificate",
            "voucher", "waiver", "consent", "aftercare", "flash", "stencil",
            "portfolio", "branding", "logo", "menu", "price list", "booking",
            "appointment", "social media", "instagram", "business card",
            "gift", "bundle", "kit", "guide", "ebook", "tutorial",
        ]

        # Check if title mentions any product-related terms
        for indicator in product_indicators:
            if indicator in title_lower:
                # Build a keyword from the niche + indicator
                return f"{niche} {indicator}"

        # Also check for "looking for" / "where can I find" / "need" patterns
        request_patterns = [
            "looking for", "where can i", "need a", "anyone know",
            "recommendation", "suggestions for", "help me find",
        ]
        for pattern in request_patterns:
            if pattern in title_lower:
                # Title itself is the signal - truncate to key part
                clean = title_lower.replace(pattern, "").strip()
                words = clean.split()[:4]
                if words:
                    return " ".join(words)

        return ""

    # =========================================================================
    # Deduplication
    # =========================================================================

    def _deduplicate_signals(self, signals):
        """Deduplicate by keyword (case-insensitive), keeping highest score."""
        seen = {}
        for signal in signals:
            key = signal["keyword"].lower().strip()
            if key in seen:
                if signal["signal_score"] > seen[key]["signal_score"]:
                    seen[key] = signal
            else:
                seen[key] = signal
        return list(seen.values())
