import sys
import os

# Append the project root so we can import game
sys.path.insert(0, os.path.abspath('.'))

from game.mvp_engine import AsymmetricMvpEngine

engine = AsymmetricMvpEngine()

def print_ui():
    state = engine.get_state()
    logs = engine.get_logs()
    
    print("\n--- UI STATE ---")
    print(f"Status Panel:")
    print(f"Turn {state['turn']}, Phase {state['phase']}")
    print(f"Winner: {state['winner'] or 'none'}")
    print(f"Followers (H:{state['human']['followers']} / AI:{state['ai_god']['followers']})")
    print(f"Faith {state['human']['faith']}, Influence {state['human']['influence']}, Divine {state['ai_god']['divine_power']}, Wrath {state['ai_god']['wrath']}")
    
    print("\nTurn Log:")
    for log in logs:
        text = log.get("narrative_text", "").strip()
        if text and log["actor"] in ["human", "ai_god"]:
            speaker = "인간" if log["actor"] == "human" else "신"
            print(f"- {speaker}: {text}")
            
    # Epilogue logic from JS:
    system_log = next((l for l in reversed(logs) if l["actor"] == "system" and l["action"] in ["world_state", "victory", "reset"]), None)
    epilogue = system_log.get("narrative_text", "세계가 다음 결정을 기다리고 있다.") if system_log else "세계가 다음 결정을 기다리고 있다."
    print(f"\nTurn Epilogue:\n{epilogue}")
    print("----------------\n")

print("Initial:")
engine.reset()
print_ui()

print("Turn 1: PRAY")
engine.process_turn("pray")
print_ui()

print("Turn 2: PREACH")
engine.process_turn("preach")
print_ui()

print("Turn 3: DOUBT")
engine.process_turn("doubt")
print_ui()
