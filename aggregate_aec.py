"""Aggregate per-task rent allocations for AEC roles into three measured
rent vectors (Owner's Rep, General Contractor, Designer) with 95% bootstrap
confidence intervals. Each role has its own O*NET occupation code, so tier
weighting is not needed here.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

CHANNELS = ["K", "I", "P", "A", "C", "T", "R"]
SENSITIVITY = {
    "K": 0.85, "I": 0.95, "P": 0.45, "A": 0.40,
    "C": 0.50, "T": 0.25, "R": 0.10,
}


def weighted_mean_vector(allocations, weights):
    w = np.asarray(weights, dtype=float)
    w = w / w.sum() if w.sum() > 0 else np.ones(len(w)) / len(w)
    vec = {}
    for c in CHANNELS:
        v = np.asarray([a[c] for a in allocations], dtype=float)
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
    df = pd.read_csv("aec_task_allocations.csv").dropna(subset=CHANNELS)
    print(f"Loaded {len(df)} classified tasks")

    results = {}
    for role, group in df.groupby("role"):
        importance = group["importance"].fillna(group["importance"].mean()).to_numpy()
        allocations = group[CHANNELS].to_dict("records")
        vec = weighted_mean_vector(allocations, importance)
        exp = exposure(vec)
        ci = bootstrap(allocations, importance, n_boot=500, seed=42)
        results[role] = {
            "n_tasks": len(group),
            "vector": vec,
            "exposure": exp,
            "ci": ci,
        }
        print(f"\n=== {role.upper()} (n={len(group)}) ===")
        for c in CHANNELS:
            cic = ci[c]
            print(f"  {c}: {cic['mean']:.3f} [{cic['ci_lo']:.3f}, {cic['ci_hi']:.3f}]")
        eci = ci["exposure"]
        print(f"  Exposure: {exp:.3f} [{eci['ci_lo']:.3f}, {eci['ci_hi']:.3f}]")

    with open("aec_vectors.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved aec_vectors.json")


if __name__ == "__main__":
    main()
