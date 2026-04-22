"""Aggregate per-task rent allocations into (a) a base software-engineering rent
vector weighted by O*NET importance, and (b) four tier-stratified vectors
weighted by the tier-emphasis classifications. Compute 95% bootstrap CIs.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

CHANNELS = ["K", "I", "P", "A", "C", "T", "R"]
# Sensitivity vector from framework_paper_v2.md Section 2.3
SENSITIVITY = {
    "K": 0.85, "I": 0.95, "P": 0.30, "A": 0.40,
    "C": 0.50, "T": 0.25, "R": 0.10,
}


def weighted_mean_vector(allocations, weights):
    w = np.asarray(weights, dtype=float)
    w = w / w.sum() if w.sum() > 0 else np.ones(len(w)) / len(w)
    vec = {}
    for c in CHANNELS:
        v = np.asarray(
            [a[c] for a in allocations], dtype=float
        )
        vec[c] = float(np.sum(v * w))
    total = sum(vec.values())
    if total > 0:
        for c in CHANNELS:
            vec[c] = vec[c] / total
    return vec


def exposure(vec):
    return sum(vec[c] * SENSITIVITY[c] for c in CHANNELS)


def bootstrap(allocations, weights, n_boot=500, seed=42):
    rng = np.random.default_rng(seed)
    n = len(allocations)
    boots = {c: [] for c in CHANNELS}
    exp_boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        sample_alloc = [allocations[i] for i in idx]
        sample_w = [weights[i] for i in idx]
        v = weighted_mean_vector(sample_alloc, sample_w)
        for c in CHANNELS:
            boots[c].append(v[c])
        exp_boots.append(exposure(v))
    ci = {}
    for c in CHANNELS:
        arr = np.array(boots[c])
        ci[c] = {
            "mean": float(arr.mean()),
            "ci_lo": float(np.percentile(arr, 2.5)),
            "ci_hi": float(np.percentile(arr, 97.5)),
        }
    exp_arr = np.array(exp_boots)
    ci["exposure"] = {
        "mean": float(exp_arr.mean()),
        "ci_lo": float(np.percentile(exp_arr, 2.5)),
        "ci_hi": float(np.percentile(exp_arr, 97.5)),
    }
    return ci


def main():
    alloc_df = pd.read_csv("task_allocations.csv")
    tier_df = pd.read_csv("task_tier_weights.csv")

    alloc_df = alloc_df.dropna(subset=CHANNELS)
    tier_df = tier_df.dropna(subset=["junior", "mid", "senior", "principal"])

    merged = alloc_df.merge(
        tier_df[["task_id", "junior", "mid", "senior", "principal"]],
        on="task_id",
        how="inner",
    )
    print(f"Merged task count: {len(merged)}")

    # Base vector: weight by O*NET importance (fill NaN with mean)
    importance = merged["importance"].fillna(
        merged["importance"].mean()
    ).to_numpy()
    allocations = merged[CHANNELS].to_dict("records")

    base_vec = weighted_mean_vector(allocations, importance)
    base_exp = exposure(base_vec)
    base_ci = bootstrap(allocations, importance, n_boot=500, seed=42)

    print("\n=== BASE SOFTWARE ENGINEERING RENT VECTOR ===")
    for c in CHANNELS:
        ci = base_ci[c]
        print(f"  {c}: {ci['mean']:.3f} [95% CI: {ci['ci_lo']:.3f}, {ci['ci_hi']:.3f}]")
    print(f"  Exposure: {base_exp:.3f} "
          f"[95% CI: {base_ci['exposure']['ci_lo']:.3f}, "
          f"{base_ci['exposure']['ci_hi']:.3f}]")

    # Tier-stratified vectors: weight by importance × tier emphasis
    tier_results = {"base": {"vector": base_vec,
                             "exposure": base_exp,
                             "ci": base_ci}}
    tier_map = {"junior": "Junior", "mid": "Mid", "senior": "Senior",
                "principal": "Principal"}
    for tier_col, tier_name in tier_map.items():
        weights = importance * merged[tier_col].to_numpy()
        vec = weighted_mean_vector(allocations, weights)
        exp = exposure(vec)
        ci = bootstrap(allocations, weights, n_boot=500, seed=42)
        tier_results[tier_name] = {"vector": vec, "exposure": exp, "ci": ci}
        print(f"\n=== {tier_name.upper()} ===")
        for c in CHANNELS:
            cic = ci[c]
            print(f"  {c}: {cic['mean']:.3f} [{cic['ci_lo']:.3f}, {cic['ci_hi']:.3f}]")
        print(f"  Exposure: {exp:.3f} "
              f"[{ci['exposure']['ci_lo']:.3f}, {ci['exposure']['ci_hi']:.3f}]")

    with open("vectors.json", "w") as f:
        json.dump(tier_results, f, indent=2)
    print("\nSaved vectors.json")


if __name__ == "__main__":
    main()
