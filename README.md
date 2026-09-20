# ARC-AGI-3 Forensics

**Research question:** When the Executable World Model (EWM) agent
architecture — state-of-the-art on ARC-AGI-3 with a frontier model — is
driven by a consumer-scale open model (≤14B parameters) instead, which
component fails: exploration, world-model synthesis, self-verification,
or planning? And what is the single minimal intervention that recovers
the most RHAE on the official standard harness?

ARC Prize 2026 entry: ARC-AGI-3 track (submissions due 2026-11-02) and
Paper Track (papers due 2026-11-08).

## Layout

- `agent/` — the agent. `my_agent.py` is the single file spliced into the
  Kaggle submission notebook (see the ARC-AGI-3-Kaggle-Starter workflow).
- `scripts/run_logged.py` — episode runner with full structured logging.
  One JSON file per game episode in `logs/`.
- `logs/` — episode logs (gitignored). The Phase 2 failure taxonomy is
  built from these.
- `taxonomy/` — failure classification work.
- `paper/` — Paper Track draft.
- `compliance.md` — competition constraints checklist.

## Running

Requires the [ARC-AGI-3-Kaggle-Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter)
repo as a sibling directory (provides the venv and vendored agent framework):

```bash
../ARC-AGI-3-Kaggle-Starter/.venv/bin/python scripts/run_logged.py --game ls20 --max-steps 200
```

Set `ARC_API_KEY` for non-anonymous access to the ARC-AGI-3 environments.

## License

MIT-0 (see LICENSE), as required for ARC Prize 2026 eligibility.
