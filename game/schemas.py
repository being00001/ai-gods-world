from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class GodActionRequest:
    """Standard request for AI God (OpenClaw) intervention."""
    game_id: str
    turn: int
    human_action: str
    human_narrative: str
    current_state: Dict[str, Any]
    intensity_limit: str

@dataclass
class GodActionResponse:
    """Standard response from AI God (OpenClaw) intervention."""
    game_id: str
    turn: int
    action: str
    narrative: str
    intensity: str
    scale: str
