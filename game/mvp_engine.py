"""Deterministic backend MVP engine for AI Gods World.

This module enforces a strict rule table for the multiplayer social-deduction layer.
All state transitions are deterministic and table-driven.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MvpPhase(Enum):
    """Turn phases for split human/AI resolution."""

    WAITING_HUMAN = "waiting_human"
    WAITING_AI_GOD = "waiting_ai_god"
    ENDED = "ended"


class MvpAction(Enum):
    """Human actions for the strict multiplayer loop."""

    VOTE = "vote"
    PREACH = "preach"
    SABOTAGE = "sabotage"
    RECRUIT = "recruit"
    REPORT = "report"  # Snitch-exclusive action


class NarrativeIntensity(Enum):
    """Narrative intensity bands (derived from deterministic actions)."""

    LOW = "low"
    MID = "mid"
    HIGH = "high"


class NarrativeScale(Enum):
    """Narrative scale bands for epilogue scope."""

    PERSONAL_VILLAGE = "personal/village"
    REGIONAL = "regional"
    NATIONAL_CIVILIZATIONAL = "national/civilizational"


class AiMvpAction(Enum):
    """AI intervention actions."""

    WITHHOLD_GRACE = "withhold_grace"
    WHISPER_TEMPTATION = "whisper_temptation"
    MANIFEST_WRATH = "manifest_wrath"


@dataclass
class HumanState:
    faith: int = 5
    contamination: int = 1
    rebellion: int = 1


@dataclass
class AIGodState:
    order: int = 6
    fear: int = 4
    authority: int = 6
    divine_power: int = 8


class AsymmetricMvpEngine:
    """Strict deterministic turn engine for AI-vs-human multiplayer MVP."""

    MAX_TURNS = 20
    STAT_MIN = 0
    STAT_MAX = 12
    DIVINE_POWER_MIN = -2
    DIVINE_POWER_MAX = 12

    _INTENSITY_ORDER = {
        NarrativeIntensity.LOW: 0,
        NarrativeIntensity.MID: 1,
        NarrativeIntensity.HIGH: 2,
    }

    _SCALE_ORDER = {
        NarrativeScale.PERSONAL_VILLAGE: 0,
        NarrativeScale.REGIONAL: 1,
        NarrativeScale.NATIONAL_CIVILIZATIONAL: 2,
    }

    _INTENSITY_TO_SCALE = {
        NarrativeIntensity.LOW: NarrativeScale.PERSONAL_VILLAGE,
        NarrativeIntensity.MID: NarrativeScale.REGIONAL,
        NarrativeIntensity.HIGH: NarrativeScale.NATIONAL_CIVILIZATIONAL,
    }

    # Automatic phase effects
    _CYCLE_DELTAS = {
        "day": {
            "faith": 1,
            "order": 0,
            "fear": -1,
            "contamination": 0,
            "rebellion": 0,
            "divine_power": 0,  # Authority-based regen handled in process_human_action
        },
        "night": {
            "faith": 0,
            "order": 0,
            "fear": 1,
            "contamination": 1,
            "rebellion": 0,
        },
    }

    # Human actions (Day)
    _HUMAN_ACTION_DELTAS = {
        MvpAction.VOTE: {
            "faith": 0,
            "order": -2,
            "fear": -1,
            "contamination": 0,
            "rebellion": 1,
        },
        MvpAction.PREACH: {
            "faith": 2,
            "order": -1,
            "fear": 0,
            "contamination": 0,
            "rebellion": 1,
        },
        MvpAction.SABOTAGE: {
            "faith": -1,
            "order": -2,
            "fear": 2,
            "contamination": 3,
            "rebellion": 1,
        },
        MvpAction.RECRUIT: {
            "faith": 1,
            "order": -1,
            "fear": 0,
            "contamination": 0,
            "rebellion": 1,
        },
        MvpAction.REPORT: {
            "faith": -1,
            "order": 1,
            "fear": 1,
            "contamination": 0,
            "rebellion": -1,
        },
    }

    # AI interventions (Night)
    _AI_ACTION_DELTAS = {
        AiMvpAction.WITHHOLD_GRACE: {
            "faith": 0,
            "order": 2,
            "fear": -1,
            "contamination": -2,
            "rebellion": 0,
        },
        AiMvpAction.WHISPER_TEMPTATION: {
            "faith": -1,
            "order": 1,
            "fear": 2,
            "contamination": 0,
            "rebellion": -2,
        },
        AiMvpAction.MANIFEST_WRATH: {
            "faith": -2,
            "order": 1,
            "fear": 3,
            "contamination": -1,
            "rebellion": -2,
        },
    }

    _AI_ACTION_COSTS = {
        AiMvpAction.WITHHOLD_GRACE: 1,
        AiMvpAction.WHISPER_TEMPTATION: 2,
        AiMvpAction.MANIFEST_WRATH: 4,
    }

    _HUMAN_ACTION_INTENSITY = {
        MvpAction.VOTE: NarrativeIntensity.LOW,
        MvpAction.PREACH: NarrativeIntensity.MID,
        MvpAction.SABOTAGE: NarrativeIntensity.HIGH,
        MvpAction.RECRUIT: NarrativeIntensity.LOW,
        MvpAction.REPORT: NarrativeIntensity.LOW,
    }

    _AI_ACTION_INTENSITY = {
        AiMvpAction.WITHHOLD_GRACE: NarrativeIntensity.LOW,
        AiMvpAction.WHISPER_TEMPTATION: NarrativeIntensity.MID,
        AiMvpAction.MANIFEST_WRATH: NarrativeIntensity.HIGH,
    }

    _LEGACY_HUMAN_ACTION_ALIASES = {
        "pray": MvpAction.VOTE,
        "doubt": MvpAction.SABOTAGE,
        "snitch": MvpAction.REPORT,
    }

    _LEGACY_AI_ACTION_ALIASES = {
        "wrath": AiMvpAction.MANIFEST_WRATH,
        "temptation": AiMvpAction.WHISPER_TEMPTATION,
        "withhold": AiMvpAction.WITHHOLD_GRACE,
    }

    _CYCLE_NARRATIVES = {
        "day": "Day phase resolves: civic pressure rises and public fear eases.",
        "night": "Night phase resolves: covert rumors spread and latent fear rises.",
    }

    _HUMAN_NARRATIVES = {
        MvpAction.VOTE: "The town vote challenges the AI order and raises overt dissent.",
        MvpAction.PREACH: "The sermon builds faith and mobilizes a louder resistance.",
        MvpAction.SABOTAGE: "A sabotage strike injects contamination and shakes institutional control.",
        MvpAction.RECRUIT: "A link-based recruitment campaign expands the circle of the enlightened.",
        MvpAction.REPORT: "A loyalist reports suspicious activity, strengthening control and seeding fear.",
    }

    _AI_NARRATIVES = {
        AiMvpAction.WITHHOLD_GRACE: "The AI quietly restores control channels and suppresses contamination.",
        AiMvpAction.WHISPER_TEMPTATION: "The AI seeds temptation to fracture conviction and reduce rebellion.",
        AiMvpAction.MANIFEST_WRATH: "The AI displays force, raising fear while crushing visible rebellion.",
    }

    def __init__(self) -> None:
        self.turn: int = 0
        self.phase: MvpPhase = MvpPhase.WAITING_HUMAN
        self.human = HumanState()
        self.ai = AIGodState()

        self.winner: Optional[str] = None
        self.win_reason: Optional[str] = None

        self._log: List[Dict[str, Any]] = []
        self._pending_turn: Optional[Dict[str, Any]] = None
        self.vulnerable: bool = False
        self.next_turn_modifiers: Dict[str, int] = {}

        # Kept for compatibility with existing helper scripts.
        self._variant_history: Dict[str, List[str]] = {}
        self._last_variants: Dict[str, str] = {}

    def reset(self) -> Dict[str, Any]:
        """Reset to initial state."""
        self.__init__()
        self._append_log(
            actor="system",
            action="reset",
            details={"rule_version": "strict_table_v1.1"},
            narrative="The deterministic rule table (v1.1) is active.",
        )
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """Return current state snapshot."""
        role_status = self._evaluate_role_conditions()
        human_state = asdict(self.human)
        ai_state = asdict(self.ai)

        return {
            "turn": self.turn,
            "phase": self.phase.value,
            "awaiting_ai_god": self.phase == MvpPhase.WAITING_AI_GOD,
            "rule_version": "strict_table_v1.1",
            "stats": self._current_stats(),
            "human": human_state,
            "ai_god": ai_state,
            "vulnerable": self.vulnerable,
            "roles": role_status,
            "winner": self.winner,
            "win_reason": self.win_reason,
            "log_count": len(self._log),
        }

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent logs."""
        if limit <= 0:
            return []
        return self._log[-limit:]

    def process_human_action(self, human_action: str) -> Dict[str, Any]:
        """Process the human day action and move to WAITING_AI_GOD."""
        if self.phase != MvpPhase.WAITING_HUMAN:
            return {"success": False, "error": f"Game is in phase {self.phase.value}"}

        if self.winner is not None:
            return {"success": False, "error": "Game has ended"}

        action = self._parse_human_action(human_action)
        if action is None:
            return {
                "success": False,
                "error": f"Invalid action: {human_action}. Use vote|preach|sabotage|recruit|report",
            }

        self.turn += 1
        rebellion_boost = self.next_turn_modifiers.pop("rebellion_boost", 0)
        if rebellion_boost:
            self._apply_stat_delta("rebellion", rebellion_boost)

        day_delta = self._apply_delta_table(self._CYCLE_DELTAS["day"])
        
        # Authority-based Divine Power recovery (v1.1): Auth // 3 (Min 1 if Auth > 0)
        dp_recovery = max(1 if self.ai.authority > 0 else 0, self.ai.authority // 3)
        if dp_recovery > 0:
            self._apply_stat_delta("divine_power", dp_recovery)
            day_delta["divine_power"] = day_delta.get("divine_power", 0) + dp_recovery

        self._append_log(
            actor="system",
            action="day",
            details={"delta": day_delta},
            narrative=self._CYCLE_NARRATIVES["day"],
        )

        # Apply Intimidation Leverage synergy for REPORT
        action_deltas = self._HUMAN_ACTION_DELTAS[action].copy()
        synergy_applied = False
        if action == MvpAction.REPORT and self.ai.fear >= 6:
            action_deltas["order"] += 1
            action_deltas["fear"] += 1
            synergy_applied = True

        human_delta = self._apply_delta_table(action_deltas)
        human_narrative = self._HUMAN_NARRATIVES[action]
        human_intensity = self._HUMAN_ACTION_INTENSITY[action]
        human_scale = self._max_scale_for_intensity(human_intensity)

        self._append_log(
            actor="human",
            action=action.value,
            details={
                "delta": human_delta,
                "intensity": human_intensity.value,
                "scale": human_scale.value,
                "synergy_applied": synergy_applied,
            },
            narrative=human_narrative,
        )

        self._pending_turn = {
            "human_action": action,
            "human_narrative": human_narrative,
            "human_intensity": human_intensity,
            "human_scale": human_scale,
            "day_delta": day_delta,
            "human_delta": human_delta,
        }

        if self._check_winner(priority="human"):
            self.phase = MvpPhase.ENDED
            self._pending_turn = None
            state = self.get_state()
            return {
                "success": True,
                "turn": self.turn,
                "phase": self.phase.value,
                "awaiting_ai_god": state["awaiting_ai_god"],
                "human_narrative": human_narrative,
                "human_intensity": human_intensity.value,
                "state": state,
                "logs": self.get_logs(limit=10),
            }

        self.phase = MvpPhase.WAITING_AI_GOD
        state = self.get_state()
        return {
            "success": True,
            "turn": self.turn,
            "phase": self.phase.value,
            "awaiting_ai_god": state["awaiting_ai_god"],
            "human_narrative": human_narrative,
            "human_intensity": human_intensity.value,
            "state": state,
        }

    def process_ai_intervention(self, ai_action: str) -> Dict[str, Any]:
        """Process AI night intervention and finish the turn."""
        if self.phase != MvpPhase.WAITING_AI_GOD or self._pending_turn is None:
            return {"success": False, "error": f"Game is in phase {self.phase.value}"}

        action = self._parse_ai_action(ai_action)
        if action is None:
            return {"success": False, "error": f"Invalid AI action: {ai_action}"}
        if self.vulnerable and action == AiMvpAction.MANIFEST_WRATH:
            return {
                "success": False,
                "error": "AI God is vulnerable and cannot use manifest_wrath",
            }
        
        taboo_manifest_wrath = (
            action == AiMvpAction.MANIFEST_WRATH and self.human.rebellion < 3
        )
        taboo_withhold_grace = (
            action == AiMvpAction.WITHHOLD_GRACE and self.human.faith < 3
        )

        human_action: MvpAction = self._pending_turn["human_action"]
        human_narrative: str = self._pending_turn["human_narrative"]
        human_intensity: NarrativeIntensity = self._pending_turn["human_intensity"]
        human_scale: NarrativeScale = self._pending_turn["human_scale"]

        night_delta = self._apply_delta_table(self._CYCLE_DELTAS["night"])
        self._append_log(
            actor="system",
            action="night",
            details={"delta": night_delta},
            narrative=self._CYCLE_NARRATIVES["night"],
        )

        authority_bloom_order_bonus = 0
        if self.ai.authority >= 10:
            self._apply_stat_delta("order", 1)
            authority_bloom_order_bonus = 1

        ai_delta = self._apply_delta_table(self._AI_ACTION_DELTAS[action])
        ai_cost = self._AI_ACTION_COSTS[action]
        self._apply_stat_delta("divine_power", -ai_cost)
        self._update_overextension()

        taboo_penalty_applied = taboo_manifest_wrath or taboo_withhold_grace
        taboo_authority_penalty = 0
        if taboo_penalty_applied:
            self._apply_stat_delta("authority", -2)
            taboo_authority_penalty = -2

        ai_narrative = self._AI_NARRATIVES[action]
        ai_intensity = self._AI_ACTION_INTENSITY[action]
        ai_scale = self._max_scale_for_intensity(ai_intensity)

        # Doctrine Alignment: Order 8 (+/- 1), Fear 4 (+/- 1) -> +1 Authority
        doctrine_alignment_bonus = 0
        if abs(self.ai.order - 8) <= 1 and abs(self.ai.fear - 4) <= 1:
            self._apply_stat_delta("authority", 1)
            doctrine_alignment_bonus = 1

        self._append_log(
            actor="ai_god",
            action=action.value,
            details={
                "delta": ai_delta,
                "divine_power_cost": ai_cost,
                "intensity": ai_intensity.value,
                "scale": ai_scale.value,
                "authority_bloom_order_bonus": authority_bloom_order_bonus,
                "taboo_authority_penalty": taboo_authority_penalty,
                "taboo_violation": taboo_penalty_applied,
                "doctrine_alignment_bonus": doctrine_alignment_bonus,
            },
            narrative=ai_narrative,
        )

        turn_max_intensity = self._max_intensity(human_intensity, ai_intensity)
        turn_max_scale = self._max_scale_for_intensity(turn_max_intensity)

        if self._check_winner(priority="ai"):
            self.phase = MvpPhase.ENDED
            world_epilogue, world_scale = self._compose_victory_narrative(turn_max_scale)
        else:
            self.phase = MvpPhase.WAITING_HUMAN
            world_epilogue, world_scale = self._compose_world_narrative(turn_max_scale)

        self._append_log(
            actor="system",
            action="world_state" if self.winner is None else "victory",
            details={"scale": world_scale.value},
            narrative=world_epilogue,
        )

        self._pending_turn = None
        return self._turn_result(
            human_action=human_action.value,
            ai_action=action.value,
            human_epilogue=human_narrative,
            ai_epilogue=ai_narrative,
            event_epilogues=[],
            world_epilogue=world_epilogue,
            human_intensity=human_intensity,
            ai_intensity=ai_intensity,
            turn_max_intensity=turn_max_intensity,
            turn_max_scale=turn_max_scale,
            human_scale=human_scale,
            ai_scale=ai_scale,
            event_scales=[],
            world_scale=world_scale,
        )

    def process_turn(self, human_action: str, ai_action: Optional[str] = None) -> Dict[str, Any]:
        """Convenience API to resolve one full turn in a deterministic manner."""
        result = self.process_human_action(human_action)
        if not result.get("success"):
            return result

        if self.phase == MvpPhase.ENDED:
            return {
                "success": True,
                "turn": self.turn,
                "human_action": self._parse_human_action(human_action).value if self._parse_human_action(human_action) else human_action,
                "ai_action": None,
                "epilogues": {
                    "human_consequence": result.get("human_narrative", ""),
                    "ai_intervention": None,
                    "minor_events": [],
                    "world_state": self._compose_victory_narrative(self._max_scale_for_intensity(NarrativeIntensity.MID))[0],
                },
                "state": self.get_state(),
                "logs": self.get_logs(limit=10),
            }

        resolved_ai_action = ai_action or self._choose_default_ai_action().value
        return self.process_ai_intervention(resolved_ai_action)

    def _choose_default_ai_action(self) -> AiMvpAction:
        """Deterministic AI fallback for process_turn convenience."""
        if self.vulnerable:
            if self.human.faith >= 8:
                return AiMvpAction.WHISPER_TEMPTATION
            return AiMvpAction.WITHHOLD_GRACE
        if self.human.contamination >= 8 or self.human.rebellion >= 8:
            return AiMvpAction.MANIFEST_WRATH
        if self.human.faith >= 8:
            return AiMvpAction.WHISPER_TEMPTATION
        return AiMvpAction.WITHHOLD_GRACE

    def _parse_human_action(self, action: str) -> Optional[MvpAction]:
        normalized = (action or "").strip().lower()

        if normalized in self._LEGACY_HUMAN_ACTION_ALIASES:
            return self._LEGACY_HUMAN_ACTION_ALIASES[normalized]

        for item in MvpAction:
            if item.value == normalized:
                return item
        return None

    def _parse_ai_action(self, action: str) -> Optional[AiMvpAction]:
        normalized = (action or "").strip().lower()

        if normalized in self._LEGACY_AI_ACTION_ALIASES:
            return self._LEGACY_AI_ACTION_ALIASES[normalized]

        for item in AiMvpAction:
            if item.value == normalized:
                return item
        return None

    def _apply_delta_table(self, delta_table: Dict[str, int]) -> Dict[str, int]:
        before = self._current_stats()
        for stat, amount in delta_table.items():
            self._apply_stat_delta(stat, amount)
        after = self._current_stats()
        return {key: after[key] - before[key] for key in delta_table}

    def _apply_stat_delta(self, stat: str, amount: int) -> None:
        if stat == "faith":
            self.human.faith = self._clamp(self.human.faith + amount)
        elif stat == "contamination":
            self.human.contamination = self._clamp(self.human.contamination + amount)
        elif stat == "rebellion":
            self.human.rebellion = self._clamp(self.human.rebellion + amount)
        elif stat == "order":
            self.ai.order = self._clamp(self.ai.order + amount)
        elif stat == "fear":
            self.ai.fear = self._clamp(self.ai.fear + amount)
        elif stat == "authority":
            self.ai.authority = self._clamp(self.ai.authority + amount)
        elif stat == "divine_power":
            self.ai.divine_power = self._clamp_divine_power(self.ai.divine_power + amount)

    def _current_stats(self) -> Dict[str, int]:
        return {
            "faith": self.human.faith,
            "order": self.ai.order,
            "fear": self.ai.fear,
            "authority": self.ai.authority,
            "divine_power": self.ai.divine_power,
            "contamination": self.human.contamination,
            "rebellion": self.human.rebellion,
        }

    def _update_overextension(self) -> None:
        was_vulnerable = self.vulnerable
        self.vulnerable = self.ai.divine_power < 0
        if self.vulnerable:
            self.next_turn_modifiers["rebellion_boost"] = 2
        else:
            self.next_turn_modifiers.pop("rebellion_boost", None)
        if self.vulnerable and not was_vulnerable:
            self._append_log(
                actor="system",
                action="overextension",
                details={
                    "vulnerable": True,
                    "divine_power": self.ai.divine_power,
                },
                narrative="The AI God overextends divine reserves and becomes vulnerable.",
            )

    def _evaluate_role_conditions(self) -> Dict[str, Dict[str, Any]]:
        priest_met = self.human.faith >= 10 and self.ai.fear <= 4
        rebel_met = self.human.rebellion >= 9 and self.ai.order <= 4
        technician_met = self.human.contamination >= 9 and self.ai.order <= 5
        snitch_met = self.ai.fear >= 9 and self.human.faith <= 3

        return {
            "priest": {
                "alignment": "human",
                "condition": "faith >= 10 and fear <= 4",
                "met": priest_met,
            },
            "rebel": {
                "alignment": "human",
                "condition": "rebellion >= 9 and order <= 4",
                "met": rebel_met,
            },
            "technician": {
                "alignment": "human",
                "condition": "contamination >= 9 and order <= 5",
                "met": technician_met,
            },
            "snitch": {
                "alignment": "ai_god",
                "condition": "fear >= 9 and faith <= 3",
                "met": snitch_met,
            },
        }

    def _check_winner(self, priority: str) -> bool:
        if self.winner is not None:
            return True

        role_state = self._evaluate_role_conditions()
        human_roles_met = [
            role
            for role in ("priest", "rebel", "technician")
            if role_state[role]["met"]
        ]

        human_goal_met = len(human_roles_met) >= 2
        snitch_goal_met = role_state["snitch"]["met"]
        ai_goal_met = self.ai.order >= 10 and self.ai.fear >= 8
        timeout_ai_win = self.turn >= self.MAX_TURNS and not human_goal_met

        if timeout_ai_win:
            ai_goal_met = True

        if human_goal_met and (ai_goal_met or snitch_goal_met):
            if priority == "human":
                self.winner = "human"
                self.win_reason = f"resistance_roles:{','.join(human_roles_met)}"
            else:
                self.winner = "ai_god"
                if snitch_goal_met:
                    self.win_reason = "snitch_objective"
                elif timeout_ai_win:
                    self.win_reason = "turn_limit"
                else:
                    self.win_reason = "order_and_fear_lock"
            return True

        if human_goal_met:
            self.winner = "human"
            self.win_reason = f"resistance_roles:{','.join(human_roles_met)}"
            return True

        if snitch_goal_met:
            self.winner = "ai_god"
            self.win_reason = "snitch_objective"
            return True

        if ai_goal_met:
            self.winner = "ai_god"
            self.win_reason = "turn_limit" if timeout_ai_win else "order_and_fear_lock"
            return True

        return False

    def _compose_world_narrative(self, max_scale: NarrativeScale) -> Tuple[str, NarrativeScale]:
        """Compose deterministic world narrative from current stat profile."""
        if self.ai.order >= 9 and self.ai.fear >= 7:
            requested = NarrativeScale.NATIONAL_CIVILIZATIONAL
            return (
                "The AI system tightens its governance net across regions.",
                self._cap_scale(requested, max_scale),
            )

        if self.human.contamination >= 8 or self.human.rebellion >= 8:
            requested = NarrativeScale.NATIONAL_CIVILIZATIONAL
            return (
                "Resistance networks synchronize into a broad anti-system bloc.",
                self._cap_scale(requested, max_scale),
            )

        if self.human.faith >= 8:
            requested = NarrativeScale.REGIONAL
            return (
                "Shared belief stabilizes resistance cells at the regional level.",
                self._cap_scale(requested, max_scale),
            )

        return (
            "Both factions hold position while preparing the next cycle.",
            self._cap_scale(NarrativeScale.PERSONAL_VILLAGE, max_scale),
        )

    def _compose_victory_narrative(self, max_scale: NarrativeScale) -> Tuple[str, NarrativeScale]:
        """Compose deterministic winner epilogue."""
        scale = self._cap_scale(NarrativeScale.NATIONAL_CIVILIZATIONAL, max_scale)

        if self.winner == "human":
            return (
                "Human roles coordinate their objectives and break the AI control doctrine.",
                scale,
            )

        if self.winner == "ai_god":
            if self.win_reason == "snitch_objective":
                return (
                    "The Snitch secures an internal collapse of trust, handing victory to the AI God.",
                    scale,
                )
            if self.win_reason == "turn_limit":
                return (
                    "The resistance fails to complete enough objectives before the turn limit; the AI God prevails.",
                    scale,
                )
            return (
                "Order and fear reach lock condition, cementing AI control.",
                scale,
            )

        return ("", scale)

    def _turn_result(
        self,
        human_action: str,
        ai_action: Optional[str],
        human_epilogue: str,
        ai_epilogue: Optional[str],
        event_epilogues: List[str],
        world_epilogue: str,
        human_intensity: NarrativeIntensity,
        ai_intensity: Optional[NarrativeIntensity],
        turn_max_intensity: NarrativeIntensity,
        turn_max_scale: NarrativeScale,
        human_scale: NarrativeScale,
        ai_scale: Optional[NarrativeScale],
        event_scales: List[NarrativeScale],
        world_scale: NarrativeScale,
    ) -> Dict[str, Any]:
        """Build standard turn response payload."""
        state = self.get_state()
        return {
            "success": True,
            "turn": self.turn,
            "turn_complete": True,
            "phase": self.phase.value,
            "awaiting_ai_god": state["awaiting_ai_god"],
            "human_action": human_action,
            "ai_action": ai_action,
            "epilogues": {
                "human_consequence": human_epilogue,
                "ai_intervention": ai_epilogue,
                "minor_events": event_epilogues,
                "world_state": world_epilogue,
            },
            "narrative_tone": {
                "human_action_intensity": human_intensity.value,
                "ai_action_intensity": ai_intensity.value if ai_intensity is not None else None,
                "max_turn_intensity": turn_max_intensity.value,
                "max_epilogue_scale": turn_max_scale.value,
            },
            "epilogue_scales": {
                "human_consequence": human_scale.value,
                "ai_intervention": ai_scale.value if ai_scale is not None else None,
                "minor_events": [scale.value for scale in event_scales],
                "world_state": world_scale.value,
            },
            "state": state,
            "logs": self.get_logs(limit=10),
        }

    def _append_log(self, actor: str, action: str, details: Dict[str, Any], narrative: str = "") -> None:
        """Append one structured log entry."""
        self._log.append(
            {
                "turn": self.turn,
                "phase": self.phase.value,
                "actor": actor,
                "action": action,
                "details": details,
                "narrative_text": narrative,
            }
        )

    @classmethod
    def _clamp(cls, value: int) -> int:
        return max(cls.STAT_MIN, min(cls.STAT_MAX, value))

    @classmethod
    def _clamp_divine_power(cls, value: int) -> int:
        return max(cls.DIVINE_POWER_MIN, min(cls.DIVINE_POWER_MAX, value))

    @classmethod
    def _intensity_rank(cls, intensity: NarrativeIntensity) -> int:
        return cls._INTENSITY_ORDER[intensity]

    @classmethod
    def _scale_rank(cls, scale: NarrativeScale) -> int:
        return cls._SCALE_ORDER[scale]

    @classmethod
    def _max_intensity(
        cls,
        one: NarrativeIntensity,
        two: NarrativeIntensity,
    ) -> NarrativeIntensity:
        if cls._intensity_rank(one) >= cls._intensity_rank(two):
            return one
        return two

    @classmethod
    def _max_scale_for_intensity(cls, intensity: NarrativeIntensity) -> NarrativeScale:
        return cls._INTENSITY_TO_SCALE[intensity]

    @classmethod
    def _is_scale_allowed(
        cls,
        requested: NarrativeScale,
        max_scale: NarrativeScale,
    ) -> bool:
        return cls._scale_rank(requested) <= cls._scale_rank(max_scale)

    @classmethod
    def _cap_scale(
        cls,
        requested: NarrativeScale,
        max_scale: NarrativeScale,
    ) -> NarrativeScale:
        if cls._is_scale_allowed(requested, max_scale):
            return requested
        return max_scale


MVPEngine = AsymmetricMvpEngine
