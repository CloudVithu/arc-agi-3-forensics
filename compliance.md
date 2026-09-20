# ARC Prize 2026 — Compliance Checklist (ARC-AGI-3 track)

Sources: [competition overview](https://arcprize.org/competitions/2026),
[ARC-AGI-3 track page](https://arcprize.org/competitions/2026/arc-agi-3),
[Kaggle competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3),
[ARC-AGI-3 docs](https://docs.arcprize.org/arc-prize-2026),
[scoring methodology](https://docs.arcprize.org/methodology).
Last verified: 2026-09-20.

## Hard deadlines (official overview page — supersedes all third-party listings)

| Date | Event |
|---|---|
| 2026-03-25 | Competition started |
| 2026-06-30 | Milestone #1 (passed) |
| 2026-09-30 | Milestone #2 — repo must be public by this date for eligibility |
| 2026-10-26 | Entry / team merger deadline |
| **2026-11-02** | **Final submissions due** |
| **2026-11-08** | **Papers due (Paper Track)** |
| 2026-12-04 | Results announced |

NOTE: earlier third-party summaries listed Nov 8 submissions / Dec 4 papers.
The official overview page says Nov 2 / Nov 8 / Dec 4(results). Plan around
Nov 2 submission, Nov 8 paper.

## Submission mechanics

- **Format:** Kaggle code competition. You submit a notebook; Kaggle runs it
  twice — Phase A (Save & Run All validation), Phase B (competition rerun on
  the hidden game set, triggered by clicking "Submit to Competition").
  CONFIRMED (docs.arcprize.org/arc-prize-2026).
- **Official dev kit:** `arcprize/ARC-AGI-3-Kaggle-Starter`. You edit ONE file,
  `agent/my_agent.py` (a `MyAgent` class with `is_done` / `choose_action`);
  `make submit` builds the notebook and pushes it. CONFIRMED.
- **Output file:** `submission.parquet`, selected from the kernel's Output
  File dropdown when submitting. CONFIRMED.
- **Daily submission limit exists** ("clicking Submit is the deliberate moment
  you spend a daily submission"). Exact count: UNCONFIRMED — check the Kaggle
  competition page.
- **Leaderboard:** yes, public leaderboard via competition rerun on the hidden
  game set; local scorecards via `arc.get_scorecard()` and
  arcprize.org/scorecards during development. CONFIRMED.

## Compute environment

- **Runtime limit:** GPU notebook ≤ 9 hours (Kaggle timeline page). CONFIRMED.
- **Accelerator options** (set in starter's `scripts/build_notebook.py`):
  `cpu` / `t4` (T4 ×2, default) / `p100` (P100) / `rtx6000`
  (RTX 6000, `g4-standard-48`, ARC-AGI-3-exclusive, burns GPU quota faster).
  CONFIRMED. Exact VRAM/RAM/CPU per option: standard Kaggle notebook specs
  (T4×2 = 2×16GB); P100 = 16GB; RTX 6000 ≈ 48GB — UNCONFIRMED in rules text,
  verify on Kaggle docs before sizing the model.
- **Internet access during evaluation: DISABLED.** No API-based systems
  (GPT/Claude/etc.) at inference. CONFIRMED (competition overview rules +
  starter docs: "All accelerated Kaggle sessions have internet disabled").
- **Model weights:** must ship inside the notebook environment — standard
  route is Kaggle Datasets/Models attached to the notebook. Max weights size:
  UNCONFIRMED — verify Kaggle dataset size limits and any competition-specific
  cap. (Prior evidence: milestone-winning agents ran locally-deployed
  Gemma-4-31B, so multi-GB weights are feasible.)
- **Per-game wall-clock limit:** the framework enforces action caps; the
  starter agent self-caps via `MAX_ACTIONS`. Whether the competition rerun
  imposes a per-game time/action budget beyond the 9h total: UNCONFIRMED —
  verify with ARC Prize team / Kaggle rules page.
- Game environments run locally in the notebook via the `arc-agi` package
  (offline after first cache); the hidden evaluation game set is served
  through Kaggle's gateway sidecar during Phase B. CONFIRMED.

## Open-source / licensing

- **Authored code must be open-sourced under a permissive public-domain
  license — CC0 or MIT-0.** Third-party code must be under a license allowing
  public sharing (Apache-2.0, GPLv3, ...). CONFIRMED. → This repo uses MIT-0.
- Participants must open source their solutions **before receiving official
  private evaluation scores** (all three tracks). CONFIRMED.
- Milestone prize eligibility requires open-sourcing by the milestone date
  (Milestone #2: 2026-09-30). CONFIRMED.
- "All leading participants are expected to open source their solutions to be
  eligible for a prize." Prizes awarded at ARC Prize Inc.'s discretion,
  subject to Technical Team review. CONFIRMED.

## Prize structure (ARC-AGI-3 track, $850K total)

- Grand Prize $700K: first eligible agent scoring 100% (rolls over if unwon).
- Top Score Award $75K: 1st $40K / 2nd $15K / 3rd $10K / 4th $5K / 5th $5K.
- Milestone prizes $75K per milestone: 1st $25K / 2nd $10K / 3rd $2.5K.

## Scoring semantics (RHAE) — CONFIRMED via docs.arcprize.org/methodology

- **Action** = discrete environment-altering step. Tool calls, reasoning,
  retries do NOT count.
- **Human baseline:** upper-median first-time-human action count per level.
- **Per level:** `level_score = (human_baseline_actions / ai_actions)^2`,
  capped at **1.15**.
- **Per game:** weighted average of level scores, weighted by 1-indexed level
  number (later levels count more). Max game score is capped by completion:
  completing only levels 1..k of n caps the game at Σ(1..k)/Σ(1..n) —
  e.g. 4 of 5 levels caps at 66.7% regardless of efficiency.
- **Total:** unweighted average of game scores, 0–100%.
- Consequence for agent design: an action burned on a bad hypothesis costs
  quadratically. Exploration must happen in the world model, not the
  environment.

## Paper Track ($450K: $75K main + $375K bonus pool)

- **Deadline: 2026-11-08** (papers due, per official overview).
- **Format:** Kaggle Writeup + Media Gallery + Public Notebook.
  **1,500 words maximum.** CONFIRMED (third-party listing of official
  requirements — verify on the Paper Track Kaggle page).
- Main awards: 1st $50K / 2nd $20K / 3rd $5K; bonus pool $375K split among
  papers scoring ≥4.5/5 on the rubric (Accuracy, Universality, Progress,
  Theory, Completeness).
- 1,500 words is SHORT. The paper is an extended abstract: RQ, taxonomy
  table, intervention result, one figure. Plan accordingly.

## ARC API key

- Get it from your arcprize.org account (docs: "Get an ARC_API_KEY" link on
  the Get Started page). Anonymous access works for public games but a
  registered key gives full access at release and saved scorecards at
  arcprize.org/scorecards. Set as `ARC_API_KEY` in `.env`.

## UNCONFIRMED — verify with ARC Prize team / Kaggle rules page

1. Exact daily submission limit.
2. Max model-weights size / Kaggle dataset limits for this competition.
3. Per-game time/action budget during competition rerun (beyond 9h total).
4. Exact VRAM/RAM/CPU specs per accelerator option.
5. Paper Track rubric weights beyond the five named criteria.
