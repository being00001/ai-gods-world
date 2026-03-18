"""
AI Gods World - Minimum Viable Game Engine

A hybrid strategy simulation game where LLM agents act as deities
and human players interact through a web interface.
"""

from .entities import (
    Entity,
    EntityManager,
    Deity,
    Follower,
    Region,
    Building,
    Unit,
    Component,
    PositionComponent,
    ResourceComponent,
    FactionComponent,
    StatsComponent,
    BuildingComponent,
    UnitComponent,
)

from .engine import (
    GameEngine,
    GameState,
    StateManager,
    GamePhase,
    VictoryCondition,
    TurnInfo,
)

__version__ = "0.1.0"
__all__ = [
    # Entities
    'Entity',
    'EntityManager',
    'Deity',
    'Follower',
    'Region',
    'Building',
    'Unit',
    'Component',
    'PositionComponent',
    'ResourceComponent',
    'FactionComponent',
    'StatsComponent',
    'BuildingComponent',
    'UnitComponent',
    # Engine
    'GameEngine',
    'GameState',
    'StateManager',
    'GamePhase',
    'VictoryCondition',
    'TurnInfo',
]
