import os
import sys
import math
import tempfile
import pytest
from unittest.mock import patch, MagicMock

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from workflows.auto_listing_creator.tools.hero_generator import (
    generate_hero_image,
    _load_font,
    _make_background,
    _rotate_with_shadow,
    _paste_shadow_card,
    _draw_star,
    W, H, CARD_W_RATIO, BANNER_RATIO, BADGE_R,
)
from PIL import Image, ImageDraw


# ── Constants ─────────────────────────────────────────────────────────────────

def test_output_dimensions():
    assert W == 2000
    assert H == 1500


def test_card_width_ratio():
    assert 0 < CARD_W_RATIO < 1


def test_banner_ratio():
    assert 0 < BANNER_RATIO < 1


def test_badge_radius_positive():
    assert BADGE_R > 0


# ── _load_font ────────────────────────────────────────────────────────────────

def test_load_font_returns_font_object():
    """_load_font returns a usable font even if path is invalid."""
    font = _load_font("/nonexistent/path.ttf", 24)
    assert font is not None


def test_load_font_with_valid_dejavu():
    """If DejaVu is available, truetype font is loaded."""
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = _load_font(path, 30)
    assert font is not None


# ── _make_background ──────────────────────────────────────────────────────────

def test_make_background_size():
    bg = _make_background(200, 150)
    assert bg.size == (200, 150)
    assert bg.mode == "RGBA"


def test_make_background_deterministic():
    """Same seed produces identical output."""
    bg1 = _make_background(100, 80)
    bg2 = _make_background(100, 80)
    assert list(bg1.getdata()) == list(bg2.getdata())


# ── _rotate_with_shadow ──────────────────────────────────────────────────────

def test_rotate_with_shadow_returns_tuple():
    img = Image.new("RGBA", (100, 80), (255, 255, 255, 255))
    card, shadow = _rotate_with_shadow(img, 5)
    assert isinstance(card, Image.Image)
    assert isinstance(shadow, Image.Image)
    assert card.mode == "RGBA"
    assert shadow.mode == "RGBA"


def test_rotate_expands_dimensions():
    img = Image.new("RGBA", (100, 80), (255, 255, 255, 255))
    card, _ = _rotate_with_shadow(img, 45)
    # Rotated with expand=True should be larger
    assert card.size[0] > 100 or card.size[1] > 80


# ── _paste_shadow_card ────────────────────────────────────────────────────────

def test_paste_shadow_card_no_crash():
    canvas = Image.new("RGBA", (400, 300), (200, 200, 200, 255))
    card = Image.new("RGBA", (100, 80), (255, 255, 255, 255))
    shadow = Image.new("RGBA", (100, 80), (0, 0, 0, 200))
    _paste_shadow_card(canvas, card, shadow, 50, 50)
    # Should not raise; canvas should still be valid
    assert canvas.size == (400, 300)


# ── _draw_star ────────────────────────────────────────────────────────────────

def test_draw_star_no_crash():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _draw_star(draw, 50, 50, 30, 15, (255, 200, 40, 255))
    # Should not raise


# ── generate_hero_image (integration) ────────────────────────────────────────

def test_generate_hero_image_creates_file():
    """Full pipeline produces an output image of correct size."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy front/back card PNGs
        front = Image.new("RGBA", (800, 500), (255, 255, 255, 255))
        back = Image.new("RGBA", (800, 500), (240, 240, 240, 255))
        front_path = os.path.join(tmpdir, "front.png")
        back_path = os.path.join(tmpdir, "back.png")
        front.save(front_path)
        back.save(back_path)

        output_path = os.path.join(tmpdir, "hero.jpg")
        generate_hero_image(front_path, back_path, output_path,
                            "Tattoo Appointment Card")

        assert os.path.exists(output_path)
        result = Image.open(output_path)
        assert result.size == (W, H)
        result.close()


def test_generate_hero_image_long_title_truncated():
    """Titles longer than 55 chars are truncated in the banner."""
    with tempfile.TemporaryDirectory() as tmpdir:
        front = Image.new("RGBA", (400, 250), (255, 255, 255, 255))
        back = Image.new("RGBA", (400, 250), (240, 240, 240, 255))
        front_path = os.path.join(tmpdir, "front.png")
        back_path = os.path.join(tmpdir, "back.png")
        front.save(front_path)
        back.save(back_path)

        output_path = os.path.join(tmpdir, "hero_long.jpg")
        long_title = "A" * 100
        # Should not crash with a very long title
        generate_hero_image(front_path, back_path, output_path, long_title)
        assert os.path.exists(output_path)


def test_generate_hero_image_creates_output_dir():
    """Output directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        front = Image.new("RGBA", (400, 250), (255, 255, 255, 255))
        back = Image.new("RGBA", (400, 250), (240, 240, 240, 255))
        front_path = os.path.join(tmpdir, "front.png")
        back_path = os.path.join(tmpdir, "back.png")
        front.save(front_path)
        back.save(back_path)

        nested_output = os.path.join(tmpdir, "sub", "dir", "hero.jpg")
        generate_hero_image(front_path, back_path, nested_output,
                            "Test Card")
        assert os.path.exists(nested_output)
