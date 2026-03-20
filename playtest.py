import sys
sys.path.append(".")
from game.mvp_engine import AsymmetricMvpEngine
import random

engine = AsymmetricMvpEngine()
actions = ["pray", "preach", "doubt"]

print("=== 10-Turn Random Playtest ===")
for i in range(1, 11):
    action = random.choice(actions)
    res = engine.process_turn(action)
    print(f"\n[Turn {i}]")
    print(f"Human Action: {action.upper()}")
    print(f"AI Action: {res['ai_action']}")
    print(f"Human Consequence: {res['epilogues']['human_consequence']}")
    print(f"AI Intervention: {res['epilogues']['ai_intervention']}")
    print(f"World State: {res['epilogues']['world_state']}")
