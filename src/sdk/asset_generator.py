import matplotlib

matplotlib.use("Agg")  # Non-interactive backend; must precede any pyplot import.

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

# Approximate AARO UAP category counts (Annual Report, 2024).
_AARO_DATA: Dict[str, int] = {
    "Unknown / Unresolved": 171,
    "Balloons / Airships": 144,
    "Unmanned Aircraft (UAS)": 97,
    "Natural Phenomena": 83,
    "Sensor Anomalies": 52,
    "Airborne Debris": 45,
}

_AARO_COLORS = ["#b07aa1", "#4e79a7", "#59a14f", "#f28e2b", "#e15759", "#76b7b2"]


def generate_star_field(out_path: Path) -> Path:
    """Renders a Milky-Way-style star field with highlighted habitable-zone candidates."""
    rng = np.random.default_rng(42)
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#050510")
    ax.set_facecolor("#050510")

    # Background stars concentrated along the galactic plane.
    n_bg = 1200
    x_bg = rng.uniform(0, 1, n_bg)
    y_bg = np.clip(rng.normal(0.5, 0.22, n_bg), 0, 1)
    s_bg = rng.exponential(0.4, n_bg) * 2.2
    alpha_bg = rng.uniform(0.3, 0.95, n_bg)
    ax.scatter(x_bg, y_bg, s=s_bg, c="white", alpha=alpha_bg, linewidths=0)

    # Scattered field stars (blue-white tint).
    n_sc = 500
    x_sc = rng.uniform(0, 1, n_sc)
    y_sc = rng.uniform(0, 1, n_sc)
    s_sc = rng.exponential(0.25, n_sc) * 1.8
    ax.scatter(x_sc, y_sc, s=s_sc, c="lightcyan", alpha=0.55, linewidths=0)

    # Confirmed habitable-zone exoplanet host stars (gold star markers).
    hx = [0.12, 0.33, 0.50, 0.68, 0.84, 0.25, 0.60, 0.78]
    hy = [0.62, 0.38, 0.72, 0.30, 0.60, 0.18, 0.48, 0.75]
    ax.scatter(hx, hy, s=130, c="gold", alpha=0.96, marker="*", zorder=6,
               label="Confirmed habitable-zone exoplanet hosts (Kepler / TESS)")

    ax.legend(loc="upper right", facecolor="#0a0a22", labelcolor="white",
              fontsize=8.5, framealpha=0.75, edgecolor="#333355")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("The Search for Extraterrestrial Life — Habitable-Zone Candidates",
                 color="white", fontsize=11, pad=9)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def generate_uap_distribution(out_path: Path) -> Path:
    """Renders a horizontal bar chart of AARO UAP report categories."""
    cats = list(_AARO_DATA.keys())
    vals = list(_AARO_DATA.values())

    fig, ax = plt.subplots(figsize=(10, 4.5))
    bars = ax.barh(cats, vals, color=_AARO_COLORS, edgecolor="white", linewidth=0.5)

    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", fontsize=10)

    ax.set_xlabel("Number of Reports", fontsize=11)
    ax.set_title("UAP Report Categories — AARO Annual Report (approximate figures)",
                 fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(vals) + 35)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_all(asset_dir: Path) -> Dict[str, Path]:
    """Generates all pipeline assets and returns a dict of {name: path}."""
    asset_dir = Path(asset_dir)
    return {
        "star_field": generate_star_field(asset_dir / "star_field.pdf"),
        "uap_distribution": generate_uap_distribution(asset_dir / "uap_distribution.pdf"),
    }
