"""Classify O*NET task statements into the 7 rent channels using Claude.

Each task statement is given to Claude with the Rent Composition Framework's
channel definitions and is asked to allocate 100 points across the 7 channels
based on what kind of work the task describes.

Output: JSON with per-task allocations + aggregated rent vectors per occupation.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx
import pandas as pd

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-6"

CHANNELS = ["K", "I", "P", "A", "C", "T", "R"]
CHANNEL_NAMES = {
    "K": "Knowledge — substantive domain facts the client lacks",
    "I": "Interpretation — synthesis, reconciliation, judgment on ambiguous information",
    "P": "Process — controlling the workflow that produces the outcome",
    "A": "Access — gating information or opportunities the client cannot reach directly",
    "C": "Credential — costly observable signals (licenses, certifications, degrees)",
    "T": "Technical — difficult physical, procedural, or embodied execution (incl. hands-on coding, debugging, deployment)",
    "R": "Relational — trusted long-duration relationships and accountability for outcomes",
}

SYSTEM = """You are an expert in economics of professional services and labor markets. \
Your task is to decompose a professional work task into its underlying economic \
rent channels based on the Rent Composition Framework. You allocate exactly 100 \
points across seven channels based on what kinds of economic rent the task \
earns for the professional doing it. Respond ONLY with a JSON object."""

CHANNEL_DEFS_TEXT = "\n".join(f"- **{c}** ({CHANNEL_NAMES[c]})" for c in CHANNELS)

USER_TEMPLATE = """Task statement (from O*NET, for the occupation "{occ_title}"):

"{task}"

Allocate exactly 100 points across these seven rent channels, based on what \
kinds of economic rent a professional earns when performing this task:

{defs}

Rules:
- Points must sum to exactly 100.
- A task typically concentrates in 1-3 channels; rarely does a task draw on all seven.
- "Technical" in software engineering includes the embodied skill of writing, \
debugging, and deploying code — not just physical labor.
- "Interpretation" includes translating product requirements into specifications, \
reading documentation, synthesizing multiple information sources.
- "Relational" includes long-term client/stakeholder relationships and accountability \
for outcomes, NOT short-term collaboration.
- "Process" is about controlling a workflow (e.g., approval gates, release pipelines).
- Be specific. If the task is "Write code to implement feature X", weight heavily to \
Interpretation (spec -> code) and Technical (actual coding), with minor Knowledge.

Respond with a single JSON object, nothing else. Format:
{{"K": <int>, "I": <int>, "P": <int>, "A": <int>, "C": <int>, "T": <int>, "R": <int>, "rationale": "<1 sentence>"}}
"""


def classify(task: str, occ_title: str) -> dict:
    prompt = USER_TEMPLATE.format(
        task=task, occ_title=occ_title, defs=CHANNEL_DEFS_TEXT
    )
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 400,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }
    with httpx.Client(timeout=60) as c:
        for attempt in range(3):
            try:
                r = c.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=body,
                )
                if r.status_code == 200:
                    content = r.json()["content"][0]["text"].strip()
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.lstrip().lower().startswith("json"):
                            content = content.split("\n", 1)[1]
                        content = content.split("```")[0]
                    parsed = json.loads(content.strip())
                    s = sum(parsed[c] for c in CHANNELS)
                    if s != 100:
                        for c in CHANNELS:
                            parsed[c] = round(100 * parsed[c] / s)
                        drift = 100 - sum(parsed[c] for c in CHANNELS)
                        if drift:
                            parsed["I"] += drift
                    return parsed
                elif r.status_code in (429, 500, 502, 503, 529):
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise RuntimeError(
                        f"HTTP {r.status_code}: {r.text[:200]}"
                    )
            except (httpx.TimeoutException, httpx.ReadTimeout):
                time.sleep(2 ** attempt)
                continue
    raise RuntimeError("classify failed after retries")


def main():
    df = pd.read_csv("se_tasks_with_importance.csv")
    results = []
    for idx, row in df.iterrows():
        print(
            f"[{idx+1}/{len(df)}] {row['Title']} — {row['Task'][:70]}..."
        )
        try:
            alloc = classify(row["Task"], row["Title"])
            results.append({
                "soc": row["O*NET-SOC Code"],
                "title": row["Title"],
                "task_id": row["Task ID"],
                "task": row["Task"],
                "importance": row["Importance"]
                    if pd.notna(row["Importance"])
                    else None,
                **{c: alloc[c] for c in CHANNELS},
                "rationale": alloc.get("rationale", ""),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "soc": row["O*NET-SOC Code"],
                "title": row["Title"],
                "task_id": row["Task ID"],
                "task": row["Task"],
                "importance": row["Importance"]
                    if pd.notna(row["Importance"])
                    else None,
                **{c: None for c in CHANNELS},
                "rationale": f"ERROR: {e}",
            })

    out = pd.DataFrame(results)
    out.to_csv("task_allocations.csv", index=False)
    print(f"\nSaved {len(out)} allocations -> task_allocations.csv")
    print(
        f"Successful: "
        f"{out[CHANNELS[0]].notna().sum()}/{len(out)}"
    )


if __name__ == "__main__":
    main()
