"""Classify each task's seniority-tier emphasis.

For each task, rate how strongly the task is characteristic of each tier
(Junior / Mid / Senior / Principal) on a 0-1 scale. These are then used as
weights when aggregating rent vectors to produce tier-specific estimates.

Rationale: O*NET tasks are occupation-level and do not natively stratify by
tier. Published tech-industry career ladders (Google, Meta, GitLab public
handbook, Stripe's engineering levels) show that tiers differ primarily in
which task categories dominate. We use an LLM rubric grounded in these
public ladder descriptions to assign per-task tier weights.
"""

from __future__ import annotations

import json
import os
import time

import httpx
import pandas as pd

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-6"

SYSTEM = """You rate how characteristic a given software engineering task is of \
each seniority tier on a career ladder, based on published FAANG and industry \
career ladders (Google SWE ladder, Meta E3-E7, GitLab public handbook, Stripe \
engineering levels). Respond ONLY with a JSON object."""

USER_TEMPLATE = """Task (O*NET, occupation "{occ_title}"):

"{task}"

Rate how characteristic this task is of each of four tiers on a 0 to 1 scale. \
A value of 1.0 means this task is highly representative of work at that tier; \
0.0 means it is never done by someone at that tier. The four values do NOT \
need to sum to 1 — each tier is rated independently.

Tier definitions (from public career ladders):
- **Junior (L3 / E3 / IC1)**: Well-scoped implementation of assigned components. Primarily writes code from specs. Debugging under guidance. Learning the codebase.
- **Mid-Level (L4 / E4 / IC2)**: Owns feature-level work end-to-end. Translates product requirements into implementations. Some design judgment within established patterns. Debugging independently.
- **Senior (L5 / E5 / IC3)**: Owns subsystem-level design. Performance engineering. Cross-team collaboration. Mentors juniors. Debugs complex distributed issues.
- **Principal / Staff (L6+ / E6+ / IC4+)**: Cross-organizational technical leadership. System architecture. Technical strategy. Mentors seniors. Represents the engineering org externally. Makes technology selection decisions.

Respond with a single JSON object, nothing else:
{{"junior": <0-1>, "mid": <0-1>, "senior": <0-1>, "principal": <0-1>, "rationale": "<1 sentence>"}}
"""


def tier_classify(task: str, occ_title: str) -> dict:
    prompt = USER_TEMPLATE.format(task=task, occ_title=occ_title)
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 300,
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
                    return json.loads(content.strip())
                elif r.status_code in (429, 500, 502, 503, 529):
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            except (httpx.TimeoutException, httpx.ReadTimeout):
                time.sleep(2 ** attempt)
                continue
    raise RuntimeError("tier_classify failed after retries")


def main():
    df = pd.read_csv("se_tasks_with_importance.csv")
    results = []
    for idx, row in df.iterrows():
        print(f"[{idx+1}/{len(df)}] {row['Task'][:70]}...")
        try:
            tier = tier_classify(row["Task"], row["Title"])
            results.append({
                "soc": row["O*NET-SOC Code"],
                "task_id": row["Task ID"],
                "junior": tier["junior"],
                "mid": tier["mid"],
                "senior": tier["senior"],
                "principal": tier["principal"],
                "rationale": tier.get("rationale", ""),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "soc": row["O*NET-SOC Code"],
                "task_id": row["Task ID"],
                "junior": None,
                "mid": None,
                "senior": None,
                "principal": None,
                "rationale": f"ERROR: {e}",
            })
    out = pd.DataFrame(results)
    out.to_csv("task_tier_weights.csv", index=False)
    print(f"\nSaved {len(out)} tier weights -> task_tier_weights.csv")


if __name__ == "__main__":
    main()
