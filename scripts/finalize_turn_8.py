#!/usr/bin/env python3
"""Complete Turn 8 for playtest-session-001."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine  # noqa: E402
from game.schemas import GodActionResponse  # noqa: E402

# Data from Turn 8 intervention provided by OpenClaw/User
INPUT_RESPONSE = {
    "game_id": "playtest-session-001",
    "turn": 8,
    "action": "whisper_temptation",
    "narrative": "신은 불어나는 설교의 열기를 곧장 짓누르기보다, 그 안에 숨어든 허영과 경쟁심을 키우는 편이 낫다고 판단했다. 같은 구호를 외치던 이들 사이에서 누가 진정한 신앙을 품었는지, 누가 군중의 환호를 탐하는지에 대한 의심이 번지며 결속이 서서히 갈라지기 시작한다. 신의 속삭임은 공개된 공포보다 더 조용하게, 그러나 더 깊숙이 도시의 의사결정 구조를 침식한다.",
    "intensity": "mid",
    "scale": "regional",
}

STATE_DIR = PROJECT_ROOT / "scripts" / "_mvp_states"


def _state_path(game_id: str) -> Path:
    return STATE_DIR / f"{game_id}.json"


def _serialize_pending_turn(pending_turn: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if pending_turn is None:
        return None
    return {
        "human_action": pending_turn["human_action"].value if hasattr(pending_turn["human_action"], 'value') else pending_turn["human_action"],
        "human_narrative": pending_turn["human_narrative"],
        "human_intensity": pending_turn["human_intensity"].value if hasattr(pending_turn["human_intensity"], 'value') else pending_turn["human_intensity"],
        "human_scale": pending_turn["human_scale"].value if hasattr(pending_turn["human_scale"], 'value') else pending_turn["human_scale"],
    }


def _serialize_engine(engine: mvp_engine.AsymmetricMvpEngine) -> Dict[str, Any]:
    return {
        "turn": engine.turn,
        "phase": engine.phase.value,
        "human": asdict(engine.human),
        "ai": asdict(engine.ai),
        "winner": engine.winner,
        "log": engine.get_logs(limit=10_000),
        "variant_history": engine._variant_history,
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


def _deserialize_engine(
    state: Dict[str, Any],
) -> mvp_engine.AsymmetricMvpEngine:
    engine = mvp_engine.MVPEngine()

    engine.turn = _coerce_int(state.get("turn"), 0)
    engine.phase = _safe_phase(state.get("phase", mvp_engine.MvpPhase.WAITING_HUMAN.value))

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
    engine.winner = state.get("winner")
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

    pending = state.get("pending_turn")
    if isinstance(pending, dict):
        human_action = engine._parse_human_action(str(pending.get("human_action", "")))
        intensity = _safe_narrative_intensity(pending.get("human_intensity"))
        default_scale = engine._max_scale_for_intensity(intensity)
        engine._pending_turn = {
            "human_action": human_action or mvp_engine.MvpAction.VOTE,
            "human_narrative": str(pending.get("human_narrative", "")),
            "human_intensity": intensity,
            "human_scale": _safe_narrative_scale(pending.get("human_scale"), default_scale),
        }
    else:
        engine._pending_turn = None

    return engine


def _load_or_init_engine(game_id: str) -> Tuple[mvp_engine.AsymmetricMvpEngine, str]:
    path = _state_path(game_id)
    if not path.exists():
        engine = mvp_engine.MVPEngine()
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


def main() -> None:
    response = GodActionResponse(**INPUT_RESPONSE)
    engine, source = _load_or_init_engine(response.game_id)

    if engine.phase != mvp_engine.MvpPhase.WAITING_AI_GOD:
        raise RuntimeError(f"Engine phase is {engine.phase}, expected WAITING_AI_GOD")

    if engine.turn != response.turn:
        raise RuntimeError(
            f"Turn mismatch before intervention (engine={engine.turn}, response={response.turn})."
        )

    # Set the AI narrative text from the response to be used in the engine result
    # In mvp_engine.py, process_ai_intervention doesn't take the narrative text, 
    # but the log record usually uses the engine's internal logic. 
    # We might need to ensure the engine uses this narrative.
    # For now, let's just proceed as the engine uses deterministic rules for deltas.
    
    result = engine.process_ai_intervention(response.action)
    if not result.get("success"):
        raise RuntimeError(f"AI intervention failed: {result.get('error')}")

    # Patch the last log entry with the actual narrative if needed
    if engine._log and engine._log[-1]["actor"] == "ai_god":
        engine._log[-1]["narrative_text"] = response.narrative

    state_path = _save_engine(response.game_id, engine)

    output = {
        "game_id": response.game_id,
        "loaded_state": source,
        "turn": result["turn"],
        "epilogue": result["epilogues"],
        "world_narrative": result["epilogues"]["world_state"],
        "stats": result["state"]["stats"],
        "openclaw_response": {
            "action": response.action,
            "narrative": response.narrative,
            "intensity": response.intensity,
            "scale": response.scale,
        },
        "saved_state_path": os.fspath(state_path),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
