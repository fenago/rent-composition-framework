"""Classify AEC (Architecture, Engineering, Construction) task statements.

Uses the same classification prompt as classify.py but reads AEC tasks
instead of software engineering tasks. Produces aec_task_allocations.csv.
"""

from __future__ import annotations

import pandas as pd

import classify as base


def main():
    df = pd.read_csv("aec_tasks_with_importance.csv")
    results = []
    for idx, row in df.iterrows():
        print(f"[{idx+1}/{len(df)}] {row['Title']} — {row['Task'][:70]}...")
        try:
            alloc = base.classify(row["Task"], row["Title"])
            results.append({
                "soc": row["O*NET-SOC Code"],
                "title": row["Title"],
                "role": row["role"],
                "task_id": row["Task ID"],
                "task": row["Task"],
                "importance": row["Importance"] if pd.notna(row["Importance"]) else None,
                **{c: alloc[c] for c in base.CHANNELS},
                "rationale": alloc.get("rationale", ""),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "soc": row["O*NET-SOC Code"],
                "title": row["Title"],
                "role": row["role"],
                "task_id": row["Task ID"],
                "task": row["Task"],
                "importance": row["Importance"] if pd.notna(row["Importance"]) else None,
                **{c: None for c in base.CHANNELS},
                "rationale": f"ERROR: {e}",
            })

    out = pd.DataFrame(results)
    out.to_csv("aec_task_allocations.csv", index=False)
    print(f"\nSaved {len(out)} allocations -> aec_task_allocations.csv")
    print(f"Successful: {out[base.CHANNELS[0]].notna().sum()}/{len(out)}")


if __name__ == "__main__":
    main()
