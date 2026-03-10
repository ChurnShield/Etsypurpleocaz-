import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ListingQualityValidator(BaseValidator):
    """Validates individual listing content quality after Phase 2.

    Checks each generated listing for:
      - Title length (100-140 chars)
      - Exactly 13 tags
      - No duplicate tags
      - Description word count (150+ words)
      - Price is set (> 0)

    Returns a quality_score (0-100) per listing and an overall pass/fail.
    """

    TITLE_MIN = 100
    TITLE_MAX = 140
    REQUIRED_TAGS = 13
    MIN_DESCRIPTION_WORDS = 150

    # Points per check (total = 100)
    WEIGHT_TITLE_LENGTH = 25
    WEIGHT_TAG_COUNT = 25
    WEIGHT_NO_DUPLICATE_TAGS = 15
    WEIGHT_DESCRIPTION_WORDS = 25
    WEIGHT_PRICE_SET = 10

    def validate(self, data, context=None):
        issues = []
        if not isinstance(data, dict):
            return {
                "passed": False, "issues": ["Not a dict"], "needs_more": False,
                "validator_name": self.get_name(), "metadata": {},
            }

        listings = data.get("generated_listings", [])
        if not listings:
            return {
                "passed": False, "issues": ["No listings to validate"],
                "needs_more": False, "validator_name": self.get_name(),
                "metadata": {},
            }

        scores = []
        listing_details = []

        for i, listing in enumerate(listings):
            score = 0
            listing_issues = []

            # 1. Title length
            title = listing.get("title", "")
            title_len = len(title)
            if self.TITLE_MIN <= title_len <= self.TITLE_MAX:
                score += self.WEIGHT_TITLE_LENGTH
            else:
                listing_issues.append(
                    f"Title length {title_len} chars "
                    f"(expected {self.TITLE_MIN}-{self.TITLE_MAX})"
                )

            # 2. Exactly 13 tags
            tags = listing.get("tags", [])
            tag_count = len(tags)
            if tag_count == self.REQUIRED_TAGS:
                score += self.WEIGHT_TAG_COUNT
            else:
                listing_issues.append(
                    f"{tag_count} tags (expected {self.REQUIRED_TAGS})"
                )

            # 3. No duplicate tags
            tags_lower = [t.lower().strip() for t in tags]
            unique_tags = set(tags_lower)
            if len(unique_tags) == len(tags_lower):
                score += self.WEIGHT_NO_DUPLICATE_TAGS
            else:
                dupes = len(tags_lower) - len(unique_tags)
                listing_issues.append(f"{dupes} duplicate tag(s)")

            # 4. Description word count
            description = listing.get("description", "")
            word_count = len(description.split())
            if word_count >= self.MIN_DESCRIPTION_WORDS:
                score += self.WEIGHT_DESCRIPTION_WORDS
            else:
                listing_issues.append(
                    f"Description {word_count} words "
                    f"(minimum {self.MIN_DESCRIPTION_WORDS})"
                )

            # 5. Price is set
            price = listing.get("price", 0)
            try:
                price_val = float(price)
            except (ValueError, TypeError):
                price_val = 0
            if price_val > 0:
                score += self.WEIGHT_PRICE_SET
            else:
                listing_issues.append("Price not set or zero")

            scores.append(score)
            listing_details.append({
                "index": i,
                "title": title[:60],
                "score": score,
                "issues": listing_issues,
            })

            if listing_issues:
                short_title = title[:40] or f"Listing {i+1}"
                for issue in listing_issues:
                    issues.append(f"[{short_title}] {issue}")

        avg_score = sum(scores) / len(scores) if scores else 0
        passed = avg_score >= 70

        return {
            "passed": passed,
            "issues": issues,
            "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {
                "average_score": round(avg_score, 1),
                "scores": scores,
                "listing_details": listing_details,
                "listings_checked": len(listings),
            },
        }
