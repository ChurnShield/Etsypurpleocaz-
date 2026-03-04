# =============================================================================
# workflows/auto_listing_creator/tools/image_compositor.py
#
# Pillow-based image manipulation:
#   - composite_hero:         dark bg, fanned cards with shadows, band, badge
#   - copy_boilerplate_pages: copies and resizes boilerplate pages 3-5
# =============================================================================

import os
import shutil

from tools.design_constants import (
    EXPORT_DIR, IMG_W, IMG_H, BAND_H, TMPL_W, TMPL_H,
    DARK_BG_RGB, BOILERPLATE_PAGES,
)


def _create_rich_background(w, h):
    """Create a rich dark background with subtle gradient and ambient glow."""
    from PIL import Image, ImageDraw, ImageFilter
    import random

    bg = Image.new("RGBA", (w, h), (10, 8, 14, 255))

    # Warm ambient glow from top-center (simulates studio lighting)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r in range(600, 0, -4):
        alpha = int(6 * (r / 600))
        glow_draw.ellipse(
            [w // 2 - r * 2, -r, w // 2 + r * 2, r * 2],
            fill=(201, 168, 76, alpha),
        )
    bg = Image.alpha_composite(bg, glow)

    # Subtle bottom-up gradient (dark to slightly less dark)
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(grad)
    for y in range(h):
        frac = y / h
        a = int(25 * frac)
        grad_draw.line([(0, y), (w, y)], fill=(15, 12, 20, a))
    bg = Image.alpha_composite(bg, grad)

    # Noise texture for depth
    noise = Image.new("L", (w // 4, h // 4))
    noise_data = [random.randint(0, 8) for _ in range((w // 4) * (h // 4))]
    noise.putdata(noise_data)
    noise = noise.resize((w, h), Image.BILINEAR)
    noise_rgba = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    noise_rgba.putalpha(noise)
    bg = Image.alpha_composite(bg, noise_rgba)

    return bg


def composite_hero(template_path, band_path, badge_path, safe_title):
    """Composite a premium hero image (page 1) with rich background,
    dramatic shadows, and professional card layout."""
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

    # Product showcase area (above the band)
    showcase_h = IMG_H - BAND_H

    # Start with a rich textured background
    hero = _create_rich_background(IMG_W, IMG_H)

    template = Image.open(template_path).convert("RGBA")

    # Slightly boost contrast on the template for more visual punch
    enhancer = ImageEnhance.Contrast(template)
    template = enhancer.enhance(1.1)

    showcase_cy = showcase_h // 2
    showcase_cx = IMG_W // 2

    # 3 fanned cards — front card dominates, back cards provide depth
    # (scale, rotation, x-offset, y-offset, is_back_card)
    cards = [
        (0.60, 15, -180, -120, True),    # Back-left
        (0.64, -11, 200, -60, True),     # Back-right
        (0.92, 1.5, 0, 80, False),       # Front-center (dominant)
    ]

    for scale, rot, ox, oy, is_back in cards:
        card_w = int(TMPL_W * scale)
        card_h = int(TMPL_H * scale)
        card = template.resize((card_w, card_h), Image.LANCZOS)

        # Darken back cards to simulate the reverse side
        if is_back:
            dark_overlay = Image.new("RGBA", (card_w, card_h), (18, 16, 22, 180))
            card = Image.alpha_composite(card, dark_overlay)

        # Create dramatic drop shadow
        shadow_expand = 60
        shadow = Image.new(
            "RGBA",
            (card_w + shadow_expand * 2, card_h + shadow_expand * 2),
            (0, 0, 0, 0),
        )
        shadow_fill = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 130))
        shadow.paste(shadow_fill, (shadow_expand + 12, shadow_expand + 18))
        shadow = shadow.filter(ImageFilter.GaussianBlur(30))
        shadow_rot = shadow.rotate(
            rot, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

        # Add subtle edge glow (gold reflection)
        glow_expand = 8
        edge_glow = Image.new(
            "RGBA",
            (card_w + glow_expand * 2, card_h + glow_expand * 2),
            (0, 0, 0, 0),
        )
        glow_fill = Image.new(
            "RGBA", (card_w, card_h), (201, 168, 76, 15),
        )
        edge_glow.paste(glow_fill, (glow_expand, glow_expand))
        edge_glow = edge_glow.filter(ImageFilter.GaussianBlur(8))
        edge_glow_rot = edge_glow.rotate(
            rot, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

        card_rot = card.rotate(
            rot, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

        cx = showcase_cx + ox - card_rot.width // 2
        cy = showcase_cy + oy - card_rot.height // 2
        sx = showcase_cx + ox - shadow_rot.width // 2
        sy = showcase_cy + oy - shadow_rot.height // 2
        gx = showcase_cx + ox - edge_glow_rot.width // 2
        gy = showcase_cy + oy - edge_glow_rot.height // 2

        hero.paste(shadow_rot, (sx, sy), shadow_rot)
        hero.paste(edge_glow_rot, (gx, gy), edge_glow_rot)
        hero.paste(card_rot, (cx, cy), card_rot)

    # Paste bottom band
    band = Image.open(band_path).convert("RGBA")
    hero.paste(band, (0, IMG_H - BAND_H), band)

    # Paste badge with shadow
    badge = Image.open(badge_path).convert("RGBA")
    badge_mask = Image.new("L", badge.size, 0)
    badge_draw = ImageDraw.Draw(badge_mask)
    badge_draw.ellipse([0, 0, badge.width - 1, badge.height - 1], fill=255)
    badge_final = Image.new("RGBA", badge.size, (0, 0, 0, 0))
    badge_final.paste(badge, mask=badge_mask)

    # Badge shadow
    badge_shadow = Image.new("RGBA", (badge.width + 20, badge.height + 20), (0, 0, 0, 0))
    bs_draw = ImageDraw.Draw(badge_shadow)
    bs_draw.ellipse([5, 5, badge.width + 15, badge.height + 15], fill=(0, 0, 0, 80))
    badge_shadow = badge_shadow.filter(ImageFilter.GaussianBlur(10))

    badge_x = IMG_W - badge.width - 140
    badge_y = IMG_H - BAND_H - badge.height // 2
    hero.paste(badge_shadow, (badge_x - 10, badge_y + 4), badge_shadow)
    hero.paste(badge_final, (badge_x, badge_y), badge_final)

    # Save as RGB PNG
    hero_rgb = hero.convert("RGB")
    path = os.path.join(EXPORT_DIR, f"{safe_title}_page1.png")
    hero_rgb.save(path, "PNG")
    hero_rgb.close()
    hero.close()
    template.close()
    return path


def copy_boilerplate_pages(safe_title):
    """Copy and resize boilerplate pages 3-5, returning list of paths."""
    from PIL import Image

    paths = []
    for page_num in (3, 4, 5):
        bp_src = BOILERPLATE_PAGES.get(page_num)
        if bp_src and os.path.exists(bp_src):
            dst = os.path.join(EXPORT_DIR, f"{safe_title}_page{page_num}.png")
            shutil.copy2(bp_src, dst)

            bp_img = Image.open(dst)
            if bp_img.size != (IMG_W, IMG_H):
                bp_img = bp_img.resize((IMG_W, IMG_H), Image.LANCZOS)
                bp_img.save(dst, "PNG")
                bp_img.close()

            paths.append(dst)
            print(f"       Page {page_num}: boilerplate copied", flush=True)
        else:
            print(f"       Page {page_num}: boilerplate MISSING", flush=True)

    return paths
