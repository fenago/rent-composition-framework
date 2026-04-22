"""Generate the three figures for the Pathway B empirical section.

Fig 1: Measured vs expert-elicited rent vectors, with 95% bootstrap CI whiskers.
Fig 2: Tier-stratified exposure scores (Junior/Mid/Senior/Principal) — measured.
Fig 3: Rent composition heatmap across tiers — measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CHANNELS = ["K", "I", "P", "A", "C", "T", "R"]
CHANNEL_LABELS = {
    "K": "Knowledge",
    "I": "Interpretation",
    "P": "Process",
    "A": "Access",
    "C": "Credential",
    "T": "Technical",
    "R": "Relational",
}

# Expert-elicited vectors from §4.2 of framework_paper_v2.md
EXPERT_ELICITED = {
    "base_se": {"K": 0.175, "I": 0.465, "P": 0.05, "A": 0.00,
                "C": 0.05, "T": 0.165, "R": 0.10},
    "Junior":    {"K": 0.10, "I": 0.60, "P": 0.00, "A": 0.00,
                  "C": 0.10, "T": 0.15, "R": 0.05},
    "Mid":       {"K": 0.20, "I": 0.50, "P": 0.05, "A": 0.00,
                  "C": 0.05, "T": 0.15, "R": 0.05},
    "Senior":    {"K": 0.25, "I": 0.25, "P": 0.15, "A": 0.00,
                  "C": 0.00, "T": 0.20, "R": 0.15},
    "Principal": {"K": 0.15, "I": 0.10, "P": 0.25, "A": 0.00,
                  "C": 0.00, "T": 0.15, "R": 0.35},
}


def plt_style():
    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
    })


def fig1_measured_vs_expert(vectors):
    """Grouped bar chart of measured (O*NET) vs expert-elicited base SE
    rent vectors, with 95% bootstrap CI whiskers on the measured bars."""
    meas = vectors["base"]["vector"]
    ci = vectors["base"]["ci"]
    expert = EXPERT_ELICITED["base_se"]

    x = np.arange(len(CHANNELS))
    w = 0.38
    meas_vals = [meas[c] for c in CHANNELS]
    expert_vals = [expert[c] for c in CHANNELS]
    meas_err_lo = [meas[c] - ci[c]["ci_lo"] for c in CHANNELS]
    meas_err_hi = [ci[c]["ci_hi"] - meas[c] for c in CHANNELS]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    bars1 = ax.bar(
        x - w/2, meas_vals, w,
        yerr=[meas_err_lo, meas_err_hi],
        capsize=3, color="#2E86AB",
        label="Measured from O*NET (this paper)",
    )
    bars2 = ax.bar(
        x + w/2, expert_vals, w,
        color="#E07A5F",
        label="Expert-elicited (framework §4.2)",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{c}\n{CHANNEL_LABELS[c]}" for c in CHANNELS], fontsize=9,
    )
    ax.set_ylabel("Rent share")
    ax.set_title(
        "Base Software Engineering Rent Vector:\n"
        "Measured vs Expert-Elicited (95% bootstrap CI on measured)",
    )
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(max(meas_vals), max(expert_vals)) * 1.35)
    plt.tight_layout()
    plt.savefig("fig1_measured_vs_expert.png")
    plt.savefig("fig1_measured_vs_expert.pdf")
    plt.close()
    print("Saved fig1_measured_vs_expert.{png,pdf}")


def fig2_tier_exposure(vectors):
    """Exposure scores by tier: measured vs expert-elicited, with CI bars on measured."""
    tiers = ["Junior", "Mid", "Senior", "Principal"]
    meas_exp = [vectors[t]["exposure"] for t in tiers]
    meas_ci_lo = [vectors[t]["ci"]["exposure"]["ci_lo"] for t in tiers]
    meas_ci_hi = [vectors[t]["ci"]["exposure"]["ci_hi"] for t in tiers]

    # Expert-elicited exposures from §4.2 (recomputed with v2.1 sensitivities)
    expert_exp = {
        "Junior": 0.75, "Mid": 0.73, "Senior": 0.56, "Principal": 0.37,
    }

    x = np.arange(len(tiers))
    w = 0.38

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    err_lo = [meas_exp[i] - meas_ci_lo[i] for i in range(len(tiers))]
    err_hi = [meas_ci_hi[i] - meas_exp[i] for i in range(len(tiers))]
    ax.bar(
        x - w/2, meas_exp, w,
        yerr=[err_lo, err_hi], capsize=3,
        color="#2E86AB", label="Measured (this paper)",
    )
    ax.bar(
        x + w/2, [expert_exp[t] for t in tiers], w,
        color="#E07A5F", label="Expert-elicited (§4.2)",
    )

    # Tier thresholds
    for y, label, color in [
        (0.30, "Resilient/Adapting", "#999"),
        (0.50, "Adapting/Exposed", "#999"),
        (0.70, "Exposed/High-Risk", "#999"),
    ]:
        ax.axhline(y, color=color, linestyle=":", linewidth=1, alpha=0.6)
        ax.text(
            3.5, y + 0.01, label, fontsize=8,
            color=color, ha="right", alpha=0.8,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel("AI Exposure Score")
    ax.set_ylim(0, 1)
    ax.set_title(
        "Tier-Stratified AI Exposure — Software Engineering\n"
        "Measured vs Expert-Elicited, with 95% CI on measured",
    )
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("fig2_tier_exposure.png")
    plt.savefig("fig2_tier_exposure.pdf")
    plt.close()
    print("Saved fig2_tier_exposure.{png,pdf}")


def fig3_heatmap(vectors):
    """Heatmap of measured rent shares by tier × channel."""
    tiers = ["Junior", "Mid", "Senior", "Principal"]
    matrix = np.array([[vectors[t]["vector"][c] for c in CHANNELS]
                       for t in tiers])

    fig, ax = plt.subplots(figsize=(8, 3.5))
    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=0.6)
    ax.set_xticks(range(len(CHANNELS)))
    ax.set_xticklabels(
        [f"{c}\n{CHANNEL_LABELS[c]}" for c in CHANNELS], fontsize=9,
    )
    ax.set_yticks(range(len(tiers)))
    ax.set_yticklabels(tiers)
    for i in range(len(tiers)):
        for j in range(len(CHANNELS)):
            v = matrix[i, j]
            ax.text(
                j, i, f"{v:.2f}",
                ha="center", va="center",
                color="white" if v > 0.35 else "black",
                fontsize=9,
            )
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Rent share")
    ax.set_title(
        "Measured Rent Composition by Software Engineering Tier",
    )
    plt.tight_layout()
    plt.savefig("fig3_tier_heatmap.png")
    plt.savefig("fig3_tier_heatmap.pdf")
    plt.close()
    print("Saved fig3_tier_heatmap.{png,pdf}")


def main():
    plt_style()
    with open("vectors.json") as f:
        vectors = json.load(f)
    fig1_measured_vs_expert(vectors)
    fig2_tier_exposure(vectors)
    fig3_heatmap(vectors)


if __name__ == "__main__":
    main()
