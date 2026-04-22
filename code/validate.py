"""Inter-prompt reliability validation.

Pick 5 held-out tasks from the 78-task dataset. Re-classify them with an
alternate prompt designed to be semantically equivalent but syntactically
different. Compute Pearson correlation between the primary classification
and the alternate classification for each of the 7 channels. Report the
overall agreement statistic.

This is an inter-prompt reliability test of the classifier, not a human-
vs-LLM inter-rater test. We recommend human re-coding of the same 5 tasks
as follow-on work.
"""

from __future__ import annotations

import json
import os
import time

import httpx
import numpy as np
import pandas as pd

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-6"
CHANNELS = ["K", "I", "P", "A", "C", "T", "R"]

# Alternative system prompt: focused on compensation-premium framing
ALT_SYSTEM = """You analyze professional-service tasks through the lens of \
compensation-premium economics. For each task, you estimate what fraction \
of a practitioner's earned premium above a market-floor salary is \
attributable to each of seven economic channels. Reply with a JSON object only."""

ALT_USER = """Professional task (occupation: {occ}):

"{task}"

Allocate exactly 100 points across these channels, representing what kind \
of economic rent the task produces for the practitioner performing it:

1. K (Knowledge Rent): proprietary domain facts
2. I (Interpretation Rent): synthesizing complex or ambiguous information
3. P (Process Rent): controlling a workflow
4. A (Access Rent): gating information or opportunities
5. C (Credential Rent): formal certification signal value
6. T (Technical Rent): difficult physical/procedural execution
7. R (Relational Rent): trust and accountability in ongoing relationships

Points sum to 100 exactly. JSON: {{"K":<int>,"I":<int>,"P":<int>,"A":<int>,"C":<int>,"T":<int>,"R":<int>}}
"""


def classify_alt(task: str, occ: str) -> dict:
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 300,
        "system": ALT_SYSTEM,
        "messages": [{"role": "user", "content": ALT_USER.format(occ=occ, task=task)}],
    }
    with httpx.Client(timeout=60) as c:
        for _ in range(3):
            r = c.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers, json=body,
            )
            if r.status_code == 200:
                content = r.json()["content"][0]["text"].strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.lstrip().lower().startswith("json"):
                        content = content.split("\n", 1)[1]
                    content = content.split("```")[0]
                parsed = json.loads(content.strip())
                s = sum(parsed[ch] for ch in CHANNELS)
                if s != 100:
                    for ch in CHANNELS:
                        parsed[ch] = round(100 * parsed[ch] / s)
                    drift = 100 - sum(parsed[ch] for ch in CHANNELS)
                    if drift:
                        parsed["I"] += drift
                return parsed
            time.sleep(2)
    raise RuntimeError("classify_alt failed")


def main():
    # Load primary classifications
    primary = pd.read_csv("task_allocations.csv")

    # Pick 5 held-out tasks spanning the 3 occupations, with different content types
    # Seed for reproducibility
    np.random.seed(2026)
    # Stratified sample: 2 from Software Dev, 2 from QA, 1 from Web Dev
    sds = primary[primary["title"] == "Software Developers"].sample(2, random_state=2026)
    qas = primary[
        primary["title"] == "Software Quality Assurance Analysts and Testers"
    ].sample(2, random_state=2026)
    wds = primary[primary["title"] == "Web Developers"].sample(1, random_state=2026)
    held_out = pd.concat([sds, qas, wds], ignore_index=True)

    print(f"=== INTER-PROMPT RELIABILITY TEST — 5 held-out tasks ===\n")
    alt_results = []
    for _, row in held_out.iterrows():
        print(f"Task: {row['task'][:80]}...")
        alt = classify_alt(row["task"], row["title"])
        alt_results.append({"task_id": row["task_id"], **alt})
        # Print comparison
        print(f"  Primary:   K={row['K']}  I={row['I']}  P={row['P']}  A={row['A']}  C={row['C']}  T={row['T']}  R={row['R']}")
        print(f"  Alternate: K={alt['K']}  I={alt['I']}  P={alt['P']}  A={alt['A']}  C={alt['C']}  T={alt['T']}  R={alt['R']}")
        print()

    # Compute per-channel Pearson correlation
    alt_df = pd.DataFrame(alt_results)
    merged = held_out[["task_id"] + CHANNELS].merge(
        alt_df, on="task_id", suffixes=("_primary", "_alt"),
    )

    print("=== CHANNEL-LEVEL AGREEMENT ===")
    correlations = {}
    for c in CHANNELS:
        primary_vals = merged[f"{c}_primary"].to_numpy()
        alt_vals = merged[f"{c}_alt"].to_numpy()
        r = np.corrcoef(primary_vals, alt_vals)[0, 1]
        mae = np.abs(primary_vals - alt_vals).mean()
        correlations[c] = {"pearson_r": float(r), "mae": float(mae)}
        print(f"  {c}: Pearson r = {r:.3f}, MAE = {mae:.1f} pts")

    # Overall correlation across all (task, channel) pairs
    all_primary = merged[[f"{c}_primary" for c in CHANNELS]].to_numpy().flatten()
    all_alt = merged[[f"{c}_alt" for c in CHANNELS]].to_numpy().flatten()
    overall_r = np.corrcoef(all_primary, all_alt)[0, 1]
    overall_mae = np.abs(all_primary - all_alt).mean()
    print(f"\nOVERALL: Pearson r = {overall_r:.3f}, MAE = {overall_mae:.1f} pts across {len(all_primary)} (task, channel) pairs")

    out = {
        "n_tasks": len(held_out),
        "per_channel": correlations,
        "overall": {"pearson_r": float(overall_r), "mae": float(overall_mae)},
        "tasks": held_out[["task_id", "title", "task"] + CHANNELS].to_dict("records"),
        "alt_classifications": alt_results,
    }
    with open("validation_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved validation_results.json")


if __name__ == "__main__":
    main()
