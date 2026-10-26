"""My ARC-AGI-3 agent.

Strategy: try each available action, measure the changed cells in frame[0],
attribute changes to the preceding action, then exploit the highest-scoring
action. This is a baseline for experiments, not a general solver.
"""
from __future__ import annotations

import copy
import random
from typing import Any

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


class MyAgent(Agent):
    MAX_ACTIONS = 80

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.action_scores: dict[GameAction, int] = {}
        self.action_attempts: dict[GameAction, int] = {}

        self.previous_grid = None
        self.previous_action = None
        self.action_index = 0

    @property
    def name(self) -> str:
        return f"{super().name}.{self.MAX_ACTIONS}"

    def is_done(
        self,
        frames: list[FrameData],
        latest_frame: FrameData,
    ) -> bool:
        return latest_frame.state is GameState.WIN

    @staticmethod
    def count_changed_cells(previous_grid: Any, current_grid: Any) -> int:
        """Count changed cells between two grid snapshots."""
        changed = 0

        for old_row, new_row in zip(previous_grid, current_grid):
            for old_cell, new_cell in zip(old_row, new_row):
                if old_cell != new_cell:
                    changed += 1

        return changed

    def reset_tracking(self) -> None:
        self.action_scores.clear()
        self.action_attempts.clear()
        self.previous_grid = None
        self.previous_action = None
        self.action_index = 0

    def choose_action(
        self,
        frames: list[FrameData],
        latest_frame: FrameData,
    ) -> GameAction:
        if latest_frame.state in (
            GameState.NOT_PLAYED,
            GameState.GAME_OVER,
        ):
            self.reset_tracking()
            return GameAction.RESET

        # Use only layer zero for this baseline experiment.
        current_grid = latest_frame.frame[0]

        # Attribute this observation's changes to the action taken last turn.
        if self.previous_grid is not None and self.previous_action is not None:
            changed = self.count_changed_cells(
                self.previous_grid,
                current_grid,
            )

            self.action_scores[self.previous_action] = (
                self.action_scores.get(self.previous_action, 0) + changed
            )
            self.action_attempts[self.previous_action] = (
                self.action_attempts.get(self.previous_action, 0) + 1
            )

        # Snapshot the grid so later frame updates cannot alter our baseline.
        self.previous_grid = copy.deepcopy(current_grid)
        self.action_index += 1

        candidates = [
            GameAction.from_id(action_id)
            for action_id in latest_frame.available_actions
        ]
        candidates = [
            action for action in candidates
            if action is not GameAction.RESET
        ]

        if not candidates:
            self.previous_action = None
            return GameAction.RESET

        # First explore every available action at least once.
        untried = [
            action for action in candidates
            if action not in self.action_attempts
        ]

        if untried:
            action = untried[0]
            mode = "explore"
            reason = "Selected an available action not yet attempted."
        else:
            action = max(
                candidates,
                key=lambda candidate: (
                    self.action_scores.get(candidate, 0)
                    / max(self.action_attempts.get(candidate, 0), 1)
                ),
            )
            mode = "exploit"
            reason = (
                "Selected the action with the highest average "
                "observed changed-cell count."
            )

        if action.is_complex():
            action.set_data({
                "x": random.randint(0, 63),
                "y": random.randint(0, 63),
            })

        action.reasoning = (
            f"step={self.action_index}; mode={mode}; "
            f"action={action}; {reason}"
        )

        self.previous_action = action
        return action
