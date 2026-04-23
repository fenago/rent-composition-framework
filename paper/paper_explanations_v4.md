# Paper Explanations — v4

*A plain-English walkthrough of "Itemizing the Knowledge Tax" for Dr. Ernesto Lee. Companion to `framework_paper_v4.md`. Not a summary of the paper — an explanation of how every piece of the paper got built, what decisions we made along the way, and where the numbers come from.*

---

## 1. What kind of paper is this?

Three things are happening at once, and it helps to name them separately so nothing gets confused with anything else.

**It's a framework paper.** The primary contribution is a new way of thinking about professional services and AI. We propose that every professional's fee premium is actually a bundle of seven distinct "rent channels" — seven different reasons a client pays above-market prices for that service. Then we say AI attacks each of those seven channels differently, so you can predict exposure by looking at the bundle. The framework is the intellectual scaffolding. It's not a finding; it's a way of seeing.

**It's a simulation paper, inside the framework paper.** Case Study One (AEC — Architecture, Engineering, Construction) uses agent-based modeling — a kind of computer simulation where lots of little software "agents" interact and you see what emerges from their interactions. We built a simulation of 500 agents representing Owner's Representatives, General Contractors, and Designers, and watched what happened to their margins when AI adoption dialed up from 0 to 100 percent. That simulation is reported in detail in a separate companion paper but summarized in Section 3 of the framework paper.

**It's an empirical validation paper, also inside the framework paper.** Case Study Two (Software Engineering) and Case Study One updated (AEC) have a fundamentally different kind of evidence: we actually measured rent vectors from real data (U.S. Department of Labor's O*NET database) using an LLM as a classifier, computed confidence intervals, and compared against our expert-elicited predictions. That's a small empirical study that happens to live inside a framework paper.

So the research design is **theory-plus-evidence, three-case-study, mixed-methods**. Some parts are theoretical (the framework itself, the sensitivity coefficients). Some parts are simulated (the AEC ABM). Some parts are empirical (the O*NET measurements). Some parts are predictive (the three falsifiable predictions in Section 7). The paper is intentionally hybrid because a pure theory paper could not test itself and a pure empirical paper could not generalize.

---

## 2. The problem we're solving

For centuries, professionals charged above-market fees because they knew something their clients didn't. A doctor, a lawyer, a construction manager, an architect — each of them held information their client couldn't independently verify, and each charged a premium for that privilege. That premium is what KP Reddy calls the "knowledge tax."

The internet knocked one wall of that premium down (access to raw information — Zillow, WebMD, LegalZoom), but left the other walls intact. Professionals could still charge the premium because *access to information is not the same as the ability to use it*. You can read the medical literature. You cannot diagnose yourself. You can see the comps on Zillow. You cannot assess what they mean for your purchase. Interpretation stayed with the expert.

Generative AI attacks that interpretation layer directly. A large language model can now read a 60-page inspection report and tell you what it means for you specifically. It can read a contract and flag unusual provisions. It can synthesize patient histories into differential diagnoses. So the question everyone is asking is: **which professionals will be affected, how much, and by when?**

Two research communities have tried to answer this question and neither has answered it fully.

**The labor-economics community** (most visibly Eloundou, Manning, Mishkin, and Rock in their 2024 *Science* paper) has been measuring *task-level exposure*. They take each occupation, catalog its tasks, rate each task for LLM substitutability, and estimate overall exposure. That work is rigorous and widely cited, but it treats an occupation as just a bag of tasks. It can tell you that a software engineer's tasks are heavily exposed; it cannot tell you what will happen to software engineer compensation, what will happen to the junior-vs-senior wage gap, or which roles within the profession survive.

**The industry-practitioner community** (most visibly KP Reddy's 2025 whitepaper *The End of the Knowledge Tax*) has been describing the economic mechanism. Reddy argues the knowledge tax is being repealed, and he describes the historical sequence (internet collapsed access, AI is now attacking interpretation). But his work is qualitative. It cannot produce a number. You cannot submit Reddy to peer review and have anyone test whether he's right.

Our paper is the bridge. We take the economic framing from Reddy (rent as the thing being attacked) and pair it with the numerical discipline of the labor-economics community (anchored coefficients, confidence intervals, falsifiable predictions). The result is a formula — a single number between zero and one — that predicts AI exposure for any knowledge-work role, computable in minutes, directly testable against future labor-market data.

---

## 3. The framework in plain English

### Rent, plainly

"Rent" in this paper doesn't mean what you pay a landlord. It's a term of art in economics that means *the extra money somebody gets paid above what the work itself actually costs*. If a plumber would take $40/hour for routine work but charges $200/hour in a 2 AM emergency, that $160 difference is rent. It exists because of scarcity, urgency, information, licensing — things other than the labor itself.

Every professional fee has rent baked into it. A doctor's $500 for 15 minutes isn't just labor cost; it's a premium she earns because you don't know medicine, you can't interpret your own symptoms, she has a license you don't, and she's been your doctor for years. Each of those is a different kind of rent.

### The seven channels

We identified seven distinct economic reasons a professional earns above-market fees:

1. **Knowledge rent (K)**: they know substantive domain facts you don't
2. **Interpretation rent (I)**: they can synthesize and render judgment on complex information
3. **Process rent (P)**: they control the workflow — the approval pipeline, the sequence of steps
4. **Access rent (A)**: they gate information or opportunities you can't reach otherwise
5. **Credential rent (C)**: they have licenses/degrees/certifications that you can't quickly acquire
6. **Technical rent (T)**: they can do physical or procedural work that's hard to automate
7. **Relational rent (R)**: they have trusted long-duration relationships and bear accountability

The seven together are supposed to capture the full set of reasons somebody might charge a premium. Not every profession uses all seven. A surgeon leans heavily on Technical (actually doing the operation). A judge leans heavily on Credential (being duly appointed). A construction manager leans heavily on Process (controlling what gets built when). A family doctor uses a little of everything.

For any specific role, we assign "shares" to each channel. We make the shares sum to 1 (or 100 points out of 100) so the vector is a clean partition. A family physician's share vector might be K = 0.25, I = 0.30, P = 0.10, A = 0, C = 0.15, T = 0.10, R = 0.10. That says: 25% of her premium comes from knowing things, 30% from interpreting them, 10% from controlling the workflow, 15% from her MD, and so on.

### The sensitivity vector

Every channel has a different AI vulnerability. We assigned each channel a coefficient between 0 and 1 representing how much of that channel's rent AI can substitute.

- K = 0.85 (AI knows most facts professionals know, but not tacit edge cases)
- I = 0.95 (AI interprets complex documents at near-professional level)
- P = 0.45 (agentic AI is starting to run workflows but isn't fully autonomous yet)
- A = 0.40 (AI helps discovery but doesn't open gated networks)
- C = 0.50 (credentials erode when alternative signals appear but institutions persist)
- T = 0.25 (embodied physical work is hard for current AI)
- R = 0.10 (trust and long-term relationships are nearly unreplicable)

These numbers are *informed estimates anchored to published benchmarks*, not measurements. For example, Interpretation gets 0.95 partly because Google's Med-PaLM 2 scored 86.5% on medical licensing exam questions and frontier models do comparable work on legal reasoning benchmarks. Process got raised from 0.30 to 0.45 during this project because our empirical measurement of Software Engineering showed Process is a much bigger share of SE rent than we initially thought, and agentic AI tools (GitHub agents, Claude Code, Copilot Workspace) are actively eating that share. When the data taught us something, we updated the framework. That's an honest feedback loop.

### The exposure score

The exposure score is just the dot product of the rent vector and the sensitivity vector. In plain English: multiply each channel's share by its AI vulnerability, then add them all up.

For the family physician above:
```
(0.25 × 0.85) + (0.30 × 0.95) + (0.10 × 0.45) + (0 × 0.40)
+ (0.15 × 0.50) + (0.10 × 0.25) + (0.10 × 0.10) = 0.65
```

Her exposure score is 0.65. That means *roughly 65% of her compensation premium is tied to work AI can in principle perform*. It does NOT mean she will lose 65% of her income. It does NOT mean 65% of her job goes away. It means two-thirds of her pricing power sits in channels AI is actively eroding, and one-third sits in channels AI cannot touch. Her strategic adaptation path is to lean into the one-third (procedures, long-term relationships, patient trust) and decouple her fee structure from the two-thirds (diagnostic interpretation she could have AI-assist with instead of billing time for).

### Tiers

To make the scores digestible, we grouped them into four tiers:

- **Resilient (0–0.30)**: AI mostly augments; little repricing pressure
- **Adapting (0.30–0.50)**: moderate exposure; multi-year adaptation window
- **Exposed (0.50–0.70)**: substantial compression coming in 2–5 years; service-delivery redesign urgent
- **High-Risk (0.70–1.00)**: most of the pricing power is AI-substitutable; strategic reinvention on 18-month horizon

---

## 4. Case Study 1 — AEC (the simulation part)

### What AEC is

Architecture, Engineering, and Construction. A roughly $1.9 trillion sector in the U.S. For any sizable building project, three professional roles are present:

- **Owner's Representative (OR)**: hired by the owner to manage contractors and designers on the owner's behalf
- **General Contractor (GC)**: builds the thing
- **Designer/Architect**: designs the thing

Each charges fees as a percentage of construction cost. OR fees run 1–3%, GC margins 3–6%, Designer fees 8–15% (of total construction cost).

### Why we picked AEC as Case 1

Because KP Reddy's whitepaper focuses on AEC (he's an AEC-industry CEO), and we want to engage his argument directly. He predicts that the Owner's Representative role *thrives* while contractors and designers get compressed. We tested that prediction.

### The simulation design

We built an agent-based model. An agent-based model is a computer simulation where you create many software "agents" — here, 500 of them — each representing a professional in the market. You give each agent a set of rules (how they price, how they compete, how they respond to AI adoption). You run the simulation forward in time. You see what emerges.

The specifics:
- 500 agents total: 100 Owner's Reps, 150 GCs, 150 Designers, 100 Owner agents (clients)
- 20-year time horizon
- AI adoption rate α swept from 0 to 1 across 11 levels
- 50 random-seed replications at each α level (so we can get means and confidence intervals)

At each AI level, we reduced each channel's rent share by (1 − sensitivity × α). So at α = 0.5, Interpretation rent is halved; at α = 1.0, it's gone entirely. Then the agents compete, earn margin, and sometimes fall below their reservation margin (they "exit" the market).

### What the simulation found

- At α = 0 (pre-AI): OR margin = 30.4%, GC margin = 13.3%, Designer margin = 17.1%. These roughly match empirical survey data from CMAA, AGC, and AIA.
- At α = 1 (full AI): OR margin = 14.3%, GC margin = 4.0%, Designer margin = 10.1%
- Margin retention: OR 47%, GC 30%, Designer 59%
- GC extinction rate (agents falling below reservation margin and exiting): **73%** at full AI
- OR extinction rate: stays below 5% throughout

**The interpretation is nuanced.** Reddy said OR thrives. We found OR doesn't thrive — OR loses more than half its margin. But OR doesn't *exit* the market, because the reservation-margin floor for OR is protected by liability absorption (clients need a responsible party, and that party has to be human). GC has no such floor, so GC margins crash through zero and agents exit en masse.

So Reddy was directionally right but quantitatively inaccurate. OR survives. OR doesn't thrive. GC is the existential loser. Designer is mildly resilient because Credential rent holds up better than Interpretation rent.

### Honest limitation of Case 1

**The rent vectors for OR, GC, and Designer in the original paper are expert-elicited, not measured.** We assigned them based on our reading of the industry. This is the single biggest weakness of the AEC case: *the simulation tests what we assumed, but we assumed the rent composition rather than measuring it*.

That's why Case Study 1's empirical update (Section 3.1a, added in v4.1 as part of the SR-acceptance push) matters — we now have O*NET-based measurements of the three AEC roles using the same LLM-classifier protocol as the Software Engineering case, so the framework has real data behind both AEC and SE, not just SE.

---

## 5. Case Study 2 — Software Engineering (the empirical part)

### Why SE

Three reasons. First, software engineering is the profession that *builds* the AI systems attacking every other profession. Reddy's whitepaper doesn't cover software engineering (he focuses on nine other industries). That omission is conspicuous — it's the profession most directly in contact with the disruption, and it should be studied. Second, software engineering's rent composition is unusually public — compensation data from Levels.fyi, hiring data from Indeed, career-ladder descriptions from Google/Meta/Stripe/etc. are all scrapeable or publicly posted. Third, the Builder's Paradox — the profession that builds AI is subject to its own tools — is an intellectually striking finding that deserved its own case study.

### The data we used

**O*NET** (Occupational Information Network) is the U.S. Department of Labor's free public database describing every occupation in the country. For each occupation, O*NET provides a list of "task statements" — discrete activities that people in that occupation do — plus importance ratings that tell you how central each task is.

For software engineering we pulled task statements for three O*NET occupations:
- Software Developers (15-1252.00) — 19 tasks
- Software Quality Assurance Analysts and Testers (15-1253.00) — 30 tasks
- Web Developers (15-1254.00) — 29 tasks

Total: 78 task statements, each paired with its O*NET importance score.

### The LLM as a classifier

This is the novel methodological move. For each of those 78 task statements, we fed the text into a large language model (Anthropic's Claude Sonnet 4.6) with a prompt asking: "Given this task, allocate exactly 100 points across these seven rent channels based on what kind of economic rent a practitioner earns by performing it." The model returned an allocation plus a one-sentence rationale.

Why use an LLM instead of having a human code it? Three reasons.

1. **Reproducibility**: if a human codes 78 tasks, another researcher can't exactly replicate that human's judgment. An LLM with a fixed prompt, fixed model version, and fixed random seed produces the same output every time. That's scientific rigor.

2. **Scale**: coding 78 tasks by hand would take several days of expert time. The LLM does it in 2 minutes at ~$1 of API cost. That opens the door to larger-scale replications (hundreds of occupations) that would be infeasible with human coding alone.

3. **Published methodology**: using LLMs as classifiers for text-annotation tasks is itself a legitimate and published methodology. Zheng et al. (2023) validated LLM-as-judge for reasoning tasks; Gilardi, Alizadeh, and Kubli (2023) showed in PNAS that ChatGPT exceeds crowd-worker inter-rater reliability on text classification. So we're on established methodological ground.

### How we validated the classifier

We did an inter-prompt reliability test. We picked 5 tasks (stratified: 2 from Software Devs, 2 from QA, 1 from Web Devs, sampled with seed 2026 for reproducibility). We re-classified them with a semantically equivalent but syntactically distinct prompt (reframed around compensation-premium language instead of rent-channel language). Then we correlated the primary and alternate classifications channel by channel.

**Result: Pearson r = 0.85 overall across 35 (task × channel) pairs, MAE = 5.5 points.** Per-channel: Process r = 0.96, Access r = 0.93, Technical r = 0.88, Knowledge r = 0.85, Interpretation r = 0.71, Relational r = 0.53, Credential r = 0.40. The lower numbers on Relational and Credential reflect the fact that those channels usually get small allocations (5–15 points), and small absolute differences become large relative differences.

0.85 overall is solid inter-prompt reliability. It's not inter-*rater* reliability (we'd need a human second rater for that), but it tells us the classifier is stable — two plausibly-phrased prompts produce similar outputs.

### Confidence intervals and bootstrap

For every aggregate measurement, we report 95% bootstrap confidence intervals. "Bootstrap" is a statistical technique for quantifying uncertainty when you don't know the true population distribution.

The procedure: take your 78 task classifications. Randomly resample them *with replacement* (i.e., some tasks appear multiple times in the resample; others don't appear). Compute the aggregate rent vector on that resample. Do this 500 times. The 2.5th and 97.5th percentiles of the resulting distribution are your 95% CI.

Why task-level resampling? Because the biggest source of uncertainty isn't within-task (the classifier is stable per the inter-prompt test) — it's which tasks O*NET chose to include in its occupational inventory. Another task inventory from another year or another source might produce a different rent vector. Bootstrap at the task level tells us how sensitive our aggregate is to that task-set selection.

Seed 42 for the bootstrap (because it's the convention, and it lets anyone reproduce our exact CI values).

### What we found

Aggregate software engineering rent vector (measured from O*NET, weighted by importance):
- K = 0.19 [95% CI 0.17, 0.22]
- I = 0.28 [0.25, 0.31]
- P = 0.20 [0.18, 0.23]
- A = 0.03 [0.02, 0.04]
- C = 0.05 [0.04, 0.05]
- T = 0.20 [0.16, 0.23]
- R = 0.05 [0.04, 0.06]
- **Exposure Score: 0.61 [95% CI 0.59, 0.63]**

Expert-elicited mean across tiers (what we predicted in Section 4.2): Exposure 0.62.

**The measurement validates the aggregate prediction** — measured 0.61 and elicited 0.62 are within the confidence interval. The framework's headline number survives the empirical test.

**The measurement does NOT validate the channel composition**. Expert judgment over-weighted Interpretation (we predicted 0.36 on average, measured 0.28), over-weighted Relational (0.15 predicted, 0.05 measured), and under-weighted Process (0.11 predicted, 0.20 measured). That's a finding about expert elicitation, not about the framework — it tells us that when people apply the rubric by gut, they cluster too much at Interpretation and miss Process rent.

### The tier-stratification surprise

We also tried to produce tier-specific rent vectors (Junior / Mid / Senior / Principal) by weighting the same task set with tier-emphasis scores. The measurement produced:

- Junior: 0.56
- Mid: 0.59
- Senior: 0.62
- Principal: 0.65

Which is the *opposite* direction from what we predicted from expert elicitation:

- Junior: 0.75
- Mid: 0.74
- Senior: 0.58
- Principal: 0.41

Elicitation says exposure *falls* with seniority. Measurement says exposure *rises* with seniority.

**We reported this honestly.** The explanation (in Section 4.3a and Section 8) is that O*NET task inventories describe *what work exists in the occupation* but not *how time is allocated across tasks by tier*. A senior engineer might spend 40% of her time on one O*NET task; a junior only 5%. Our tier-weighting classifier can't capture that time-allocation difference from an occupation-level inventory.

So the measurement reveals the framework's limit: **scalar scores can be measured from occupation-level data; tier stratification needs time-allocation data**. That's a useful methodological finding about the framework itself, not a contradiction of the Builder's Paradox. The Builder's Paradox prediction rests on the 2023–2025 labor-market data we document in Section 4.3 (Stanford's 67% decline in entry-level tech postings, Levels.fyi compensation data showing widening tier gaps, etc.) — not on the O*NET tier-stratified measurement.

---

## 6. Case Study 3 — Higher Education (the reasoned hypothesis)

### Why HE

Because Reddy covered higher education but treated it as a monolith, focusing on the degree-as-credential angle. That misses institutional heterogeneity. Elite research universities and community colleges have fundamentally different rent compositions. Dr. Lee writes from inside a community college (Miami Dade College), which provides an unusually credible vantage point.

### What we did

We built expert-elicited rent vectors for four higher-ed roles:
- R1 Research Faculty: K = 0.30, I = 0.40, P = 0.05, A = 0, C = 0.15, T = 0, R = 0.10 — **Exposure 0.74**
- Community College Faculty: K = 0.15, I = 0.15, P = 0.05, A = 0, C = 0.10, T = 0.35, R = 0.20 — **Exposure 0.45**
- Academic Advisors: Exposure 0.46
- Executive Leadership: Exposure 0.40

**The prediction — the "Mid-Market Mirror" hypothesis — is that community colleges face LESS exposure than elite research universities.** This inverts the conventional narrative (in which community colleges are supposed to lose to AI tutoring). The reasoning: community college value rests on hands-on skill transfer and student-relationship accountability; elite universities rest on credential signaling and research production. AI eats credentials and research tasks faster than it eats hands-on instruction.

### The supporting evidence (not proof)

The National Student Clearinghouse Research Center (NSCRC) reports:
- Fall 2023: community college enrollment grew 2.6% (+118,000 students) — the first enrollment increase since the pandemic
- Fall 2024: community college enrollment grew ~6%, outpacing public four-year (3.2%)
- Short-term credential programs grew 9.9% in Fall 2023 vs. 3.6% for associate degrees

This is consistent with the Mid-Market Mirror hypothesis but doesn't prove it. The rebound might be pandemic-recovery dynamics, labor-market cooling, or demographic timing rather than AI-driven. A causal identification would require a research design we didn't attempt (e.g., difference-in-difference comparing institutions that adopted AI tutoring early vs. late).

So HE is presented as a **falsifiable prediction** rather than a tested finding. Section 7 states it formally: if community college growth doesn't outpace four-year growth by at least 3 percentage points cumulatively over 2025–2030, the hypothesis is wrong.

---

## 7. How we justified every number

People will ask where the sensitivity coefficients came from. Here's the honest answer per coefficient.

**K = 0.85** — Frontier LLMs beat the mean credentialed professional on closed-knowledge benchmarks. Specific anchor: Med-PaLM 2 scored 86.5% on MedQA (Singhal et al., 2023), exceeding the typical USMLE pass threshold. LegalBench shows similar performance on factual retrieval tasks. We left 0.15 as residual for tacit, unpublished, or edge-case knowledge that stays with humans.

**I = 0.95** — Frontier models match expert medians on synthesis-and-reasoning benchmarks. Same Med-PaLM 2 paper on long-form medical reasoning. GPT-4 and successors on LegalBench reasoning tasks. Residual 0.05 captures irreducible judgment under genuine uncertainty.

**P = 0.45** — Raised from our original 0.30 after the SE measurement surprised us. Agentic AI in 2025–2026 (Claude Code, Copilot Workspace, GitHub agents, CI/CD automation, auto-merge tools) increasingly executes multi-step workflow control that previously required human gatekeeping. We kept 0.55 as residual for regulatory sign-offs, cross-organization approvals, and institutional workflow that agentic AI cannot yet handle credibly.

**A = 0.40** — AI expands information discovery but doesn't open gated networks or off-market deal flow.

**C = 0.50** — Credentials are both informational signals and institutional gatekeeping devices. AI erodes the informational component (alternative signals like skill assessments and portfolios become viable) but not the institutional one (state medical boards don't accept AI as a proxy for MD licensure).

**T = 0.25** — Embodied physical execution remains mostly outside current AI capability. Robotics adoption in professional services (surgical robots, construction robotics) is narrow and expensive.

**R = 0.10** — Trust and accountability embodied in long-term human relationships are minimally substitutable. The residual captures AI-augmented relationship-adjacent tasks (scheduling, follow-up, preparation) that accompany rather than replace the relationship.

These are informed estimates anchored to published benchmarks, not free parameters. Different benchmarks would produce modestly different coefficients. Section 8 explicitly names this as a limitation and calls for more rigorous benchmark-to-coefficient mapping in follow-on work.

---

## 8. Decisions we made and why

### Why seven channels instead of four

Reddy uses four (Knowledge, Process, Access, Interpretation). We expanded to seven because Reddy's four conflate economically distinct sources of rent. In particular:

- **Credential** is not the same as Knowledge. A doctor can earn credential rent even when her knowledge isn't special (if the state requires an MD to prescribe, the MD has credential rent regardless of what she knows). Separating them matters because credential rent erodes differently than knowledge rent.
- **Technical** (embodied execution) is not the same as Knowledge (informational advantage). A surgeon's value includes actual steady hands, and those are AI-resistant in a different way than her medical knowledge.
- **Relational** is not captured by any of Reddy's four. This is a major omission — liability absorption and trust are arguably the most AI-resistant channels, and any framework that doesn't distinguish them from Interpretation can't predict which roles survive.

So we kept Reddy's four and added three. The expansion is defensible because each of the three new channels has a distinct economic mechanism and a distinct AI-vulnerability profile.

### Why O*NET and not scraped job postings

Scraped job postings would be methodologically richer (they'd stratify by tier explicitly) but legally gray. Indeed and LinkedIn prohibit scraping in their Terms of Service. Using scraped data in a peer-reviewed paper invites questions we didn't want to have to answer. O*NET is free, public, U.S. government data. It's also the data source Eloundou et al. used, which puts us on identical methodological footing as the most cited recent paper in this space.

### Why Claude Sonnet 4.6 as the classifier

Cost, reproducibility, accessibility. Claude Sonnet 4.6 is accessible via API at modest cost (~$1 for our entire classification), it's documented and version-pinned, and it's capable enough to do the classification reliably (per the inter-prompt reliability test). A different LLM (GPT-4, Gemini) would likely produce similar results — that's a robustness check future work can run.

### Why we raised s_P from 0.30 to 0.45 mid-project

Because the O*NET measurement found Process rent was 0.20 of SE compensation, not 0.05 as we had elicited. If Process is a much bigger share of SE rent than we thought, AND agentic AI is actively substituting Process work, our original 0.30 was too conservative. 0.45 reflects the combined evidence: bigger share + higher substitution capability. This is an example of the framework learning from its own measurement — a feature, not a bug.

### Why we didn't remove the tier-stratified SE prediction after the measurement contradicted it

Because the contradiction is about *data scope*, not about the prediction's underlying logic. O*NET is an occupation-level inventory and can't distinguish tier-level time allocation. The labor-market signals we document in Section 4.3 (Stanford's 67% decline in entry-level postings, Levels.fyi compensation tier widening, 20% decline in 22–25-year-old software developer employment) directly support the barbell prediction. Those are realized data, not just informed guesses. The framework's tier prediction is supported by labor-market evidence and limited by measurement tooling — we said both, transparently.

### Why we chose SR as the primary submission target instead of IEEE Access

SR is in the Nature portfolio. Accept rate is lower (~50% vs. IEEE Access's ~30% officially but typically higher for framework papers), but citation impact is 2–3x higher over a 3-year window. Dr. Lee has a prior SR publication (the blood-cancer prediction paper) and is an active SR reviewer, which materially improves acceptance odds through community-member recognition. The paper's scope (interdisciplinary applied AI + labor economics + higher education policy) matches SR's editorial remit better than IEEE Access, which leans more computer-science.

---

## 9. What would disprove this paper

If the framework is correct, specific things should happen by 2030. Section 7 states three falsifiable predictions; here they are in plain English.

**Prediction 1 — AEC by 2028.** The Associated General Contractors' (AGC) Financial Survey annually reports average net margins for U.S. general contractors. By 2028, those margins should have compressed by 25% or more from their 2023 baseline. Owner's Representative fees (per CMAA annual surveys) should decline by less than 15%. Designer fees (per AIA Firm Survey) should decline by 15–25%.

**Prediction 2 — Software Engineering by 2028.** The ratio of open software engineering positions labeled "junior" or "entry-level" to those labeled "senior" or "staff/principal" should remain below 0.5, compared to a pre-2023 baseline of approximately 1.2. Compensation premium for principal engineers over junior engineers at major tech employers should exceed 3.0x. Entry-level software engineering postings should remain below 50% of their 2022 level. All testable against Levels.fyi, Indeed Hiring Lab, Stack Overflow Developer Survey, and BLS OES data.

**Prediction 3 — Higher Education by 2030.** Community college enrollment growth should outperform four-year public non-research institution enrollment growth by 3 percentage points or more cumulatively over the 2025–2030 period. Short-term credential enrollment growth should outperform bachelor's enrollment growth by 5 percentage points or more. Research-intensive faculty-to-student ratios at R1 institutions should decline. All testable against NCES IPEDS and NSCRC data.

If these predictions fail, the framework needs revision. That's what makes it science and not just commentary.

---

## 10. What this means for real people

This paper has three audiences.

**For practitioners** (doctors, lawyers, engineers, architects, consultants): Use the Scorecard in Section 6. Allocate 100 points across the seven channels based on where your fee premium comes from. Compute your score. The score tells you *how much of your pricing power is at risk*. The channel breakdown tells you *where to adapt*. High Interpretation rent → pivot to relationship-heavy work or outcome-based pricing. High Credential rent → cultivate skill signals that survive credential devaluation. High Process rent → the time-sensitive one, because agentic AI is eating it fastest.

**For policymakers**: Section 5's Mid-Market Mirror hypothesis has direct workforce-development implications. If community colleges are *less* exposed than elite research universities, workforce-development dollars should flow toward community colleges and regional institutions — not away from them. The conventional narrative (in which AI tutoring threatens community colleges first) appears to be backwards.

**For researchers**: The framework is a scaffold. Every number in it is a research question. Can rent vectors be measured more rigorously? (Section 4.3a's O*NET measurement is one attempt; a time-allocation measurement from real practitioner logs would be better.) Can sensitivity coefficients be formally derived from benchmark scores? (We anchored; we didn't formally map.) Does the framework generalize to healthcare, law, finance? (Worked examples in Section 2.4a and Section 6.2 suggest yes; proper studies would confirm.)

---

## 11. Where the numbers came from — summary table

| Number | Source | Method |
|---|---|---|
| Seven rent channels | Theoretical derivation | Extension of Reddy's four-type taxonomy |
| Sensitivity coefficients | Published AI capability benchmarks | Informed estimation anchored to Med-PaLM 2, LegalBench, agentic AI capability state |
| AEC rent vectors (§3) | Expert elicitation | Author's industry knowledge; empirical update in §3.1a (v4.1) |
| SE expert-elicited rent vectors (§4.2) | Expert elicitation | Grounded in public career ladder docs |
| SE measured rent vectors (§4.3a) | O*NET 28.3 task statements | LLM-as-classifier (Claude Sonnet 4.6) with fixed prompt |
| SE exposure scores measured | Dot product of measured vector × sensitivity | Plus 500-sample bootstrap CIs |
| HE rent vectors | Expert elicitation | Author's institutional knowledge |
| AEC simulation results | Agent-based model | 500 agents, 11 α levels, 50 MC seeds, 20-year horizon |
| Inter-prompt reliability (r = 0.85) | 5 held-out tasks re-classified with alternate prompt | Pearson correlation across (task × channel) pairs |
| Community college enrollment data | NSCRC Current Term Enrollment Estimates | Primary-source reporting |
| Industry hiring data | Stanford, Stack Overflow, Indeed Hiring Lab, Levels.fyi | Primary-source reporting |
| Construction fee calibration | CMAA, AGC, AIA annual surveys | Primary-source reporting |

---

## 12. One-paragraph summary of the whole thing

For centuries, professionals charged premium fees because their clients couldn't independently verify what they were paying for. KP Reddy calls this the "knowledge tax." The internet knocked one wall of the knowledge tax down (raw information access) but left three walls standing. Generative AI is now attacking the interpretation wall, and everyone wants to know which professionals lose how much and by when. Our paper decomposes every professional's fee premium into seven distinct rent channels, assigns each channel a published-benchmark-anchored AI sensitivity coefficient, and produces a single scalar exposure score per role. We validate the framework in three ways: by agent-based simulation of the AEC industry, by an empirical measurement of software engineering rent vectors using O*NET and a Claude-Sonnet-based classifier with bootstrap CIs and inter-prompt reliability, and by a reasoned hypothesis about higher education supported by recent enrollment data. The framework produces falsifiable, role-specific, industry-specific predictions by 2028 and 2030. It is the first model that makes the knowledge tax computable — a single number between zero and one, that any practitioner can compute in ten minutes, that tells her how much of her pricing power is at risk and where her durable value still lives. Reddy said the knowledge tax is ending. We itemized it.

---

*End of plain-English explanation. Read the formal paper at `framework_paper_v4.md`. Browse the replication code and data at https://github.com/fenago/rent-composition-framework.*
