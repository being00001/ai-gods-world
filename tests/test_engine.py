import pytest

from game.mvp_engine import AsymmetricMvpEngine as DeterministicEngine


DAY_BASELINE_DELTA = {
    "faith": 1,
    "order": 0,
    "fear": -1,
    "divine_power": 1,
    "contamination": 0,
    "rebellion": 0,
}

NIGHT_BASELINE_DELTA = {
    "faith": 0,
    "order": 0,
    "fear": 1,
    "contamination": 1,
    "rebellion": 0,
}

ALL_DELTA_TABLES = (
    DAY_BASELINE_DELTA,
    NIGHT_BASELINE_DELTA,
    *DeterministicEngine._HUMAN_ACTION_DELTAS.values(),
    *DeterministicEngine._AI_ACTION_DELTAS.values(),
)


@pytest.mark.parametrize(
    "human_action, expected_delta",
    [
        (
            "vote",
            {
                "faith": 0,
                "order": -2,
                "fear": -1,
                "contamination": 0,
                "rebellion": 1,
            },
        ),
        (
            "preach",
            {
                "faith": 2,
                "order": -1,
                "fear": 0,
                "contamination": 0,
                "rebellion": 1,
            },
        ),
        (
            "sabotage",
            {
                "faith": -1,
                "order": -2,
                "fear": 2,
                "contamination": 3,
                "rebellion": 1,
            },
        ),
        (
            "recruit",
            {
                "faith": 1,
                "order": -1,
                "fear": 0,
                "contamination": 0,
                "rebellion": 1,
            },
        ),
    ],
)
def test_day_and_human_action_deltas_match_rule_table(human_action, expected_delta):
    engine = DeterministicEngine()

    result = engine.process_human_action(human_action)

    assert result["success"] is True
    assert result["phase"] == "waiting_ai_god"

    logs = engine.get_logs(limit=10)
    day_log = next(log for log in logs if log["actor"] == "system" and log["action"] == "day")
    human_log = next(
        log for log in logs if log["actor"] == "human" and log["action"] == human_action
    )

    assert day_log["details"]["delta"] == DAY_BASELINE_DELTA
    assert human_log["details"]["delta"] == expected_delta


def test_recruit_action_has_specific_deterministic_delta():
    engine = DeterministicEngine()

    result = engine.process_human_action("recruit")

    assert result["success"] is True
    assert result["phase"] == "waiting_ai_god"

    logs = engine.get_logs(limit=10)
    recruit_log = next(log for log in logs if log["actor"] == "human" and log["action"] == "recruit")

    assert recruit_log["details"]["delta"] == {
        "faith": 1,
        "order": -1,
        "fear": 0,
        "contamination": 0,
        "rebellion": 1,
    }
    assert recruit_log["narrative_text"] == (
        "A link-based recruitment campaign expands the circle of the enlightened."
    )


@pytest.mark.parametrize(
    "ai_action, expected_delta",
    [
        (
            "withhold_grace",
            {
                "faith": 0,
                "order": 2,
                "fear": -1,
                "contamination": -2,
                "rebellion": 0,
            },
        ),
        (
            "whisper_temptation",
            {
                "faith": -1,
                "order": 1,
                "fear": 2,
                "contamination": 0,
                "rebellion": -2,
            },
        ),
        (
            "manifest_wrath",
            {
                "faith": -2,
                "order": 1,
                "fear": 3,
                "contamination": -1,
                "rebellion": -2,
            },
        ),
    ],
)
def test_night_and_ai_action_deltas_match_rule_table(ai_action, expected_delta):
    engine = DeterministicEngine()

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True

    ai_result = engine.process_ai_intervention(ai_action)
    assert ai_result["success"] is True

    logs = engine.get_logs(limit=20)
    night_log = next(log for log in logs if log["actor"] == "system" and log["action"] == "night")
    ai_log = next(log for log in logs if log["actor"] == "ai_god" and log["action"] == ai_action)

    assert night_log["details"]["delta"] == NIGHT_BASELINE_DELTA
    assert ai_log["details"]["delta"] == expected_delta


def _set_stats(
    engine,
    *,
    faith,
    order,
    fear,
    contamination,
    rebellion,
    authority=6,
    divine_power=8,
):
    engine.human.faith = faith
    engine.ai.order = order
    engine.ai.fear = fear
    engine.ai.authority = authority
    engine.ai.divine_power = divine_power
    engine.human.contamination = contamination
    engine.human.rebellion = rebellion


def _assert_stats_are_clamped(engine):
    stats = engine.get_state()["stats"]
    assert set(stats.keys()) == {
        "faith",
        "order",
        "fear",
        "authority",
        "divine_power",
        "contamination",
        "rebellion",
    }
    assert 0 <= stats["faith"] <= 12
    assert 0 <= stats["order"] <= 12
    assert 0 <= stats["fear"] <= 12
    assert 0 <= stats["authority"] <= 12
    assert -2 <= stats["divine_power"] <= 12
    assert 0 <= stats["contamination"] <= 12
    assert 0 <= stats["rebellion"] <= 12


@pytest.mark.parametrize("boundary_value", [0, 12])
def test_stat_clamping_keeps_all_core_stats_in_range_for_every_delta_table(boundary_value):
    engine = DeterministicEngine()

    for delta_table in ALL_DELTA_TABLES:
        _set_stats(
            engine,
            faith=boundary_value,
            order=boundary_value,
            fear=boundary_value,
            contamination=boundary_value,
            rebellion=boundary_value,
            authority=boundary_value,
            divine_power=boundary_value,
        )

        engine._apply_delta_table(delta_table)
        _assert_stats_are_clamped(engine)


def test_divine_power_clamps_to_extended_range():
    engine = DeterministicEngine()
    engine.ai.divine_power = 8

    engine._apply_stat_delta("divine_power", -99)
    assert engine.ai.divine_power == -2

    engine._apply_stat_delta("divine_power", 99)
    assert engine.ai.divine_power == 12


@pytest.mark.parametrize(
    "role_name, stats",
    [
        (
            "priest",
            {
                "faith": 10,
                "order": 6,
                "fear": 4,
                "contamination": 1,
                "rebellion": 1,
            },
        ),
        (
            "rebel",
            {
                "faith": 5,
                "order": 4,
                "fear": 5,
                "contamination": 1,
                "rebellion": 9,
            },
        ),
        (
            "technician",
            {
                "faith": 5,
                "order": 5,
                "fear": 4,
                "contamination": 9,
                "rebellion": 1,
            },
        ),
        (
            "snitch",
            {
                "faith": 3,
                "order": 6,
                "fear": 9,
                "contamination": 1,
                "rebellion": 1,
            },
        ),
    ],
)
def test_role_objectives_are_calculated_per_case(role_name, stats):
    engine = DeterministicEngine()
    _set_stats(engine, **stats)

    roles = engine.get_state()["roles"]

    assert roles[role_name]["met"] is True


@pytest.mark.parametrize(
    "role_name, stats",
    [
        (
            "priest",
            {
                "faith": 9,
                "order": 6,
                "fear": 4,
                "contamination": 1,
                "rebellion": 1,
            },
        ),
        (
            "rebel",
            {
                "faith": 5,
                "order": 5,
                "fear": 5,
                "contamination": 1,
                "rebellion": 8,
            },
        ),
        (
            "technician",
            {
                "faith": 5,
                "order": 6,
                "fear": 4,
                "contamination": 8,
                "rebellion": 1,
            },
        ),
        (
            "snitch",
            {
                "faith": 4,
                "order": 6,
                "fear": 8,
                "contamination": 1,
                "rebellion": 1,
            },
        ),
    ],
)
def test_role_objectives_fail_when_thresholds_not_met(role_name, stats):
    engine = DeterministicEngine()
    _set_stats(engine, **stats)

    roles = engine.get_state()["roles"]

    assert roles[role_name]["met"] is False


def test_human_coalition_win_requires_two_human_roles():
    engine = DeterministicEngine()
    _set_stats(
        engine,
        faith=10,
        order=4,
        fear=4,
        contamination=1,
        rebellion=9,
    )

    resolved = engine._check_winner(priority="human")

    assert resolved is True
    assert engine.winner == "human"
    assert engine.win_reason == "resistance_roles:priest,rebel"


def test_snitch_condition_grants_ai_victory():
    engine = DeterministicEngine()
    _set_stats(
        engine,
        faith=3,
        order=6,
        fear=9,
        contamination=1,
        rebellion=1,
    )

    resolved = engine._check_winner(priority="ai")

    assert resolved is True
    assert engine.winner == "ai_god"
    assert engine.win_reason == "snitch_objective"


def test_human_priority_wins_when_human_and_snitch_objectives_overlap_after_human_step():
    engine = DeterministicEngine()
    _set_stats(
        engine,
        faith=3,
        order=6,
        fear=8,
        contamination=6,
        rebellion=8,
    )

    result = engine.process_human_action("sabotage")

    assert result["success"] is True
    assert result["phase"] == "ended"
    assert result["state"]["winner"] == "human"
    assert result["state"]["win_reason"] == "resistance_roles:rebel,technician"
    assert result["state"]["roles"]["snitch"]["met"] is True


def test_ai_priority_wins_when_human_and_snitch_objectives_overlap_after_ai_step():
    engine = DeterministicEngine()
    _set_stats(
        engine,
        faith=3,
        order=5,
        fear=8,
        contamination=8,
        rebellion=10,
    )

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True
    assert human_result["phase"] == "waiting_ai_god"
    assert human_result["state"]["winner"] is None

    ai_result = engine.process_ai_intervention("whisper_temptation")

    assert ai_result["success"] is True
    assert ai_result["state"]["winner"] == "ai_god"
    assert ai_result["state"]["win_reason"] == "snitch_objective"
    assert ai_result["state"]["roles"]["rebel"]["met"] is True
    assert ai_result["state"]["roles"]["technician"]["met"] is True
    assert ai_result["state"]["roles"]["snitch"]["met"] is True


def test_turn_limit_grants_ai_win_at_turn_20_without_order_and_fear_lock():
    engine = DeterministicEngine()
    engine.turn = 19
    _set_stats(
        engine,
        faith=5,
        order=6,
        fear=4,
        contamination=1,
        rebellion=1,
    )

    result = engine.process_human_action("vote")

    assert result["success"] is True
    assert result["turn"] == 20
    assert result["phase"] == "ended"
    assert result["state"]["winner"] == "ai_god"
    assert result["state"]["win_reason"] == "turn_limit"
    assert result["state"]["stats"]["order"] < 10
    assert result["state"]["stats"]["fear"] < 8


def test_snitch_objective_ends_game_immediately_after_human_step():
    engine = DeterministicEngine()
    _set_stats(
        engine,
        faith=3,
        order=6,
        fear=8,
        contamination=1,
        rebellion=1,
    )

    result = engine.process_human_action("sabotage")

    assert result["success"] is True
    assert result["phase"] == "ended"
    assert result["state"]["winner"] == "ai_god"
    assert result["state"]["win_reason"] == "snitch_objective"

    ai_result = engine.process_ai_intervention("withhold_grace")
    assert ai_result["success"] is False
    assert ai_result["error"] == "Game is in phase ended"


@pytest.mark.parametrize(
    "ai_action, expected_cost",
    [
        ("withhold_grace", 1),
        ("whisper_temptation", 2),
        ("manifest_wrath", 4),
    ],
)
def test_ai_intervention_costs_reduce_divine_power(ai_action, expected_cost):
    engine = DeterministicEngine()
    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True

    ai_result = engine.process_ai_intervention(ai_action)
    assert ai_result["success"] is True
    assert ai_result["state"]["ai_god"]["divine_power"] == 9 - expected_cost

    logs = engine.get_logs(limit=20)
    ai_log = next(log for log in logs if log["actor"] == "ai_god" and log["action"] == ai_action)
    assert ai_log["details"]["divine_power_cost"] == expected_cost


def test_overextension_sets_vulnerable_and_blocks_manifest_wrath():
    engine = DeterministicEngine()
    engine.ai.divine_power = 0

    human_result = engine.process_human_action("vote")
    assert human_result["success"] is True

    ai_result = engine.process_ai_intervention("whisper_temptation")
    assert ai_result["success"] is True
    assert ai_result["state"]["ai_god"]["divine_power"] == -1
    assert ai_result["state"]["vulnerable"] is True

    logs = engine.get_logs(limit=30)
    overextension_log = next(
        log for log in logs if log["actor"] == "system" and log["action"] == "overextension"
    )
    assert overextension_log["details"]["vulnerable"] is True
    assert overextension_log["details"]["divine_power"] == -1

    next_human = engine.process_human_action("vote")
    assert next_human["success"] is True
    blocked = engine.process_ai_intervention("manifest_wrath")
    assert blocked["success"] is False
    assert blocked["error"] == "AI God is vulnerable and cannot use manifest_wrath"
