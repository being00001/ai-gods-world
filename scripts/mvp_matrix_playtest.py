#!/usr/bin/env python3
"""Run a one-off human action on a saved session and generate a Matrix intervention request for OpenClaw."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine
from game.schemas import GodActionRequest
from game.adapters.matrix_god_adapter import MatrixGodAdapter

STATE_DIR = PROJECT_ROOT / "scripts" / "_mvp_states"

def _state_path(game_id: str) -> Path:
    return STATE_DIR / f"{game_id}.json"


def _serialize_pending_turn(pending_turn: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if pending_turn is None:
        return None
    return {
        "human_action": pending_turn["human_action"].value,
        "human_narrative": pending_turn["human_narrative"],
        "human_intensity": pending_turn["human_intensity"].value,
        "human_scale": pending_turn["human_scale"].value,
        "day_delta": pending_turn["day_delta"],
        "human_delta": pending_turn["human_delta"],
    }


def _presentation_turn(engine: mvp_engine.AsymmetricMvpEngine) -> int:
    if (
        engine.phase == mvp_engine.MvpPhase.WAITING_HUMAN
        and engine._pending_turn is None
        and engine.winner is None
    ):
        return engine.turn + 1
    return engine.turn


def _serialize_engine(engine: mvp_engine.AsymmetricMvpEngine) -> Dict[str, Any]:
    return {
        "turn": _presentation_turn(engine),
        "phase": engine.phase.value,
        "human": asdict(engine.human),
        "ai": asdict(engine.ai),
        "vulnerable": engine.vulnerable,
        "next_turn_modifiers": engine.next_turn_modifiers,
        "winner": engine.winner,
        "win_reason": engine.win_reason,
        "log": engine.get_logs(limit=10_000),
        "variant_history": engine._variant_history,
        "last_variants": dict(engine._last_variants),
        "pending_turn": _serialize_pending_turn(engine._pending_turn),
    }


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dict_or_empty(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_phase(value: Any) -> mvp_engine.MvpPhase:
    try:
        return mvp_engine.MvpPhase(value)
    except (TypeError, ValueError):
        return mvp_engine.MvpPhase.WAITING_HUMAN


def _safe_narrative_intensity(value: Any) -> mvp_engine.NarrativeIntensity:
    try:
        return mvp_engine.NarrativeIntensity(str(value))
    except (TypeError, ValueError):
        return mvp_engine.NarrativeIntensity.LOW


def _safe_narrative_scale(
    value: Any,
    default: mvp_engine.NarrativeScale,
) -> mvp_engine.NarrativeScale:
    try:
        return mvp_engine.NarrativeScale(str(value))
    except (TypeError, ValueError):
        return default


def _deserialize_engine(state: Dict[str, Any]) -> mvp_engine.AsymmetricMvpEngine:
    engine = mvp_engine.AsymmetricMvpEngine()
    phase = _safe_phase(state.get("phase", mvp_engine.MvpPhase.WAITING_HUMAN.value))
    pending = state.get("pending_turn")
    external_turn = _coerce_int(state.get("turn"), 0)
    if (
        phase == mvp_engine.MvpPhase.WAITING_HUMAN
        and not isinstance(pending, dict)
        and state.get("winner") is None
        and external_turn > 0
    ):
        engine.turn = external_turn - 1
    else:
        engine.turn = external_turn
    engine.phase = phase

    human = _dict_or_empty(state.get("human"))
    ai = _dict_or_empty(state.get("ai"))
    default_human = mvp_engine.HumanState()
    default_ai = mvp_engine.AIGodState()
    engine.human = mvp_engine.HumanState(
        faith=_coerce_int(human.get("faith"), default_human.faith),
        contamination=_coerce_int(human.get("contamination"), default_human.contamination),
        rebellion=_coerce_int(human.get("rebellion"), default_human.rebellion),
    )
    engine.ai = mvp_engine.AIGodState(
        order=_coerce_int(ai.get("order"), default_ai.order),
        fear=_coerce_int(ai.get("fear"), default_ai.fear),
        authority=_coerce_int(ai.get("authority"), default_ai.authority),
        divine_power=_coerce_int(ai.get("divine_power"), default_ai.divine_power),
    )
    engine.vulnerable = bool(state.get("vulnerable", False))
    engine.next_turn_modifiers = _dict_or_empty(state.get("next_turn_modifiers"))
    engine.winner = state.get("winner")
    engine.win_reason = state.get("win_reason")
    raw_log = state.get("log")
    engine._log = list(raw_log) if isinstance(raw_log, list) else []

    raw_variant_history = state.get("variant_history")
    variant_history: Dict[str, list[str]] = {}
    if isinstance(raw_variant_history, dict):
        for key, value in raw_variant_history.items():
            if isinstance(value, list):
                variant_history[str(key)] = [str(item) for item in value]
            elif isinstance(value, str):
                variant_history[str(key)] = [value]
    engine._variant_history = variant_history

    raw_last_variants = state.get("last_variants")
    if isinstance(raw_last_variants, dict):
        engine._last_variants = {
            str(key): str(value) for key, value in raw_last_variants.items()
        }
    elif variant_history:
        engine._last_variants = {
            key: values[-1] for key, values in variant_history.items() if values
        }

    if isinstance(pending, dict):
        action = engine._parse_human_action(str(pending.get("human_action", "")))
        intensity = _safe_narrative_intensity(pending.get("human_intensity"))
        default_scale = engine._max_scale_for_intensity(intensity)
        engine._pending_turn = {
            "human_action": action or mvp_engine.MvpAction.VOTE,
            "human_narrative": str(pending.get("human_narrative", "")),
            "human_intensity": intensity,
            "human_scale": _safe_narrative_scale(pending.get("human_scale"), default_scale),
            "day_delta": _dict_or_empty(pending.get("day_delta")),
            "human_delta": _dict_or_empty(pending.get("human_delta")),
        }
    else:
        engine._pending_turn = None

    return engine


def _load_or_init_engine(game_id: str) -> Tuple[mvp_engine.AsymmetricMvpEngine, str]:
    path = _state_path(game_id)

    if not path.exists():
        engine = mvp_engine.AsymmetricMvpEngine()
        engine.reset()
        return engine, "new"

    with path.open("r", encoding="utf-8") as f:
        state = json.load(f)
    return _deserialize_engine(state), "loaded"


def _save_engine(game_id: str, engine: mvp_engine.AsymmetricMvpEngine) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = _state_path(game_id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(_serialize_engine(engine), f, ensure_ascii=False, indent=2)
    return path


def main() -> int:
    game_id = os.environ.get("GAME_ID", "playtest-session-002")
    action = os.environ.get("HUMAN_ACTION", "preach")
    request_path = Path(
        os.environ.get("REQUEST_PATH", os.fspath(PROJECT_ROOT / "playtest_request.json"))
    )

    path = _state_path(game_id)
    engine, source = _load_or_init_engine(game_id)
    adapter = MatrixGodAdapter(god_handle="OpenClaw")

    if not path.exists():
        print(f"Initialized new state at {path}")
    else:
        print(f"Loaded state from {path} ({source})")

    if engine.phase != mvp_engine.MvpPhase.WAITING_HUMAN:
        print(
            f"Error: Engine is in {engine.phase.value} phase, not WAITING_HUMAN. "
            "Complete or reset this session before applying another human action."
        )
        return 1

    print(f"Executing human action: {action} (Turn {engine.turn + 1})")

    result = engine.process_human_action(action)
    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        return 1

    saved_state_path = _save_engine(game_id, engine)

    human_intensity_str = result["human_intensity"]
    human_intensity = _safe_narrative_intensity(human_intensity_str)
    intensity_limit = (
        "mid" if human_intensity == mvp_engine.NarrativeIntensity.LOW else "high"
    )

    request = GodActionRequest(
        game_id=game_id,
        turn=result["turn"],
        human_action=action,
        human_narrative=result["human_narrative"],
        current_state=result["state"],
        intensity_limit=intensity_limit,
    )

    payload = adapter.prepare_intervention(request)

    print("\n--- MATRIX INTERVENTION REQUEST ---")
    print(payload["message"])
    print("--- END REQUEST ---")

    request_path.parent.mkdir(parents=True, exist_ok=True)
    with request_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(
        f"\nState updated to WAITING_AI_GOD at {saved_state_path} and request saved to {request_path}."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
