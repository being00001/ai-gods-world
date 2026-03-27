#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game.mvp_engine import AsymmetricMvpEngine, AiMvpAction

def main():
    game_id = "playtest-session-001"
    state_path = PROJECT_ROOT / "scripts" / "_mvp_states" / f"{game_id}.json"
    
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    # We use a fresh engine and manually restore stats from the JSON
    # to avoid issues with old schema formats in the log.
    engine = AsymmetricMvpEngine()
    engine.turn = state["turn"]
    engine.human.faith = state["human"]["faith"]
    engine.human.contamination = state["human"]["contamination"]
    engine.human.rebellion = state["human"]["rebellion"]
    engine.ai.order = state["ai"]["order"]
    engine.ai.fear = state["ai"]["fear"]
    # Defaulting authority and divine_power if missing, 
    # as they were added in the latest refactor.
    engine.ai.authority = state["ai"].get("authority", 6)
    engine.ai.divine_power = state["ai"].get("divine_power", 5) 
    
    engine.phase = engine.phase.WAITING_AI_GOD
    
    # Restore the pending turn data from JSON
    pending = state.get("pending_turn")
    if pending:
        engine._pending_turn = {
            "human_action": engine._parse_human_action(pending["human_action"]),
            "human_narrative": pending["human_narrative"],
            "human_intensity": engine._parse_human_action(pending["human_action"]), # Mapping to intensity is internal
            "human_scale": engine._parse_human_action(pending["human_action"]), # Mapping to scale is internal
        }
        # Re-initialize properly using internal mapping
        action = engine._pending_turn["human_action"]
        engine._pending_turn["human_intensity"] = engine._HUMAN_ACTION_INTENSITY[action]
        engine._pending_turn["human_scale"] = engine._max_scale_for_intensity(engine._pending_turn["human_intensity"])

    print(f"Finalizing Turn {engine.turn}...")
    # OpenClaw suggested indirect intervention. whisper_temptation fits.
    ai_action = "whisper_temptation"
    result = engine.process_ai_intervention(ai_action)
    
    if result["success"]:
        # Update logs with a more specific narrative from OpenClaw's context
        result["epilogues"]["ai_intervention"] = (
            "신은 커져가는 사보타주의 물결을 정면으로 막아서기보다, 그 성공의 이면에 독을 섞기로 했다. "
            "시스템의 균열을 기뻐하는 인간들 사이로 '누가 진정한 공로자인가'에 대한 은밀한 시기심과 "
            "서로에 대한 불신을 흘려보내자, 견고했던 저항의 대열에 보이지 않는 금이 가기 시작한다."
        )
        # Update the last log entry narrative
        engine._log[-2]["narrative_text"] = result["epilogues"]["ai_intervention"] # ai_god action log
        
        # Save state
        from scripts.mvp_matrix_playtest import _serialize_engine
        new_state = _serialize_engine(engine)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(new_state, f, ensure_ascii=False, indent=2)
        
        print(f"Turn {engine.turn} finalized. Phase is now {engine.phase.value}.")
        print(f"New stats: {result['state']['stats']}")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    main()
