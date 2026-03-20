"""Matrix adapter for formatting AI God intervention requests.

This adapter intentionally does not call any external messaging tool.
It only prepares a prompt/payload that an orchestrator can send to OpenClaw.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from game.schemas import GodActionRequest


class MatrixGodAdapter:
    """Build Matrix-ready requests for OpenClaw intervention."""

    def __init__(self, god_handle: str = "OpenClaw", channel: str = "matrix") -> None:
        self.god_handle = god_handle
        self.channel = channel

    def build_openclaw_message(self, request: GodActionRequest) -> str:
        """Return a deterministic instruction message for OpenClaw."""
        serialized_state = json.dumps(
            request.current_state,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        return "\n".join(
            [
                f"[AI Gods World] {self.god_handle} intervention request",
                f"- game_id: {request.game_id}",
                f"- turn: {request.turn}",
                f"- human_action: {request.human_action}",
                f"- intensity_limit: {request.intensity_limit}",
                "- human_narrative:",
                request.human_narrative,
                "- current_state_json:",
                serialized_state,
                "",
                "Please respond in JSON with keys:",
                'action, narrative, intensity, scale (and keep game_id/turn unchanged).',
                "Allowed actions: withhold_grace | whisper_temptation | manifest_wrath",
                "Allowed intensity: low | mid | high",
                "Allowed scale: personal/village | regional | national/civilizational",
            ]
        )

    def build_matrix_payload(self, request: GodActionRequest) -> Dict[str, Any]:
        """Return channel payload that an external sender can dispatch."""
        return {
            "channel": self.channel,
            "recipient": self.god_handle,
            "message": self.build_openclaw_message(request),
            "metadata": {
                "game_id": request.game_id,
                "turn": request.turn,
                "intensity_limit": request.intensity_limit,
            },
        }

    def prepare_intervention(self, request: GodActionRequest) -> Dict[str, Any]:
        """Alias for callers that want one public entry-point."""
        return self.build_matrix_payload(request)
