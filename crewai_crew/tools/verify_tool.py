"""
verify_tool.py — Tools for verification, file I/O, and sprint contract.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from crewai.tools import tool

PROJECT = Path("/root/NEW-AI-PROJECT")


def _run(cmd: list, timeout: int = 120) -> dict:
    result = subprocess.run(
        cmd, cwd=str(PROJECT), capture_output=True, timeout=timeout
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace"),
        "stderr": result.stderr.decode("utf-8", errors="replace"),
    }


def _refresh_etsy_token() -> str:
    """Refresh and return Etsy access token inline."""
    import urllib.request, urllib.parse
    from dotenv import load_dotenv
    load_dotenv(PROJECT / ".env")
    ks = os.environ["ETSY_API_KEYSTRING"]
    ss = os.environ["ETSY_SHARED_SECRET"]
    tf = PROJECT / "workflows/etsy_analytics/etsy_tokens.json"
    tokens = json.loads(tf.read_text())
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": ks,
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token", data=data, method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", f"{ks}:{ss}")
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
    tf.write_text(json.dumps(resp, indent=2))
    return resp["access_token"]


@tool("run_verify")
def run_verify(listing_id: str) -> str:
    """
    Run verify_listing.py on an Etsy listing.

    Always uses --bundle flag (mega bundles are £39.99, not £2.99).
    Refreshes the Etsy OAuth token first to prevent 401 errors.
    Returns PASS/FAIL with full verification report.

    Args:
        listing_id: The numeric Etsy listing ID as a string.
    """
    _refresh_etsy_token()
    r = _run(["python3", "scripts/verify_listing.py", listing_id, "--bundle"])
    passed = r["exit_code"] == 0
    return (
        f"VERIFY: {'PASS' if passed else 'FAIL'} (exit {r['exit_code']})\n"
        f"{'=' * 60}\n"
        f"{r['stdout']}\n"
        + (f"STDERR:\n{r['stderr']}\n" if r["stderr"].strip() else "")
    )


@tool("run_evaluate")
def run_evaluate(listing_id: str) -> str:
    """
    Run evaluate_listing.py on an Etsy listing.

    Checks for: duplicate images (perceptual hash), hero quality (text-only
    detection, min 2000px), and variant coverage (dark/light mix).
    Refreshes the Etsy OAuth token first.
    Returns PASS/FAIL with full evaluation report.

    Args:
        listing_id: The numeric Etsy listing ID as a string.
    """
    _refresh_etsy_token()
    r = _run(["python3", "scripts/evaluate_listing.py", listing_id], timeout=180)
    passed = r["exit_code"] == 0
    return (
        f"EVALUATE: {'PASS' if passed else 'FAIL'} (exit {r['exit_code']})\n"
        f"{'=' * 60}\n"
        f"{r['stdout']}\n"
        + (f"STDERR:\n{r['stderr']}\n" if r["stderr"].strip() else "")
    )


@tool("read_file")
def read_file(path: str) -> str:
    """
    Read and return the contents of a file.
    Use this to read configs/niches/sample_niche.json before creating a new config.

    Args:
        path: Relative path from project root (e.g. 'configs/niches/sample_niche.json').
    """
    full = PROJECT / path
    if not full.exists():
        return f"ERROR: File not found: {full}"
    return full.read_text(encoding="utf-8")


def _sanitize_json_string(content: str) -> str:
    """
    Fix invalid control characters embedded inside JSON string values.
    Gemini Flash sometimes emits literal newlines/tabs inside strings.
    Walks char-by-char: inside a string, replaces raw \\n/\\r/\\t with escapes.
    Then re-dumps via json.loads/dumps to guarantee canonical formatting.
    """
    result = []
    in_string = False
    i = 0
    while i < len(content):
        c = content[i]
        if in_string:
            if c == '\\':
                result.append(c)
                if i + 1 < len(content):
                    result.append(content[i + 1])
                i += 2
                continue
            elif c == '"':
                in_string = False
                result.append(c)
            elif c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            else:
                result.append(c)
        else:
            if c == '"':
                in_string = True
                result.append(c)
            else:
                result.append(c)
        i += 1
    fixed = ''.join(result)
    # Re-parse and re-dump to catch any remaining structural issues
    parsed = json.loads(fixed)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


@tool("write_file")
def write_file(path: str, content: str) -> str:
    """
    Write content to a file, creating parent directories as needed.
    Use this to write niche JSON configs and sprint contract files.

    Args:
        path:    Relative path from project root (e.g. 'configs/niches/nail_tech.json').
        content: Full file content as a string.
    """
    full = PROJECT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    if path.endswith(".json"):
        try:
            content = _sanitize_json_string(content)
        except (json.JSONDecodeError, Exception) as e:
            return f"ERROR: JSON sanitization failed for {path}: {e}\nContent preview:\n{content[:500]}"
    full.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {full}"


@tool("write_sprint_contract")
def write_sprint_contract(slug: str, listing_id: str,
                           factory_passed: bool, hero_passed: bool,
                           verify_passed: bool, evaluate_passed: bool,
                           notes: str = "") -> str:
    """
    Write the sprint contract checklist for a completed niche build.

    Saves to outputs/{slug}/sprint_contract.md.
    Returns the path and a PASS/FAIL summary.

    Args:
        slug:             Niche slug (e.g. 'nail_tech').
        listing_id:       Etsy draft listing ID.
        factory_passed:   True if niche_template_factory.py exited 0.
        hero_passed:      True if hero_pipeline_v3.py exited 0.
        verify_passed:    True if verify_listing.py exited 0.
        evaluate_passed:  True if evaluate_listing.py exited 0.
        notes:            Any extra notes or failure details.
    """
    def tick(b): return "✅" if b else "❌"

    all_pass = all([factory_passed, hero_passed, verify_passed, evaluate_passed])

    contract = f"""# Sprint Contract — {slug}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Listing: #{listing_id}
Result: **{"ALL CHECKS PASSED" if all_pass else "FAILED — review items below"}**

## Definition of Done

- {tick(factory_passed)} All templates in config rendered to PNG
- {tick(factory_passed)} All PNGs uploaded to DO Spaces (HTTP 200 verified)
- {tick(factory_passed)} Delivery PDF generated with correct template count
- {tick(factory_passed)} Etsy DRAFT listing created with correct price (£39.99)
- {tick(factory_passed)} 7 listing images uploaded (ranks 1–7)
- {tick(factory_passed)} Delivery PDF attached to listing
- {tick(hero_passed)}    Hero image built (device mockups + perspective cards)
- {tick(hero_passed)}    Hero uploaded to DO Spaces and set as rank 1
- {tick(verify_passed)}  verify_listing.py PASSES (tags, price, images, PDF)
- {tick(evaluate_passed)} evaluate_listing.py PASSES (no dupes, hero quality, variant coverage)

## Next Step

{"Andy can review and activate the draft listing manually." if all_pass else "Fix the failing items above, then re-run the relevant scripts."}
{("Etsy draft: https://www.etsy.com/listing/" + listing_id) if listing_id else ""}

## Notes

{notes or "None."}
"""

    out = PROJECT / "outputs" / slug / "sprint_contract.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(contract, encoding="utf-8")

    return (
        f"Sprint contract written → {out}\n"
        f"RESULT: {'ALL PASS' if all_pass else 'FAILED'}\n\n"
        + contract
    )
