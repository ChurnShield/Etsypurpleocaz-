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
    DARK_BG_RGB, BOILERPLATE_PAGES, BEIGE_RGB,
)


def composite_hero(template_path, band_path, badge_path, safe_title,
                    light_bg=False):
    """Composite the hero image (page 1).

    Args:
        light_bg: When True uses a warm beige/fabric background matching
                  the Etsy flat-lay mockup aesthetic instead of dark.
    """
    from PIL import Image, ImageDraw, ImageFilter

    bg_rgb = BEIGE_RGB if light_bg else DARK_BG_RGB
    hero = Image.new("RGBA", (IMG_W, IMG_H), bg_rgb + (255,))

    template = Image.open(template_path).convert("RGBA")

    # Product showcase area: y=0 to y=(IMG_H - BAND_H)
    showcase_h = IMG_H - BAND_H
    showcase_cy = showcase_h // 2
    showcase_cx = IMG_W // 2

    # 3 fanned card copies with subtle shadows (back to front)
    cards = [
        (0.65, 12, -120, -180),   # Back-left card
        (0.72, -8, 140, -40),     # Middle-right card
        (0.90, 3, 0, 100),        # Front-center card (largest)
    ]

    for scale, rot, ox, oy in cards:
        card_w = int(TMPL_W * scale)
        card_h = int(TMPL_H * scale)
        card = template.resize((card_w, card_h), Image.LANCZOS)

        shadow_expand = 40
        shadow = Image.new(
            "RGBA",
            (card_w + shadow_expand * 2, card_h + shadow_expand * 2),
            (0, 0, 0, 0),
        )
        shadow_fill = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 90))
        shadow.paste(shadow_fill, (shadow_expand + 8, shadow_expand + 8))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        shadow_rot = shadow.rotate(
            rot, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

        card_rot = card.rotate(
            rot, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0),
        )

        cx = showcase_cx + ox - card_rot.width // 2
        cy = showcase_cy + oy - card_rot.height // 2
        sx = showcase_cx + ox - shadow_rot.width // 2
        sy = showcase_cy + oy - shadow_rot.height // 2

        hero.paste(shadow_rot, (sx, sy), shadow_rot)
        hero.paste(card_rot, (cx, cy), card_rot)

    # Paste bottom band
    band = Image.open(band_path).convert("RGBA")
    hero.paste(band, (0, IMG_H - BAND_H), band)

    # Paste "EDIT IN CANVA" badge
    badge = Image.open(badge_path).convert("RGBA")
    badge_mask = Image.new("L", badge.size, 0)
    badge_draw = ImageDraw.Draw(badge_mask)
    badge_draw.ellipse([0, 0, badge.width - 1, badge.height - 1], fill=255)
    badge_final = Image.new("RGBA", badge.size, (0, 0, 0, 0))
    badge_final.paste(badge, mask=badge_mask)

    badge_x = IMG_W - badge.width - 120
    badge_y = IMG_H - BAND_H - badge.height // 2
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
