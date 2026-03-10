import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ImageQualityValidator(BaseValidator):
    """Validates hero images after Phase 3.

    Checks each product's hero image (page 1) for:
      - File exists and is over 100KB
      - Dimensions are exactly 2250x3000

    Returns pass/fail per image and an overall score.
    """

    MIN_FILE_SIZE_KB = 100
    EXPECTED_WIDTH = 2250
    EXPECTED_HEIGHT = 3000

    def validate(self, data, context=None):
        issues = []
        if not isinstance(data, dict):
            return {
                "passed": False, "issues": ["Not a dict"], "needs_more": False,
                "validator_name": self.get_name(), "metadata": {},
            }

        exports = data.get("exports", [])
        if not exports:
            return {
                "passed": False, "issues": ["No exports to validate"],
                "needs_more": False, "validator_name": self.get_name(),
                "metadata": {},
            }

        checked = 0
        passed_count = 0
        image_details = []

        for export in exports:
            if export.get("status") != "CREATED":
                continue

            png_paths = export.get("png_paths", [])
            if not png_paths:
                issues.append(f"[{export.get('title', '?')[:40]}] No images")
                image_details.append({
                    "title": export.get("title", "")[:60],
                    "passed": False,
                    "issues": ["No images produced"],
                })
                checked += 1
                continue

            hero_path = png_paths[0]
            img_issues = []
            checked += 1

            # 1. File exists and size check
            if not os.path.exists(hero_path):
                img_issues.append("Hero image file missing")
            else:
                file_size_kb = os.path.getsize(hero_path) / 1024
                if file_size_kb < self.MIN_FILE_SIZE_KB:
                    img_issues.append(
                        f"File size {file_size_kb:.0f}KB "
                        f"(minimum {self.MIN_FILE_SIZE_KB}KB)"
                    )

                # 2. Dimensions check (only if file exists)
                try:
                    from PIL import Image
                    with Image.open(hero_path) as img:
                        w, h = img.size
                    if w != self.EXPECTED_WIDTH or h != self.EXPECTED_HEIGHT:
                        img_issues.append(
                            f"Dimensions {w}x{h} "
                            f"(expected {self.EXPECTED_WIDTH}x{self.EXPECTED_HEIGHT})"
                        )
                except Exception as e:
                    img_issues.append(f"Cannot read image: {str(e)[:80]}")

            title_short = export.get("title", "")[:40]
            if img_issues:
                for issue in img_issues:
                    issues.append(f"[{title_short}] {issue}")
            else:
                passed_count += 1

            image_details.append({
                "title": export.get("title", "")[:60],
                "hero_path": hero_path,
                "passed": len(img_issues) == 0,
                "issues": img_issues,
            })

        pass_rate = passed_count / checked if checked > 0 else 0
        # Score: percentage of images that passed all checks
        score = round(pass_rate * 100, 1)
        passed = pass_rate >= 0.7

        return {
            "passed": passed,
            "issues": issues,
            "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {
                "score": score,
                "images_checked": checked,
                "images_passed": passed_count,
                "pass_rate": round(pass_rate, 3),
                "image_details": image_details,
            },
        }
