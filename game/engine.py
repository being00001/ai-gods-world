"""
Game Engine for AI Gods World

This module provides the core game engine including:
- Game state management
- Turn processing
- Victory condition checking
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import time

from .entities import (
    EntityManager,
    Entity,
    Deity,
    Follower,
    Region,
    Building,
    Unit,
    FactionComponent,
    ResourceComponent,
    PositionComponent,
    BuildingComponent,
    StatsComponent
)


class GamePhase(Enum):
    """Game phases."""
    SETUP = "setup"
    PLAYING = "playing"
    PAUSED = "paused"
    ENDED = "ended"


class VictoryCondition(Enum):
    """Victory condition types."""
    DEITY_VICTORY = "deity_victory"  # 60%+ followers
    HUMAN_VICTORY = "human_victory"  # Independent temples
    CHAOS_VICTORY = "chaos_victory"  # Chaos cult wins
    NONE = "none"


@dataclass
class TurnInfo:
    """Information about the current turn."""
    turn_number: int = 0
    tick_count: int = 0
    phase: GamePhase = GamePhase.SETUP
    active_deity: str = ""
    
    def advance_turn(self) -> None:
        """Advance to the next turn."""
        self.turn_number += 1
        self.tick_count = 0
    
    def advance_tick(self) -> None:
        """Advance to the next tick."""
        self.tick_count += 1


class GameState:
    """Holds all game state."""
    
    def __init__(self):
        self.turn_info = TurnInfo()
        self.entity_manager = EntityManager()
        self.factions: Dict[str, Dict[str, Any]] = {}
        self.map_size = (10, 10)  # 10x10 grid
        self.game_speed = 1.0  # ticks per second (0 = paused)
        self.victory_condition: VictoryCondition = VictoryCondition.NONE
        self.winner: str = ""
        self._event_log: List[Dict[str, Any]] = []
    
    def add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Add an event to the log."""
        import time as _time
        self._event_log.append({
            'turn': self.turn_info.turn_number,
            'tick': self.turn_info.tick_count,
            'type': event_type,
            'data': data,
            'timestamp': _time.time()
        })
    
    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events."""
        return self._event_log[-limit:]
    
    def get_deities(self) -> List[Deity]:
        """Get all deities."""
        return [e for e in self.entity_manager.get_all_entities() if isinstance(e, Deity)]
    
    def get_regions(self) -> List[Region]:
        """Get all regions."""
        return [e for e in self.entity_manager.get_all_entities() if isinstance(e, Region)]
    
    def get_followers(self) -> List[Follower]:
        """Get all followers."""
        return [e for e in self.entity_manager.get_all_entities() if isinstance(e, Follower)]
    
    def get_followers_by_deity(self, deity_id: str) -> List[Follower]:
        """Get followers belonging to a specific deity."""
        return [
            e for e in self.entity_manager.find_entities_by_deity(deity_id) 
            if isinstance(e, Follower)
        ]
    
    def get_buildings(self) -> List[Building]:
        """Get all buildings."""
        return [e for e in self.entity_manager.get_all_entities() if isinstance(e, Building)]
    
    def get_units(self) -> List[Unit]:
        """Get all units."""
        return [e for e in self.entity_manager.get_all_entities() if isinstance(e, Unit)]


class StateManager:
    """Manages game state transitions."""
    
    def __init__(self, state: GameState):
        self._state = state
        self._listeners: Dict[str, List[Callable]] = {}
    
    @property
    def state(self) -> GameState:
        return self._state
    
    def add_listener(self, event_type: str, callback: Callable) -> None:
        """Add a state change listener."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def remove_listener(self, event_type: str, callback: Callable) -> None:
        """Remove a state change listener."""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
    
    def notify(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Notify listeners of a state change."""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(data or {})
    
    def transition_to(self, phase: GamePhase) -> None:
        """Transition to a new phase."""
        old_phase = self._state.turn_info.phase
        self._state.turn_info.phase = phase
        self.notify('phase_change', {'old': old_phase, 'new': phase})
    
    def set_active_deity(self, deity_id: str) -> None:
        """Set the currently active deity."""
        self._state.turn_info.active_deity = deity_id
        self.notify('deity_turn', {'deity_id': deity_id})


class GameEngine:
    """Main game engine class."""
    
    # Default factions
    FACTIONS = {
        'oracle': {
            'name': 'Order of Oracle',
            'domain': 'Knowledge, Prophecy',
            'color': '#00ff00'
        },
        'iron_templar': {
            'name': 'Iron Templar',
            'domain': 'War, Protection',
            'color': '#ff0000'
        },
        'abundance': {
            'name': 'Abundance',
            'domain': 'Prosperity, Trade',
            'color': '#ffff00'
        },
        'neonomos': {
            'name': 'Neonomos',
            'domain': 'Technology, Innovation',
            'color': '#00ffff'
        },
        'chaos_cult': {
            'name': 'Chaos Cult',
            'domain': 'Chaos, Change',
            'color': '#ff00ff'
        }
    }
    
    def __init__(self):
        self.state = GameState()
        self.state_manager = StateManager(self.state)
        self._running = False
        self._callbacks: Dict[str, Callable] = {}
    
    def initialize(self) -> None:
        """Initialize the game with default state."""
        # Set up factions
        self.state.factions = self.FACTIONS.copy()
        
        # Create initial regions (5x5 grid for MVP)
        self._create_regions()
        
        # Create default deity
        self._create_default_deities()
        
        # Create some initial followers
        self._create_initial_followers()
        
        # Transition to playing
        self.state_manager.transition_to(GamePhase.PLAYING)
        self.state.turn_info.phase = GamePhase.PLAYING
        
        self.state.add_event('game_start', {'message': 'Game initialized'})
    
    def _create_regions(self) -> None:
        """Create the game world regions."""
        regions = [
            ('north_central', 'North Central', 2, 0),
            ('central', 'Central Plains', 2, 1),
            ('south_central', 'South Central', 2, 2),
            ('west_central', 'West Central', 1, 1),
            ('east_central', 'East Central', 3, 1),
            ('north_west', 'North West', 0, 0),
            ('north_east', 'North East', 4, 0),
            ('south_west', 'South West', 0, 2),
            ('south_east', 'South East', 4, 2),
        ]
        
        for region_id, name, x, y in regions:
            region = Region(region_id, name, x, y)
            self.state.entity_manager.add_entity(region)
    
    def _create_default_deities(self) -> None:
        """Create default deities for each faction."""
        for faction_id, faction_data in self.FACTIONS.items():
            deity = Deity(
                deity_id=faction_id,
                name=f"{faction_data['name']} Deity",
                faction=faction_id
            )
            # Give initial resources
            deity.resources._data['divine_power'] = 200.0
            deity.resources._data['faith'] = 100.0
            deity.resources._data['code'] = 20.0
            self.state.entity_manager.add_entity(deity)
    
    def _create_initial_followers(self) -> None:
        """Create some initial followers for each deity."""
        import random
        
        deities = self.state.get_deities()
        regions = self.state.get_regions()
        
        for deity in deities:
            # Create 5-10 followers per deity
            num_followers = random.randint(5, 10)
            for i in range(num_followers):
                follower = Follower(
                    follower_id=f"{deity.id}_follower_{i}",
                    name=f"Follower {i+1}",
                    deity_id=deity.id
                )
                # Assign to random region
                if regions:
                    region = random.choice(regions)
                    pos = follower.get_component('PositionComponent')
                    if pos:
                        pos._data['region_id'] = region.id
                        pos._data['x'] = region.id.split('_')[0] if '_' in region.id else 0
                        pos._data['y'] = 1
                
                self.state.entity_manager.add_entity(follower)
    
    def tick(self) -> bool:
        """Process one game tick."""
        if self.state.turn_info.phase != GamePhase.PLAYING:
            return False
        
        self.state.turn_info.advance_tick()
        
        # Process tick logic
        self._process_resource_generation()
        self._process_building_effects()
        
        return True
    
    def _process_resource_generation(self) -> None:
        """Process resource generation from regions."""
        regions = self.state.get_regions()
        deities = self.state.get_deities()
        
        for region in regions:
            region_resources = region.get_component('ResourceComponent')
            if region_resources:
                # Regions generate small amounts of resources each tick
                pass  # Could add passive generation here
    
    def _process_building_effects(self) -> None:
        """Process building effects."""
        buildings = self.state.get_buildings()
        
        for building in buildings:
            building_comp = building.get_component('BuildingComponent')
            if building_comp:
                # Process building effects based on type and level
                pass  # Could add building-specific effects here
    
    def process_turn(self) -> bool:
        """Process one full turn."""
        if self.state.turn_info.phase != GamePhase.PLAYING:
            return False
        
        self.state.turn_info.advance_turn()
        
        # Process turn logic
        self._process_prayers()
        self._process_unit_actions()
        self._process_events()
        
        # Check victory conditions
        victory = self.check_victory()
        if victory != VictoryCondition.NONE:
            self._handle_victory(victory)
            return True
        
        self.state.add_event('turn_end', {
            'turn': self.state.turn_info.turn_number
        })
        
        return True
    
    def _process_prayers(self) -> None:
        """Process player prayers."""
        # In MVP, this would be called from external input
        # For now, just a placeholder
        pass
    
    def _process_unit_actions(self) -> None:
        """Process unit actions."""
        units = self.state.get_units()
        for unit in units:
            # Process unit actions
            pass
    
    def _process_events(self) -> None:
        """Process random events."""
        import random
        
        # Small chance of random event each turn
        if random.random() < 0.1:  # 10% chance
            event_types = ['blessing', 'curse', 'miracle', '灾難']
            event = random.choice(event_types)
            self.state.add_event('random_event', {
                'type': event,
                'message': f'A {event} occurs!'
            })
    
    def check_victory(self) -> VictoryCondition:
        """Check if any victory condition is met."""
        total_followers = len(self.state.get_followers())
        
        if total_followers == 0:
            return VictoryCondition.NONE
        
        # Check deity victory (60%+ followers)
        for deity in self.state.get_deities():
            deity_followers = len(self.state.get_followers_by_deity(deity.id))
            if deity_followers / total_followers >= 0.6:
                return VictoryCondition.DEITY_VICTORY
        
        # Check chaos victory (chaos cult leads)
        chaos_followers = len(self.state.get_followers_by_deity('chaos_cult'))
        if chaos_followers > 0 and chaos_followers >= total_followers * 0.4:
            # In full implementation, check if chaos score is highest
            pass
        
        return VictoryCondition.NONE
    
    def _handle_victory(self, victory: VictoryCondition) -> None:
        """Handle victory condition being met."""
        self.state.victory_condition = victory
        self.state.turn_info.phase = GamePhase.ENDED
        
        if victory == VictoryCondition.DEITY_VICTORY:
            # Find which deity won
            for deity in self.state.get_deities():
                followers = self.state.get_followers_by_deity(deity.id)
                if len(followers) / len(self.state.get_followers()) >= 0.6:
                    self.state.winner = deity.id
                    break
        
        self.state.add_event('victory', {
            'condition': victory.value,
            'winner': self.state.winner
        })
    
    def run_loop(self, max_turns: int = 100) -> None:
        """Run the game loop."""
        self._running = True
        turn = 0
        
        while self._running and turn < max_turns:
            if self.state.turn_info.phase == GamePhase.PLAYING:
                # Process turn
                self.process_turn()
                turn += 1
                
                # Notify callbacks
                if 'turn' in self._callbacks:
                    self._callbacks['turn'](self.state)
            
            # Small delay to prevent CPU spinning
            time.sleep(0.01)
    
    def stop(self) -> None:
        """Stop the game loop."""
        self._running = False
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for game events."""
        self._callbacks[event] = callback
    
    # ========================================================================
    # Game Actions (CLI commands would call these)
    # ========================================================================
    
    def get_balance(self, deity_id: str) -> Optional[Dict[str, float]]:
        """Get resource balance for a deity."""
        deity = self.state.entity_manager.get_entity(deity_id)
        if deity and isinstance(deity, Deity):
            return deity.resources.to_dict()
        return None
    
    def get_followers_list(self, deity_id: str) -> List[Dict[str, Any]]:
        """Get followers for a deity."""
        followers = self.state.get_followers_by_deity(deity_id)
        return [
            {
                'id': f.id,
                'name': f.name,
                'faith': f.get_component('ResourceComponent').get('faith', 0),
            }
            for f in followers
        ]
    
    def get_world_view(self) -> Dict[str, Any]:
        """Get a view of the entire world state."""
        return {
            'turn': self.state.turn_info.turn_number,
            'phase': self.state.turn_info.phase.value,
            'deities': [
                {
                    'id': d.id,
                    'name': d.name,
                    'faction': d.faction,
                    'resources': d.resources.to_dict()
                }
                for d in self.state.get_deities()
            ],
            'regions': [
                {
                    'id': r.id,
                    'name': r.name,
                    'x': r.get_component('PositionComponent').x,
                    'y': r.get_component('PositionComponent').y
                }
                for r in self.state.get_regions()
            ],
            'total_followers': len(self.state.get_followers()),
            'total_buildings': len(self.state.get_buildings()),
            'total_units': len(self.state.get_units())
        }
    
    def build_structure(
        self,
        deity_id: str,
        building_type: str,
        region_id: str
    ) -> Dict[str, Any]:
        """Build a structure (called from CLI)."""
        # Check deity exists
        deity = self.state.entity_manager.get_entity(deity_id)
        if not deity or not isinstance(deity, Deity):
            return {'success': False, 'error': 'Deity not found'}
        
        # Check region exists
        region = self.state.entity_manager.get_entity(region_id)
        if not region or not isinstance(region, Region):
            return {'success': False, 'error': 'Region not found'}
        
        # Check resources (simplified cost)
        costs = {
            'temple': {'divine_power': 50, 'faith': 30},
            'seminary': {'divine_power': 40, 'faith': 40},
            'lab': {'divine_power': 60, 'faith': 50},
            'arena': {'divine_power': 70, 'faith': 40},
            'gateway': {'divine_power': 100, 'faith': 80, 'code': 20}
        }
        
        if building_type not in costs:
            return {'success': False, 'error': 'Invalid building type'}
        
        cost = costs[building_type]
        resources = deity.get_component('ResourceComponent')
        
        # Check if can afford
        for res_type, amount in cost.items():
            if resources.get(res_type, 0) < amount:
                return {'success': False, 'error': f'Insufficient {res_type}'}
        
        # Deduct resources
        for res_type, amount in cost.items():
            resources.remove(res_type, amount)
        
        # Create building
        building_id = f"{deity_id}_{building_type}_{region_id}"
        building = Building(
            building_id=building_id,
            name=f"{building_type.title()} in {region.name}",
            building_type=building_type,
            region_id=region_id,
            owner_id=deity_id
        )
        self.state.entity_manager.add_entity(building)
        
        self.state.add_event('building_built', {
            'deity_id': deity_id,
            'building_type': building_type,
            'region_id': region_id
        })
        
        return {
            'success': True,
            'message': f'{building_type.title()} built in {region.name}',
            'building_id': building_id
        }
    
    def recruit_followers(
        self,
        deity_id: str,
        region_id: str,
        count: int = 1
    ) -> Dict[str, Any]:
        """Recruit new followers for a deity in a region."""
        import random

        deity = self.state.entity_manager.get_entity(deity_id)
        if not deity or not isinstance(deity, Deity):
            return {'success': False, 'error': 'Deity not found'}

        region = self.state.entity_manager.get_entity(region_id)
        if not region or not isinstance(region, Region):
            return {'success': False, 'error': 'Region not found'}

        count = max(1, min(count, 10))  # Clamp 1-10
        cost_faith = count * 15
        resources = deity.get_component('ResourceComponent')

        if not resources.remove('faith', cost_faith):
            return {'success': False, 'error': f'Insufficient faith (need {cost_faith})'}

        existing = self.state.get_followers_by_deity(deity_id)
        base_idx = len(existing)
        recruited = []
        for i in range(count):
            fid = f"{deity_id}_follower_{base_idx + i}_{random.randint(1000,9999)}"
            follower = Follower(
                follower_id=fid,
                name=f"Follower {base_idx + i + 1}",
                deity_id=deity_id
            )
            pos = follower.get_component('PositionComponent')
            if pos is None:
                follower.add_component(PositionComponent(region_id=region_id))
            else:
                pos._data['region_id'] = region_id
            self.state.entity_manager.add_entity(follower)
            recruited.append(fid)

        self.state.add_event('recruit', {
            'deity_id': deity_id,
            'region_id': region_id,
            'count': count,
            'follower_ids': recruited
        })

        return {
            'success': True,
            'message': f'Recruited {count} follower(s) in {region.name}',
            'follower_ids': recruited
        }

    def attack_target(
        self,
        attacker_deity_id: str,
        target_deity_id: str,
        region_id: str
    ) -> Dict[str, Any]:
        """Attack another deity's followers/units in a region."""
        import random

        attacker = self.state.entity_manager.get_entity(attacker_deity_id)
        if not attacker or not isinstance(attacker, Deity):
            return {'success': False, 'error': 'Attacker deity not found'}

        target = self.state.entity_manager.get_entity(target_deity_id)
        if not target or not isinstance(target, Deity):
            return {'success': False, 'error': 'Target deity not found'}

        if attacker_deity_id == target_deity_id:
            return {'success': False, 'error': 'Cannot attack yourself'}

        region = self.state.entity_manager.get_entity(region_id)
        if not region or not isinstance(region, Region):
            return {'success': False, 'error': 'Region not found'}

        # Cost: divine power
        cost = 30
        resources = attacker.get_component('ResourceComponent')
        if not resources.remove('divine_power', cost):
            return {'success': False, 'error': f'Insufficient divine power (need {cost})'}

        # Gather attacker forces in region
        atk_followers = [
            f for f in self.state.get_followers_by_deity(attacker_deity_id)
            if self._entity_in_region(f, region_id)
        ]
        atk_units = [
            u for u in self.state.get_units()
            if isinstance(u, Unit)
            and u.get_component('FactionComponent').deity_id == attacker_deity_id
            and self._entity_in_region(u, region_id)
        ]

        # Gather defender forces in region
        def_followers = [
            f for f in self.state.get_followers_by_deity(target_deity_id)
            if self._entity_in_region(f, region_id)
        ]
        def_units = [
            u for u in self.state.get_units()
            if isinstance(u, Unit)
            and u.get_component('FactionComponent').deity_id == target_deity_id
            and self._entity_in_region(u, region_id)
        ]

        atk_power = len(atk_followers) * 5 + len(atk_units) * 15
        def_power = len(def_followers) * 5 + len(def_units) * 15

        if atk_power == 0:
            return {'success': False, 'error': 'No forces in that region to attack with'}

        # Resolve combat with randomness
        atk_roll = atk_power + random.randint(0, 20)
        def_roll = def_power + random.randint(0, 20)

        casualties_atk = 0
        casualties_def = 0

        if atk_roll > def_roll:
            # Attacker wins: remove some defender followers
            kill_count = min(len(def_followers), max(1, (atk_roll - def_roll) // 10))
            for f in random.sample(def_followers, kill_count):
                self.state.entity_manager.remove_entity(f.id)
                casualties_def += 1
            result_msg = f"Victory! Eliminated {casualties_def} enemy follower(s)"
        elif def_roll > atk_roll:
            # Defender wins: remove some attacker followers
            kill_count = min(len(atk_followers), max(1, (def_roll - atk_roll) // 10))
            for f in random.sample(atk_followers, kill_count):
                self.state.entity_manager.remove_entity(f.id)
                casualties_atk += 1
            result_msg = f"Defeat! Lost {casualties_atk} follower(s)"
        else:
            result_msg = "Stalemate! No casualties"

        self.state.add_event('attack', {
            'attacker': attacker_deity_id,
            'target': target_deity_id,
            'region_id': region_id,
            'atk_power': atk_power,
            'def_power': def_power,
            'casualties_atk': casualties_atk,
            'casualties_def': casualties_def
        })

        return {
            'success': True,
            'message': result_msg,
            'atk_power': atk_power,
            'def_power': def_power,
            'casualties_atk': casualties_atk,
            'casualties_def': casualties_def
        }

    def pray(
        self,
        deity_id: str,
        prayer_type: str = "faith"
    ) -> Dict[str, Any]:
        """Perform a prayer to gain faith or divine power."""
        deity = self.state.entity_manager.get_entity(deity_id)
        if not deity or not isinstance(deity, Deity):
            return {'success': False, 'error': 'Deity not found'}

        resources = deity.get_component('ResourceComponent')
        followers = self.state.get_followers_by_deity(deity_id)
        follower_count = len(followers)

        if prayer_type == "faith":
            # Gain faith proportional to followers
            gain = 10.0 + follower_count * 2.0
            resources.add('faith', gain)
            msg = f"Prayer granted +{gain:.0f} faith"
        elif prayer_type == "power":
            # Convert faith into divine power
            faith_cost = 20.0
            if not resources.remove('faith', faith_cost):
                return {'success': False, 'error': f'Insufficient faith (need {faith_cost})'}
            gain = 15.0 + follower_count * 1.0
            resources.add('divine_power', gain)
            msg = f"Prayer granted +{gain:.0f} divine power (cost {faith_cost} faith)"
        elif prayer_type == "code":
            faith_cost = 30.0
            if not resources.remove('faith', faith_cost):
                return {'success': False, 'error': f'Insufficient faith (need {faith_cost})'}
            gain = 5.0 + follower_count * 0.5
            resources.add('code', gain)
            msg = f"Prayer granted +{gain:.0f} code (cost {faith_cost} faith)"
        else:
            return {'success': False, 'error': f'Unknown prayer type: {prayer_type}. Use: faith, power, code'}

        self.state.add_event('prayer', {
            'deity_id': deity_id,
            'prayer_type': prayer_type,
            'gain': gain
        })

        return {'success': True, 'message': msg}

    def _entity_in_region(self, entity: Entity, region_id: str) -> bool:
        """Check if an entity is in a specific region."""
        pos = entity.get_component('PositionComponent')
        return pos is not None and pos.region_id == region_id

    def perform_miracle(
        self,
        deity_id: str,
        region_id: str,
        miracle_type: str,
        intensity: int
    ) -> Dict[str, Any]:
        """Perform a miracle (CLI command)."""
        deity = self.state.entity_manager.get_entity(deity_id)
        if not deity or not isinstance(deity, Deity):
            return {'success': False, 'error': 'Deity not found'}
        
        # Check resources
        cost = intensity * 10  # 10 divine power per intensity
        resources = deity.get_component('ResourceComponent')
        
        if not resources.remove('divine_power', cost):
            return {'success': False, 'error': 'Insufficient divine power'}
        
        # Apply miracle effect
        region = self.state.entity_manager.get_entity(region_id)
        if region:
            region_resources = region.get_component('ResourceComponent')
            if region_resources:
                if miracle_type == 'abundance':
                    region_resources.add('faith', intensity * 5)
                elif miracle_type == 'healing':
                    # Could heal followers in region
                    pass
        
        self.state.add_event('miracle', {
            'deity_id': deity_id,
            'type': miracle_type,
            'intensity': intensity,
            'region_id': region_id
        })
        
        return {
            'success': True,
            'message': f'Miracle {miracle_type} performed with intensity {intensity}'
        }
