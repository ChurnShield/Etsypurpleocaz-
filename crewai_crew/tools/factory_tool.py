"""
factory_tool.py — Tools that wrap the template factory and hero pipeline.
"""

import json
import os
import re
import subprocess
from pathlib import Path

from crewai.tools import tool

PROJECT = Path("/root/NEW-AI-PROJECT")


def _run(cmd: list, stdin_data: bytes = None, timeout: int = 600) -> dict:
    """Run a subprocess, return {exit_code, stdout, stderr}."""
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT),
        input=stdin_data,
        capture_output=True,
        timeout=timeout,
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace"),
        "stderr": result.stderr.decode("utf-8", errors="replace"),
    }


@tool("run_template_factory")
def run_template_factory(config_path: str) -> str:
    """
    Run the niche template factory pipeline.

    Takes a path to a niche JSON config file (e.g. configs/niches/nail_tech.json).
    Renders all templates, uploads to DO Spaces, generates delivery PDF,
    creates an Etsy DRAFT listing (state: draft — NOT activated), uploads 7 listing
    images, and attaches the delivery PDF.

    Returns stdout + stderr, exit code, and the Etsy listing ID extracted from output.
    Always passes --bundle to disable price enforcement (mega bundles are £39.99).
    """
    r = _run(["python3", "scripts/niche_template_factory.py", config_path], timeout=600)

    # Extract listing ID from output line: "COMPLETE — Draft #4480000000"
    listing_id = None
    for pattern in [r"COMPLETE — Draft #(\d+)", r"Draft created: #(\d+)"]:
        m = re.search(pattern, r["stdout"])
        if m:
            listing_id = m.group(1)
            break

    header = (
        f"EXIT CODE: {r['exit_code']}\n"
        f"LISTING ID: {listing_id or 'NOT FOUND — check stdout'}\n"
        f"{'=' * 60}\n"
        f"STDOUT:\n{r['stdout']}\n"
    )
    if r["stderr"].strip():
        header += f"STDERR:\n{r['stderr']}\n"
    return header


@tool("run_hero_pipeline")
def run_hero_pipeline(config_path: str, listing_id: str) -> str:
    """
    Build a "wow" hero image for the listing using hero_pipeline_v3.py.

    Reads the niche config to determine slug and accent colour, generates an
    Ideogram lifestyle background, composites iPad + phone device mockups and
    perspective-printed cards, uploads to DO Spaces, then automatically replaces
    rank 1 on the Etsy listing (auto-confirms — no manual prompt needed).

    Args:
        config_path: Path to the niche JSON config (same file used by factory).
        listing_id:  Etsy listing ID string returned by run_template_factory.
    """
    # Load config to get slug + primary colour
    cfg_full = PROJECT / config_path
    with open(cfg_full) as f:
        cfg = json.load(f)

    slug = cfg["niche"]["slug"]
    palette = cfg.get("palette", {})
    primary = palette.get("primary", [13, 92, 99])
    accent = ",".join(str(c) for c in primary)

    templates_dir = f"outputs/{slug}/"
    output_path   = f"outputs/{slug}/listing/hero_v3.png"

    cmd = [
        "python3", "scripts/hero_pipeline_v3.py",
        "--niche",         slug,
        "--templates-dir", templates_dir,
        "--output",        output_path,
        "--listing-id",    listing_id,
        "--accent",        accent,
    ]

    # Auto-confirm the Etsy replace prompt by sending newline to stdin
    r = _run(cmd, stdin_data=b"\n", timeout=300)

    return (
        f"EXIT CODE: {r['exit_code']}\n"
        f"NICHE: {slug} | ACCENT: {accent} | LISTING: #{listing_id}\n"
        f"{'=' * 60}\n"
        f"STDOUT:\n{r['stdout']}\n"
        + (f"STDERR:\n{r['stderr']}\n" if r["stderr"].strip() else "")
    )
