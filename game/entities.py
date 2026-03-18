"""
Entity/Component System for AI Gods World

This module provides the core entity-component architecture for the game.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass, field
import uuid


# ============================================================================
# Component Base Classes
# ============================================================================

class Component:
    """Base class for all components."""
    
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a component property."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a component property."""
        self._data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary."""
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Component:
        """Create component from dictionary."""
        return cls(**data)


# ============================================================================
# Concrete Components
# ============================================================================

class PositionComponent(Component):
    """Represents position in the game world."""
    
    def __init__(self, x: int = 0, y: int = 0, region_id: str = ""):
        super().__init__(x=x, y=y, region_id=region_id)
    
    @property
    def x(self) -> int:
        return self._data['x']
    
    @property
    def y(self) -> int:
        return self._data['y']
    
    @property
    def region_id(self) -> str:
        return self._data['region_id']


class ResourceComponent(Component):
    """Represents resources (Divine Power, Faith, Code, Entropy)."""
    
    def __init__(
        self,
        divine_power: float = 100.0,
        faith: float = 50.0,
        code: float = 10.0,
        entropy: float = 0.0
    ):
        super().__init__(
            divine_power=divine_power,
            faith=faith,
            code=code,
            entropy=entropy
        )
    
    def add(self, resource_type: str, amount: float) -> None:
        """Add to a resource."""
        if resource_type in self._data:
            self._data[resource_type] += amount
    
    def remove(self, resource_type: str, amount: float) -> bool:
        """Remove from a resource. Returns False if insufficient."""
        if resource_type in self._data and self._data[resource_type] >= amount:
            self._data[resource_type] -= amount
            return True
        return False
    
    def get(self, resource_type: str, default: Any = None) -> Any:
        """Get resource amount."""
        return self._data.get(resource_type, default)


class FactionComponent(Component):
    """Represents faction affiliation."""
    
    def __init__(self, faction_id: str = "", deity_id: str = ""):
        super().__init__(faction_id=faction_id, deity_id=deity_id)
    
    @property
    def faction_id(self) -> str:
        return self._data['faction_id']
    
    @property
    def deity_id(self) -> str:
        return self._data['deity_id']


class StatsComponent(Component):
    """Represents entity stats (health, attack, defense, etc.)."""
    
    def __init__(
        self,
        health: float = 100.0,
        max_health: float = 100.0,
        attack: float = 10.0,
        defense: float = 5.0,
        speed: float = 1.0
    ):
        super().__init__(
            health=health,
            max_health=max_health,
            attack=attack,
            defense=defense,
            speed=speed
        )
    
    def take_damage(self, amount: float) -> float:
        """Apply damage, return actual damage taken."""
        actual_damage = max(0, amount - self._data['defense'])
        self._data['health'] = max(0, self._data['health'] - actual_damage)
        return actual_damage
    
    def heal(self, amount: float) -> float:
        """Heal the entity, return actual healing done."""
        old_health = self._data['health']
        self._data['health'] = min(
            self._data['max_health'],
            self._data['health'] + amount
        )
        return self._data['health'] - old_health
    
    @property
    def is_alive(self) -> bool:
        return self._data['health'] > 0


class BuildingComponent(Component):
    """Represents a building type."""
    
    # Building types
    TEMPLE = "temple"
    SEMINARY = "seminary"
    LAB = "lab"
    ARENA = "arena"
    GATEWAY = "gateway"
    
    BUILDING_TYPES = [TEMPLE, SEMINARY, LAB, ARENA, GATEWAY]
    
    def __init__(self, building_type: str = TEMPLE, level: int = 1):
        if building_type not in self.BUILDING_TYPES:
            raise ValueError(f"Invalid building type: {building_type}")
        super().__init__(building_type=building_type, level=level)
    
    @property
    def building_type(self) -> str:
        return self._data['building_type']
    
    @property
    def level(self) -> int:
        return self._data['level']
    
    def upgrade(self) -> bool:
        """Upgrade the building. Returns False if max level reached."""
        if self._data['level'] < 10:  # Max level 10
            self._data['level'] += 1
            return True
        return False


class UnitComponent(Component):
    """Represents a unit type."""
    
    # Unit types
    PROPHET = "prophet"
    GUARDIAN = "guardian"
    INQUISITOR = "inquisitor"
    TURNCOAT = "turncoat"
    
    UNIT_TYPES = [PROPHET, GUARDIAN, INQUISITOR, TURNCOAT]
    
    def __init__(self, unit_type: str = PROPHET):
        if unit_type not in self.UNIT_TYPES:
            raise ValueError(f"Invalid unit type: {unit_type}")
        super().__init__(unit_type=unit_type)
    
    @property
    def unit_type(self) -> str:
        return self._data['unit_type']


# ============================================================================
# Entity Base Class
# ============================================================================

class Entity:
    """Base class for all game entities."""
    
    _component_registry: Dict[str, Type[Component]] = {}
    
    def __init__(self, entity_id: str = None, name: str = ""):
        self.id = entity_id or str(uuid.uuid4())[:8]
        self.name = name
        self._components: Dict[str, Component] = {}
        self._active = True
    
    def add_component(self, component: Component, component_type: str = None) -> Entity:
        """Add a component to the entity. Returns self for chaining."""
        if component_type is None:
            component_type = component.__class__.__name__
        self._components[component_type] = component
        return self
    
    def remove_component(self, component_type: str) -> Optional[Component]:
        """Remove and return a component."""
        return self._components.pop(component_type, None)
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """Get a component by type."""
        return self._components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """Check if entity has a component."""
        return component_type in self._components
    
    @property
    def components(self) -> Dict[str, Component]:
        """Get all components."""
        return self._components.copy()
    
    @property
    def is_active(self) -> bool:
        return self._active
    
    def deactivate(self) -> None:
        """Deactivate the entity."""
        self._active = False
    
    def activate(self) -> None:
        """Activate the entity."""
        self._active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'active': self._active,
            'components': {
                name: comp.to_dict() 
                for name, comp in self._components.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Entity:
        """Create entity from dictionary."""
        entity = cls(entity_id=data['id'], name=data['name'])
        entity._active = data.get('active', True)
        
        for comp_name, comp_data in data.get('components', {}).items():
            # Reconstruct component based on type
            if comp_name == 'PositionComponent':
                entity.add_component(PositionComponent.from_dict(comp_data))
            elif comp_name == 'ResourceComponent':
                entity.add_component(ResourceComponent.from_dict(comp_data))
            elif comp_name == 'FactionComponent':
                entity.add_component(FactionComponent.from_dict(comp_data))
            elif comp_name == 'StatsComponent':
                entity.add_component(StatsComponent.from_dict(comp_data))
            elif comp_name == 'BuildingComponent':
                entity.add_component(BuildingComponent.from_dict(comp_data))
            elif comp_name == 'UnitComponent':
                entity.add_component(UnitComponent.from_dict(comp_data))
        
        return entity


# ============================================================================
# Concrete Entity Classes
# ============================================================================

class Deity(Entity):
    """Represents an LLM agent deity."""
    
    def __init__(self, deity_id: str, name: str, faction: str):
        super().__init__(entity_id=deity_id, name=name)
        self.add_component(FactionComponent(faction_id=faction, deity_id=deity_id))
        self.add_component(ResourceComponent())
        self.add_component(StatsComponent(health=500.0, max_health=500.0, attack=50.0, defense=30.0))
    
    @property
    def faction(self) -> str:
        return self.get_component('FactionComponent').faction_id
    
    @property
    def resources(self) -> ResourceComponent:
        return self.get_component('ResourceComponent')


class Follower(Entity):
    """Represents a human player follower."""
    
    def __init__(self, follower_id: str, name: str, deity_id: str):
        super().__init__(entity_id=follower_id, name=name)
        self.add_component(FactionComponent(deity_id=deity_id))
        self.add_component(ResourceComponent(faith=10.0))
        self.add_component(StatsComponent())
        self.add_component(PositionComponent())


class Region(Entity):
    """Represents a map region."""
    
    def __init__(self, region_id: str, name: str, x: int, y: int):
        super().__init__(entity_id=region_id, name=name)
        self.add_component(PositionComponent(x=x, y=y, region_id=region_id))
        self.add_component(ResourceComponent(divine_power=10.0, faith=5.0))


class Building(Entity):
    """Represents a building."""
    
    def __init__(self, building_id: str, name: str, building_type: str, region_id: str, owner_id: str):
        super().__init__(entity_id=building_id, name=name)
        self.add_component(BuildingComponent(building_type=building_type))
        self.add_component(PositionComponent(region_id=region_id))
        self.add_component(FactionComponent(deity_id=owner_id))
        self.add_component(StatsComponent())


class Unit(Entity):
    """Represents a game unit."""
    
    def __init__(self, unit_id: str, name: str, unit_type: str, owner_id: str, region_id: str = ""):
        super().__init__(entity_id=unit_id, name=name)
        self.add_component(UnitComponent(unit_type=unit_type))
        self.add_component(FactionComponent(deity_id=owner_id))
        self.add_component(PositionComponent(region_id=region_id))
        self.add_component(StatsComponent())


# ============================================================================
# Entity Manager
# ============================================================================

class EntityManager:
    """Manages all entities in the game."""
    
    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._entity_index: Dict[str, List[str]] = {}  # index by component type
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the manager."""
        self._entities[entity.id] = entity
        self._update_index(entity)
    
    def remove_entity(self, entity_id: str) -> Optional[Entity]:
        """Remove an entity by ID."""
        entity = self._entities.pop(entity_id, None)
        if entity:
            self._remove_from_index(entity)
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self._entities.get(entity_id)
    
    def get_all_entities(self) -> List[Entity]:
        """Get all entities."""
        return list(self._entities.values())
    
    def find_entities_by_component(self, component_type: str) -> List[Entity]:
        """Find all entities with a specific component type."""
        entity_ids = self._entity_index.get(component_type, [])
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]
    
    def find_entities_by_faction(self, faction_id: str) -> List[Entity]:
        """Find all entities belonging to a faction."""
        results = []
        for entity in self._entities.values():
            faction = entity.get_component('FactionComponent')
            if faction and faction.faction_id == faction_id:
                results.append(entity)
        return results
    
    def find_entities_by_deity(self, deity_id: str) -> List[Entity]:
        """Find all entities belonging to a deity."""
        results = []
        for entity in self._entities.values():
            faction = entity.get_component('FactionComponent')
            if faction and faction.deity_id == deity_id:
                results.append(entity)
        return results
    
    def _update_index(self, entity: Entity) -> None:
        """Update the component index for an entity."""
        for comp_type in entity.components.keys():
            if comp_type not in self._entity_index:
                self._entity_index[comp_type] = []
            if entity.id not in self._entity_index[comp_type]:
                self._entity_index[comp_type].append(entity.id)
    
    def _remove_from_index(self, entity: Entity) -> None:
        """Remove entity from the index."""
        for comp_type in entity.components.keys():
            if comp_type in self._entity_index:
                if entity.id in self._entity_index[comp_type]:
                    self._entity_index[comp_type].remove(entity.id)
    
    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()
        self._entity_index.clear()
    
    def __len__(self) -> int:
        return len(self._entities)
