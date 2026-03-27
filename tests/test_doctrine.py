from game.mvp_engine import AsymmetricMvpEngine as DeterministicEngine


def _ai_log(engine, action):
    logs = engine.get_logs(limit=30)
    return next(log for log in logs if log["actor"] == "ai_god" and log["action"] == action)


def test_authority_bloom_adds_order_when_authority_is_high_enough():
    engine = DeterministicEngine()
    engine.ai.authority = 10

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True
    pre_order = engine.ai.order

    ai_result = engine.process_ai_intervention("withhold_grace")
    assert ai_result["success"] is True
    assert ai_result["state"]["ai_god"]["order"] == pre_order + 3

    ai_log = _ai_log(engine, "withhold_grace")
    assert ai_log["details"]["authority_bloom_order_bonus"] == 1


def test_taboo_violation_manifest_wrath_with_low_rebellion_reduces_authority():
    engine = DeterministicEngine()
    engine.ai.authority = 6

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True
    assert engine.human.rebellion < 3

    ai_result = engine.process_ai_intervention("manifest_wrath")
    assert ai_result["success"] is True
    assert ai_result["state"]["ai_god"]["authority"] == 4

    ai_log = _ai_log(engine, "manifest_wrath")
    assert ai_log["details"]["taboo_violation"] is True
    assert ai_log["details"]["taboo_authority_penalty"] == -2


def test_taboo_violation_withhold_grace_with_low_faith_reduces_authority_and_clamps():
    engine = DeterministicEngine()
    engine.ai.authority = 1
    engine.human.faith = 2

    human_result = engine.process_human_action("sabotage")
    assert human_result["success"] is True
    assert engine.human.faith < 3

    ai_result = engine.process_ai_intervention("withhold_grace")
    assert ai_result["success"] is True
    assert ai_result["state"]["ai_god"]["authority"] == 0

    ai_log = _ai_log(engine, "withhold_grace")
    assert ai_log["details"]["taboo_violation"] is True
    assert ai_log["details"]["taboo_authority_penalty"] == -2


def test_overextension_sets_next_turn_rebellion_boost_and_consumes_it_on_human_action():
    engine = DeterministicEngine()
    engine.ai.divine_power = 1

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True

    ai_result = engine.process_ai_intervention("whisper_temptation")
    assert ai_result["success"] is True
    assert ai_result["state"]["vulnerable"] is True
    assert engine.human.rebellion == 0
    assert engine.next_turn_modifiers.get("rebellion_boost") == 2

    next_human_result = engine.process_human_action("vote")
    assert next_human_result["success"] is True
    assert next_human_result["state"]["human"]["rebellion"] == 3
    assert "rebellion_boost" not in engine.next_turn_modifiers


def test_next_turn_rebellion_boost_applies_with_clamp():
    engine = DeterministicEngine()
    engine.human.rebellion = 10
    engine.next_turn_modifiers["rebellion_boost"] = 2

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True
    assert human_result["state"]["human"]["rebellion"] == 12
    assert "rebellion_boost" not in engine.next_turn_modifiers


def test_doctrine_alignment_recovery_increases_authority_when_stats_match():
    engine = DeterministicEngine()
    # Doctrine target: Order 8, Fear 4
    engine.ai.order = 7  # within +/- 1
    engine.ai.fear = 5   # within +/- 1
    engine.ai.authority = 5

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True
    # Day baseline reduces Fear -1 -> Fear 4. Order stays 7.
    assert engine.ai.fear == 4
    assert engine.ai.order == 5  # Vote reduces Order -2

    # After human action, we need to get back to alignment range for the test.
    engine.ai.order = 8
    engine.ai.fear = 4

    ai_result = engine.process_ai_intervention("withhold_grace")
    assert ai_result["success"] is True
    # Withhold Grace: Order +2, Fear -1
    # End of Night: Order 10, Fear 3.
    # Wait, the alignment check is at the end of the Night phase AFTER deltas.
    # Let's set it so it ends up in range.
    engine.ai.order = 6  # +2 -> 8
    engine.ai.fear = 5   # -1 -> 4
    
    ai_result = engine.process_ai_intervention("withhold_grace")
    assert engine.ai.order == 8
    assert engine.ai.fear == 4
    assert engine.ai.authority == 6  # 5 + 1 alignment bonus

    ai_log = _ai_log(engine, "withhold_grace")
    assert ai_log["details"]["doctrine_alignment_bonus"] == 1
