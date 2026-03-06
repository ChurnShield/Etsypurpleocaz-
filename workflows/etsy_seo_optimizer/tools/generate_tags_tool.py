# =============================================================================
# workflows/etsy_seo_optimizer/tools/generate_tags_tool.py
#
# Phase 2: Uses Claude to generate optimized, unique tags for each listing.
#
# Key rules for Etsy tags:
#   - Max 13 tags per listing
#   - Each tag max 20 characters
#   - Tags should be long-tail and specific (not generic)
#   - Tags should NOT duplicate across similar listings
#   - Tags should match what buyers actually search for
#
# Checkpointing: saves progress after each batch to a JSON file so
# interrupted runs can resume without re-generating already-done listings.
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
CHECKPOINT_FILE   = os.path.join(_workflow, ".seo_checkpoint.json")


class GenerateTagsTool(BaseTool):
    """Use Claude to generate optimized Etsy tags for listings."""

    def execute(self, **kwargs) -> dict:
        listings       = kwargs.get("listings", [])
        overused_tags  = kwargs.get("overused_tags", [])
        api_key        = kwargs.get("anthropic_api_key", "")
        model          = kwargs.get("model", "claude-sonnet-4-20250514")
        batch_size     = kwargs.get("batch_size", 10)
        focus_niche    = kwargs.get("focus_niche", "tattoo")

        if not api_key:
            return {
                "success": False, "data": None,
                "error": "anthropic_api_key required",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to optimize",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # -- Load checkpoint if exists --
            all_results, used_tags_this_run, done_ids = self._load_checkpoint()

            if done_ids:
                print(f"     Resuming from checkpoint: {len(done_ids)} listings already done",
                      flush=True)

            total_batches = (len(listings) + batch_size - 1) // batch_size

            # Process in batches
            for i in range(0, len(listings), batch_size):
                batch = listings[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                # Skip batches where ALL listings are already done
                remaining = [l for l in batch if l["listing_id"] not in done_ids]
                if not remaining:
                    print(f"     Batch {batch_num}/{total_batches} "
                          f"({i+1}-{min(i+batch_size, len(listings))} of {len(listings)})... "
                          f"SKIPPED (checkpoint)", flush=True)
                    continue

                print(f"     Batch {batch_num}/{total_batches} "
                      f"({i+1}-{min(i+batch_size, len(listings))} of {len(listings)})...",
                      flush=True)

                prompt = self._build_prompt(remaining, overused_tags, used_tags_this_run, focus_niche)
                response = self._call_claude(api_key, model, prompt)

                # Parse the response
                batch_results = self._parse_response(response, remaining)
                batch_success = 0
                for result in batch_results:
                    # Track used tags
                    for tag in result.get("new_tags", []):
                        used_tags_this_run.add(tag.lower())
                    all_results.append(result)
                    done_ids.add(result["listing_id"])
                    if result.get("new_tags"):
                        batch_success += 1
                print(f"       -> {batch_success}/{len(remaining)} generated", flush=True)

                # Save checkpoint after every batch
                self._save_checkpoint(all_results, used_tags_this_run, done_ids)

                # Rate limit between batches
                if i + batch_size < len(listings):
                    time.sleep(1)

            # -- All done, remove checkpoint --
            self._clear_checkpoint()

            # Calculate improvement stats
            improved = sum(1 for r in all_results if r.get("new_tags"))
            avg_old_score = round(
                sum(l.get("seo_score", 0) for l in listings) / len(listings), 1
            ) if listings else 0

            return {
                "success": True,
                "data": {
                    "optimized_listings": all_results,
                    "stats": {
                        "total_processed":  len(listings),
                        "tags_generated":   improved,
                        "failed":           len(listings) - improved,
                        "avg_original_score": avg_old_score,
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "listings_processed": len(listings),
                    "tags_generated": improved,
                    "batches": (len(listings) + batch_size - 1) // batch_size,
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # -------------------------------------------------------------------------
    # Checkpoint helpers
    # -------------------------------------------------------------------------

    def _load_checkpoint(self):
        """Load progress from checkpoint file if it exists."""
        if not os.path.exists(CHECKPOINT_FILE):
            return [], set(), set()

        try:
            with open(CHECKPOINT_FILE, "r") as f:
                cp = json.load(f)
            all_results = cp.get("results", [])
            used_tags = set(cp.get("used_tags", []))
            done_ids = set(cp.get("done_ids", []))
            return all_results, used_tags, done_ids
        except Exception:
            return [], set(), set()

    def _save_checkpoint(self, all_results, used_tags, done_ids):
        """Save current progress to checkpoint file."""
        try:
            cp = {
                "results": all_results,
                "used_tags": list(used_tags),
                "done_ids": list(done_ids),
            }
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(cp, f)
        except Exception:
            pass  # Don't fail the run if checkpoint save fails

    def _clear_checkpoint(self):
        """Remove checkpoint file after successful completion."""
        try:
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Prompt building
    # -------------------------------------------------------------------------

    def _build_prompt(self, batch, overused_tags, used_tags_this_run, focus_niche):
        """Build the Claude prompt for tag generation."""
        listings_text = ""
        for idx, l in enumerate(batch, 1):
            listings_text += f"""
Listing {idx}:
  ID: {l['listing_id']}
  Title: {l['title']}
  Current tags: {', '.join(l.get('current_tags', []))}
  SEO Score: {l.get('seo_score', 0)}/100
  Issues: {'; '.join(l.get('issues', []))}
  Views: {l.get('views', 0)} | Favs: {l.get('num_favorers', 0)}
"""

        overused_list = ", ".join(sorted(overused_tags)[:40])
        already_used = ", ".join(sorted(list(used_tags_this_run)[:50]))

        return f"""You are an Etsy SEO expert specializing in digital templates and the {focus_niche} niche.

TASK: Generate optimized tags for each listing below. Each listing needs exactly 13 tags.

RULES:
1. Each tag must be 20 characters or fewer
2. Tags must be specific and long-tail (what buyers actually search)
3. DO NOT use these overused generic tags (used 50+ times across the shop): {overused_list}
4. DO NOT duplicate tags that were already assigned to other listings in this batch or earlier: {already_used}
5. Each listing's 13 tags must be unique to THAT listing
6. Include the product type in at least 2 tags (e.g. "gift certificate", "voucher template")
7. Include the niche/industry in at least 2 tags (e.g. "tattoo parlor", "ink studio")
8. Include buyer intent tags (e.g. "last minute gift", "business branding")
9. Mix broad and specific: some category tags + some very specific long-tail tags
10. Think about what a BUYER would type into Etsy search

LISTINGS TO OPTIMIZE:
{listings_text}

RESPOND IN EXACT JSON FORMAT (no markdown, no explanation, just JSON):
[
  {{
    "listing_id": 12345,
    "new_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
    "reasoning": "Brief explanation of tag strategy"
  }}
]"""

    def _call_claude(self, api_key, model, prompt):
        """Call the Anthropic Claude API."""
        payload = json.dumps({
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(ANTHROPIC_API_URL, data=payload, method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("anthropic-version", "2023-06-01")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Extract text from response
        content = data.get("content", [])
        for block in content:
            if block.get("type") == "text":
                return block.get("text", "")
        return ""

    def _parse_response(self, response_text, batch):
        """Parse Claude's JSON response into structured results."""
        results = []

        # Try to extract JSON from the response
        text = response_text.strip()
        # Handle case where Claude wraps in markdown code block
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            text = text.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON array in the response
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(text[start:end])
                except json.JSONDecodeError:
                    parsed = []
            else:
                parsed = []

        # Match parsed results to batch listings
        parsed_by_id = {item.get("listing_id"): item for item in parsed}

        for listing in batch:
            lid = listing["listing_id"]
            if lid in parsed_by_id:
                item = parsed_by_id[lid]
                new_tags = item.get("new_tags", [])
                # Enforce rules: max 13 tags, max 20 chars each
                new_tags = [t[:20] for t in new_tags[:13]]
                results.append({
                    "listing_id":   lid,
                    "title":        listing["title"],
                    "current_tags": listing.get("current_tags", []),
                    "new_tags":     new_tags,
                    "reasoning":    item.get("reasoning", ""),
                    "seo_score":    listing.get("seo_score", 0),
                    "views":        listing.get("views", 0),
                    "num_favorers": listing.get("num_favorers", 0),
                    "url":          listing.get("url", ""),
                })
            else:
                # Claude missed this listing
                results.append({
                    "listing_id":   lid,
                    "title":        listing["title"],
                    "current_tags": listing.get("current_tags", []),
                    "new_tags":     [],
                    "reasoning":    "Failed to generate - not in Claude response",
                    "seo_score":    listing.get("seo_score", 0),
                    "views":        listing.get("views", 0),
                    "num_favorers": listing.get("num_favorers", 0),
                    "url":          listing.get("url", ""),
                })

        return results
