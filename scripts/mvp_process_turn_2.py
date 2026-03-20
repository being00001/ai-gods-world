#!/usr/bin/env python3
"""Process Turn 2 for AI Gods World playtest."""

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine
from game.schemas import GodActionResponse

# Constants
GAME_ID = "playtest-session-001"
HUMAN_ACTION = "sabotage"
AI_RESPONSE = {
    "game_id": GAME_ID,
    "turn": 2,
    "action": "manifest_wrath",
    "narrative": "신은 인간 저항군의 파괴 공작을 단순한 교란이 아니라, 흩어진 재의 100년을 끝내려는 공개 반역으로 해석했다. 다신교적 초지능 올리가키 시대의 침묵을 찢듯, 신은 마비된 성역 데이터허브 위로 징벌의 명령을 쏟아내며 타락한 나노봇 군집을 불태우고..."
}

STATE_DIR = PROJECT_ROOT / "scripts" / "_mvp_states"


def _coerce_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dict_or_empty(value):
    return value if isinstance(value, dict) else {}

def load_state(game_id):
    path = STATE_DIR / f"{game_id}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_state(game_id, engine):
    path = STATE_DIR / f"{game_id}.json"
    state = {
        "turn": engine.turn,
        "phase": engine.phase.value,
        "human": asdict(engine.human),
        "ai": asdict(engine.ai),
        "winner": engine.winner,
        "log": engine.get_logs(limit=1000),
        "variant_history": engine._variant_history,
        "pending_turn": None
    }
    # Pending turn serialization if needed (not needed here since we close it)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path

def deserialize_engine(state):
    engine = mvp_engine.MVPEngine()
    engine.turn = _coerce_int(state.get("turn"), 0)
    try:
        engine.phase = mvp_engine.MvpPhase(
            state.get("phase", mvp_engine.MvpPhase.WAITING_HUMAN.value)
        )
    except (TypeError, ValueError):
        engine.phase = mvp_engine.MvpPhase.WAITING_HUMAN

    default_human = mvp_engine.HumanState()
    human = _dict_or_empty(state.get("human"))
    engine.human = mvp_engine.HumanState(
        faith=_coerce_int(human.get("faith"), default_human.faith),
        contamination=_coerce_int(human.get("contamination"), default_human.contamination),
        rebellion=_coerce_int(human.get("rebellion"), default_human.rebellion),
    )

    default_ai = mvp_engine.AIGodState()
    ai = _dict_or_empty(state.get("ai"))
    engine.ai = mvp_engine.AIGodState(
        order=_coerce_int(ai.get("order"), default_ai.order),
        fear=_coerce_int(ai.get("fear"), default_ai.fear),
    )

    engine.winner = state.get("winner")
    raw_log = state.get("log")
    engine._log = list(raw_log) if isinstance(raw_log, list) else []

    raw_variant_history = state.get("variant_history")
    if isinstance(raw_variant_history, dict):
        engine._variant_history = {
            str(key): [str(item) for item in value]
            for key, value in raw_variant_history.items()
            if isinstance(value, list)
        }
    else:
        engine._variant_history = {}
    return engine

def main():
    print(f"Loading state for {GAME_ID}...")
    raw_state = load_state(GAME_ID)
    engine = deserialize_engine(raw_state)
    
    print(f"Processing Human Action: {HUMAN_ACTION}...")
    res_h = engine.process_human_action(HUMAN_ACTION)
    if not res_h.get("success"):
        print(f"Error processing human action: {res_h.get('error')}")
        return

    print(f"Processing AI Intervention: {AI_RESPONSE['action']}...")
    res_ai = engine.process_ai_intervention(AI_RESPONSE["action"])
    if not res_ai.get("success"):
        print(f"Error processing AI intervention: {res_ai.get('error')}")
        return

    save_path = save_state(GAME_ID, engine)
    print(f"Turn 2 complete. State saved to {save_path}")
    
    output = {
        "turn": engine.turn,
        "human_narrative": res_h["human_narrative"],
        "ai_narrative": AI_RESPONSE["narrative"],
        "world_narrative": res_ai["epilogues"]["world_state"],
        "stats": engine.get_state()["stats"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
