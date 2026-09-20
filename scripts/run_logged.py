"""Run an ARC-AGI-3 agent against real games with full episode logging.

Writes one structured JSON file per game episode to logs/. The Phase 2
failure taxonomy is built entirely from these logs — treat schema changes
as breaking and bump SCHEMA_VERSION.

Usage (from the repo root, using the Kaggle starter's venv):
    ../ARC-AGI-3-Kaggle-Starter/.venv/bin/python scripts/run_logged.py \
        --game ls20 --max-steps 200

Requires the ARC-AGI-3-Agents framework. Point ARC_AGI3_FRAMEWORK at it,
or leave the default (the vendored copy in the sibling starter repo).

Agent instrumentation convention: an agent may expose
  - self.token_usage: dict updated per turn, e.g.
        {"input_tokens": int, "output_tokens": int}
  - self.episode_extras: dict drained at episode end, e.g.
        {"world_model_code": str, "verification_events": [ {...} ]}
Both are optional; missing values are logged as null/[].
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"

FRAMEWORK = Path(
    os.environ.get(
        "ARC_AGI3_FRAMEWORK",
        ROOT.parent / "ARC-AGI-3-Kaggle-Starter" / "vendor" / "ARC-AGI-3-Agents",
    )
)
AGENT_FILE = ROOT / "agent" / "my_agent.py"


def load_agent_class():
    if not FRAMEWORK.exists():
        raise SystemExit(
            f"Framework not found at {FRAMEWORK}. "
            "Run `make setup` in the ARC-AGI-3-Kaggle-Starter repo, "
            "or set ARC_AGI3_FRAMEWORK."
        )
    sys.path.insert(0, str(FRAMEWORK))
    spec = importlib.util.spec_from_file_location("user_agent_module", AGENT_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "MyAgent"):
        raise SystemExit(f"{AGENT_FILE} must define a class named `MyAgent`")
    return module.MyAgent


def make_logged_agent(MyAgentCls):
    class LoggedAgent(MyAgentCls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.episode_log = {
                "schema_version": SCHEMA_VERSION,
                "episode_id": str(uuid.uuid4()),
                "game_id": self.game_id,
                "agent": self.agent_name,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "turns": [],
                "world_model_code": None,
                "verification_events": [],
                "result": None,
                "failure_classification": None,  # filled in Phase 2
            }
            self._turn_started = None
            self._pending = None

        def choose_action(self, frames, latest_frame):
            self._turn_started = time.perf_counter()
            action = super().choose_action(frames, latest_frame)
            self._pending = {
                "turn": self.action_counter,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision_wall_clock_ms": round(
                    (time.perf_counter() - self._turn_started) * 1000, 2
                ),
                "action": action.name,
                "action_data": action.action_data.model_dump(),
                "reasoning": getattr(action, "reasoning", None),
                "token_usage": getattr(self, "token_usage", None),
            }
            return action

        def take_action(self, action):
            frame = super().take_action(action)
            if self._pending is not None:
                turn = self._pending
                self._pending = None
                turn["observation"] = (
                    None
                    if frame is None
                    else {
                        "state": str(frame.state),
                        "levels_completed": frame.levels_completed,
                        "available_actions": frame.available_actions,
                        "frame": frame.frame,
                    }
                )
                self.episode_log["turns"].append(turn)
            return frame

        def cleanup(self, scorecard=None):
            super().cleanup(scorecard)
            extras = getattr(self, "episode_extras", {}) or {}
            self.episode_log["world_model_code"] = extras.get("world_model_code")
            self.episode_log["verification_events"] = extras.get(
                "verification_events", []
            )
            self.episode_log["ended_at"] = datetime.now(timezone.utc).isoformat()
            self.episode_log["result"] = {
                "state": str(self.state),
                "levels_completed": self.levels_completed,
                "actions": self.action_counter,
                "total_wall_clock_s": self.seconds,
            }
            LOGS_DIR.mkdir(exist_ok=True)
            path = LOGS_DIR / f"{self.episode_log['episode_id']}.{self.game_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.episode_log, f)
            logger.info(f"episode log written to {path}")

    return LoggedAgent


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", default=None, help="Game id(s), comma-separated. Default: all.")
    p.add_argument("--max-steps", type=int, default=200)
    p.add_argument("--list", action="store_true")
    p.add_argument("--tag", action="append", default=[], help="Tag for this run.")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    import arc_agi
    from arc_agi import OperationMode

    arc = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    all_envs = arc.get_environments()

    if args.list:
        for e in all_envs:
            print(f"  {e.game_id}: {getattr(e, 'title', '?')}")
        return

    if args.game:
        wanted = {g.strip().split("-")[0] for g in args.game.split(",")}
        game_ids = [e.game_id.split("-")[0] for e in all_envs
                    if e.game_id.split("-")[0] in wanted]
        missing = wanted - set(game_ids)
        if missing:
            raise SystemExit(f"Unknown game id(s): {sorted(missing)}")
    else:
        game_ids = [e.game_id.split("-")[0] for e in all_envs]

    LoggedAgent = make_logged_agent(load_agent_class())
    if hasattr(LoggedAgent, "MAX_ACTIONS"):
        LoggedAgent.MAX_ACTIONS = min(LoggedAgent.MAX_ACTIONS, args.max_steps)

    for i, game_id in enumerate(game_ids, 1):
        print(f"=== [{i}/{len(game_ids)}] {game_id} ===")
        env = arc.make(game_id)
        agent = LoggedAgent(
            card_id="forensics",
            game_id=game_id,
            agent_name=f"forensics.{game_id}",
            ROOT_URL="http://localhost",
            record=False,
            arc_env=env,
            tags=["forensics"] + args.tag,
        )
        agent.main()

    sc = arc.get_scorecard()
    scorecard_path = LOGS_DIR / f"scorecard.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(scorecard_path, "w", encoding="utf-8") as f:
        json.dump(
            sc.model_dump() if hasattr(sc, "model_dump") else json.loads(str(sc)),
            f,
            indent=2,
            default=str,
        )
    print(f"\nScorecard saved to {scorecard_path}")
    print(f"Aggregate score: {sc.score if hasattr(sc, 'score') else sc}")


if __name__ == "__main__":
    main()
