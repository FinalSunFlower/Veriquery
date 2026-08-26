"""Plot the supplementary ERC layer-readiness profile."""

from __future__ import annotations

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .layer_readiness import audit
from .paths import PACKAGE_ROOT


OUT = PACKAGE_ROOT / "outputs"


def draw() -> list[Path]:
    profile = audit()
    labels = list(profile["layer_requirements"])
    values = [profile["cases_with_all_requirements"].get(label, 0) for label in labels]
    names = [label.replace("_", " ").replace("L1 ", "L1: ").replace("L2 ", "L2: ").replace("L3 ", "L3: ").replace("L4 ", "L4: ") for label in labels]
    plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans", "sans-serif"], "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    colors = ["#0F4D92", "#42949E", "#2E7D32", "#B64342"]
    bars = ax.bar(names, values, color=colors, edgecolor="black", linewidth=0.7)
    ax.set_ylim(0, profile["case_count"] + 5)
    ax.set_ylabel("Expanded cases with prerequisites")
    ax.set_title("ERC evidence-layer readiness (62 formal cases)", fontsize=11, pad=10)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1, str(value), ha="center", va="bottom", fontsize=9)
    fig.text(0.5, 0.01, "Readiness is not layer-wise performance; absent prerequisites prevent an independent ablation.", ha="center", fontsize=8.5, color="#5E6670")
    fig.tight_layout(rect=(0, 0.08, 1, 1), pad=1.2)
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("pdf", "svg", "png"):
        path = OUT / f"layer_readiness.{ext}"
        fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
        paths.append(path)
    plt.close(fig)
    return paths


if __name__ == "__main__":
    print("\n".join(str(path) for path in draw()))
