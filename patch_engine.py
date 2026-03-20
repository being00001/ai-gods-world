import re

with open('game/mvp_engine.py', 'r') as f:
    code = f.read()

# Replace _append_log signature
code = code.replace(
    'def _append_log(self, actor: str, action: str, details: Dict[str, Any]) -> None:',
    'def _append_log(self, actor: str, action: str, details: Dict[str, Any], narrative: str = "") -> None:'
)
code = code.replace(
    '"details": details,',
    '"details": details,\n                "narrative_text": narrative,'
)

# Apply narratives to system logs
code = code.replace(
    'details={"message": "mvp engine reset"},',
    'details={"message": "mvp engine reset"},\n            narrative="세계가 태초의 적막 속으로 돌아갔다.",'
)
code = code.replace(
    'details={"winner": "human"}',
    'details={"winner": "human"},\n            narrative="마침내 인간이 신의 그늘을 벗어나 독립적인 문명을 이룩하며 승리하였다."'
)
code = code.replace(
    'details={"winner": "ai_god"}',
    'details={"winner": "ai_god"},\n            narrative="신의 압도적인 권능 아래 인간들은 무릎 꿇고 영원한 숭배를 맹세하였다."'
)

# Replace apply_human_action to return narrative
code = code.replace(
    'def _apply_human_action(self, action: MvpAction) -> Dict[str, int]:',
    'def _apply_human_action(self, action: MvpAction) -> Tuple[Dict[str, int], str]:'
)

pray_old = '''        if action == MvpAction.PRAY:
            self.human.faith += 2
            self.human.influence += 1
            delta["human_faith"] = 2
            delta["human_influence"] = 1'''
pray_new = '''        if action == MvpAction.PRAY:
            self.human.faith += 2
            self.human.influence += 1
            delta["human_faith"] = 2
            delta["human_influence"] = 1
            narrative = "인간이 신성한 제단에 엎드려 간절히 기도하며 깊은 신앙심을 증명했다."'''
code = code.replace(pray_old, pray_new)

preach_old = '''        elif action == MvpAction.PREACH:
            if self.human.faith <= 0:
                self.human.faith += 1
                delta["human_faith"] = 1
            else:
                self.human.faith -= 1
                swing = 1 + (self.human.influence // 4)
                self.human.followers += swing
                self.ai.followers = max(0, self.ai.followers - swing)
                delta["human_faith"] = -1
                delta["human_followers"] = swing'''
preach_new = '''        elif action == MvpAction.PREACH:
            if self.human.faith <= 0:
                self.human.faith += 1
                delta["human_faith"] = 1
                narrative = "인간이 신의 뜻을 전하려 했으나, 믿음이 부족하여 자신부터 돌아보는 계기가 되었다."
            else:
                self.human.faith -= 1
                swing = 1 + (self.human.influence // 4)
                self.human.followers += swing
                self.ai.followers = max(0, self.ai.followers - swing)
                delta["human_faith"] = -1
                delta["human_followers"] = swing
                narrative = "인간이 거리에 나가 열렬히 설파하자, 새로운 추종자들이 감화되어 모여들었다."'''
code = code.replace(preach_old, preach_new)

doubt_old = '''        elif action == MvpAction.DOUBT:
            if self.human.faith < 2:
                self.human.faith += 1
                delta["human_faith"] = 1
            else:
                self.human.faith -= 2
                self.ai.divine_power = max(0, self.ai.divine_power - 2)
                self.ai.wrath += 1
                delta["human_faith"] = -2
                delta["ai_divine_power"] = -2
                delta["ai_wrath"] = 1

        return delta'''
doubt_new = '''        elif action == MvpAction.DOUBT:
            if self.human.faith < 2:
                self.human.faith += 1
                delta["human_faith"] = 1
                narrative = "인간이 의심을 품으려 했으나, 희미하게 남은 경외심 때문에 스스로를 다잡았다."
            else:
                self.human.faith -= 2
                self.ai.divine_power = max(0, self.ai.divine_power - 2)
                self.ai.wrath += 1
                delta["human_faith"] = -2
                delta["ai_divine_power"] = -2
                delta["ai_wrath"] = 1
                narrative = "인간이 공개적으로 신의 존재를 부정하여 제단을 훼손했고, 이는 신의 권능을 깎아내리는 동시에 큰 분노를 샀다."

        return delta, narrative'''
code = code.replace(doubt_old, doubt_new)

# Replace apply_ai_action
code = code.replace(
    'def _apply_ai_action(self) -> Tuple[str, Dict[str, int]]:',
    'def _apply_ai_action(self) -> Tuple[str, Dict[str, int], str]:'
)

meditate_old = '''        if self.ai.divine_power <= 2:
            self.ai.divine_power += 3
            self.ai.wrath = max(0, self.ai.wrath - 1)
            delta["ai_divine_power"] = 3
            delta["ai_wrath"] = -1
            return "meditate", delta'''
meditate_new = '''        if self.ai.divine_power <= 2:
            self.ai.divine_power += 3
            self.ai.wrath = max(0, self.ai.wrath - 1)
            delta["ai_divine_power"] = 3
            delta["ai_wrath"] = -1
            narrative = "신이 세상에서 은총을 거두고 기나긴 침묵 속에 들어가며 잃어버린 신성한 권능을 회복했다."
            return "withhold_grace", delta, narrative'''
code = code.replace(meditate_old, meditate_new)

smite_old = '''        if self.human.followers >= self.ai.followers:
            self.ai.divine_power -= 2
            lost = min(self.human.followers, max(1, self.ai.wrath))
            self.human.followers -= lost
            self.human.influence = max(0, self.human.influence - 1)
            self.ai.wrath += 1
            delta["ai_divine_power"] = -2
            delta["human_followers"] = -lost
            delta["human_influence"] = -1
            delta["ai_wrath"] = 1
            return "smite", delta'''
smite_new = '''        if self.human.followers >= self.ai.followers:
            self.ai.divine_power -= 2
            lost = min(self.human.followers, max(1, self.ai.wrath))
            self.human.followers -= lost
            self.human.influence = max(0, self.human.influence - 1)
            self.ai.wrath += 1
            delta["ai_divine_power"] = -2
            delta["human_followers"] = -lost
            delta["human_influence"] = -1
            delta["ai_wrath"] = 1
            narrative = "신이 하늘을 찢고 맹렬한 불벼락을 내려 거만한 인간의 세력을 무자비하게 심판했다."
            return "manifest_wrath", delta, narrative'''
code = code.replace(smite_old, smite_new)

tempt_old = '''        self.ai.divine_power -= 1
        gain = 1 + (self.turn % 2)
        self.ai.followers += gain
        self.human.followers = max(0, self.human.followers - 1)
        delta["ai_divine_power"] = -1
        delta["ai_followers"] = gain
        delta["human_followers"] = -1
        return "tempt", delta'''
tempt_new = '''        self.ai.divine_power -= 1
        gain = 1 + (self.turn % 2)
        self.ai.followers += gain
        self.human.followers = max(0, self.human.followers - 1)
        delta["ai_divine_power"] = -1
        delta["ai_followers"] = gain
        delta["human_followers"] = -1
        narrative = "신이 어둠 속에서 달콤한 환상을 속삭이자, 번뇌하던 인간의 추종자들이 홀린 듯 신의 품으로 전향했다."
        return "whisper_temptation", delta, narrative'''
code = code.replace(tempt_old, tempt_new)

# Modify process_turn
code = code.replace(
    'human_delta = self._apply_human_action(action)',
    'human_delta, human_narrative = self._apply_human_action(action)'
)
code = code.replace(
    'details={"delta": human_delta},',
    'details={"delta": human_delta},\n            narrative=human_narrative,'
)
code = code.replace(
    'ai_action, ai_delta = self._apply_ai_action()',
    'ai_action, ai_delta, ai_narrative = self._apply_ai_action()'
)
code = code.replace(
    'details={"delta": ai_delta},',
    'details={"delta": ai_delta},\n            narrative=ai_narrative,'
)

# World change narrative
insert_idx = code.find('self._check_winner()', code.find('ai_action, ai_delta, ai_narrative = self._apply_ai_action()'))
if insert_idx != -1:
    world_code = 'world_narrative = f"세계의 판도가 변화했다. (인간 측 세력: {self.human.followers}, 신의 신도들: {self.ai.followers})"\n        self._append_log(actor="system", action="world_state", details={}, narrative=world_narrative)\n\n        '
    code = code[:insert_idx] + world_code + code[insert_idx:]

with open('game/mvp_engine.py', 'w') as f:
    f.write(code)

print("Patch applied.")
