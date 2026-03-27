#!/usr/bin/env python3
"""Apply a human action (Day phase) to the current MVP session."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine  # noqa: E402
from scripts.mvp_complete_turn import _load_or_init_engine, _save_engine  # noqa: E402


def _presentation_turn(engine: mvp_engine.AsymmetricMvpEngine) -> int:
    if (
        engine.phase == mvp_engine.MvpPhase.WAITING_HUMAN
        and engine._pending_turn is None
        and engine.winner is None
    ):
        return engine.turn + 1
    return engine.turn


def _human_action_state(engine: mvp_engine.AsymmetricMvpEngine) -> str:
    if engine.phase == mvp_engine.MvpPhase.WAITING_HUMAN:
        return "pending"
    if engine.phase == mvp_engine.MvpPhase.WAITING_AI_GOD:
        return "already_applied"
    if engine.phase == mvp_engine.MvpPhase.ENDED:
        return "game_ended"
    return "unknown"


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: mvp_apply_human_action.py <game_id> <action>")
        print("   or: mvp_apply_human_action.py <game_id> --status")
        sys.exit(1)

    game_id = sys.argv[1]
    mode_or_action = sys.argv[2]

    engine, source = _load_or_init_engine(game_id)

    if mode_or_action in {"--status", "-s"}:
        output = {
            "success": True,
            "game_id": game_id,
            "loaded_state": source,
            "turn": _presentation_turn(engine),
            "phase": engine.phase.value,
            "human_action_state": _human_action_state(engine),
            "winner": engine.winner,
            "pending_turn": bool(engine._pending_turn),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    human_action = mode_or_action

    if engine.phase != mvp_engine.MvpPhase.WAITING_HUMAN:
        print(json.dumps({"success": False, "error": f"Game is in phase {engine.phase.value}, not WAITING_HUMAN"}))
        sys.exit(1)

    result = engine.process_human_action(human_action)
    if not result.get("success"):
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    state_path = _save_engine(game_id, engine)

    output = {
        "success": True,
        "game_id": game_id,
        "loaded_state": source,
        "turn": result["turn"],
        "phase": result["phase"],
        "human_action": human_action,
        "human_narrative": result["human_narrative"],
        "stats": result["state"]["stats"],
        "roles": result["state"]["roles"],
        "vulnerable": result["state"]["vulnerable"],
        "saved_state_path": os.fspath(state_path),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
