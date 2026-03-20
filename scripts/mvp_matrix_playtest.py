#!/usr/bin/env python3
"""Run a one-off human action on a saved session and generate a Matrix intervention request for OpenClaw."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine
from game.schemas import GodActionRequest
from game.adapters.matrix_god_adapter import MatrixGodAdapter

STATE_DIR = PROJECT_ROOT / "scripts" / "_mvp_states"

def _state_path(game_id: str) -> Path:
    return STATE_DIR / f"{game_id}.json"

def _serialize_engine(engine: mvp_engine.AsymmetricMvpEngine) -> Dict[str, Any]:
    return {
        "turn": engine.turn,
        "phase": engine.phase.value,
        "human": asdict(engine.human),
        "ai": asdict(engine.ai),
        "winner": engine.winner,
        "log": engine.get_logs(limit=10_000),
        "last_variants": dict(engine._last_variants),
    }


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dict_or_empty(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _deserialize_engine(state: Dict[str, Any]) -> mvp_engine.AsymmetricMvpEngine:
    engine = mvp_engine.AsymmetricMvpEngine()
    engine.turn = _coerce_int(state.get("turn"), 0)
    phase_value = state.get("phase", mvp_engine.MvpPhase.WAITING_HUMAN.value)
    try:
        engine.phase = mvp_engine.MvpPhase(phase_value)
    except (TypeError, ValueError):
        engine.phase = mvp_engine.MvpPhase.WAITING_HUMAN

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
    )
    engine.winner = state.get("winner")
    raw_log = state.get("log")
    engine._log = list(raw_log) if isinstance(raw_log, list) else []

    raw_last_variants = state.get("last_variants")
    if isinstance(raw_last_variants, dict):
        engine._last_variants = {
            str(key): str(value) for key, value in raw_last_variants.items()
        }
    else:
        # Backward-compat recovery for old state dumps that stored variant history lists.
        recovered: Dict[str, str] = {}
        raw_history = state.get("variant_history", {})
        if isinstance(raw_history, dict):
            for key, value in raw_history.items():
                if isinstance(value, list) and value:
                    recovered[str(key)] = str(value[-1])
                elif isinstance(value, str):
                    recovered[str(key)] = value
        engine._last_variants = recovered
    return engine

def main():
    game_id = "playtest-session-001"
    path = _state_path(game_id)
    
    if not path.exists():
        print(f"Error: State file {path} not found.")
        return

    with path.open("r", encoding="utf-8") as f:
        state = json.load(f)
    
    engine = _deserialize_engine(state)
    adapter = MatrixGodAdapter(god_handle="OpenClaw")

    if engine.phase != mvp_engine.MvpPhase.WAITING_HUMAN:
        print(f"Error: Engine is in {engine.phase} phase, not WAITING_HUMAN.")
        return

    # For manual override, you can change this action
    action = os.environ.get("HUMAN_ACTION", "preach")
    print(f"Executing human action: {action} (Turn {engine.turn + 1})")
    
    result = engine.process_turn(action)
    
    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        return

    # Save the updated state after one full turn resolution.
    with path.open("w", encoding="utf-8") as f:
        json.dump(_serialize_engine(engine), f, ensure_ascii=False, indent=2)

    # Build the request schema
    human_intensity_str = result["narrative_tone"]["human_action_intensity"]
    human_intensity = mvp_engine.NarrativeIntensity(human_intensity_str)
    
    intensity_limit = "mid" if human_intensity == mvp_engine.NarrativeIntensity.LOW else "high"

    request = GodActionRequest(
        game_id=game_id,
        turn=result["turn"],
        human_action=action,
        human_narrative=result["epilogues"]["human_consequence"],
        current_state=result["state"],
        intensity_limit=intensity_limit
    )

    # Generate the Matrix payload
    payload = adapter.prepare_intervention(request)
    
    print("\n--- MATRIX INTERVENTION REQUEST ---")
    print(payload["message"])
    print("--- END REQUEST ---")
    
    # Save to playtest_request.json for easy access
    with open(PROJECT_ROOT / "playtest_request.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    print(f"\nState updated and request saved to playtest_request.json.")

if __name__ == "__main__":
    main()
