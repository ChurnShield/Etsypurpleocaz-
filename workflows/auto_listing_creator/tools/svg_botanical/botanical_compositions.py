# =============================================================================
# botanical_compositions.py
#
# Composition functions that combine primitives into complete botanical designs.
# Each function takes an svgwrite.Drawing and adds elements to it.
# All designs target a 1000x1000 viewBox centered at (500, 500).
# =============================================================================

import math
import svgwrite

from . import botanical_primitives as bp

STROKE = "#000000"
STROKE_W = 2
FILL = "none"
CX, CY = 500, 500  # Canvas center

_PATH_STYLE = {"fill": FILL, "stroke": STROKE, "stroke_width": STROKE_W,
               "stroke_linecap": "round", "stroke_linejoin": "round"}


def _add_path(dwg, group, d):
    """Add a single path to a group with standard styling."""
    group.add(dwg.path(d=d, **_PATH_STYLE))


def _add_paths(dwg, group, paths):
    """Add multiple paths to a group."""
    for d in paths:
        _add_path(dwg, group, d)


def _g(dwg, tx=0, ty=0, rotate=0, scale=1.0):
    """Create a transform group."""
    parts = []
    if tx != 0 or ty != 0:
        parts.append(f"translate({tx:.1f},{ty:.1f})")
    if rotate != 0:
        parts.append(f"rotate({rotate})")
    if scale != 1.0:
        parts.append(f"scale({scale})")
    return dwg.g(transform=" ".join(parts)) if parts else dwg.g()


# ── Roses ────────────────────────────────────────────────────────────────────

def rose_open(dwg, cx=CX, cy=CY, size=1.0):
    """Full open rose, top-down view. Spiral center + layered petals."""
    root = _g(dwg, cx, cy, scale=size)
    # Spiral center
    _add_path(dwg, root, bp.center_spiral(turns=2, max_radius=15))
    # Inner petals (5, small)
    for i in range(5):
        angle = i * 72 + 10
        g = _g(dwg, rotate=angle)
        _add_path(dwg, g, bp.petal_teardrop(length=50, width=22))
        root.add(g)
    # Middle petals (7, medium)
    for i in range(7):
        angle = i * (360 / 7) + 25
        rad = math.radians(angle)
        tx = math.cos(rad) * 20
        ty = math.sin(rad) * 20
        g = _g(dwg, tx, ty, rotate=angle)
        _add_path(dwg, g, bp.petal_teardrop(length=70, width=30))
        root.add(g)
    # Outer petals (9, large)
    for i in range(9):
        angle = i * 40 + 5
        rad = math.radians(angle)
        tx = math.cos(rad) * 40
        ty = math.sin(rad) * 40
        g = _g(dwg, tx, ty, rotate=angle)
        _add_path(dwg, g, bp.petal_round(radius=35))
        root.add(g)
    dwg.add(root)


def rose_side(dwg, cx=CX, cy=CY, size=1.0):
    """Side-view rose with visible petals and calyx."""
    root = _g(dwg, cx, cy, scale=size)
    # Cup shape (outer petals visible from side)
    for i, (sx, rot) in enumerate([
        (1, -20), (1, -5), (1, 10), (1, 25),
        (-1, 20), (-1, 5), (-1, -10), (-1, -25),
    ]):
        g = _g(dwg, sx * (i % 4) * 8, -10, rotate=rot)
        _add_path(dwg, g, bp.petal_tulip(length=60 + i * 5, width=25 + i * 2))
        root.add(g)
    # Inner spiral peek
    g = _g(dwg, 0, -40)
    _add_path(dwg, g, bp.center_spiral(turns=1.5, max_radius=10))
    root.add(g)
    # Stem
    g = _g(dwg, 0, 30)
    _add_path(dwg, g, bp.stem_straight(length=180))
    root.add(g)
    # Calyx (small pointed leaves at base)
    for angle in (-30, 0, 30):
        g = _g(dwg, 0, 30, rotate=angle)
        _add_path(dwg, g, bp.leaf_olive(length=25, width=6))
        root.add(g)
    dwg.add(root)


def rose_bud(dwg, cx=CX, cy=CY, size=1.0):
    """Closed rosebud on a stem."""
    root = _g(dwg, cx, cy, scale=size)
    # Bud (overlapping petals)
    for angle in (-15, 0, 15):
        g = _g(dwg, 0, -80, rotate=angle)
        _add_path(dwg, g, bp.petal_tulip(length=45, width=18))
        root.add(g)
    # Calyx
    for angle in (-25, 0, 25):
        g = _g(dwg, 0, -55, rotate=angle + 180)
        _add_path(dwg, g, bp.leaf_olive(length=30, width=7))
        root.add(g)
    # Stem
    _add_path(dwg, root, bp.stem_curved(length=200, curve=25))
    # Leaves on stem
    for i, (a, y_off) in enumerate([(-40, -60), (35, -120)]):
        g = _g(dwg, 0, y_off, rotate=a)
        outline, vein = bp.leaf_simple(length=55, width=18)
        _add_path(dwg, g, outline)
        _add_path(dwg, g, vein)
        root.add(g)
    dwg.add(root)


def rose_stem_single(dwg, cx=CX, cy=CY, size=1.0):
    """Single rose bloom on a long curved stem with leaves."""
    root = _g(dwg, cx, cy + 100, scale=size)
    # Stem
    _add_path(dwg, root, bp.stem_curved(length=350, curve=30))
    # Rose at top
    g = _g(dwg, 0, -350)
    _add_path(dwg, g, bp.center_spiral(turns=2, max_radius=12))
    for i in range(6):
        sg = _g(dwg, rotate=i * 60)
        _add_path(dwg, sg, bp.petal_teardrop(length=45, width=20))
        g.add(sg)
    for i in range(8):
        sg = _g(dwg, rotate=i * 45 + 20)
        _add_path(dwg, sg, bp.petal_round(radius=28))
        g.add(sg)
    root.add(g)
    # Leaves
    for y_off, angle, sz in [(-120, -35, 60), (-200, 30, 50), (-280, -25, 45)]:
        g = _g(dwg, 0, y_off, rotate=angle)
        outline, vein = bp.leaf_simple(length=sz, width=sz * 0.35)
        _add_path(dwg, g, outline)
        _add_path(dwg, g, vein)
        root.add(g)
    dwg.add(root)


def rose_bouquet_pair(dwg, cx=CX, cy=CY, size=1.0):
    """Two roses with intertwined stems."""
    root = _g(dwg, cx, cy + 80, scale=size)
    for side, curve in [(-1, -30), (1, 30)]:
        sg = _g(dwg, side * 40, 0)
        _add_path(dwg, sg, bp.stem_curved(length=280, curve=curve))
        # Rose bloom
        bg = _g(dwg, 0, -280)
        _add_path(dwg, bg, bp.center_spiral(turns=1.8, max_radius=10))
        for i in range(5):
            pg = _g(dwg, rotate=i * 72 + side * 10)
            _add_path(dwg, pg, bp.petal_teardrop(length=40, width=18))
            bg.add(pg)
        for i in range(7):
            pg = _g(dwg, rotate=i * 51 + 15)
            _add_path(dwg, pg, bp.petal_round(radius=25))
            bg.add(pg)
        sg.add(bg)
        # Leaves
        for y_off, la in [(-100, side * -30), (-180, side * 25)]:
            lg = _g(dwg, 0, y_off, rotate=la)
            o, v = bp.leaf_simple(length=50, width=17)
            _add_path(dwg, lg, o)
            _add_path(dwg, lg, v)
            sg.add(lg)
        root.add(sg)
    dwg.add(root)


def rose_climbing(dwg, cx=CX, cy=CY, size=1.0):
    """Climbing rose vine with multiple small blooms."""
    root = _g(dwg, cx, cy + 150, scale=size)
    _add_path(dwg, root, bp.stem_vine(length=400, waves=5, amplitude=40))
    positions = [
        (-30, -80, 0.6), (25, -160, 0.5), (-20, -240, 0.7),
        (30, -320, 0.55), (-10, -380, 0.45),
    ]
    for bx, by, bs in positions:
        bg = _g(dwg, bx, by, scale=bs)
        _add_path(dwg, bg, bp.center_spiral(turns=1.5, max_radius=8))
        for i in range(5):
            pg = _g(dwg, rotate=i * 72)
            _add_path(dwg, pg, bp.petal_teardrop(length=35, width=15))
            bg.add(pg)
        root.add(bg)
    # Scattered leaves
    for lx, ly, la in [(15, -50, 20), (-25, -130, -25), (20, -200, 30),
                        (-15, -290, -20), (25, -360, 15)]:
        lg = _g(dwg, lx, ly, rotate=la)
        o, v = bp.leaf_simple(length=35, width=12)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


# ── Wildflowers ──────────────────────────────────────────────────────────────

def daisy(dwg, cx=CX, cy=CY, size=1.0, petals=12, with_stem=True):
    """Classic daisy with elongated petals around center circle."""
    root = _g(dwg, cx, cy + (50 if with_stem else 0), scale=size)
    flower_y = -180 if with_stem else 0
    fg = _g(dwg, 0, flower_y)
    _add_path(dwg, fg, bp.center_circle(radius=15))
    for i in range(petals):
        pg = _g(dwg, rotate=i * (360 / petals))
        _add_path(dwg, pg, bp.petal_elongated(length=55, width=14))
        fg.add(pg)
    root.add(fg)
    if with_stem:
        _add_path(dwg, root, bp.stem_curved(length=200, curve=15))
        for y_off, a in [(-80, -30), (-140, 25)]:
            lg = _g(dwg, 0, y_off, rotate=a)
            o, v = bp.leaf_simple(length=45, width=15)
            _add_path(dwg, lg, o)
            _add_path(dwg, lg, v)
            root.add(lg)
    dwg.add(root)


def poppy(dwg, cx=CX, cy=CY, size=1.0, with_stem=True):
    """Poppy flower with 4-5 large rounded petals."""
    root = _g(dwg, cx, cy + (50 if with_stem else 0), scale=size)
    flower_y = -160 if with_stem else 0
    fg = _g(dwg, 0, flower_y)
    _add_path(dwg, fg, bp.center_dots(count=8, spread=8))
    for i in range(5):
        pg = _g(dwg, rotate=i * 72)
        _add_path(dwg, pg, bp.petal_round(radius=45))
        fg.add(pg)
    root.add(fg)
    if with_stem:
        _add_path(dwg, root, bp.stem_curved(length=180, curve=-20))
    dwg.add(root)


def lavender(dwg, cx=CX, cy=CY, size=1.0):
    """Lavender sprig with tiny buds along curved stem."""
    root = _g(dwg, cx, cy + 120, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=320, curve=20))
    # Buds along top portion
    for i in range(12):
        t = 0.1 + i * 0.06
        y = -320 * t
        side = 1 if i % 2 == 0 else -1
        bx = side * 8
        bg = _g(dwg, bx, y, rotate=side * 15)
        _add_path(dwg, bg, bp.petal_teardrop(length=12, width=6))
        root.add(bg)
    # Small leaves at base
    for a in (-35, 35):
        lg = _g(dwg, 0, -40, rotate=a)
        _add_path(dwg, lg, bp.leaf_olive(length=40, width=8))
        root.add(lg)
    dwg.add(root)


def chamomile(dwg, cx=CX, cy=CY, size=1.0):
    """Chamomile with many thin petals and raised center."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=18))
    _add_path(dwg, fg, bp.center_dots(count=6, spread=10))
    for i in range(16):
        pg = _g(dwg, rotate=i * 22.5)
        _add_path(dwg, pg, bp.petal_elongated(length=40, width=10))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=190))
    # Feathery leaves
    for y_off, a in [(-60, -30), (-100, 25), (-140, -20)]:
        lg = _g(dwg, 0, y_off, rotate=a)
        _add_path(dwg, lg, bp.leaf_fern_segment(length=30, width=8))
        root.add(lg)
    dwg.add(root)


def sunflower(dwg, cx=CX, cy=CY, size=1.0):
    """Sunflower with double ring of petals and dotted center."""
    root = _g(dwg, cx, cy + 80, scale=size)
    fg = _g(dwg, 0, -220)
    # Large dotted center
    _add_path(dwg, fg, bp.center_circle(radius=35))
    _add_path(dwg, fg, bp.center_dots(count=8, spread=18))
    _add_path(dwg, fg, bp.center_dots(count=5, spread=10))
    # Inner petals
    for i in range(14):
        pg = _g(dwg, rotate=i * (360 / 14))
        _add_path(dwg, pg, bp.petal_pointed(length=50, width=16))
        fg.add(pg)
    # Outer petals (offset)
    for i in range(14):
        pg = _g(dwg, rotate=i * (360 / 14) + 13)
        _add_path(dwg, pg, bp.petal_pointed(length=60, width=18))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=240))
    for y_off, a, sz in [(-80, -35, 70), (-160, 30, 60)]:
        lg = _g(dwg, 0, y_off, rotate=a)
        o, v = bp.leaf_simple(length=sz, width=sz * 0.4)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def cosmos(dwg, cx=CX, cy=CY, size=1.0):
    """Cosmos flower with 8 notched petals."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=10))
    for i in range(8):
        pg = _g(dwg, rotate=i * 45)
        _add_path(dwg, pg, bp.petal_teardrop(length=55, width=22))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_curved(length=190, curve=-15))
    lg = _g(dwg, 0, -80, rotate=-25)
    _add_path(dwg, lg, bp.leaf_fern_segment(length=35, width=10))
    root.add(lg)
    dwg.add(root)


def forget_me_not(dwg, cx=CX, cy=CY, size=1.0):
    """Cluster of tiny 5-petal forget-me-nots on branching stem."""
    root = _g(dwg, cx, cy + 100, scale=size)
    branches = bp.stem_branch(length=250, branch_count=4, branch_len=50, side=0)
    _add_paths(dwg, root, branches)
    positions = [(0, -250), (-30, -180), (25, -200), (-20, -130), (30, -150)]
    for fx, fy in positions:
        fg = _g(dwg, fx, fy, scale=0.6)
        _add_path(dwg, fg, bp.center_circle(radius=4))
        for i in range(5):
            pg = _g(dwg, rotate=i * 72)
            _add_path(dwg, pg, bp.petal_round(radius=10))
            fg.add(pg)
        root.add(fg)
    dwg.add(root)


def wildflower_mixed_a(dwg, cx=CX, cy=CY, size=1.0):
    """Mixed wildflower arrangement: daisy + poppy + small blooms."""
    root = _g(dwg, cx, cy + 80, scale=size)
    # Central daisy
    fg = _g(dwg, 0, -200)
    _add_path(dwg, fg, bp.center_circle(radius=12))
    for i in range(10):
        pg = _g(dwg, rotate=i * 36)
        _add_path(dwg, pg, bp.petal_elongated(length=40, width=11))
        fg.add(pg)
    root.add(fg)
    # Side poppy
    pg = _g(dwg, 60, -160, scale=0.7)
    _add_path(dwg, pg, bp.center_dots(count=5, spread=6))
    for i in range(4):
        ptg = _g(dwg, rotate=i * 90)
        _add_path(dwg, ptg, bp.petal_round(radius=30))
        pg.add(ptg)
    root.add(pg)
    # Stems
    _add_path(dwg, root, bp.stem_curved(length=220, curve=10))
    sg = _g(dwg, 20, -30)
    _add_path(dwg, sg, bp.stem_curved(length=180, curve=30))
    root.add(sg)
    # Leaves
    for y_off, a in [(-60, -25), (-120, 30)]:
        lg = _g(dwg, 0, y_off, rotate=a)
        o, v = bp.leaf_simple(length=40, width=14)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


# ── Birth Flowers ────────────────────────────────────────────────────────────

def _birth_flower(dwg, cx, cy, size, petal_fn, petal_count, petal_args,
                  center_fn, center_args, with_stem=True, leaf_count=2):
    """Generic birth flower builder."""
    root = _g(dwg, cx, cy + (50 if with_stem else 0), scale=size)
    flower_y = -170 if with_stem else 0
    fg = _g(dwg, 0, flower_y)
    _add_path(dwg, fg, center_fn(**center_args))
    for i in range(petal_count):
        pg = _g(dwg, rotate=i * (360 / petal_count))
        _add_path(dwg, pg, petal_fn(**petal_args))
        fg.add(pg)
    root.add(fg)
    if with_stem:
        _add_path(dwg, root, bp.stem_curved(length=190, curve=12))
        for idx in range(leaf_count):
            y_off = -60 - idx * 60
            a = (-30 if idx % 2 == 0 else 30)
            lg = _g(dwg, 0, y_off, rotate=a)
            o, v = bp.leaf_simple(length=40, width=14)
            _add_path(dwg, lg, o)
            _add_path(dwg, lg, v)
            root.add(lg)
    dwg.add(root)


def birth_carnation(dwg, cx=CX, cy=CY, size=1.0):
    """January: Carnation - ruffled petals."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    for ring, (count, r_sz) in enumerate([(8, 25), (10, 35), (12, 40)]):
        for i in range(count):
            pg = _g(dwg, rotate=i * (360 / count) + ring * 15)
            _add_path(dwg, pg, bp.petal_round(radius=r_sz - ring * 3))
            fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=190))
    dwg.add(root)


def birth_violet(dwg, cx=CX, cy=CY, size=1.0):
    """February: Violet."""
    _birth_flower(dwg, cx, cy, size,
                  bp.petal_round, 5, {"radius": 25},
                  bp.center_circle, {"radius": 6})


def birth_daffodil(dwg, cx=CX, cy=CY, size=1.0):
    """March: Daffodil - 6 petals + central trumpet."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=20))
    _add_path(dwg, fg, bp.center_circle(radius=12))
    for i in range(6):
        pg = _g(dwg, rotate=i * 60)
        _add_path(dwg, pg, bp.petal_pointed(length=55, width=22))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_curved(length=190, curve=15))
    dwg.add(root)


def birth_sweet_pea(dwg, cx=CX, cy=CY, size=1.0):
    """April: Sweet Pea."""
    _birth_flower(dwg, cx, cy, size,
                  bp.petal_tulip, 4, {"length": 45, "width": 25},
                  bp.center_circle, {"radius": 5})


def birth_lily_of_valley(dwg, cx=CX, cy=CY, size=1.0):
    """May: Lily of the Valley - bell-shaped flowers along arching stem."""
    root = _g(dwg, cx, cy + 100, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=300, curve=35))
    for i in range(7):
        t = 0.15 + i * 0.1
        y = -300 * t
        side = 1 if i % 2 == 0 else -1
        bg = _g(dwg, side * 15, y, rotate=side * 20)
        _add_path(dwg, bg, bp.petal_tulip(length=18, width=12))
        root.add(bg)
    # Two large leaves
    for a in (-15, 15):
        lg = _g(dwg, a * 3, 0, rotate=a)
        o, v = bp.leaf_simple(length=120, width=35)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def birth_rose(dwg, cx=CX, cy=CY, size=1.0):
    """June: Rose (delegates to rose_open)."""
    rose_open(dwg, cx, cy, size * 0.8)


def birth_larkspur(dwg, cx=CX, cy=CY, size=1.0):
    """July: Larkspur - tall spike of flowers."""
    root = _g(dwg, cx, cy + 120, scale=size)
    _add_path(dwg, root, bp.stem_straight(length=350))
    for i in range(10):
        y = -80 - i * 28
        side = 1 if i % 2 == 0 else -1
        fg = _g(dwg, side * 10, y, scale=0.5 + 0.05 * (10 - i))
        for j in range(5):
            pg = _g(dwg, rotate=j * 72)
            _add_path(dwg, pg, bp.petal_pointed(length=25, width=10))
            fg.add(pg)
        root.add(fg)
    dwg.add(root)


def birth_gladiolus(dwg, cx=CX, cy=CY, size=1.0):
    """August: Gladiolus."""
    root = _g(dwg, cx, cy + 130, scale=size)
    _add_path(dwg, root, bp.stem_straight(length=380))
    for i in range(8):
        y = -100 - i * 35
        fg = _g(dwg, 0, y, scale=0.6 + 0.04 * (8 - i))
        for j in range(6):
            pg = _g(dwg, rotate=j * 60)
            _add_path(dwg, pg, bp.petal_tulip(length=30, width=16))
            fg.add(pg)
        root.add(fg)
    dwg.add(root)


def birth_aster(dwg, cx=CX, cy=CY, size=1.0):
    """September: Aster - many thin petals."""
    _birth_flower(dwg, cx, cy, size,
                  bp.petal_elongated, 20, {"length": 40, "width": 8},
                  bp.center_dots, {"count": 8, "spread": 8})


def birth_marigold(dwg, cx=CX, cy=CY, size=1.0):
    """October: Marigold - dense ruffled layers."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=10))
    for ring in range(4):
        count = 8 + ring * 3
        r_off = ring * 5
        for i in range(count):
            pg = _g(dwg, rotate=i * (360 / count) + ring * 12)
            _add_path(dwg, pg, bp.petal_teardrop(
                length=25 + ring * 8, width=10 + ring * 2))
            fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=190))
    dwg.add(root)


def birth_chrysanthemum(dwg, cx=CX, cy=CY, size=1.0):
    """November: Chrysanthemum - many layered thin petals."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=8))
    for ring in range(5):
        count = 10 + ring * 2
        for i in range(count):
            pg = _g(dwg, rotate=i * (360 / count) + ring * 9)
            _add_path(dwg, pg, bp.petal_elongated(
                length=20 + ring * 10, width=5 + ring))
            fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=190))
    dwg.add(root)


def birth_narcissus(dwg, cx=CX, cy=CY, size=1.0):
    """December: Narcissus - 6 petals + central corona."""
    root = _g(dwg, cx, cy + 50, scale=size)
    fg = _g(dwg, 0, -170)
    _add_path(dwg, fg, bp.center_circle(radius=22))
    _add_path(dwg, fg, bp.center_circle(radius=14))
    _add_path(dwg, fg, bp.center_dots(count=5, spread=6))
    for i in range(6):
        pg = _g(dwg, rotate=i * 60)
        _add_path(dwg, pg, bp.petal_teardrop(length=50, width=22))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_curved(length=190, curve=-10))
    dwg.add(root)


# ── Botanical Stems ──────────────────────────────────────────────────────────

def eucalyptus_branch(dwg, cx=CX, cy=CY, size=1.0, leaf_count=8):
    """Eucalyptus branch with round alternating leaves."""
    root = _g(dwg, cx, cy + 130, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=350, curve=20))
    for i in range(leaf_count):
        t = 0.15 + i * 0.1
        y = -350 * t
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 5, y, rotate=side * 40)
        o, v = bp.leaf_round(length=28 - i, width=20 - i)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def fern_frond(dwg, cx=CX, cy=CY, size=1.0, segments=10):
    """Fern frond with alternating leaflets."""
    root = _g(dwg, cx, cy + 150, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=380, curve=15))
    for i in range(segments):
        t = 0.1 + i * 0.08
        y = -380 * t
        seg_size = 25 - i * 1.2
        if seg_size < 8:
            seg_size = 8
        for side in (1, -1):
            lg = _g(dwg, side * 3, y, rotate=side * 50)
            _add_path(dwg, lg, bp.leaf_fern_segment(
                length=seg_size, width=seg_size * 0.35))
            root.add(lg)
    dwg.add(root)


def olive_branch(dwg, cx=CX, cy=CY, size=1.0, leaf_count=10):
    """Olive branch with narrow alternating leaves."""
    root = _g(dwg, cx, cy + 120, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=340, curve=-25))
    for i in range(leaf_count):
        t = 0.1 + i * 0.08
        y = -340 * t
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 4, y, rotate=side * 45)
        _add_path(dwg, lg, bp.leaf_olive(length=25 - i * 0.5, width=7))
        root.add(lg)
    dwg.add(root)


def monstera_leaf(dwg, cx=CX, cy=CY, size=1.0):
    """Single monstera leaf on stem."""
    root = _g(dwg, cx, cy + 100, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=200, curve=15))
    lg = _g(dwg, 0, -200)
    outline, holes, vein = bp.leaf_monstera(radius=120)
    _add_path(dwg, lg, outline)
    _add_path(dwg, lg, holes)
    _add_path(dwg, lg, vein)
    root.add(lg)
    dwg.add(root)


def palm_leaf_single(dwg, cx=CX, cy=CY, size=1.0):
    """Single palm leaf fan."""
    root = _g(dwg, cx, cy + 100, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=180, curve=10))
    fg = _g(dwg, 0, -180)
    fronds = bp.leaf_palm(length=150, fronds=9)
    _add_paths(dwg, fg, fronds)
    root.add(fg)
    dwg.add(root)


def ivy_vine(dwg, cx=CX, cy=CY, size=1.0):
    """Trailing ivy vine with heart-shaped leaves."""
    root = _g(dwg, cx, cy + 150, scale=size)
    _add_path(dwg, root, bp.stem_vine(length=400, waves=5, amplitude=35))
    for i in range(8):
        t = 0.08 + i * 0.11
        y = -400 * t
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 20, y, rotate=side * 30, scale=0.7 - i * 0.03)
        # Heart-shaped leaf (modified monstera without holes)
        o, _, v = bp.leaf_monstera(radius=30)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


# ── Mini / Tiny Designs ──────────────────────────────────────────────────────

def mini_rose(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny rose for finger/ear tattoo."""
    root = _g(dwg, cx, cy, scale=size * 0.5)
    _add_path(dwg, root, bp.center_spiral(turns=1.5, max_radius=10))
    for i in range(5):
        pg = _g(dwg, rotate=i * 72)
        _add_path(dwg, pg, bp.petal_teardrop(length=30, width=14))
        root.add(pg)
    dwg.add(root)


def mini_daisy(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny daisy."""
    root = _g(dwg, cx, cy, scale=size * 0.45)
    _add_path(dwg, root, bp.center_circle(radius=8))
    for i in range(8):
        pg = _g(dwg, rotate=i * 45)
        _add_path(dwg, pg, bp.petal_elongated(length=30, width=9))
        root.add(pg)
    dwg.add(root)


def mini_leaf(dwg, cx=CX, cy=CY, size=1.0):
    """Single tiny leaf."""
    root = _g(dwg, cx, cy, scale=size * 0.5)
    o, v = bp.leaf_simple(length=50, width=18)
    _add_path(dwg, root, o)
    _add_path(dwg, root, v)
    dwg.add(root)


def mini_bud(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny flower bud."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    for a in (-10, 0, 10):
        pg = _g(dwg, rotate=a)
        _add_path(dwg, pg, bp.petal_tulip(length=30, width=14))
        root.add(pg)
    sg = _g(dwg, 0, 15)
    _add_path(dwg, sg, bp.stem_straight(length=50))
    root.add(sg)
    dwg.add(root)


def mini_berry(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny berry branch."""
    root = _g(dwg, cx, cy, scale=size * 0.5)
    _add_path(dwg, root, bp.berry_cluster(count=3, spread=12))
    sg = _g(dwg, 0, 15)
    _add_path(dwg, sg, bp.stem_straight(length=40))
    root.add(sg)
    dwg.add(root)


def mini_star(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny star flower."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.center_circle(radius=5))
    for i in range(5):
        pg = _g(dwg, rotate=i * 72)
        _add_path(dwg, pg, bp.petal_pointed(length=25, width=10))
        root.add(pg)
    dwg.add(root)


def mini_sprig(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny botanical sprig."""
    root = _g(dwg, cx, cy, scale=size * 0.45)
    _add_path(dwg, root, bp.stem_curved(length=80, curve=10))
    for i in range(4):
        y = -20 - i * 18
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 3, y, rotate=side * 40)
        _add_path(dwg, lg, bp.leaf_olive(length=18, width=5))
        root.add(lg)
    dwg.add(root)


def mini_tulip(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny tulip."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    fg = _g(dwg, 0, -40)
    for a in (-12, 0, 12):
        pg = _g(dwg, rotate=a)
        _add_path(dwg, pg, bp.petal_tulip(length=35, width=16))
        fg.add(pg)
    root.add(fg)
    _add_path(dwg, root, bp.stem_straight(length=60))
    dwg.add(root)


def mini_fern(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny fern curl."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.vine_tendril(length=50, coils=1.5))
    for i in range(3):
        y = -10 - i * 15
        lg = _g(dwg, 5, y, rotate=30)
        _add_path(dwg, lg, bp.leaf_fern_segment(length=15, width=5))
        root.add(lg)
    dwg.add(root)


def mini_crescent(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny crescent moon with flower."""
    root = _g(dwg, cx, cy, scale=size * 0.45)
    # Crescent arc
    r = 40
    _add_path(dwg, root,
              f"M {-r * 0.7:.1f},{-r:.1f} "
              f"A {r},{r} 0 1,1 {-r * 0.7:.1f},{r:.1f} "
              f"A {r * 0.7},{r * 0.7} 0 1,0 {-r * 0.7:.1f},{-r:.1f}")
    # Tiny flower on crescent
    fg = _g(dwg, r * 0.3, 0, scale=0.6)
    _add_path(dwg, fg, bp.center_circle(radius=5))
    for i in range(5):
        pg = _g(dwg, rotate=i * 72)
        _add_path(dwg, pg, bp.petal_teardrop(length=18, width=8))
        fg.add(pg)
    root.add(fg)
    dwg.add(root)


def mini_heart_botanical(dwg, cx=CX, cy=CY, size=1.0):
    """Heart shape made from two leaves."""
    root = _g(dwg, cx, cy, scale=size * 0.5)
    for side in (1, -1):
        lg = _g(dwg, side * 2, -5, rotate=side * -30)
        o, v = bp.leaf_simple(length=55, width=20)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def mini_lavender(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny lavender sprig."""
    root = _g(dwg, cx, cy, scale=size * 0.35)
    _add_path(dwg, root, bp.stem_straight(length=80))
    for i in range(6):
        y = -20 - i * 10
        side = 1 if i % 2 == 0 else -1
        bg = _g(dwg, side * 5, y, rotate=side * 15)
        _add_path(dwg, bg, bp.petal_teardrop(length=8, width=4))
        root.add(bg)
    dwg.add(root)


def mini_sunflower(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny sunflower."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.center_circle(radius=12))
    _add_path(dwg, root, bp.center_dots(count=5, spread=6))
    for i in range(10):
        pg = _g(dwg, rotate=i * 36)
        _add_path(dwg, pg, bp.petal_pointed(length=30, width=10))
        root.add(pg)
    dwg.add(root)


def mini_eucalyptus(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny eucalyptus sprig."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.stem_straight(length=70))
    for i in range(5):
        y = -15 - i * 12
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 3, y, rotate=side * 40)
        o, v = bp.leaf_round(length=16, width=12)
        _add_path(dwg, lg, o)
        root.add(lg)
    dwg.add(root)


def mini_wildflower(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny generic wildflower."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.center_circle(radius=6))
    for i in range(6):
        pg = _g(dwg, rotate=i * 60)
        _add_path(dwg, pg, bp.petal_teardrop(length=22, width=10))
        root.add(pg)
    sg = _g(dwg, 0, 10)
    _add_path(dwg, sg, bp.stem_straight(length=40))
    root.add(sg)
    dwg.add(root)


def mini_vine(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny vine segment."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.stem_vine(length=80, waves=2, amplitude=15))
    for i in range(3):
        y = -20 - i * 25
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 8, y, rotate=side * 30)
        o, v = bp.leaf_simple(length=20, width=8)
        _add_path(dwg, lg, o)
        root.add(lg)
    dwg.add(root)


def mini_poppy(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny poppy."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.center_dots(count=4, spread=4))
    for i in range(4):
        pg = _g(dwg, rotate=i * 90)
        _add_path(dwg, pg, bp.petal_round(radius=22))
        root.add(pg)
    dwg.add(root)


def mini_cherry_blossom(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny cherry blossom."""
    root = _g(dwg, cx, cy, scale=size * 0.45)
    _add_path(dwg, root, bp.center_circle(radius=5))
    line, head = bp.stamen(length=12, head_radius=2)
    for i in range(5):
        pg = _g(dwg, rotate=i * 72)
        _add_path(dwg, pg, bp.petal_round(radius=18))
        sg = _g(dwg, rotate=i * 72 + 36)
        _add_path(dwg, sg, line)
        _add_path(dwg, sg, head)
        root.add(sg)
        root.add(pg)
    dwg.add(root)


def mini_cosmos(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny cosmos flower."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.center_circle(radius=6))
    for i in range(8):
        pg = _g(dwg, rotate=i * 45)
        _add_path(dwg, pg, bp.petal_teardrop(length=28, width=12))
        root.add(pg)
    dwg.add(root)


def mini_olive(dwg, cx=CX, cy=CY, size=1.0):
    """Tiny olive branch."""
    root = _g(dwg, cx, cy, scale=size * 0.4)
    _add_path(dwg, root, bp.stem_curved(length=70, curve=-10))
    for i in range(5):
        y = -15 - i * 12
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 3, y, rotate=side * 45)
        _add_path(dwg, lg, bp.leaf_olive(length=16, width=5))
        root.add(lg)
    dwg.add(root)


# ── Wreaths & Frames ────────────────────────────────────────────────────────

def wreath_circle(dwg, cx=CX, cy=CY, size=1.0, elements=16):
    """Circular wreath of leaves and small flowers."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 160
    for i in range(elements):
        angle = 360 * i / elements
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        if i % 4 == 0:
            # Small flower every 4th position
            _add_path(dwg, lg, bp.center_circle(radius=5))
            for j in range(5):
                pg = _g(dwg, rotate=j * 72)
                _add_path(dwg, pg, bp.petal_teardrop(length=15, width=7))
                lg.add(pg)
        else:
            o, v = bp.leaf_simple(length=35, width=12)
            _add_path(dwg, lg, o)
            _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def wreath_eucalyptus(dwg, cx=CX, cy=CY, size=1.0):
    """Eucalyptus wreath with round leaves."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 155
    for i in range(20):
        angle = 360 * i / 20
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        o, v = bp.leaf_round(length=25, width=18)
        _add_path(dwg, lg, o)
        root.add(lg)
    dwg.add(root)


def wreath_berry(dwg, cx=CX, cy=CY, size=1.0):
    """Wreath with berries and small leaves."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 150
    for i in range(24):
        angle = 360 * i / 24
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        if i % 3 == 0:
            _add_path(dwg, lg, bp.berry_cluster(count=3, spread=8))
        else:
            _add_path(dwg, lg, bp.leaf_olive(length=22, width=6))
        root.add(lg)
    dwg.add(root)


def half_wreath_top(dwg, cx=CX, cy=CY, size=1.0):
    """Half wreath (top arc) of mixed botanicals."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 160
    for i in range(12):
        angle = 180 + 15 * i  # Top half
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        if i % 3 == 0:
            _add_path(dwg, lg, bp.center_circle(radius=4))
            for j in range(5):
                pg = _g(dwg, rotate=j * 72)
                _add_path(dwg, pg, bp.petal_teardrop(length=14, width=6))
                lg.add(pg)
        else:
            o, v = bp.leaf_simple(length=30, width=10)
            _add_path(dwg, lg, o)
            _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def half_wreath_side(dwg, cx=CX, cy=CY, size=1.0):
    """Half wreath (left arc)."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 160
    for i in range(12):
        angle = 90 + 15 * i
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        o, v = bp.leaf_simple(length=28, width=10)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def corner_frame_botanical(dwg, cx=CX, cy=CY, size=1.0):
    """L-shaped corner frame with botanical elements."""
    root = _g(dwg, cx, cy, scale=size)
    # Horizontal branch
    for i in range(8):
        x = -150 + i * 38
        lg = _g(dwg, x, 150, rotate=-10 + i * 3)
        o, v = bp.leaf_simple(length=28, width=10)
        _add_path(dwg, lg, o)
        root.add(lg)
    # Vertical branch
    for i in range(8):
        y = 150 - i * 38
        lg = _g(dwg, -150, y, rotate=80 + i * 3)
        o, v = bp.leaf_simple(length=28, width=10)
        _add_path(dwg, lg, o)
        root.add(lg)
    # Corner flower
    fg = _g(dwg, -150, 150, scale=0.6)
    _add_path(dwg, fg, bp.center_circle(radius=6))
    for i in range(6):
        pg = _g(dwg, rotate=i * 60)
        _add_path(dwg, pg, bp.petal_teardrop(length=20, width=9))
        fg.add(pg)
    root.add(fg)
    dwg.add(root)


def corner_frame_vine(dwg, cx=CX, cy=CY, size=1.0):
    """Vine corner frame."""
    root = _g(dwg, cx, cy, scale=size)
    # L-shaped vine path
    _add_path(dwg, root,
              f"M {-150},150 Q {-150},{-50} {-150},{-150} Q {-50},{-150} 150,{-150}")
    for i in range(6):
        x = -150 + i * 50
        lg = _g(dwg, x, -150, rotate=20)
        _add_path(dwg, lg, bp.leaf_olive(length=20, width=5))
        root.add(lg)
    for i in range(6):
        y = 150 - i * 50
        lg = _g(dwg, -150, y, rotate=-70)
        _add_path(dwg, lg, bp.leaf_olive(length=20, width=5))
        root.add(lg)
    dwg.add(root)


def crescent_wreath(dwg, cx=CX, cy=CY, size=1.0):
    """Crescent moon shape wreath."""
    root = _g(dwg, cx, cy, scale=size)
    radius = 150
    for i in range(10):
        angle = 200 + 16 * i
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        lg = _g(dwg, tx, ty, rotate=angle + 90)
        if i % 3 == 0:
            _add_path(dwg, lg, bp.center_circle(radius=4))
            for j in range(5):
                pg = _g(dwg, rotate=j * 72)
                _add_path(dwg, pg, bp.petal_teardrop(length=12, width=5))
                lg.add(pg)
        else:
            o, v = bp.leaf_simple(length=25, width=9)
            _add_path(dwg, lg, o)
            root.add(lg)
            continue
        root.add(lg)
    dwg.add(root)


# ── Bouquets ─────────────────────────────────────────────────────────────────

def _bouquet_base(dwg, root, stem_count=5, splay=40):
    """Add bundled stems for bouquet base."""
    for i in range(stem_count):
        offset = -splay + (2 * splay / max(stem_count - 1, 1)) * i
        _add_path(dwg, root,
                  f"M {offset * 0.3:.1f},0 L {offset:.1f},{-250}")


def bouquet_roses(dwg, cx=CX, cy=CY, size=1.0):
    """Bouquet of 3 roses with greenery."""
    root = _g(dwg, cx, cy + 120, scale=size)
    _bouquet_base(dwg, root, stem_count=5, splay=50)
    positions = [(0, -280, 0.7), (-50, -250, 0.55), (45, -245, 0.6)]
    for fx, fy, fs in positions:
        fg = _g(dwg, fx, fy, scale=fs)
        _add_path(dwg, fg, bp.center_spiral(turns=1.5, max_radius=8))
        for i in range(5):
            pg = _g(dwg, rotate=i * 72)
            _add_path(dwg, pg, bp.petal_teardrop(length=35, width=15))
            fg.add(pg)
        for i in range(7):
            pg = _g(dwg, rotate=i * 51 + 20)
            _add_path(dwg, pg, bp.petal_round(radius=22))
            fg.add(pg)
        root.add(fg)
    # Leaves
    for lx, ly, la in [(-60, -180, -35), (55, -170, 30), (-40, -120, -20)]:
        lg = _g(dwg, lx, ly, rotate=la)
        o, v = bp.leaf_simple(length=45, width=15)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def bouquet_wildflowers(dwg, cx=CX, cy=CY, size=1.0):
    """Mixed wildflower bouquet."""
    root = _g(dwg, cx, cy + 120, scale=size)
    _bouquet_base(dwg, root, stem_count=7, splay=60)
    # Daisy top-center
    fg = _g(dwg, 0, -290, scale=0.5)
    _add_path(dwg, fg, bp.center_circle(radius=10))
    for i in range(10):
        pg = _g(dwg, rotate=i * 36)
        _add_path(dwg, pg, bp.petal_elongated(length=35, width=10))
        fg.add(pg)
    root.add(fg)
    # Poppy left
    pg2 = _g(dwg, -55, -260, scale=0.45)
    _add_path(dwg, pg2, bp.center_dots(count=5, spread=5))
    for i in range(4):
        ptg = _g(dwg, rotate=i * 90)
        _add_path(dwg, ptg, bp.petal_round(radius=28))
        pg2.add(ptg)
    root.add(pg2)
    # Small blooms
    for fx, fy, fs in [(50, -255, 0.4), (-30, -230, 0.35), (35, -225, 0.3)]:
        fg2 = _g(dwg, fx, fy, scale=fs)
        _add_path(dwg, fg2, bp.center_circle(radius=5))
        for i in range(6):
            pg3 = _g(dwg, rotate=i * 60)
            _add_path(dwg, pg3, bp.petal_teardrop(length=20, width=9))
            fg2.add(pg3)
        root.add(fg2)
    # Filler leaves
    for lx, ly, la in [(-50, -190, -30), (60, -180, 25), (0, -150, 10)]:
        lg = _g(dwg, lx, ly, rotate=la)
        o, v = bp.leaf_simple(length=40, width=13)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def bouquet_mixed_large(dwg, cx=CX, cy=CY, size=1.0):
    """Large mixed bouquet with 7 flowers and abundant greenery."""
    root = _g(dwg, cx, cy + 130, scale=size)
    _bouquet_base(dwg, root, stem_count=9, splay=70)
    # Flowers at different heights/positions
    flower_specs = [
        (0, -300, 0.6, "rose"), (-60, -270, 0.5, "daisy"),
        (55, -265, 0.5, "poppy"), (-30, -240, 0.4, "bud"),
        (40, -235, 0.4, "star"), (-55, -220, 0.35, "bud"),
        (25, -210, 0.35, "star"),
    ]
    for fx, fy, fs, ftype in flower_specs:
        fg = _g(dwg, fx, fy, scale=fs)
        if ftype == "rose":
            _add_path(dwg, fg, bp.center_spiral(turns=1.5, max_radius=8))
            for i in range(5):
                pg = _g(dwg, rotate=i * 72)
                _add_path(dwg, pg, bp.petal_teardrop(length=35, width=15))
                fg.add(pg)
            for i in range(7):
                pg = _g(dwg, rotate=i * 51 + 20)
                _add_path(dwg, pg, bp.petal_round(radius=22))
                fg.add(pg)
        elif ftype == "daisy":
            _add_path(dwg, fg, bp.center_circle(radius=8))
            for i in range(10):
                pg = _g(dwg, rotate=i * 36)
                _add_path(dwg, pg, bp.petal_elongated(length=30, width=8))
                fg.add(pg)
        elif ftype == "poppy":
            _add_path(dwg, fg, bp.center_dots(count=5, spread=5))
            for i in range(4):
                pg = _g(dwg, rotate=i * 90)
                _add_path(dwg, pg, bp.petal_round(radius=25))
                fg.add(pg)
        elif ftype == "bud":
            for a in (-8, 0, 8):
                pg = _g(dwg, rotate=a)
                _add_path(dwg, pg, bp.petal_tulip(length=22, width=10))
                fg.add(pg)
        else:  # star
            _add_path(dwg, fg, bp.center_circle(radius=4))
            for i in range(5):
                pg = _g(dwg, rotate=i * 72)
                _add_path(dwg, pg, bp.petal_pointed(length=20, width=8))
                fg.add(pg)
        root.add(fg)
    # Dense greenery
    for lx, ly, la in [(-70, -200, -40), (65, -190, 35), (-45, -160, -25),
                        (50, -150, 20), (-30, -120, -15), (30, -110, 10)]:
        lg = _g(dwg, lx, ly, rotate=la)
        o, v = bp.leaf_simple(length=35, width=12)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def bouquet_minimal(dwg, cx=CX, cy=CY, size=1.0):
    """Minimal 3-stem bouquet with one flower and buds."""
    root = _g(dwg, cx, cy + 100, scale=size)
    _bouquet_base(dwg, root, stem_count=3, splay=25)
    # Central flower
    fg = _g(dwg, 0, -260, scale=0.6)
    _add_path(dwg, fg, bp.center_circle(radius=8))
    for i in range(6):
        pg = _g(dwg, rotate=i * 60)
        _add_path(dwg, pg, bp.petal_teardrop(length=30, width=13))
        fg.add(pg)
    root.add(fg)
    # Side buds
    for sx, sy in [(-20, -240), (22, -235)]:
        bg = _g(dwg, sx, sy, scale=0.4)
        for a in (-8, 0, 8):
            pg = _g(dwg, rotate=a)
            _add_path(dwg, pg, bp.petal_tulip(length=25, width=12))
            bg.add(pg)
        root.add(bg)
    dwg.add(root)


# ── Decorative ───────────────────────────────────────────────────────────────

def single_leaf_detailed(dwg, cx=CX, cy=CY, size=1.0):
    """Large detailed leaf with vein pattern."""
    root = _g(dwg, cx, cy, scale=size)
    o, v = bp.leaf_simple(length=200, width=70)
    _add_path(dwg, root, o)
    veins = bp.leaf_vein_lines(length=200, vein_count=6)
    _add_paths(dwg, root, veins)
    dwg.add(root)


def berry_branch(dwg, cx=CX, cy=CY, size=1.0):
    """Branch with berry clusters."""
    root = _g(dwg, cx, cy + 80, scale=size)
    _add_path(dwg, root, bp.stem_curved(length=250, curve=-20))
    for i in range(4):
        t = 0.2 + i * 0.2
        y = -250 * t
        side = 1 if i % 2 == 0 else -1
        bg = _g(dwg, side * 15, y, rotate=side * 20)
        _add_path(dwg, bg, bp.berry_cluster(count=4, spread=10))
        root.add(bg)
    # Small leaves between clusters
    for i in range(3):
        y = -250 * (0.3 + i * 0.2)
        side = -1 if i % 2 == 0 else 1
        lg = _g(dwg, side * 10, y, rotate=side * 35)
        _add_path(dwg, lg, bp.leaf_olive(length=22, width=6))
        root.add(lg)
    dwg.add(root)


def vine_trailing(dwg, cx=CX, cy=CY, size=1.0):
    """Trailing decorative vine."""
    root = _g(dwg, cx, cy + 150, scale=size)
    _add_path(dwg, root, bp.stem_vine(length=380, waves=5, amplitude=35))
    for i in range(7):
        t = 0.08 + i * 0.12
        y = -380 * t
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 18, y, rotate=side * 35)
        o, v = bp.leaf_simple(length=28, width=10)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    # Tendrils
    for ty in (-100, -220, -340):
        tg = _g(dwg, 20, ty, rotate=30)
        _add_path(dwg, tg, bp.vine_tendril(length=25, coils=1))
        root.add(tg)
    dwg.add(root)


def branch_simple(dwg, cx=CX, cy=CY, size=1.0):
    """Simple branch with scattered leaves."""
    root = _g(dwg, cx, cy + 100, scale=size)
    branches = bp.stem_branch(length=280, branch_count=4, branch_len=70, side=0)
    _add_paths(dwg, root, branches)
    for i in range(6):
        y = -60 - i * 40
        side = 1 if i % 2 == 0 else -1
        lg = _g(dwg, side * 30, y, rotate=side * 25)
        o, v = bp.leaf_simple(length=35, width=12)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)


def leaf_pair(dwg, cx=CX, cy=CY, size=1.0):
    """Symmetrical pair of leaves on short stem."""
    root = _g(dwg, cx, cy + 20, scale=size)
    _add_path(dwg, root, bp.stem_straight(length=100))
    for side in (1, -1):
        lg = _g(dwg, 0, -60, rotate=side * 40)
        o, v = bp.leaf_simple(length=80, width=28)
        _add_path(dwg, lg, o)
        _add_path(dwg, lg, v)
        root.add(lg)
    dwg.add(root)
