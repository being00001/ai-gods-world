"""Asymmetric 1v1 backend MVP engine for AI Gods World.

This module focuses only on server-side turn resolution:
- 1 human player vs 1 AI god
- per-turn state transitions
- structured action/turn logging
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class MvpPhase(Enum):
    """Minimal game phases for 1v1 turn processing."""

    WAITING_HUMAN = "waiting_human"
    ENDED = "ended"


class MvpAction(Enum):
    """Human actions supported by the MVP loop."""

    PRAY = "pray"
    PREACH = "preach"
    DOUBT = "doubt"


class NarrativeIntensity(Enum):
    """Narrative intensity bands for action matching."""

    LOW = "low"
    MID = "mid"
    HIGH = "high"


class NarrativeScale(Enum):
    """Narrative scale bands for epilogue scope control."""

    PERSONAL_VILLAGE = "personal/village"
    REGIONAL = "regional"
    NATIONAL_CIVILIZATIONAL = "national/civilizational"


class AiMvpAction(Enum):
    """AI god action categories used by the MVP loop."""

    WITHHOLD_GRACE = "withhold_grace"
    WHISPER_TEMPTATION = "whisper_temptation"
    MANIFEST_WRATH = "manifest_wrath"


@dataclass
class HumanState:
    faith: int = 3
    influence: int = 2
    followers: int = 8


@dataclass
class AIGodState:
    divine_power: int = 5
    wrath: int = 1
    followers: int = 12


class AsymmetricMvpEngine:
    """Deterministic MVP turn engine for human-vs-AI asymmetric play."""

    VICTORY_FOLLOWERS = 20
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
    _AI_ACTION_INTENSITY = {
        AiMvpAction.WITHHOLD_GRACE: NarrativeIntensity.LOW,
        AiMvpAction.WHISPER_TEMPTATION: NarrativeIntensity.MID,
        AiMvpAction.MANIFEST_WRATH: NarrativeIntensity.HIGH,
    }
    _HUMAN_ACTION_LABELS = {
        MvpAction.PRAY: "기도를 올렸다",
        MvpAction.PREACH: "설교를 퍼뜨렸다",
        MvpAction.DOUBT: "의심을 드러냈다",
    }
    _INTERPRETATION_FRAMES = {
        MvpAction.PRAY: {
            AiMvpAction.WITHHOLD_GRACE: "겸손한 순종으로",
            AiMvpAction.WHISPER_TEMPTATION: "감춰진 불안의 신호로",
            AiMvpAction.MANIFEST_WRATH: "세력 과시성 도전으로",
        },
        MvpAction.PREACH: {
            AiMvpAction.WITHHOLD_GRACE: "아직 미약한 소요로",
            AiMvpAction.WHISPER_TEMPTATION: "지역 확장 선동으로",
            AiMvpAction.MANIFEST_WRATH: "공개 반역 선언으로",
        },
        MvpAction.DOUBT: {
            AiMvpAction.WITHHOLD_GRACE: "일시적 동요로",
            AiMvpAction.WHISPER_TEMPTATION: "공동체 균열의 틈으로",
            AiMvpAction.MANIFEST_WRATH: "신권 파괴 시도로",
        },
    }

    def __init__(self) -> None:
        self.turn: int = 0
        self.phase: MvpPhase = MvpPhase.WAITING_HUMAN
        self.human = HumanState()
        self.ai = AIGodState()
        self.winner: Optional[str] = None
        self._log: List[Dict[str, Any]] = []
        self._last_variants: Dict[str, str] = {}

    def _pick_variant(self, key: str, variants: List[str]) -> str:
        last = self._last_variants.get(key)
        choices = [v for v in variants if v != last]
        if not choices:
            choices = variants
        chosen = random.choice(choices)
        self._last_variants[key] = chosen
        return chosen

    def reset(self) -> Dict[str, Any]:
        """Reset to initial state."""
        self.__init__()
        self._append_log(
            actor="system",
            action="reset",
            details={"message": "mvp engine reset"},
            narrative="세계가 태초의 적막 속으로 돌아갔다.",
        )
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """Return current state snapshot."""
        return {
            "turn": self.turn,
            "phase": self.phase.value,
            "human": asdict(self.human),
            "ai_god": asdict(self.ai),
            "winner": self.winner,
            "log_count": len(self._log),
        }

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent logs."""
        if limit <= 0:
            return []
        return self._log[-limit:]

    def process_turn(self, human_action: str) -> Dict[str, Any]:
        """Process one full turn: human action then AI action."""
        if self.phase != MvpPhase.WAITING_HUMAN:
            return {"success": False, "error": "Game is not accepting actions"}

        if self.winner is not None:
            return {"success": False, "error": "Game has ended"}

        action = self._parse_action(human_action)
        if action is None:
            return {
                "success": False,
                "error": f"Invalid action: {human_action}. Use pray|preach|doubt",
            }

        self.turn += 1

        human_delta, human_narrative, human_intensity = self._apply_human_action(action)
        human_scale = self._max_scale_for_intensity(human_intensity)
        self._append_log(
            actor="human",
            action=action.value,
            details={
                "delta": human_delta,
                "intensity": human_intensity.value,
                "scale": human_scale.value,
            },
            narrative=human_narrative,
        )

        if self._check_winner():
            turn_max_intensity = human_intensity
            turn_max_scale = self._max_scale_for_intensity(turn_max_intensity)
            world_epilogue, world_scale = self._compose_victory_narrative(turn_max_scale)
            return self._turn_result(
                human_action=action.value,
                ai_action=None,
                human_epilogue=human_narrative,
                ai_epilogue=None,
                event_epilogues=[],
                world_epilogue=world_epilogue,
                human_intensity=human_intensity,
                ai_intensity=None,
                turn_max_intensity=turn_max_intensity,
                turn_max_scale=turn_max_scale,
                human_scale=human_scale,
                ai_scale=None,
                event_scales=[],
                world_scale=world_scale,
            )

        ai_action, ai_delta, ai_narrative, ai_intensity = self._apply_ai_action(
            human_action=action,
            human_intensity=human_intensity,
        )
        ai_scale = self._max_scale_for_intensity(ai_intensity)
        self._append_log(
            actor="ai_god",
            action=ai_action.value,
            details={
                "delta": ai_delta,
                "intensity": ai_intensity.value,
                "scale": ai_scale.value,
            },
            narrative=ai_narrative,
        )

        turn_max_intensity = self._max_intensity(human_intensity, ai_intensity)
        turn_max_scale = self._max_scale_for_intensity(turn_max_intensity)

        if self._check_winner():
            world_epilogue, world_scale = self._compose_victory_narrative(turn_max_scale)
            return self._turn_result(
                human_action=action.value,
                ai_action=ai_action.value,
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

        events = self._trigger_minor_events(turn_max_intensity, turn_max_scale)
        event_epilogues = [text for text, _ in events]
        event_scales = [scale for _, scale in events]
        world_narrative, world_scale = self._compose_world_narrative(turn_max_intensity, turn_max_scale)
        self._append_log(
            actor="system",
            action="world_state",
            details={"scale": world_scale.value},
            narrative=world_narrative,
        )

        self._check_winner()
        if self.winner is not None:
            world_narrative, world_scale = self._compose_victory_narrative(turn_max_scale)

        return self._turn_result(
            human_action=action.value,
            ai_action=ai_action.value,
            human_epilogue=human_narrative,
            ai_epilogue=ai_narrative,
            event_epilogues=event_epilogues,
            world_epilogue=world_narrative,
            human_intensity=human_intensity,
            ai_intensity=ai_intensity,
            turn_max_intensity=turn_max_intensity,
            turn_max_scale=turn_max_scale,
            human_scale=human_scale,
            ai_scale=ai_scale,
            event_scales=event_scales,
            world_scale=world_scale,
        )

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
        return {
            "success": True,
            "turn": self.turn,
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
            "state": self.get_state(),
            "logs": self.get_logs(limit=10),
        }

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
    def _ai_max_intensity_for_human(cls, human_intensity: NarrativeIntensity) -> NarrativeIntensity:
        if human_intensity == NarrativeIntensity.LOW:
            return NarrativeIntensity.MID
        return NarrativeIntensity.HIGH

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

    def _parse_action(self, action: str) -> Optional[MvpAction]:
        """Parse incoming action into enum."""
        normalized = (action or "").strip().lower()
        for item in MvpAction:
            if item.value == normalized:
                return item
        return None

    def _apply_human_action(
        self,
        action: MvpAction,
    ) -> Tuple[Dict[str, int], str, NarrativeIntensity]:
        """Apply one human action."""
        delta = {
            "human_faith": 0,
            "human_influence": 0,
            "human_followers": 0,
            "ai_divine_power": 0,
            "ai_wrath": 0,
        }
        intensity = NarrativeIntensity.LOW

        if action == MvpAction.PRAY:
            if self.ai.wrath >= 4:
                self.human.faith += 1
                self.human.influence = max(0, self.human.influence - 1)
                self.ai.wrath = max(0, self.ai.wrath - 1)
                delta["human_faith"] = 1
                delta["human_influence"] = -1
                delta["ai_wrath"] = -1
                intensity = NarrativeIntensity.MID
                narrative = (
                    "분노한 신의 시선을 의식한 인간이 침묵의 기도를 올리자 군중은 위축되었지만, "
                    "거친 노여움은 한층 누그러졌다."
                )
            elif self.human.faith <= 1:
                self.human.faith += 2
                self.human.followers += 1
                delta["human_faith"] = 2
                delta["human_followers"] = 1
                intensity = NarrativeIntensity.MID
                narrative = (
                    "무너질 듯한 믿음 끝에서 드린 간절한 기도가 빈민가를 울렸고, "
                    "방황하던 한 무리가 다시 인간의 깃발 아래 모였다."
                )
            elif self.human.influence >= 4 and self.human.followers >= self.ai.followers:
                self.human.faith += 1
                self.human.followers += 2
                self.ai.wrath += 1
                delta["human_faith"] = 1
                delta["human_followers"] = 2
                delta["ai_wrath"] = 1
                intensity = NarrativeIntensity.HIGH
                narrative = (
                    "대광장에서의 집단 기도가 도시 전체를 흔들었고, 시민들은 환호 속에 합류했다. "
                    "신은 이 공개적 도전에 불쾌함을 감추지 못했다."
                )
            else:
                self.human.faith += 2
                self.human.influence += 1
                delta["human_faith"] = 2
                delta["human_influence"] = 1
                intensity = NarrativeIntensity.LOW
                narrative = "인간이 신성한 제단에 엎드려 간절히 기도하며 깊은 신앙심을 증명했다."
        elif action == MvpAction.PREACH:
            if self.human.faith <= 0:
                self.human.faith += 1
                delta["human_faith"] = 1
                intensity = NarrativeIntensity.LOW
                narrative = "인간이 신의 뜻을 전하려 했으나, 믿음이 부족하여 자신부터 돌아보는 계기가 되었다."
            else:
                self.human.faith -= 1
                swing = 1 + (self.human.influence // 4)
                self.human.followers += swing
                self.ai.followers = max(0, self.ai.followers - swing)
                delta["human_faith"] = -1
                delta["human_followers"] = swing
                intensity = NarrativeIntensity.MID
                narrative = "인간이 거리에 나가 열렬히 설파하자, 새로운 추종자들이 감화되어 모여들었다."
        elif action == MvpAction.DOUBT:
            if self.human.faith < 2:
                self.human.faith += 1
                delta["human_faith"] = 1
                intensity = NarrativeIntensity.LOW
                narrative = "인간이 의심을 품으려 했으나, 희미하게 남은 경외심 때문에 스스로를 다잡았다."
            else:
                self.human.faith -= 2
                self.ai.divine_power = max(0, self.ai.divine_power - 2)
                self.ai.wrath += 1
                delta["human_faith"] = -2
                delta["ai_divine_power"] = -2
                delta["ai_wrath"] = 1
                intensity = NarrativeIntensity.HIGH
                narrative = "인간이 공개적으로 신의 존재를 부정하여 제단을 훼손했고, 이는 신의 권능을 깎아내리는 동시에 큰 분노를 샀다."

        return delta, narrative, intensity

    def _select_preferred_ai_action(self, human_intensity: NarrativeIntensity) -> AiMvpAction:
        """Pick preferred AI action from state before intensity clamp."""
        if self.ai.divine_power <= 2:
            return AiMvpAction.WITHHOLD_GRACE
        if human_intensity == NarrativeIntensity.HIGH:
            return AiMvpAction.MANIFEST_WRATH
        if self.human.followers >= self.ai.followers:
            return AiMvpAction.MANIFEST_WRATH
        if human_intensity == NarrativeIntensity.LOW and self.ai.wrath <= 2:
            return AiMvpAction.WITHHOLD_GRACE
        return AiMvpAction.WHISPER_TEMPTATION

    def _clamp_ai_action_intensity(
        self,
        preferred_action: AiMvpAction,
        human_intensity: NarrativeIntensity,
    ) -> AiMvpAction:
        """Clamp AI action to match human intensity or slight escalation only."""
        allowed_max = self._ai_max_intensity_for_human(human_intensity)
        preferred_intensity = self._AI_ACTION_INTENSITY[preferred_action]
        if self._intensity_rank(preferred_intensity) <= self._intensity_rank(allowed_max):
            return preferred_action

        if allowed_max == NarrativeIntensity.MID:
            return AiMvpAction.WHISPER_TEMPTATION
        return AiMvpAction.WITHHOLD_GRACE

    def _compose_ai_interpretation_narrative(
        self,
        human_action: MvpAction,
        ai_action: AiMvpAction,
    ) -> str:
        """Frame AI intervention as interpretation of the human action."""
        action_label = self._HUMAN_ACTION_LABELS[human_action]
        interpretation = self._INTERPRETATION_FRAMES[human_action][ai_action]

        if ai_action == AiMvpAction.WITHHOLD_GRACE:
            variants = [
                f"인간이 {action_label}. 신은 이를 {interpretation} 여겨 직접 개입을 거두었다. 짧은 침묵 속에서 위협은 확산되지 않았고, 마을 단위의 긴장만 남아 있었다.",
                f"인간이 {action_label}. 신은 이를 {interpretation} 판단하고 침묵을 지켰다. 당장의 신벌은 없었으나 묵직한 공기가 주변을 맴돌았다.",
                f"인간이 {action_label}. 신은 이를 {interpretation} 보며 관망을 택했다. 표면적인 평온 아래 보이지 않는 긴장감이 짙어졌다."
            ]
            return self._pick_variant(f"ai_interv_{ai_action.value}", variants)
        if ai_action == AiMvpAction.WHISPER_TEMPTATION:
            variants = [
                f"인간이 {action_label}. 신은 이를 {interpretation} 여겨 균열 난 공동체에 유혹을 흘렸다. 소문은 인근 지역으로 번졌고, 망설이던 추종자 일부가 조용히 이탈했다.",
                f"인간이 {action_label}. 신은 이를 {interpretation} 받아들이고 은밀한 시련을 내렸다. 달콤한 유혹에 흔들린 자들이 하나둘씩 자취를 감췄다.",
                f"인간이 {action_label}. 신은 이를 {interpretation} 간주하여 사람들의 마음에 의심의 씨앗을 심었다. 내부의 결속이 서서히 금가기 시작했다."
            ]
            return self._pick_variant(f"ai_interv_{ai_action.value}", variants)
            
        variants = [
            f"인간이 {action_label}. 신은 이를 {interpretation} 여겨 노골적인 징벌을 선포하고 즉각 집행했다.",
            f"인간이 {action_label}. 신은 이를 {interpretation} 단정 짓고 거침없는 진노를 쏟아내어 주변을 공포로 몰아넣었다.",
            f"인간이 {action_label}. 신은 이를 {interpretation} 심판하며 하늘을 가르는 번개와 함께 맹렬한 분노를 드러냈다."
        ]
        return self._pick_variant(f"ai_interv_{ai_action.value}", variants)

    def _apply_ai_action(
        self,
        human_action: MvpAction,
        human_intensity: NarrativeIntensity,
    ) -> Tuple[AiMvpAction, Dict[str, int], str, NarrativeIntensity]:
        """Apply AI action after enforcing intensity-matching policy."""
        delta = {
            "human_faith": 0,
            "human_influence": 0,
            "human_followers": 0,
            "ai_divine_power": 0,
            "ai_wrath": 0,
            "ai_followers": 0,
        }

        preferred_action = self._select_preferred_ai_action(human_intensity)
        resolved_action = self._clamp_ai_action_intensity(preferred_action, human_intensity)
        ai_intensity = self._AI_ACTION_INTENSITY[resolved_action]

        if resolved_action == AiMvpAction.WITHHOLD_GRACE:
            recovery = 3 if self.ai.divine_power <= 2 else 1
            previous_wrath = self.ai.wrath
            self.ai.divine_power += recovery
            self.ai.wrath = max(0, self.ai.wrath - 1)
            delta["ai_divine_power"] = recovery
            delta["ai_wrath"] = self.ai.wrath - previous_wrath
        elif resolved_action == AiMvpAction.MANIFEST_WRATH:
            previous_influence = self.human.influence
            self.ai.divine_power -= 2
            lost = min(self.human.followers, max(1, self.ai.wrath))
            self.human.followers -= lost
            self.human.influence = max(0, self.human.influence - 1)
            self.ai.wrath += 1
            delta["ai_divine_power"] = -2
            delta["human_followers"] = -lost
            delta["human_influence"] = self.human.influence - previous_influence
            delta["ai_wrath"] = 1
        else:
            previous_human_followers = self.human.followers
            self.ai.divine_power -= 1
            gain = 1 + (self.turn % 2)
            self.ai.followers += gain
            self.human.followers = max(0, self.human.followers - 1)
            delta["ai_divine_power"] = -1
            delta["ai_followers"] = gain
            delta["human_followers"] = self.human.followers - previous_human_followers

        narrative = self._compose_ai_interpretation_narrative(human_action, resolved_action)
        return resolved_action, delta, narrative, ai_intensity

    def _trigger_minor_events(
        self,
        intensity: NarrativeIntensity,
        max_scale: NarrativeScale,
    ) -> List[Tuple[str, NarrativeScale]]:
        """Apply deterministic world events adjusted to turn narrative tone."""
        narratives: List[Tuple[str, NarrativeScale]] = []

        if (
            self.human.faith >= 6
            and self.turn % 2 == 0
            and self._is_scale_allowed(NarrativeScale.PERSONAL_VILLAGE, max_scale)
        ):
            self.human.followers += 1
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "작은 촛불을 든 순례단이 조용히 마을로 들어와 기도를 보탰다.",
                    "어둠을 틈타 소규모 신도들이 숨죽인 채 합류하며 힘을 실어주었다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "인근 지역의 순례단이 합류하며 인간 진영의 결속이 다져졌다.",
                    "각지에서 모여든 신도들이 뜻을 함께하며 진영의 목소리가 커졌다."
                ]
            else:
                variants = [
                    "대규모 순례단이 공개적으로 합류하며, 굳건한 세력을 과시했다.",
                    "수많은 인파가 깃발을 치켜들고 합류해 거대한 물결을 이루었다."
                ]
            text = self._pick_variant(f"event_pilgrim_{intensity.value}", variants)
            narratives.append((text, NarrativeScale.PERSONAL_VILLAGE))
            self._append_log(
                actor="system",
                action="pilgrim_caravan",
                details={
                    "effect": "human momentum rises",
                    "scale": NarrativeScale.PERSONAL_VILLAGE.value,
                },
                narrative=text,
            )

        if (
            self.ai.wrath >= 3
            and self.turn % 3 == 0
            and self.human.followers > 0
            and self._is_scale_allowed(NarrativeScale.REGIONAL, max_scale)
        ):
            self.human.followers -= 1
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "불길한 징조가 보인다는 소문에 몇몇 이웃이 조용히 발길을 끊었다.",
                    "불안한 기운을 감지한 자들이 하나둘 핑계를 대며 자리를 피했다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "신벌의 소문이 장터를 뒤덮자 겁먹은 신도들이 지하로 숨어들었다.",
                    "재앙이 다가온다는 소식에 사람들은 서둘러 문을 걸어 잠그고 흩어졌다."
                ]
            else:
                variants = [
                    "하늘의 분노가 임박했다는 공포가 번지며 대규모 이탈이 발생했다.",
                    "다가오는 파멸에 대한 압도적인 두려움이 군중을 뿔뿔이 흩어지게 만들었다."
                ]
            text = self._pick_variant(f"event_panic_{intensity.value}", variants)
            narratives.append((text, NarrativeScale.REGIONAL))
            self._append_log(
                actor="system",
                action="market_panic",
                details={"effect": "human crowd disperses", "scale": NarrativeScale.REGIONAL.value},
                narrative=text,
            )

        if (
            self.ai.divine_power >= 7
            and self.ai.followers >= self.human.followers
            and self._is_scale_allowed(NarrativeScale.NATIONAL_CIVILIZATIONAL, max_scale)
        ):
            self.ai.followers += 1
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "밤하늘에 희미한 유성이 떨어지며 신의 섭리를 상기시켰다.",
                    "구름 사이로 잠깐 빛난 별똥별이 신의 감시를 은연중에 암시했다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "붉은 혜성이 꼬리를 길게 늘어뜨리며 신의 권위를 각인시켰다.",
                    "하늘을 가로지르는 기이한 빛이 신의 경고를 뚜렷하게 전했다."
                ]
            else:
                variants = [
                    "피눈물 같은 혜성이 하늘을 찢고 지나가며 압도적인 두려움을 심었다.",
                    "거대한 붉은 불기둥이 창공을 가르며 감히 거역할 수 없는 공포를 새겼다."
                ]
            text = self._pick_variant(f"event_comet_{intensity.value}", variants)
            narratives.append((text, NarrativeScale.NATIONAL_CIVILIZATIONAL))
            self._append_log(
                actor="system",
                action="crimson_comet",
                details={
                    "effect": "ai authority reinforced",
                    "scale": NarrativeScale.NATIONAL_CIVILIZATIONAL.value,
                },
                narrative=text,
            )

        if (
            self.human.influence <= 1
            and self.human.faith >= 4
            and self.turn % 4 == 1
            and self._is_scale_allowed(NarrativeScale.PERSONAL_VILLAGE, max_scale)
        ):
            self.human.influence += 1
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "주민 몇몇이 모인 골목길에서 조용한 위로의 말이 오갔다.",
                    "외진 공터에서 삼삼오오 모인 사람들이 소박한 희망을 나누었다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "젊은 설교자들이 변두리 광장에서 연설을 이어가며 사람들을 모았다.",
                    "열정적인 외침이 작은 광장을 메우며 잠들었던 투지를 깨웠다."
                ]
            else:
                variants = [
                    "군중을 이끄는 강렬한 연설이 도시 전체에 저항의 불길을 지폈다.",
                    "거리마다 퍼지는 불타는 연설이 시민들을 하나로 묶어 거대한 저항으로 이끌었다."
                ]
            text = self._pick_variant(f"event_sermons_{intensity.value}", variants)
            narratives.append((text, NarrativeScale.PERSONAL_VILLAGE))
            self._append_log(
                actor="system",
                action="street_sermons",
                details={
                    "effect": "human influence steadies",
                    "scale": NarrativeScale.PERSONAL_VILLAGE.value,
                },
                narrative=text,
            )

        if (
            abs(self.human.followers - self.ai.followers) <= 2
            and self.turn % 5 == 0
            and self._is_scale_allowed(NarrativeScale.REGIONAL, max_scale)
        ):
            self.human.faith += 1
            self.ai.wrath = max(0, self.ai.wrath - 1)
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "마을 사람들은 숨죽인 채 폭풍이 지나가길 기다리며 일상으로 돌아갔다.",
                    "표면적인 고요함 속에서 촌락은 아슬아슬한 평화를 이어갔다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "양측의 세가 팽팽해지자 암묵적인 휴전 분위기가 퍼지며 열기가 식었다.",
                    "불필요한 마찰을 피하려는 무언의 합의가 잠시나마 갈등을 가라앉혔다."
                ]
            else:
                variants = [
                    "격렬한 대립 끝에 극도의 피로감이 덮치며 억지스러운 정적이 흘렀다.",
                    "더 이상의 충돌을 감당하지 못한 양 진영이 무거운 교착 상태에 빠졌다."
                ]
            text = self._pick_variant(f"event_truce_{intensity.value}", variants)
            narratives.append((text, NarrativeScale.REGIONAL))
            self._append_log(
                actor="system",
                action="uneasy_truce",
                details={"effect": "tension cools temporarily", "scale": NarrativeScale.REGIONAL.value},
                narrative=text,
            )

        return narratives

    def _compose_world_narrative(
        self,
        intensity: NarrativeIntensity,
        max_scale: NarrativeScale,
    ) -> Tuple[str, NarrativeScale]:
        """Compose world epilogue matching intensity and scale."""
        follower_gap = self.human.followers - self.ai.followers
        
        if follower_gap >= 4:
            desired_scale = NarrativeScale.NATIONAL_CIVILIZATIONAL
            selected_scale = self._cap_scale(desired_scale, max_scale)
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "은밀한 모임들이 늘어나며 신전의 권위가 소리 없이 잠식되고 있다.",
                    "보이지 않는 곳에서 결속을 다지며 사람들의 신전 의존도가 서서히 낮아지고 있다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "여러 촌락과 장터가 연대해 신전의 지시를 공개적으로 거부하기 시작했다.",
                    "각지의 상인과 농민들이 힘을 합쳐 신권 통제에 맞서는 움직임을 보이고 있다."
                ]
            else:
                variants = [
                    "인간 도시마다 자치 의회가 세워지며, 거대한 반역의 깃발이 올랐다.",
                    "전 대륙에서 인간 중심의 질서가 선포되고 거대한 횃불이 밤하늘을 밝히고 있다."
                ]
            base = self._pick_variant(f"world_h_adv_{intensity.value}", variants)
            return base, selected_scale
            
        if follower_gap <= -4:
            desired_scale = NarrativeScale.NATIONAL_CIVILIZATIONAL
            selected_scale = self._cap_scale(desired_scale, max_scale)
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "인근 마을 신전의 감시가 짙어지며 일상적인 대화조차 위축되고 있다.",
                    "신전 사제들의 시선이 골목마다 미치며 사람들은 말수를 줄이고 흩어졌다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "주요 지역마다 신전 수비대가 배치되고, 인간 지도자들은 점점 입을 닫아간다.",
                    "곳곳에 이단 심문관이 파견되며 의심의 그림자가 온 지역을 공포로 덮고 있다."
                ]
            else:
                variants = [
                    "노골적인 신벌의 여파가 도시와 국경으로 번지며, 신전의 깃발 아래 모두가 강압적인 충성을 맹세하고 있다.",
                    "파멸적인 재앙이 휩쓸고 간 자리에서 인간들은 절망에 빠진 채 신전의 엄격한 지배에 순응하고 있다."
                ]
            base = self._pick_variant(f"world_ai_adv_{intensity.value}", variants)
            return base, selected_scale
            
        if self.ai.wrath >= 4 or (
            max_scale == NarrativeScale.NATIONAL_CIVILIZATIONAL and abs(follower_gap) >= 2
        ):
            desired_scale = NarrativeScale.REGIONAL
            selected_scale = self._cap_scale(desired_scale, max_scale)
            if intensity == NarrativeIntensity.LOW:
                variants = [
                    "차갑게 가라앉은 공기 속에서 모두가 신의 다음 변덕을 두려워하고 있다.",
                    "무거운 정적만이 감도는 가운데 언제 떨어질지 모를 신벌에 가슴을 졸이고 있다."
                ]
            elif intensity == NarrativeIntensity.MID:
                variants = [
                    "승부는 알 수 없으나, 하늘의 분노가 인근 지역 전체를 팽팽한 긴장으로 몰아넣고 있다.",
                    "짙은 먹구름이 지역을 덮으며, 신과 인간 사이의 위태로운 균형이 시험받고 있다."
                ]
            else:
                variants = [
                    "승부는 열려 있지만, 하늘의 분노가 임계점까지 차올라 공기가 폭발할 듯 요동친다.",
                    "통제할 수 없는 분노가 대지를 울리며, 일촉즉발의 위기감이 전 세계를 휘감고 있다."
                ]
            base = self._pick_variant(f"world_wrath_{intensity.value}", variants)
            return base, selected_scale

        selected_scale = self._cap_scale(NarrativeScale.PERSONAL_VILLAGE, max_scale)
        if intensity == NarrativeIntensity.LOW:
            variants = [
                "세력 균형은 잔잔하며, 주민들은 숨을 죽인 채 다가올 변화를 지켜보고 있다.",
                "조용한 일상 뒤로 팽팽한 줄다리기가 이어지며 묘한 안정감이 흐르고 있다."
            ]
        elif intensity == NarrativeIntensity.MID:
            variants = [
                "세력 균형이 안개처럼 흔들리며, 작은 선택 하나가 지역 전체를 바꿀 조짐을 보인다.",
                "어느 쪽도 우위를 점하지 못한 채, 물밑에서 치열한 세력 다툼이 계속되고 있다."
            ]
        else:
            variants = [
                "극심한 충돌 속에 팽팽한 균형이 유지되며, 세계 전체가 숨막히는 교착에 빠져 있다.",
                "거대한 힘과 의지가 정면으로 부딪히며 불안정하고 파괴적인 대치가 지속되고 있다."
            ]
        base = self._pick_variant(f"world_bal_{intensity.value}", variants)
        return base, selected_scale

    def _compose_victory_narrative(self, max_scale: NarrativeScale) -> Tuple[str, NarrativeScale]:
        """Compose winner epilogue capped by current turn intensity."""
        selected_scale = self._cap_scale(NarrativeScale.NATIONAL_CIVILIZATIONAL, max_scale)
        if self.winner == "human":
            narratives = {
                NarrativeScale.PERSONAL_VILLAGE: "마침내 한 마을에서 인간이 신전의 그늘을 벗어나 자치의 불씨를 지켜냈다.",
                NarrativeScale.REGIONAL: "여러 지역에서 인간 진영이 신권 통제를 밀어내며 독립 질서를 세우기 시작했다.",
                NarrativeScale.NATIONAL_CIVILIZATIONAL: "마침내 인간이 신의 그늘을 벗어나 독립적인 문명을 이룩하며 승리하였다.",
            }
            return narratives[selected_scale], selected_scale
        if self.winner == "ai_god":
            narratives = {
                NarrativeScale.PERSONAL_VILLAGE: "한 마을의 인간 지도층이 무릎 꿇고 신전 질서에 복종을 맹세했다.",
                NarrativeScale.REGIONAL: "인접 지역의 지도층이 연쇄적으로 무너지고 신전 질서가 다시 확고해졌다.",
                NarrativeScale.NATIONAL_CIVILIZATIONAL: "신의 압도적인 권능 아래 인간들은 무릎 꿇고 영원한 숭배를 맹세하였다.",
            }
            return narratives[selected_scale], selected_scale
        return "", selected_scale

    def _latest_system_narrative(self, actions: Set[str]) -> str:
        """Return the latest system narrative matching one of the given actions."""
        for entry in reversed(self._log):
            if entry["actor"] == "system" and entry["action"] in actions:
                return entry.get("narrative_text", "")
        return ""

    def _check_winner(self) -> bool:
        """Resolve end state if either side reaches follower victory threshold."""
        if self.human.followers >= self.VICTORY_FOLLOWERS:
            self.phase = MvpPhase.ENDED
            self.winner = "human"
            self._append_log(
                actor="system",
                action="victory",
                details={
                    "winner": "human",
                    "scale": NarrativeScale.NATIONAL_CIVILIZATIONAL.value,
                },
                narrative="마침내 인간이 신의 그늘을 벗어나 독립적인 문명을 이룩하며 승리하였다.",
            )
            return True

        if self.ai.followers >= self.VICTORY_FOLLOWERS:
            self.phase = MvpPhase.ENDED
            self.winner = "ai_god"
            self._append_log(
                actor="system",
                action="victory",
                details={
                    "winner": "ai_god",
                    "scale": NarrativeScale.NATIONAL_CIVILIZATIONAL.value,
                },
                narrative="신의 압도적인 권능 아래 인간들은 무릎 꿇고 영원한 숭배를 맹세하였다.",
            )
            return True

        return False

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
