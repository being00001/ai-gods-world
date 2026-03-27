import json
import os
import sys
from pathlib import Path
from dataclasses import asdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from game import mvp_engine

STATE_FILE = PROJECT_ROOT / "scripts" / "_mvp_states" / "playtest-session-001.json"

def _coerce_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def patch_turn_5():
    with STATE_FILE.open("r", encoding="utf-8") as f:
        state = json.load(f)

    # 1. Initialize engine from state
    engine = mvp_engine.AsymmetricMvpEngine()
    engine.turn = _coerce_int(state.get("turn"), 0)
    # We want to re-process Turn 5 AI intervention correctly.
    # Currently, Turn 5 in the log has "system: day", "human: preach", "system: night", "ai_god: withhold_grace", "system: world_state".
    # We need to remove the auto-applied turn 5 night/ai logs and re-apply whisper_temptation.

    # Filter out turn 5 logs starting from 'night' phase
    new_log = []
    found_turn_5_night = False
    for entry in state.get("log", []):
        if entry["turn"] == 5 and entry["actor"] == "system" and entry["action"] == "night":
            found_turn_5_night = True
            break
        new_log.append(entry)
    
    if not found_turn_5_night:
        print("Warning: Turn 5 night log not found as expected. Proceeding with caution.")

    # Reset engine stats to Turn 5 start (after preach)
    # We can reconstruct it or just calculate.
    # Turn 4 end stats: Faith 9, Order 6, Fear 8, Contamination 3, Rebellion 1 (based on previous trace)
    # Turn 5 day: Faith 10, Fear 7
    # Turn 5 preach: Faith 12, Order 5, Rebellion 2
    
    # Actually, let's look at the stats BEFORE the incorrect turn 5 resolve.
    # It's better to just manually set them to turn 4 end and re-run.
    
    # Wait, the JSON's current stats are:
    # "human": {"faith": 6, "contamination": 0, "rebellion": 3}, "ai": {"order": 8, "fear": 2}
    # This is quite different. It seems the engine state was already drifted.
    
    # Let's just Trust the Log up to Turn 5 'preach'.
    # I'll rebuild the engine by replaying the log.
    
    engine.reset()
    engine._log = [] # Clear the init log entry from reset()
    
    for entry in new_log:
        actor = entry["actor"]
        action = entry["action"]
        details = entry.get("details", {})
        delta = details.get("delta", {})
        
        # Apply deltas manually to engine state
        for stat, val in delta.items():
            engine._apply_stat_delta(stat, val)
        
        engine.turn = entry["turn"]
        engine.phase = mvp_engine.MvpPhase(entry["phase"])
        engine._log.append(entry)

    # Now we are at Turn 5 after 'preach' (WAITING_AI_GOD phase)
    # Correct the phase
    engine.phase = mvp_engine.MvpPhase.WAITING_AI_GOD
    
    # Set pending_turn manually for process_ai_intervention
    # We need the preach details
    preach_entry = [e for e in new_log if e["turn"] == 5 and e["action"] == "preach"][0]
    engine._pending_turn = {
        "human_action": mvp_engine.MvpAction.PREACH,
        "human_narrative": preach_entry["narrative_text"],
        "human_intensity": mvp_engine.NarrativeIntensity(preach_entry["details"]["intensity"]),
        "human_scale": mvp_engine.NarrativeScale(preach_entry["details"]["scale"]),
        "day_delta": [e for e in new_log if e["turn"] == 5 and e["action"] == "day"][0]["details"]["delta"],
        "human_delta": preach_entry["details"]["delta"]
    }

    # Now apply OpenClaw's intervention
    print(f"Current stats before AI intervention: {engine._current_stats()}")
    
    result = engine.process_ai_intervention("whisper_temptation")
    
    # Override narrative with OpenClaw's specific text
    engine._log[-2]["narrative_text"] = "신은 커져가는 설교를 정면 탄압할 때가 아니라, 안쪽에서 갈라놓을 때라고 판단했다. 저항의 언어 속에 은밀한 허영과 불신을 흘려보내자, 같은 구호를 외치던 이들 사이에서도 누가 더 순수한 신도인지, 누가 권력을 탐하는지 의심이 번지기 시작한다. 겉으로는 신앙이 높아진 듯 보여도, 그 열기는 하나의 깃발 아래 모이지 못한 채 지역 단위의 균열과 경쟁으로 새어 나간다."
    
    print(f"Applied whisper_temptation. New phase: {engine.phase.value}")
    print(f"Result stats: {engine._current_stats()}")

    # Save
    final_state = {
        "turn": engine.turn,
        "phase": engine.phase.value,
        "human": asdict(engine.human),
        "ai": asdict(engine.ai),
        "winner": engine.winner,
        "log": engine.get_logs(limit=10_000),
        "last_variants": dict(engine._last_variants),
    }
    
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    patch_turn_5()
