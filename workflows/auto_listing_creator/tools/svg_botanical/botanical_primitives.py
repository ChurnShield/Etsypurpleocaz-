# =============================================================================
# botanical_primitives.py
#
# ~30 reusable SVG path shape functions for fine-line botanical designs.
# Each function returns a path "d" string centered at origin (0, 0).
# Use SVG <g transform="translate(x,y) rotate(a) scale(s)"> to position.
#
# Style: stroke="#000000" stroke-width="2" fill="none"
# =============================================================================

import math


# ── Petals ───────────────────────────────────────────────────────────────────

def petal_teardrop(length=40, width=15):
    """Teardrop petal pointing upward. Classic for roses and generic flowers.
    Uses multi-segment bezier for a more organic, hand-drawn feel."""
    hl = length / 2
    hw = width / 2
    # More natural shape: slightly asymmetric with a bulge
    return (
        f"M 0,{-hl:.1f} "
        f"C {hw * 0.4:.1f},{-hl * 0.7:.1f} {hw * 1.05:.1f},{-hl * 0.2:.1f} "
        f"{hw * 0.95:.1f},{hl * 0.1:.1f} "
        f"C {hw * 0.85:.1f},{hl * 0.4:.1f} {hw * 0.4:.1f},{hl * 0.85:.1f} 0,{hl:.1f} "
        f"C {-hw * 0.4:.1f},{hl * 0.85:.1f} {-hw * 0.85:.1f},{hl * 0.4:.1f} "
        f"{-hw * 0.95:.1f},{hl * 0.1:.1f} "
        f"C {-hw * 1.05:.1f},{-hl * 0.2:.1f} {-hw * 0.4:.1f},{-hl * 0.7:.1f} 0,{-hl:.1f}"
    )


def petal_round(radius=20):
    """Nearly circular petal. Used in ranunculus and full blooms."""
    r = radius
    k = r * 0.552  # Bezier approximation of circle quadrant
    return (
        f"M 0,{-r:.1f} "
        f"C {k:.1f},{-r:.1f} {r:.1f},{-k:.1f} {r:.1f},0 "
        f"C {r:.1f},{k:.1f} {k:.1f},{r:.1f} 0,{r:.1f} "
        f"C {-k:.1f},{r:.1f} {-r:.1f},{k:.1f} {-r:.1f},0 "
        f"C {-r:.1f},{-k:.1f} {-k:.1f},{-r:.1f} 0,{-r:.1f}"
    )


def petal_elongated(length=50, width=12):
    """Long narrow petal for daisies and sunflowers. Tapered with slight swell."""
    hl = length / 2
    hw = width / 2
    return (
        f"M 0,{-hl:.1f} "
        f"C {hw * 0.3:.1f},{-hl * 0.8:.1f} {hw * 1.1:.1f},{-hl * 0.3:.1f} "
        f"{hw * 0.9:.1f},{0:.1f} "
        f"C {hw * 0.7:.1f},{hl * 0.4:.1f} {hw * 0.3:.1f},{hl * 0.9:.1f} 0,{hl:.1f} "
        f"C {-hw * 0.3:.1f},{hl * 0.9:.1f} {-hw * 0.7:.1f},{hl * 0.4:.1f} "
        f"{-hw * 0.9:.1f},{0:.1f} "
        f"C {-hw * 1.1:.1f},{-hl * 0.3:.1f} {-hw * 0.3:.1f},{-hl * 0.8:.1f} 0,{-hl:.1f}"
    )


def petal_pointed(length=45, width=18):
    """Pointed petal for lilies and star flowers. Wider belly, sharp tips."""
    hl = length / 2
    hw = width / 2
    return (
        f"M 0,{-hl:.1f} "
        f"C {hw * 0.8:.1f},{-hl * 0.3:.1f} {hw:.1f},{hl * 0.1:.1f} "
        f"{hw * 0.3:.1f},{hl * 0.6:.1f} "
        f"L 0,{hl:.1f} "
        f"L {-hw * 0.3:.1f},{hl * 0.6:.1f} "
        f"C {-hw:.1f},{hl * 0.1:.1f} {-hw * 0.8:.1f},{-hl * 0.3:.1f} 0,{-hl:.1f}"
    )


def petal_tulip(length=40, width=22):
    """Cup-shaped tulip petal. Wider at top, narrow at base."""
    hl = length / 2
    hw = width / 2
    return (
        f"M 0,{hl:.1f} "
        f"C {hw * 0.3:.1f},{hl * 0.3:.1f} {hw:.1f},{-hl * 0.2:.1f} "
        f"{hw * 0.8:.1f},{-hl:.1f} "
        f"C {hw * 0.3:.1f},{-hl * 0.8:.1f} {-hw * 0.3:.1f},{-hl * 0.8:.1f} "
        f"{-hw * 0.8:.1f},{-hl:.1f} "
        f"C {-hw:.1f},{-hl * 0.2:.1f} {-hw * 0.3:.1f},{hl * 0.3:.1f} 0,{hl:.1f}"
    )


# ── Leaves ───────────────────────────────────────────────────────────────────

def leaf_simple(length=60, width=20):
    """Pointed leaf with central vein and side veins. Returns (outline_d, vein_d)."""
    hl = length / 2
    hw = width / 2
    outline = (
        f"M 0,{-hl:.1f} "
        f"C {hw * 0.5:.1f},{-hl * 0.6:.1f} {hw * 1.1:.1f},{-hl * 0.15:.1f} "
        f"{hw * 0.95:.1f},{hl * 0.1:.1f} "
        f"C {hw * 0.8:.1f},{hl * 0.45:.1f} {hw * 0.3:.1f},{hl * 0.9:.1f} 0,{hl:.1f} "
        f"C {-hw * 0.3:.1f},{hl * 0.9:.1f} {-hw * 0.8:.1f},{hl * 0.45:.1f} "
        f"{-hw * 0.95:.1f},{hl * 0.1:.1f} "
        f"C {-hw * 1.1:.1f},{-hl * 0.15:.1f} {-hw * 0.5:.1f},{-hl * 0.6:.1f} 0,{-hl:.1f}"
    )
    # Central vein + side veins for detail
    veins = [f"M 0,{-hl:.1f} L 0,{hl:.1f}"]
    vein_count = max(3, int(length / 20))
    for i in range(1, vein_count + 1):
        y = -hl + length * i / (vein_count + 1)
        vl = hw * 0.6 * (1 - abs(2 * i / (vein_count + 1) - 1))
        veins.append(f"M 0,{y:.1f} L {vl:.1f},{y - vl * 0.4:.1f}")
        veins.append(f"M 0,{y:.1f} L {-vl:.1f},{y - vl * 0.4:.1f}")
    vein = " ".join(veins)
    return outline, vein


def leaf_round(length=35, width=25):
    """Round eucalyptus-style leaf. Returns (outline_d, vein_d)."""
    hl = length / 2
    hw = width / 2
    k = 0.6
    outline = (
        f"M 0,{-hl:.1f} "
        f"C {hw * k:.1f},{-hl:.1f} {hw:.1f},{-hl * 0.3:.1f} {hw:.1f},0 "
        f"C {hw:.1f},{hl * 0.5:.1f} {hw * 0.5:.1f},{hl:.1f} 0,{hl:.1f} "
        f"C {-hw * 0.5:.1f},{hl:.1f} {-hw:.1f},{hl * 0.5:.1f} {-hw:.1f},0 "
        f"C {-hw:.1f},{-hl * 0.3:.1f} {-hw * k:.1f},{-hl:.1f} 0,{-hl:.1f}"
    )
    vein = f"M 0,{-hl:.1f} L 0,{hl:.1f}"
    return outline, vein


def leaf_fern_segment(length=25, width=8):
    """Single fern frond segment. Asymmetric teardrop."""
    hl = length / 2
    hw = width
    outline = (
        f"M 0,{-hl:.1f} "
        f"C {hw * 0.6:.1f},{-hl * 0.3:.1f} {hw:.1f},{hl * 0.3:.1f} "
        f"{hw * 0.2:.1f},{hl:.1f} "
        f"L 0,{hl * 0.7:.1f} "
        f"L {-hw * 0.1:.1f},{hl:.1f} "
        f"C {-hw * 0.3:.1f},{hl * 0.2:.1f} {-hw * 0.2:.1f},{-hl * 0.3:.1f} "
        f"0,{-hl:.1f}"
    )
    return outline


def leaf_monstera(radius=80):
    """Heart-shaped monstera leaf with split. Returns (outline_d, holes_d, vein_d)."""
    r = radius
    outline = (
        f"M 0,{-r:.1f} "
        f"C {r * 0.7:.1f},{-r:.1f} {r:.1f},{-r * 0.3:.1f} {r * 0.9:.1f},{r * 0.2:.1f} "
        f"C {r * 0.8:.1f},{r * 0.7:.1f} {r * 0.4:.1f},{r:.1f} 0,{r * 0.8:.1f} "
        f"C {-r * 0.4:.1f},{r:.1f} {-r * 0.8:.1f},{r * 0.7:.1f} "
        f"{-r * 0.9:.1f},{r * 0.2:.1f} "
        f"C {-r:.1f},{-r * 0.3:.1f} {-r * 0.7:.1f},{-r:.1f} 0,{-r:.1f}"
    )
    # Characteristic splits (elongated holes)
    holes = []
    for side in (1, -1):
        ox = side * r * 0.35
        holes.append(
            f"M {ox:.1f},{-r * 0.1:.1f} "
            f"C {ox + side * r * 0.15:.1f},{-r * 0.15:.1f} "
            f"{ox + side * r * 0.15:.1f},{r * 0.25:.1f} "
            f"{ox:.1f},{r * 0.2:.1f} "
            f"C {ox - side * r * 0.05:.1f},{r * 0.15:.1f} "
            f"{ox - side * r * 0.05:.1f},{-r * 0.05:.1f} "
            f"{ox:.1f},{-r * 0.1:.1f}"
        )
    vein = f"M 0,{-r:.1f} L 0,{r * 0.8:.1f}"
    return outline, " ".join(holes), vein


def leaf_palm(length=120, fronds=7):
    """Fan palm leaf. Returns list of (frond_d) strings."""
    paths = []
    spread = 60  # degrees each side
    for i in range(fronds):
        angle = -spread + (2 * spread / max(fronds - 1, 1)) * i
        rad = math.radians(angle)
        ex = math.sin(rad) * length
        ey = -math.cos(rad) * length
        mx = ex * 0.5 + math.sin(rad + 0.1) * length * 0.1
        my = ey * 0.5
        paths.append(
            f"M 0,0 Q {mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}"
        )
    return paths


def leaf_olive(length=30, width=8):
    """Narrow olive leaf. Returns path d string."""
    hl = length / 2
    hw = width / 2
    return (
        f"M 0,{-hl:.1f} "
        f"C {hw:.1f},{-hl * 0.6:.1f} {hw:.1f},{hl * 0.6:.1f} 0,{hl:.1f} "
        f"C {-hw:.1f},{hl * 0.6:.1f} {-hw:.1f},{-hl * 0.6:.1f} 0,{-hl:.1f}"
    )


# ── Stems ────────────────────────────────────────────────────────────────────

def stem_straight(length=200):
    """Straight vertical stem. Bottom at origin, extends upward."""
    return f"M 0,0 L 0,{-length:.1f}"


def stem_curved(length=200, curve=40):
    """Gently curved stem. S-curve or C-curve depending on sign."""
    return (
        f"M 0,0 "
        f"C {curve:.1f},{-length * 0.3:.1f} "
        f"{-curve * 0.5:.1f},{-length * 0.7:.1f} "
        f"0,{-length:.1f}"
    )


def stem_branch(length=180, branch_count=3, branch_len=60, side=1):
    """Main stem with side branches. side=1 right, side=-1 left, side=0 both."""
    paths = [f"M 0,0 L 0,{-length:.1f}"]
    for i in range(branch_count):
        y = -length * (0.3 + 0.5 * i / max(branch_count - 1, 1))
        s = side if side != 0 else (1 if i % 2 == 0 else -1)
        bx = s * branch_len
        by = y - branch_len * 0.5
        paths.append(
            f"M 0,{y:.1f} Q {bx * 0.5:.1f},{y:.1f} {bx:.1f},{by:.1f}"
        )
    return paths


def stem_vine(length=250, waves=4, amplitude=30):
    """Wavy vine stem using connected quadratic beziers."""
    seg = length / waves
    parts = [f"M 0,0"]
    for i in range(waves):
        y1 = -(i * seg + seg / 2)
        y2 = -((i + 1) * seg)
        direction = 1 if i % 2 == 0 else -1
        cx = direction * amplitude
        parts.append(f"Q {cx:.1f},{y1:.1f} 0,{y2:.1f}")
    return " ".join(parts)


# ── Flower Centers ───────────────────────────────────────────────────────────

def center_circle(radius=8):
    """Simple circle center."""
    r = radius
    k = r * 0.552
    return (
        f"M 0,{-r:.1f} "
        f"C {k:.1f},{-r:.1f} {r:.1f},{-k:.1f} {r:.1f},0 "
        f"C {r:.1f},{k:.1f} {k:.1f},{r:.1f} 0,{r:.1f} "
        f"C {-k:.1f},{r:.1f} {-r:.1f},{k:.1f} {-r:.1f},0 "
        f"C {-r:.1f},{-k:.1f} {-k:.1f},{-r:.1f} 0,{-r:.1f}"
    )


def center_dots(count=5, spread=10):
    """Cluster of small dots (tiny circles) for flower center."""
    dots = []
    r = 2.5
    k = r * 0.552
    for i in range(count):
        angle = 2 * math.pi * i / count
        cx = math.cos(angle) * spread
        cy = math.sin(angle) * spread
        dots.append(
            f"M {cx:.1f},{cy - r:.1f} "
            f"C {cx + k:.1f},{cy - r:.1f} {cx + r:.1f},{cy - k:.1f} "
            f"{cx + r:.1f},{cy:.1f} "
            f"C {cx + r:.1f},{cy + k:.1f} {cx + k:.1f},{cy + r:.1f} "
            f"{cx:.1f},{cy + r:.1f} "
            f"C {cx - k:.1f},{cy + r:.1f} {cx - r:.1f},{cy + k:.1f} "
            f"{cx - r:.1f},{cy:.1f} "
            f"C {cx - r:.1f},{cy - k:.1f} {cx - k:.1f},{cy - r:.1f} "
            f"{cx:.1f},{cy - r:.1f}"
        )
    return " ".join(dots)


def center_spiral(turns=2.5, max_radius=12):
    """Smooth logarithmic spiral for rose centers using cubic beziers."""
    points = []
    steps = int(turns * 24)
    for i in range(steps + 1):
        t = i / steps
        angle = t * turns * 2 * math.pi
        r = t * max_radius
        x = math.cos(angle) * r
        y = math.sin(angle) * r
        points.append((x, y))

    if len(points) < 2:
        return ""

    # Build smooth cubic bezier curve through points
    parts = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    for i in range(1, len(points) - 1, 2):
        p1 = points[i]
        p2 = points[min(i + 1, len(points) - 1)]
        # Use current point as control, next as endpoint
        parts.append(
            f"Q {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        )
    return " ".join(parts)


# ── Decorative Elements ──────────────────────────────────────────────────────

def berry(radius=6):
    """Single berry (filled circle outline). Same as center_circle."""
    return center_circle(radius)


def berry_cluster(count=5, spread=15):
    """Cluster of berries at semi-random positions."""
    berries = []
    r = 5
    k = r * 0.552
    # Fixed "random" offsets for determinism
    offsets = [
        (0, 0), (0.8, 0.3), (-0.6, 0.7), (0.3, -0.8), (-0.9, -0.2),
        (0.5, 0.9), (-0.4, -0.6), (0.7, -0.5), (-0.8, 0.5), (0.2, 0.6),
    ]
    for i in range(min(count, len(offsets))):
        cx = offsets[i][0] * spread
        cy = offsets[i][1] * spread
        berries.append(
            f"M {cx:.1f},{cy - r:.1f} "
            f"C {cx + k:.1f},{cy - r:.1f} {cx + r:.1f},{cy - k:.1f} "
            f"{cx + r:.1f},{cy:.1f} "
            f"C {cx + r:.1f},{cy + k:.1f} {cx + k:.1f},{cy + r:.1f} "
            f"{cx:.1f},{cy + r:.1f} "
            f"C {cx - k:.1f},{cy + r:.1f} {cx - r:.1f},{cy + k:.1f} "
            f"{cx - r:.1f},{cy:.1f} "
            f"C {cx - r:.1f},{cy - k:.1f} {cx - k:.1f},{cy - r:.1f} "
            f"{cx:.1f},{cy - r:.1f}"
        )
    return " ".join(berries)


def vine_tendril(length=40, coils=1.5):
    """Spiral tendril curl."""
    points = []
    steps = int(coils * 16)
    for i in range(steps + 1):
        t = i / steps
        angle = t * coils * 2 * math.pi
        r = length * (1 - t * 0.7)
        x = math.sin(angle) * r * 0.3
        y = -t * length
        points.append((x, y))
    parts = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    for i in range(1, len(points)):
        parts.append(f"L {points[i][0]:.1f},{points[i][1]:.1f}")
    return " ".join(parts)


def thorn(size=8):
    """Small thorn pointing right."""
    return f"M 0,{-size * 0.3:.1f} L {size:.1f},0 L 0,{size * 0.3:.1f}"


def leaf_vein_lines(length=50, vein_count=4):
    """Central vein with side vein lines. Returns list of d strings."""
    paths = [f"M 0,{-length / 2:.1f} L 0,{length / 2:.1f}"]
    for i in range(1, vein_count + 1):
        y = -length / 2 + length * i / (vein_count + 1)
        vl = length * 0.25 * (1 - abs(2 * i / (vein_count + 1) - 1))
        for side in (1, -1):
            paths.append(
                f"M 0,{y:.1f} L {side * vl:.1f},{y - vl * 0.5:.1f}"
            )
    return paths


def stamen(length=30, head_radius=3):
    """Single stamen: thin line with small circle at tip."""
    r = head_radius
    k = r * 0.552
    line = f"M 0,0 L 0,{-length:.1f}"
    tip_y = -length
    head = (
        f"M 0,{tip_y - r:.1f} "
        f"C {k:.1f},{tip_y - r:.1f} {r:.1f},{tip_y - k:.1f} {r:.1f},{tip_y:.1f} "
        f"C {r:.1f},{tip_y + k:.1f} {k:.1f},{tip_y + r:.1f} 0,{tip_y + r:.1f} "
        f"C {-k:.1f},{tip_y + r:.1f} {-r:.1f},{tip_y + k:.1f} {-r:.1f},{tip_y:.1f} "
        f"C {-r:.1f},{tip_y - k:.1f} {-k:.1f},{tip_y - r:.1f} 0,{tip_y - r:.1f}"
    )
    return line, head


# ── Composite Shape Helpers ──────────────────────────────────────────────────

def arrange_radial(path_d, count, radius, start_angle=0):
    """Return list of (d, angle, tx, ty) for radial arrangement."""
    items = []
    for i in range(count):
        angle = start_angle + 360 * i / count
        rad = math.radians(angle)
        tx = math.cos(rad) * radius
        ty = math.sin(rad) * radius
        items.append((path_d, angle + 90, tx, ty))
    return items


def arrange_along_stem(path_d, stem_length, count, spacing_ratio=0.15,
                       alternate=True, start_ratio=0.3):
    """Return list of (d, angle, tx, ty) for leaves along a stem."""
    items = []
    for i in range(count):
        t = start_ratio + spacing_ratio * i
        if t > 0.95:
            break
        y = -stem_length * t
        side = (1 if i % 2 == 0 else -1) if alternate else 1
        angle = side * 35
        tx = side * 5
        items.append((path_d, angle, tx, y))
    return items


def mirror_path(path_d):
    """Simple horizontal mirror: negate all x-coordinates in path.
    Works for M, L, C, Q commands with absolute coordinates."""
    tokens = path_d.replace(",", " ").split()
    result = []
    cmd = ""
    nums = []
    for token in tokens:
        if token[0].isalpha():
            if cmd and nums:
                result.extend(_mirror_nums(cmd, nums))
            cmd = token
            nums = []
        else:
            nums.append(float(token))
    if cmd and nums:
        result.extend(_mirror_nums(cmd, nums))
    return " ".join(str(v) for v in result)


def _mirror_nums(cmd, nums):
    """Negate x-coordinates (every other number starting from first)."""
    out = [cmd]
    for i, n in enumerate(nums):
        out.append(f"{-n:.1f}" if i % 2 == 0 else f"{n:.1f}")
    return out
