#!/usr/bin/env python3
"""
Generate product images using Nano Banana (Gemini AI).

This is the quality path — generates photorealistic product mockup images
via Google's Gemini AI instead of Pillow pixel-drawing.

Prerequisites:
    1. Get a free Gemini API key: https://aistudio.google.com/apikey
    2. Add to your .env file:  GEMINI_API_KEY=your-key-here

Usage:
    python scripts/generate_with_gemini.py
    python scripts/generate_with_gemini.py --product "appointment card" --niche tattoo
    python scripts/generate_with_gemini.py --product "gift certificate" --niche nail
"""

import os
import sys
import argparse

# Allow imports from project root and workflow tools
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_TOOLS = os.path.join(_ROOT, "workflows", "auto_listing_creator", "tools")
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "workflows", "auto_listing_creator"))

from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

from tools.gemini_image_client import generate_product_image, build_product_prompt
from tools.design_constants import EXPORT_DIR


def main():
    parser = argparse.ArgumentParser(description="Generate product images with Gemini AI")
    parser.add_argument("--product", default="appointment card",
                        help="Product type (default: appointment card)")
    parser.add_argument("--niche", default="tattoo",
                        help="Business niche (default: tattoo)")
    parser.add_argument("--theme", default="dark",
                        help="Theme (default: dark)")
    parser.add_argument("--model", default="",
                        help="Override Gemini model name")
    args = parser.parse_args()

    # ── Check API key ──
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your-gemini-api-key-here":
        print("=" * 60)
        print("  GEMINI API KEY REQUIRED")
        print("=" * 60)
        print()
        print("  Nano Banana needs a Gemini API key to generate images.")
        print()
        print("  Steps:")
        print("  1. Go to: https://aistudio.google.com/apikey")
        print("  2. Click 'Create API Key' (it's free)")
        print("  3. Add to your .env file:")
        print("     GEMINI_API_KEY=AIza...")
        print()
        print("  Then re-run this script.")
        print("=" * 60)
        return 1

    os.makedirs(EXPORT_DIR, exist_ok=True)

    # ── Build prompt ──
    print(f"\nProduct: {args.product}")
    print(f"Niche:   {args.niche}")
    print(f"Theme:   {args.theme}")
    print()

    prompt = build_product_prompt(
        product_type=args.product,
        niche=args.niche,
        theme=args.theme,
    )

    print("Prompt built. Sending to Gemini AI...")
    print(f"(prompt length: {len(prompt)} chars)")
    print()

    # ── Generate image ──
    result = generate_product_image(
        api_key=api_key,
        prompt=prompt,
        aspect_ratio="3:4",
        image_size="2K",
        max_retries=2,
        model=args.model or None,
    )

    if not result["success"]:
        print(f"\nFailed: {result['error']}")
        print()
        if "403" in str(result.get("error", "")):
            print("  A 403 error usually means:")
            print("  - Network/proxy blocking googleapis.com")
            print("  - API key doesn't have Gemini API enabled")
            print("  - Try from a different network (not behind a corporate proxy)")
        return 1

    # ── Save image ──
    model_used = result.get("model_used", "unknown")
    mime = result.get("mime_type", "image/png")
    ext = "png" if "png" in mime else "jpg"

    safe_product = args.product.replace(" ", "_")
    filename = f"gemini_{args.niche}_{safe_product}.{ext}"
    output_path = os.path.join(EXPORT_DIR, filename)

    with open(output_path, "wb") as f:
        f.write(result["image_bytes"])

    size_kb = len(result["image_bytes"]) / 1024
    print(f"\nSaved: {output_path}")
    print(f"Model: {model_used}")
    print(f"Size:  {size_kb:.0f} KB")
    print(f"Type:  {mime}")
    print()
    print("Open this file to view the AI-generated product image.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
