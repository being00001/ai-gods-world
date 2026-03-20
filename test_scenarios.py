import json
import sys
sys.path.append(".")
from game.mvp_engine import AsymmetricMvpEngine

engine = AsymmetricMvpEngine()

print("=== 1. 조용한 조합 (Low + Low) ===")
engine.reset()
engine.ai.wrath = 0
engine.ai.divine_power = 1
res1 = engine.process_turn("pray")
print("Human Action:", res1["human_action"])
print("AI Action:", res1["ai_action"])
print("Human:", res1["epilogues"]["human_consequence"])
print("AI:", res1["epilogues"]["ai_intervention"])
print("World State:", res1["epilogues"]["world_state"])
print("Tone:", res1["narrative_tone"])
print("Scales:", res1["epilogue_scales"])

print("\n=== 2. 격한 조합 (High + High) ===")
engine.reset()
engine.human.influence = 5
engine.human.followers = 15
engine.ai.followers = 10
engine.ai.wrath = 0
engine.ai.divine_power = 10
res2 = engine.process_turn("pray")
print("Human Action:", res2["human_action"])
print("AI Action:", res2["ai_action"])
print("Human:", res2["epilogues"]["human_consequence"])
print("AI:", res2["epilogues"]["ai_intervention"])
print("World State:", res2["epilogues"]["world_state"])
print("Tone:", res2["narrative_tone"])
print("Scales:", res2["epilogue_scales"])
