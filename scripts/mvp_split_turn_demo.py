#!/usr/bin/env python3
"""Validate the MVP split-turn API flow with Flask test client."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from game.web_server import app  # noqa: E402


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with app.test_client() as client:
        reset = client.post("/api/mvp/reset")
        _check(reset.status_code == 200, f"reset status={reset.status_code}")
        reset_data = reset.get_json()
        _check(reset_data["state"]["phase"] == "waiting_human", "reset phase mismatch")
        _check(reset_data["state"]["awaiting_ai_god"] is False, "reset awaiting mismatch")

        human = client.post("/api/mvp/human_action", json={"action": "preach"})
        _check(human.status_code == 200, f"human_action status={human.status_code}")
        human_data = human.get_json()
        _check(human_data["success"] is True, "human_action should succeed")
        _check(human_data["phase"] == "waiting_ai_god", "human_action phase should wait for AI")
        _check(human_data["awaiting_ai_god"] is True, "human_action awaiting flag mismatch")

        state_wait = client.get("/api/mvp/state")
        _check(state_wait.status_code == 200, f"state status={state_wait.status_code}")
        state_wait_data = state_wait.get_json()
        _check(state_wait_data["phase"] == "waiting_ai_god", "state phase should wait for AI")
        _check(state_wait_data["awaiting_ai_god"] is True, "state awaiting flag mismatch")

        intervene = client.post("/api/mvp/intervene", json={"action": "whisper_temptation"})
        _check(intervene.status_code == 200, f"intervene status={intervene.status_code}")
        intervene_data = intervene.get_json()
        _check(intervene_data["success"] is True, "intervene should succeed")
        _check(intervene_data["turn_complete"] is True, "turn should be complete after intervene")
        _check(intervene_data["phase"] in {"waiting_human", "ended"}, "invalid post-intervene phase")
        if intervene_data["phase"] == "waiting_human":
            _check(intervene_data["awaiting_ai_god"] is False, "awaiting flag should be false")

        state_done = client.get("/api/mvp/state")
        _check(state_done.status_code == 200, f"state status={state_done.status_code}")
        state_done_data = state_done.get_json()
        _check(state_done_data["phase"] in {"waiting_human", "ended"}, "invalid final state phase")
        if state_done_data["phase"] == "waiting_human":
            _check(state_done_data["awaiting_ai_god"] is False, "final awaiting flag should be false")

        print(
            json.dumps(
                {
                    "reset_phase": reset_data["state"]["phase"],
                    "human_phase": human_data["phase"],
                    "intervene_phase": intervene_data["phase"],
                    "final_phase": state_done_data["phase"],
                    "turn": intervene_data["turn"],
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
