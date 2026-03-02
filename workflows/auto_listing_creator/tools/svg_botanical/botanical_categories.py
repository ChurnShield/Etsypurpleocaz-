# =============================================================================
# botanical_categories.py
#
# Design registry mapping all ~130 botanical designs to their composition
# functions, categories, and metadata for the SVG generator.
# =============================================================================

from . import botanical_compositions as comp


# Category constants
CAT_ROSES = "Roses"
CAT_WILDFLOWERS = "Wildflowers"
CAT_BIRTH = "Birth-Flowers"
CAT_STEMS = "Botanical-Stems"
CAT_MINI = "Mini"
CAT_WREATHS = "Wreaths-and-Frames"
CAT_BOUQUETS = "Bouquets"
CAT_DECORATIVE = "Decorative"

ALL_CATEGORIES = [
    CAT_ROSES, CAT_WILDFLOWERS, CAT_BIRTH, CAT_STEMS,
    CAT_MINI, CAT_WREATHS, CAT_BOUQUETS, CAT_DECORATIVE,
]


def _entry(name, category, fn, description, **extra_kwargs):
    """Build a design registry entry."""
    return {
        "name": name,
        "category": category,
        "fn": fn,
        "description": description,
        "extra_kwargs": extra_kwargs,
    }


# ── Full Design Registry ────────────────────────────────────────────────────

DESIGN_REGISTRY = [
    # ── Roses (12) ──
    _entry("Rose-Open-Bloom", CAT_ROSES, comp.rose_open,
           "Full open rose, top-down view with spiral center"),
    _entry("Rose-Open-Bloom-Large", CAT_ROSES, comp.rose_open,
           "Large open rose bloom", size=1.2),
    _entry("Rose-Side-View", CAT_ROSES, comp.rose_side,
           "Side view rose with visible petals and calyx"),
    _entry("Rose-Side-View-Small", CAT_ROSES, comp.rose_side,
           "Small side view rose", size=0.8),
    _entry("Rosebud-Stem", CAT_ROSES, comp.rose_bud,
           "Closed rosebud on curved stem with leaves"),
    _entry("Rosebud-Stem-Curved", CAT_ROSES, comp.rose_bud,
           "Rosebud with more pronounced curve", size=0.9),
    _entry("Rose-Single-Stem", CAT_ROSES, comp.rose_stem_single,
           "Single rose bloom on long stem with leaves"),
    _entry("Rose-Single-Stem-Tall", CAT_ROSES, comp.rose_stem_single,
           "Tall single rose on extended stem", size=0.85),
    _entry("Rose-Pair", CAT_ROSES, comp.rose_bouquet_pair,
           "Two roses with intertwined stems"),
    _entry("Rose-Pair-Compact", CAT_ROSES, comp.rose_bouquet_pair,
           "Compact pair of roses", size=0.8),
    _entry("Rose-Climbing-Vine", CAT_ROSES, comp.rose_climbing,
           "Climbing rose vine with multiple small blooms"),
    _entry("Rose-Climbing-Vine-Long", CAT_ROSES, comp.rose_climbing,
           "Extended climbing rose vine", size=0.9),

    # ── Wildflowers (18) ──
    _entry("Daisy-Single", CAT_WILDFLOWERS, comp.daisy,
           "Classic daisy with stem and leaves"),
    _entry("Daisy-Bloom-Only", CAT_WILDFLOWERS, comp.daisy,
           "Daisy bloom without stem", with_stem=False),
    _entry("Daisy-Dense-Petals", CAT_WILDFLOWERS, comp.daisy,
           "Daisy with 16 petals", petals=16),
    _entry("Poppy-Single", CAT_WILDFLOWERS, comp.poppy,
           "Poppy flower with 5 rounded petals on stem"),
    _entry("Poppy-Bloom-Only", CAT_WILDFLOWERS, comp.poppy,
           "Poppy bloom without stem", with_stem=False),
    _entry("Lavender-Sprig", CAT_WILDFLOWERS, comp.lavender,
           "Lavender sprig with tiny buds along curved stem"),
    _entry("Lavender-Sprig-Small", CAT_WILDFLOWERS, comp.lavender,
           "Small lavender sprig", size=0.8),
    _entry("Chamomile", CAT_WILDFLOWERS, comp.chamomile,
           "Chamomile with many thin petals and feathery leaves"),
    _entry("Chamomile-Small", CAT_WILDFLOWERS, comp.chamomile,
           "Small chamomile", size=0.8),
    _entry("Sunflower", CAT_WILDFLOWERS, comp.sunflower,
           "Sunflower with double ring of pointed petals"),
    _entry("Sunflower-Small", CAT_WILDFLOWERS, comp.sunflower,
           "Compact sunflower", size=0.8),
    _entry("Cosmos-Flower", CAT_WILDFLOWERS, comp.cosmos,
           "Cosmos with 8 teardrop petals"),
    _entry("Cosmos-Flower-Small", CAT_WILDFLOWERS, comp.cosmos,
           "Small cosmos flower", size=0.8),
    _entry("Forget-Me-Not-Cluster", CAT_WILDFLOWERS, comp.forget_me_not,
           "Cluster of tiny forget-me-nots on branching stem"),
    _entry("Wildflower-Mix-A", CAT_WILDFLOWERS, comp.wildflower_mixed_a,
           "Mixed wildflower arrangement: daisy + poppy + small blooms"),
    _entry("Wildflower-Mix-A-Small", CAT_WILDFLOWERS, comp.wildflower_mixed_a,
           "Small mixed wildflower arrangement", size=0.8),
    _entry("Poppy-Large", CAT_WILDFLOWERS, comp.poppy,
           "Large poppy bloom", size=1.1),
    _entry("Daisy-Large", CAT_WILDFLOWERS, comp.daisy,
           "Large daisy with 14 petals", petals=14, size=1.1),

    # ── Birth Flowers (12) ──
    _entry("Birth-01-Carnation", CAT_BIRTH, comp.birth_carnation,
           "January birth flower: Carnation with ruffled petals"),
    _entry("Birth-02-Violet", CAT_BIRTH, comp.birth_violet,
           "February birth flower: Violet"),
    _entry("Birth-03-Daffodil", CAT_BIRTH, comp.birth_daffodil,
           "March birth flower: Daffodil with 6 petals and trumpet"),
    _entry("Birth-04-Sweet-Pea", CAT_BIRTH, comp.birth_sweet_pea,
           "April birth flower: Sweet Pea"),
    _entry("Birth-05-Lily-of-Valley", CAT_BIRTH, comp.birth_lily_of_valley,
           "May birth flower: Lily of the Valley bells on arching stem"),
    _entry("Birth-06-Rose", CAT_BIRTH, comp.birth_rose,
           "June birth flower: Rose"),
    _entry("Birth-07-Larkspur", CAT_BIRTH, comp.birth_larkspur,
           "July birth flower: Larkspur tall spike"),
    _entry("Birth-08-Gladiolus", CAT_BIRTH, comp.birth_gladiolus,
           "August birth flower: Gladiolus"),
    _entry("Birth-09-Aster", CAT_BIRTH, comp.birth_aster,
           "September birth flower: Aster with many thin petals"),
    _entry("Birth-10-Marigold", CAT_BIRTH, comp.birth_marigold,
           "October birth flower: Marigold dense ruffled layers"),
    _entry("Birth-11-Chrysanthemum", CAT_BIRTH, comp.birth_chrysanthemum,
           "November birth flower: Chrysanthemum layered petals"),
    _entry("Birth-12-Narcissus", CAT_BIRTH, comp.birth_narcissus,
           "December birth flower: Narcissus with corona"),

    # ── Botanical Stems (12) ──
    _entry("Eucalyptus-Branch", CAT_STEMS, comp.eucalyptus_branch,
           "Eucalyptus branch with round alternating leaves"),
    _entry("Eucalyptus-Branch-Long", CAT_STEMS, comp.eucalyptus_branch,
           "Long eucalyptus branch with many leaves", leaf_count=12),
    _entry("Eucalyptus-Branch-Short", CAT_STEMS, comp.eucalyptus_branch,
           "Short eucalyptus sprig", leaf_count=5, size=0.8),
    _entry("Fern-Frond", CAT_STEMS, comp.fern_frond,
           "Fern frond with alternating leaflets"),
    _entry("Fern-Frond-Dense", CAT_STEMS, comp.fern_frond,
           "Dense fern frond with many segments", segments=14),
    _entry("Olive-Branch", CAT_STEMS, comp.olive_branch,
           "Olive branch with narrow alternating leaves"),
    _entry("Olive-Branch-Long", CAT_STEMS, comp.olive_branch,
           "Long olive branch", leaf_count=14),
    _entry("Monstera-Leaf", CAT_STEMS, comp.monstera_leaf,
           "Single monstera leaf with splits on stem"),
    _entry("Monstera-Leaf-Large", CAT_STEMS, comp.monstera_leaf,
           "Large monstera leaf", size=1.15),
    _entry("Palm-Leaf", CAT_STEMS, comp.palm_leaf_single,
           "Single palm leaf fan"),
    _entry("Palm-Leaf-Compact", CAT_STEMS, comp.palm_leaf_single,
           "Compact palm leaf", size=0.8),
    _entry("Ivy-Vine-Trail", CAT_STEMS, comp.ivy_vine,
           "Trailing ivy vine with heart-shaped leaves"),

    # ── Mini / Tiny (25) ──
    _entry("Mini-Rose", CAT_MINI, comp.mini_rose, "Tiny rose for finger tattoo"),
    _entry("Mini-Daisy", CAT_MINI, comp.mini_daisy, "Tiny daisy"),
    _entry("Mini-Leaf", CAT_MINI, comp.mini_leaf, "Single tiny leaf"),
    _entry("Mini-Bud", CAT_MINI, comp.mini_bud, "Tiny flower bud"),
    _entry("Mini-Berry", CAT_MINI, comp.mini_berry, "Tiny berry branch"),
    _entry("Mini-Star-Flower", CAT_MINI, comp.mini_star, "Tiny star flower"),
    _entry("Mini-Sprig", CAT_MINI, comp.mini_sprig, "Tiny botanical sprig"),
    _entry("Mini-Tulip", CAT_MINI, comp.mini_tulip, "Tiny tulip"),
    _entry("Mini-Fern-Curl", CAT_MINI, comp.mini_fern, "Tiny fern curl"),
    _entry("Mini-Crescent-Flower", CAT_MINI, comp.mini_crescent,
           "Tiny crescent moon with flower"),
    _entry("Mini-Heart-Botanical", CAT_MINI, comp.mini_heart_botanical,
           "Heart shape made from two leaves"),
    _entry("Mini-Lavender", CAT_MINI, comp.mini_lavender,
           "Tiny lavender sprig"),
    _entry("Mini-Sunflower", CAT_MINI, comp.mini_sunflower,
           "Tiny sunflower"),
    _entry("Mini-Eucalyptus", CAT_MINI, comp.mini_eucalyptus,
           "Tiny eucalyptus sprig"),
    _entry("Mini-Wildflower", CAT_MINI, comp.mini_wildflower,
           "Tiny generic wildflower"),
    _entry("Mini-Vine", CAT_MINI, comp.mini_vine,
           "Tiny vine segment"),
    _entry("Mini-Poppy", CAT_MINI, comp.mini_poppy,
           "Tiny poppy"),
    _entry("Mini-Cherry-Blossom", CAT_MINI, comp.mini_cherry_blossom,
           "Tiny cherry blossom with stamens"),
    _entry("Mini-Cosmos", CAT_MINI, comp.mini_cosmos,
           "Tiny cosmos flower"),
    _entry("Mini-Olive", CAT_MINI, comp.mini_olive,
           "Tiny olive branch"),
    _entry("Mini-Rose-Large", CAT_MINI, comp.mini_rose,
           "Slightly larger mini rose", size=1.3),
    _entry("Mini-Daisy-Large", CAT_MINI, comp.mini_daisy,
           "Slightly larger mini daisy", size=1.3),
    _entry("Mini-Star-Large", CAT_MINI, comp.mini_star,
           "Slightly larger mini star", size=1.3),
    _entry("Mini-Leaf-Large", CAT_MINI, comp.mini_leaf,
           "Slightly larger mini leaf", size=1.3),
    _entry("Mini-Bud-Large", CAT_MINI, comp.mini_bud,
           "Slightly larger mini bud", size=1.3),

    # ── Wreaths & Frames (12) ──
    _entry("Wreath-Circle-Mixed", CAT_WREATHS, comp.wreath_circle,
           "Circular wreath of leaves and small flowers"),
    _entry("Wreath-Circle-Dense", CAT_WREATHS, comp.wreath_circle,
           "Dense circular wreath with more elements", elements=22),
    _entry("Wreath-Eucalyptus", CAT_WREATHS, comp.wreath_eucalyptus,
           "Eucalyptus round wreath"),
    _entry("Wreath-Berry", CAT_WREATHS, comp.wreath_berry,
           "Wreath with berries and small leaves"),
    _entry("Half-Wreath-Top", CAT_WREATHS, comp.half_wreath_top,
           "Half wreath across the top"),
    _entry("Half-Wreath-Side", CAT_WREATHS, comp.half_wreath_side,
           "Half wreath along the side"),
    _entry("Corner-Frame-Botanical", CAT_WREATHS, comp.corner_frame_botanical,
           "L-shaped corner frame with flowers and leaves"),
    _entry("Corner-Frame-Vine", CAT_WREATHS, comp.corner_frame_vine,
           "Vine-style corner frame"),
    _entry("Crescent-Wreath", CAT_WREATHS, comp.crescent_wreath,
           "Crescent moon shape botanical wreath"),
    _entry("Crescent-Wreath-Small", CAT_WREATHS, comp.crescent_wreath,
           "Small crescent wreath", size=0.8),
    _entry("Wreath-Circle-Small", CAT_WREATHS, comp.wreath_circle,
           "Small circular wreath", size=0.8, elements=12),
    _entry("Half-Wreath-Top-Dense", CAT_WREATHS, comp.half_wreath_top,
           "Dense half wreath", size=1.1),

    # ── Bouquets (15) ──
    _entry("Bouquet-Roses-3", CAT_BOUQUETS, comp.bouquet_roses,
           "Bouquet of 3 roses with greenery"),
    _entry("Bouquet-Roses-3-Small", CAT_BOUQUETS, comp.bouquet_roses,
           "Small rose bouquet", size=0.8),
    _entry("Bouquet-Roses-3-Large", CAT_BOUQUETS, comp.bouquet_roses,
           "Large rose bouquet", size=1.1),
    _entry("Bouquet-Wildflower-Mix", CAT_BOUQUETS, comp.bouquet_wildflowers,
           "Mixed wildflower bouquet"),
    _entry("Bouquet-Wildflower-Small", CAT_BOUQUETS, comp.bouquet_wildflowers,
           "Small wildflower bouquet", size=0.8),
    _entry("Bouquet-Wildflower-Large", CAT_BOUQUETS, comp.bouquet_wildflowers,
           "Large wildflower bouquet", size=1.1),
    _entry("Bouquet-Mixed-Large-7", CAT_BOUQUETS, comp.bouquet_mixed_large,
           "Large mixed bouquet with 7 flowers"),
    _entry("Bouquet-Mixed-Large-Compact", CAT_BOUQUETS, comp.bouquet_mixed_large,
           "Compact large mixed bouquet", size=0.85),
    _entry("Bouquet-Minimal-3", CAT_BOUQUETS, comp.bouquet_minimal,
           "Minimal 3-stem bouquet"),
    _entry("Bouquet-Minimal-3-Small", CAT_BOUQUETS, comp.bouquet_minimal,
           "Small minimal bouquet", size=0.8),
    _entry("Bouquet-Minimal-3-Large", CAT_BOUQUETS, comp.bouquet_minimal,
           "Large minimal bouquet", size=1.15),
    _entry("Bouquet-Roses-Tight", CAT_BOUQUETS, comp.bouquet_roses,
           "Tightly arranged rose bouquet", size=0.9),
    _entry("Bouquet-Wildflower-Tall", CAT_BOUQUETS, comp.bouquet_wildflowers,
           "Tall wildflower bouquet", size=1.05),
    _entry("Bouquet-Mixed-Medium", CAT_BOUQUETS, comp.bouquet_mixed_large,
           "Medium mixed bouquet", size=0.75),
    _entry("Bouquet-Minimal-Tall", CAT_BOUQUETS, comp.bouquet_minimal,
           "Tall minimal bouquet", size=1.05),

    # ── Decorative (14) ──
    _entry("Leaf-Detailed-Single", CAT_DECORATIVE, comp.single_leaf_detailed,
           "Large detailed leaf with vein pattern"),
    _entry("Leaf-Detailed-Small", CAT_DECORATIVE, comp.single_leaf_detailed,
           "Small detailed leaf", size=0.7),
    _entry("Leaf-Detailed-Large", CAT_DECORATIVE, comp.single_leaf_detailed,
           "Extra large detailed leaf", size=1.2),
    _entry("Berry-Branch", CAT_DECORATIVE, comp.berry_branch,
           "Branch with berry clusters"),
    _entry("Berry-Branch-Small", CAT_DECORATIVE, comp.berry_branch,
           "Small berry branch", size=0.75),
    _entry("Berry-Branch-Long", CAT_DECORATIVE, comp.berry_branch,
           "Long berry branch", size=1.1),
    _entry("Vine-Trailing", CAT_DECORATIVE, comp.vine_trailing,
           "Trailing decorative vine with leaves"),
    _entry("Vine-Trailing-Short", CAT_DECORATIVE, comp.vine_trailing,
           "Short trailing vine", size=0.7),
    _entry("Vine-Trailing-Long", CAT_DECORATIVE, comp.vine_trailing,
           "Long trailing vine", size=1.1),
    _entry("Branch-Simple", CAT_DECORATIVE, comp.branch_simple,
           "Simple branch with scattered leaves"),
    _entry("Branch-Simple-Short", CAT_DECORATIVE, comp.branch_simple,
           "Short simple branch", size=0.7),
    _entry("Leaf-Pair", CAT_DECORATIVE, comp.leaf_pair,
           "Symmetrical pair of leaves on short stem"),
    _entry("Leaf-Pair-Large", CAT_DECORATIVE, comp.leaf_pair,
           "Large leaf pair", size=1.2),
    _entry("Leaf-Pair-Small", CAT_DECORATIVE, comp.leaf_pair,
           "Small leaf pair", size=0.7),
]


def get_designs_by_category(category):
    """Return all designs in a given category."""
    return [d for d in DESIGN_REGISTRY if d["category"] == category]


def get_all_designs():
    """Return the full design registry."""
    return list(DESIGN_REGISTRY)


def get_design_count():
    """Return total number of registered designs."""
    return len(DESIGN_REGISTRY)


def get_category_counts():
    """Return dict of category -> count."""
    counts = {}
    for d in DESIGN_REGISTRY:
        cat = d["category"]
        counts[cat] = counts.get(cat, 0) + 1
    return counts
