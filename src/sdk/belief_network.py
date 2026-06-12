import matplotlib

matplotlib.use("Agg")  # Non-interactive backend; must precede any pyplot import.

from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# Candidate Hebrew-capable fonts, in preference order (Windows Arial first).
_HEBREW_FONTS = ("Arial", "Noto Sans Hebrew", "FreeSans", "Arial Hebrew")

# Multi-factor model: three parent drivers feeding the central belief node.
_PARENTS = (
    ("צרכים אנושיים בסיסיים", "צורך אטיולוגי · חוסר ביטחון"),
    ("מנגנונים קוגניטיביים", "הטיית אישוש · אפקט חשיפה"),
    ("גורמים חברתיים", "חוסר אמון · רטוריקה"),
)
_CENTRAL = "אמונה בתיאוריות קשר חוצניות"
_PARENT_FC = ("#dbe9f6", "#e3f0dd", "#f6e3df")


def _hebrew_font() -> font_manager.FontProperties:
    """Resolves the first available Hebrew-capable font, else the default."""
    for name in _HEBREW_FONTS:
        try:
            path = font_manager.findfont(name, fallback_to_default=False)
            return font_manager.FontProperties(fname=path)
        except (ValueError, RuntimeError):
            continue
    return font_manager.FontProperties()


def _rtl(text: str) -> str:
    """Reorders a Hebrew string to correct visual (right-to-left) order."""
    return get_display(text)


def _box(ax, xy: Tuple[float, float], wh: Tuple[float, float], title: str,
         sub: Optional[str], font, fc: str) -> None:
    x, y = xy
    w, h = wh
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.06,rounding_size=0.18",
        fc=fc, ec="#2b2b40", lw=1.5, zorder=3,
    ))
    ax.text(x, y + (0.16 if sub else 0.0), _rtl(title), ha="center", va="center",
            fontproperties=font, fontsize=12.5, fontweight="bold", color="#1a1a2e", zorder=4)
    if sub:
        ax.text(x, y - 0.30, _rtl(sub), ha="center", va="center",
                fontproperties=font, fontsize=9, color="#3a3a55", zorder=4)


def generate_belief_network(out_path: Path) -> Path:
    """Renders the multi-factor conspiracy-belief network diagram (Hebrew)."""
    font = _hebrew_font()
    fig, ax = plt.subplots(figsize=(10, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    pw, ph = 2.7, 1.05
    cw, ch = 3.6, 1.25
    cx, cy = 5.0, 1.7
    xs = (1.75, 5.0, 8.25)
    py = 6.2

    for x, (title, sub), fc in zip(xs, _PARENTS, _PARENT_FC):
        _box(ax, (x, py), (pw, ph), title, sub, font, fc)
        ax.add_patch(FancyArrowPatch(
            (x, py - ph / 2), (cx, cy + ch / 2),
            arrowstyle="-|>", mutation_scale=20, color="#4e79a7",
            lw=2.0, connectionstyle="arc3,rad=0.06", zorder=2,
        ))

    # Cross-link: existential insecurity reinforces distrust in institutions.
    ax.add_patch(FancyArrowPatch(
        (xs[0] + pw / 2, py + 0.1), (xs[2] - pw / 2, py + 0.1),
        arrowstyle="-|>", mutation_scale=14, color="#888899",
        lw=1.3, linestyle=(0, (5, 3)), connectionstyle="arc3,rad=-0.32", zorder=1,
    ))

    _box(ax, (cx, cy), (cw, ch), _CENTRAL, None, font, "#f4d58d")
    ax.set_title(_rtl("מודל רב-גורמי להיווצרות אמונה בתיאוריות קשר חוצניות"),
                 fontproperties=font, fontsize=13.5, pad=12, color="#1a1a2e")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path
