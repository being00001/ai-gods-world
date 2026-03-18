#!/usr/bin/env python3
"""
Main entry point for AI Gods World game.

This module provides a basic CLI interface to interact with the game engine.
"""

import sys
import cmd
import argparse
import json
from typing import Optional

from .engine import GameEngine, GamePhase, VictoryCondition
from .entities import BuildingComponent


class GameCLI(cmd.Cmd):
    """CLI interface for the game."""
    
    intro = """
╔═══════════════════════════════════════════════════════════════╗
║                   🏛️ AI GODS WORLD 🏛️                          ║
║                  Minimum Viable Game Engine                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Commands:                                                     ║
║    /world view     - View world state                         ║
║    /balance        - Check your resources                     ║
║    /followers      - List your followers                      ║
║    /build          - Build a structure                         ║
║    /recruit        - Recruit followers                          ║
║    /attack         - Attack another deity                      ║
║    /pray           - Pray for resources                        ║
║    /miracle        - Perform a miracle                         ║
║    /turn           - Advance one turn                          ║
║    /help           - Show this help                            ║
║    /quit           - Exit the game                             ║
╚═══════════════════════════════════════════════════════════════╝
"""
    
    prompt = "AI Gods World > "
    
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.engine.initialize()
        self.current_deity = "oracle"  # Default deity
        self._running = True
    
    def run(self):
        """Run the game loop."""
        print(self.intro)
        self._print_status()
        
        while self._running:
            try:
                command = input(self.prompt).strip()
                if not command:
                    continue
                
                self._process_command(command)
                
            except KeyboardInterrupt:
                print("\nUse /quit to exit the game.")
            except EOFError:
                break
        
        print("Thanks for playing AI Gods World!")
    
    def _process_command(self, command: str):
        """Process a command."""
        # Handle commands with or without /
        if command.startswith('/'):
            command = command[1:]
        
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in ['quit', 'exit']:
            self._running = False
        
        elif cmd in ['help', 'h', '?']:
            print(self.intro)
        
        elif cmd in ['world', 'view']:
            self._cmd_world_view()
        
        elif cmd in ['balance', 'bal']:
            self._cmd_balance()
        
        elif cmd in ['followers', 'fl']:
            self._cmd_followers()
        
        elif cmd in ['recruit', 'rec']:
            self._cmd_recruit(args)

        elif cmd in ['attack', 'atk']:
            self._cmd_attack(args)

        elif cmd in ['pray', 'prayer']:
            self._cmd_pray(args)

        elif cmd in ['build', 'b']:
            self._cmd_build(args)
        
        elif cmd in ['miracle', 'mir']:
            self._cmd_miracle(args)
        
        elif cmd in ['turn', 'next', 't']:
            self._cmd_turn()
        
        elif cmd in ['regions', 'map']:
            self._cmd_regions()
        
        elif cmd in ['deities', 'gods']:
            self._cmd_deities()
        
        elif cmd in ['status', 'stat']:
            self._print_status()
        
        else:
            print(f"Unknown command: /{cmd}")
            print("Type /help for available commands.")
    
    def _print_status(self):
        """Print current game status."""
        world = self.engine.get_world_view()
        print(f"\n--- Turn {world['turn']} | Phase: {world['phase']} ---")
        print(f"Deities: {len(world['deities'])}")
        print(f"Regions: {len(world['regions'])}")
        print(f"Followers: {world['total_followers']}")
        print(f"Buildings: {world['total_buildings']}")
        print(f"Units: {world['total_units']}")
    
    def _cmd_world_view(self):
        """Show world view."""
        world = self.engine.get_world_view()
        print("\n" + "=" * 50)
        print("🌍 WORLD VIEW")
        print("=" * 50)
        print(f"Turn: {world['turn']}")
        print(f"Phase: {world['phase']}")
        
        print("\n--- Deities ---")
        for deity in world['deities']:
            print(f"  {deity['name']} ({deity['id']})")
            print(f"    Faction: {deity['faction']}")
            print(f"    Divine Power: {deity['resources']['divine_power']:.1f}")
            print(f"    Faith: {deity['resources']['faith']:.1f}")
            print(f"    Code: {deity['resources']['code']:.1f}")
            print()
        
        print(f"\n--- World Stats ---")
        print(f"Total Regions: {len(world['regions'])}")
        print(f"Total Followers: {world['total_followers']}")
        print(f"Total Buildings: {world['total_buildings']}")
        print(f"Total Units: {world['total_units']}")
    
    def _cmd_balance(self):
        """Show resource balance for current deity."""
        balance = self.engine.get_balance(self.current_deity)
        if balance:
            print(f"\n--- Resources for {self.current_deity} ---")
            print(f"  Divine Power: {balance['divine_power']:.1f}")
            print(f"  Faith: {balance['faith']:.1f}")
            print(f"  Code: {balance['code']:.1f}")
            print(f"  Entropy: {balance['entropy']:.1f}")
        else:
            print("Deity not found.")
    
    def _cmd_followers(self):
        """List followers of current deity."""
        followers = self.engine.get_followers_list(self.current_deity)
        print(f"\n--- Followers of {self.current_deity} ---")
        if followers:
            for f in followers:
                print(f"  - {f['name']} ({f['id']}) - Faith: {f['faith']:.1f}")
        else:
            print("  No followers yet.")
    
    def _cmd_recruit(self, args):
        """Recruit new followers."""
        if len(args) < 1:
            print("Usage: /recruit <region_id> [count]")
            print("  count: 1-10 (default: 1)")
            return

        region_id = args[0].lower()
        count = int(args[1]) if len(args) > 1 else 1

        result = self.engine.recruit_followers(
            deity_id=self.current_deity,
            region_id=region_id,
            count=count
        )

        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")

    def _cmd_attack(self, args):
        """Attack another deity's forces."""
        if len(args) < 2:
            print("Usage: /attack <target_deity_id> <region_id>")
            print("  target_deity_id: oracle, iron_templar, abundance, neonomos, chaos_cult")
            return

        target_deity_id = args[0].lower()
        region_id = args[1].lower()

        result = self.engine.attack_target(
            attacker_deity_id=self.current_deity,
            target_deity_id=target_deity_id,
            region_id=region_id
        )

        if result['success']:
            print(f"⚔️ {result['message']}")
            print(f"  Attack power: {result['atk_power']} vs Defense: {result['def_power']}")
        else:
            print(f"❌ Error: {result['error']}")

    def _cmd_pray(self, args):
        """Pray for resources."""
        prayer_type = args[0].lower() if args else "faith"

        result = self.engine.pray(
            deity_id=self.current_deity,
            prayer_type=prayer_type
        )

        if result['success']:
            print(f"🙏 {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")

    def _cmd_build(self, args):
        """Build a structure."""
        if len(args) < 2:
            print("Usage: /build <building_type> <region_id>")
            print(f"Building types: {', '.join(BuildingComponent.BUILDING_TYPES)}")
            print("Regions: north_central, central, south_central, west_central, east_central, etc.")
            return
        
        building_type = args[0].lower()
        region_id = args[1].lower()
        
        result = self.engine.build_structure(
            deity_id=self.current_deity,
            building_type=building_type,
            region_id=region_id
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    def _cmd_miracle(self, args):
        """Perform a miracle."""
        if len(args) < 2:
            print("Usage: /miracle <region_id> <type> [intensity]")
            print("Types: abundance, healing, protection")
            print("Intensity: 1-10 (default: 1)")
            return
        
        region_id = args[0].lower()
        miracle_type = args[1].lower()
        intensity = int(args[2]) if len(args) > 2 else 1
        
        result = self.engine.perform_miracle(
            deity_id=self.current_deity,
            region_id=region_id,
            miracle_type=miracle_type,
            intensity=intensity
        )
        
        if result['success']:
            print(f"✨ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    def _cmd_turn(self):
        """Advance one turn."""
        self.engine.process_turn()
        self._print_status()
        
        # Check for victory
        if self.engine.state.turn_info.phase == GamePhase.ENDED:
            print(f"\n🎉 GAME OVER!")
            print(f"Victory Condition: {self.engine.state.victory_condition.value}")
            print(f"Winner: {self.engine.state.winner}")
    
    def _cmd_regions(self):
        """List all regions."""
        world = self.engine.get_world_view()
        print("\n--- Regions ---")
        for region in world['regions']:
            print(f"  {region['name']} ({region['id']}) - Position: ({region['x']}, {region['y']})")
    
    def _cmd_deities(self):
        """List all deities."""
        world = self.engine.get_world_view()
        print("\n--- Deities ---")
        for deity in world['deities']:
            print(f"  {deity['name']} - {deity['faction']}")


def run_game():
    """Run the game."""
    cli = GameCLI()
    cli.run()


def run_automated(num_turns: int = 10):
    """Run the game automatically for testing."""
    engine = GameEngine()
    engine.initialize()
    
    print("=== AI Gods World - Automated Run ===")
    print(f"Running {num_turns} turns...\n")
    
    for turn in range(num_turns):
        print(f"--- Turn {turn + 1} ---")
        
        # Process turn
        engine.process_turn()
        
        # Show some stats
        world = engine.get_world_view()
        print(f"  Followers: {world['total_followers']}")
        print(f"  Buildings: {world['total_buildings']}")
        
        # Show active deity resources
        for deity in world['deities'][:2]:  # First 2 deities
            print(f"  {deity['id']}: Power={deity['resources']['divine_power']:.0f}, Faith={deity['resources']['faith']:.0f}")
        
        print()
        
        # Check for game end
        if engine.state.turn_info.phase == GamePhase.ENDED:
            print(f"GAME OVER - {engine.state.victory_condition.value}")
            break
    
    print("=== Run Complete ===")


def run_command(command: str, args_str: str = "", deity: str = "oracle") -> str:
    """Run a single command and return JSON result. For LLM agent interaction."""
    engine = GameEngine()
    engine.initialize()

    args = args_str.split() if args_str else []
    result = None

    if command == "recruit":
        region_id = args[0] if len(args) > 0 else "central"
        count = int(args[1]) if len(args) > 1 else 1
        result = engine.recruit_followers(deity_id=deity, region_id=region_id, count=count)
    elif command == "attack":
        target = args[0] if len(args) > 0 else ""
        region_id = args[1] if len(args) > 1 else ""
        if not target or not region_id:
            result = {"success": False, "error": "Usage: --args 'target_deity region_id'"}
        else:
            result = engine.attack_target(attacker_deity_id=deity, target_deity_id=target, region_id=region_id)
    elif command == "pray":
        prayer_type = args[0] if args else "faith"
        result = engine.pray(deity_id=deity, prayer_type=prayer_type)
    elif command == "build":
        btype = args[0] if len(args) > 0 else ""
        region_id = args[1] if len(args) > 1 else ""
        if not btype or not region_id:
            result = {"success": False, "error": "Usage: --args 'building_type region_id'"}
        else:
            result = engine.build_structure(deity_id=deity, building_type=btype, region_id=region_id)
    elif command == "miracle":
        region_id = args[0] if len(args) > 0 else ""
        mtype = args[1] if len(args) > 1 else ""
        intensity = int(args[2]) if len(args) > 2 else 1
        if not region_id or not mtype:
            result = {"success": False, "error": "Usage: --args 'region_id type [intensity]'"}
        else:
            result = engine.perform_miracle(deity_id=deity, region_id=region_id, miracle_type=mtype, intensity=intensity)
    elif command == "balance":
        result = engine.get_balance(deity) or {"error": "Deity not found"}
    elif command == "world":
        result = engine.get_world_view()
    elif command == "followers":
        result = {"followers": engine.get_followers_list(deity)}
    else:
        result = {"success": False, "error": f"Unknown command: {command}"}

    return json.dumps(result, ensure_ascii=False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Gods World game")
    parser.add_argument('--auto', type=int, nargs='?', const=10, default=None,
                        help='Run automated mode for N turns (default: 10)')
    parser.add_argument('--command', '-c', type=str, default=None,
                        help='Execute a single command (recruit, attack, pray, build, miracle, balance, world, followers)')
    parser.add_argument('--args', '-a', type=str, default="",
                        help='Arguments for the command')
    parser.add_argument('--deity', '-d', type=str, default="oracle",
                        help='Deity ID to act as (default: oracle)')

    parsed = parser.parse_args()

    if parsed.command:
        print(run_command(parsed.command, parsed.args, parsed.deity))
    elif parsed.auto is not None:
        run_automated(parsed.auto)
    else:
        run_game()


if __name__ == '__main__':
    main()
