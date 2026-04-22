# Itemizing the Knowledge Tax

**A Rent Composition Framework for Predicting AI Exposure Across Professional Services**

Replication materials for the manuscript *"Itemizing the Knowledge Tax: A Rent Composition Framework for Predicting AI Exposure Across Professional Services"* (Lee, 2026).

This repository contains the code, data, and figures needed to reproduce the empirical measurement in Section 4.3a of the manuscript: the O*NET-based rent-vector measurement for software engineering, with bootstrap confidence intervals and tier stratification.

## What's in the paper

The Rent Composition Framework decomposes any knowledge-work role's AI exposure into seven rent channels: Knowledge, Interpretation, Process, Access, Credential, Technical, Relational. Each channel has an AI sensitivity coefficient anchored to published capability benchmarks. A role's AI exposure score is the dot product of its rent composition vector and the sensitivity vector — a single number between 0 and 1 that quantifies how much of the role's compensation premium AI can substitute.

The framework is illustrated across three professional-services industries (construction, software engineering, higher education). Section 4.3a of the paper validates the framework empirically against the U.S. Department of Labor's O*NET 28.3 database. This repository reproduces that validation.

## Repository structure

```
.
├── README.md                    # this file
├── LICENSE                      # MIT
├── paper/
│   ├── framework_paper.md       # full manuscript
│   └── figures/                 # Figures 1–3 (PNG + PDF)
├── code/
│   ├── classify.py              # LLM classifier: task statement → 7-channel rent allocation
│   ├── tier_classify.py         # LLM classifier: task statement → Junior/Mid/Senior/Principal weights
│   ├── aggregate.py             # Weighted aggregation + bootstrap CIs
│   └── figures.py               # Figure generation (matplotlib)
├── data/
│   ├── se_tasks_with_importance.csv   # 78 O*NET task statements with importance ratings
│   ├── task_allocations.csv           # Per-task rent-channel allocations (classifier output)
│   └── task_tier_weights.csv          # Per-task tier-emphasis weights (classifier output)
└── results/
    └── vectors.json             # Aggregated rent vectors + bootstrap CIs + exposure scores
```

## How to reproduce

### Prerequisites

- Python 3.11+
- Anthropic API key (for the classifier; set `ANTHROPIC_API_KEY` in your environment)
- Packages: `pandas`, `numpy`, `matplotlib`, `httpx`, `openpyxl`

```bash
pip install pandas numpy matplotlib httpx openpyxl
```

### Option A — Use the released classifications (fast, ~1 minute)

If you want to reproduce only the aggregation, bootstrap, and figures using the already-classified data:

```bash
cd code
python aggregate.py  # uses data/task_allocations.csv and data/task_tier_weights.csv
python figures.py    # reads results/vectors.json
```

This reproduces `vectors.json` and all three figures exactly (fixed random seed 42).

### Option B — Re-run the full classification (requires API credits, ~10 minutes, ~$2)

If you want to re-run the LLM classifier from the O*NET source data:

```bash
# Download O*NET 28.3 source data
curl -sL "https://www.onetcenter.org/dl_files/database/db_28_3_excel/Task%20Statements.xlsx" -o task_statements.xlsx
curl -sL "https://www.onetcenter.org/dl_files/database/db_28_3_excel/Task%20Ratings.xlsx" -o task_ratings.xlsx

# (Produce se_tasks_with_importance.csv from those two files — code in paper repo)

# Run the full pipeline
export ANTHROPIC_API_KEY=sk-ant-...
python code/classify.py        # ~2 min, ~$1
python code/tier_classify.py   # ~2 min, ~$1
python code/aggregate.py       # fast
python code/figures.py         # fast
```

## Key results

| Measurement | Value |
|---|---|
| Base software engineering exposure score (measured) | 0.58 (95% CI 0.55–0.61) |
| Base software engineering exposure score (expert-elicited) | 0.61 |
| Junior tier exposure (measured) | 0.53 (95% CI 0.51–0.56) |
| Mid tier exposure (measured) | 0.56 (95% CI 0.54–0.59) |
| Senior tier exposure (measured) | 0.59 (95% CI 0.57–0.62) |
| Principal tier exposure (measured) | 0.62 (95% CI 0.59–0.65) |
| Tasks classified | 78 |
| Bootstrap resamples | 500 |
| Random seed | 42 |
| LLM model (classifier) | `claude-sonnet-4-6` |
| O*NET version | 28.3 |

## Rent Composition Framework — sensitivity vector

The scalar AI exposure score is computed as:

```
E = 0.85*K + 0.95*I + 0.30*P + 0.40*A + 0.50*C + 0.25*T + 0.10*R
```

where K, I, P, A, C, T, R are the role's rent shares (summing to 1) across the seven channels: Knowledge, Interpretation, Process, Access, Credential, Technical, Relational. The seven coefficients are anchored to published AI capability benchmarks (Med-PaLM 2, LegalBench, Eloundou et al. 2024, and others — see manuscript §2.3).

## The Role Vulnerability Scorecard

The manuscript also packages the framework as a one-page self-assessment tool. Allocate 100 points across the seven channels based on where your role's compensation premium comes from, then compute the exposure score. See §6 of the manuscript for the full Scorecard including worked examples across industries.

## Citation

If you use this framework or replicate these results, please cite:

```
Lee, E. (2026). Itemizing the Knowledge Tax: A Rent Composition Framework for
Predicting AI Exposure Across Professional Services. Working paper.
GitHub: https://github.com/fenago/rent-composition-framework
```

## Data sources and attribution

- **O*NET 28.3** — U.S. Department of Labor, Employment and Training Administration. Public domain. https://www.onetcenter.org/
- **LLM classifier** — Anthropic Claude Sonnet 4.6 via the Anthropic Messages API. Classifier prompts and per-task responses are included in the repository under `data/` for full reproducibility.

## Author and contact

**Dr. Ernesto Lee, DBA** — School of Engineering and Technology, Miami Dade College.
- Email: elee@mdc.edu
- ORCID: [0000-0002-1209-8565](https://orcid.org/0000-0002-1209-8565)
- Google Scholar: https://scholar.google.com/citations?user=eHc8Yc4AAAAJ

## License

MIT License — see `LICENSE`. The O*NET source data is public domain; our derived classifications and aggregations are released under the same terms as the code.

## AI-use disclosure

The rent-channel and tier classifications in this repository were produced by Anthropic's Claude Sonnet 4.6 acting as a zero-shot classifier. Classifier prompts are included in the code files. Author reviewed all classifications and takes full responsibility for the empirical findings. The manuscript text was drafted with Claude as a writing assistant; the author reviewed and substantially revised all generated content.
