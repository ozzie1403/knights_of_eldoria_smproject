from typing import List, Optional, Dict, Set, Any
from dataclasses import dataclass
import random
import math
from src.core.grid import Grid
from src.core.entities.position import Position
from src.core.entities.treasure import Treasure, TreasureType
from src.core.entities.hunter import Hunter
from src.core.entities.knight import Knight
from src.core.entities.hideout import Hideout
from src.core.enums import EntityType, TreasureType, HunterSkill, KnightAction

class Simulation:
    def __init__(self, grid_size: int = 20, num_hunters: int = 3, num_treasures: int = 10, num_hideouts: int = 2):
        self.grid = Grid(grid_size)
        self.step_count = 0
        self.total_treasure_collected = 0
        self._nearest_cache: Dict[Position, Dict[str, Any]] = {}
        self.initialize_simulation(num_hunters, num_treasures, num_hideouts)

    def initialize_simulation(self, num_hunters: int, num_treasures: int, num_hideouts: int) -> None:
        """Initialize the simulation with hunters, treasures, and hideouts."""
        # Place hideouts first
        for _ in range(num_hideouts):
            pos = self.grid.get_random_empty_position()
            if pos:
                hideout = Hideout(pos)
                self.grid.add_entity(hideout)

        # Place hunters in hideouts
        for _ in range(num_hunters):
            if self.grid.hideouts:
                hideout = random.choice(self.grid.hideouts)
                if hideout.can_accommodate():
                    hunter = Hunter(hideout.position)
                    if self.grid.add_entity(hunter):
                        hideout.add_hunter(hunter)

        # Place treasures with proper type distribution
        treasure_types = [TreasureType.BRONZE] * 4 + [TreasureType.SILVER] * 3 + [TreasureType.GOLD] * 3
        for _ in range(num_treasures):
            pos = self.grid.get_random_empty_position()
            if pos:
                treasure_type = random.choice(treasure_types)
                treasure = Treasure(pos, treasure_type)
                self.grid.add_entity(treasure)

    def validate_state(self) -> bool:
        """Validate the current simulation state."""
        # Check if all entities are in the correct lists
        for pos, entity in self.grid.entities.items():
            if hasattr(entity, 'treasure_type') and entity not in self.grid.treasures:
                return False
            if hasattr(entity, 'stamina') and entity not in self.grid.hunters:
                return False
            if hasattr(entity, 'max_hunters') and entity not in self.grid.hideouts:
                return False
        return True

    def update_treasures(self) -> None:
        """Update all treasures in the simulation."""
        treasures_to_remove: List[Position] = []
        for treasure in self.grid.treasures[:]:  # Create a copy of the list
            try:
                treasure.decay()
                if treasure.is_depleted():
                    treasures_to_remove.append(treasure.position)
            except Exception as e:
                print(f"Error updating treasure at {treasure.position}: {e}")
                treasures_to_remove.append(treasure.position)
        
        for pos in treasures_to_remove:
            try:
                self.grid.remove_entity(pos)
            except Exception as e:
                print(f"Error removing treasure at {pos}: {e}")

    def update_hunters(self) -> None:
        """Update all hunters in the simulation."""
        hunters_to_remove: List[Position] = []
        
        for hunter in self.grid.hunters[:]:  # Create a copy of the list
            try:
                if not hunter.can_move():
                    if hunter.is_collapsed and hunter.steps_since_collapse >= 3:
                        hunters_to_remove.append(hunter.position)
                    continue

                # Check if hunter needs to rest
                if hunter.needs_rest():
                    nearest_hideout = self.find_nearest_hideout(hunter.position)
                    if nearest_hideout:
                        self.move_towards(hunter, nearest_hideout.position)
                        if hunter.position == nearest_hideout.position:
                            hunter.rest()
                            continue

                # If carrying treasure, move to nearest hideout
                if hunter.carrying_treasure:
                    nearest_hideout = self.find_nearest_hideout(hunter.position)
                    if nearest_hideout:
                        self.move_towards(hunter, nearest_hideout.position)
                        if hunter.position == nearest_hideout.position:
                            hideout = self.grid.get_entity_at(nearest_hideout.position)
                            if isinstance(hideout, Hideout):
                                hideout.store_treasure(hunter.deposit_treasure())
                                self.total_treasure_collected += 1
                else:
                    # Look for nearest treasure
                    nearest_treasure = self.find_nearest_treasure(hunter.position)
                    if nearest_treasure:
                        self.move_towards(hunter, nearest_treasure.position)
                        if hunter.position == nearest_treasure.position:
                            treasure = self.grid.get_entity_at(nearest_treasure.position)
                            if isinstance(treasure, Treasure):
                                hunter.pick_up_treasure(treasure)
                                self.grid.remove_entity(treasure.position)
            except Exception as e:
                print(f"Error updating hunter at {hunter.position}: {e}")
                hunters_to_remove.append(hunter.position)

        # Remove collapsed hunters
        for pos in hunters_to_remove:
            try:
                self.grid.remove_entity(pos)
            except Exception as e:
                print(f"Error removing hunter at {pos}: {e}")

    def update_knights(self) -> None:
        """Update all knights in the simulation."""
        for knight in self.grid.knights:
            if knight.needs_rest():
                knight.rest()
                continue

            # Detect hunters within 3 cells
            knight.detect_hunters(self.grid.hunters)
            target = knight.choose_target()
            
            if target:
                action = knight.choose_action(target)
                
                if action == KnightAction.PURSUE:
                    self.move_towards(target, target.position)
                    if target.position == target.position:
                        knight.interact_with_hunter(target)
                elif action == KnightAction.PATROL:
                    # Move randomly
                    adjacent = self.grid.get_adjacent_positions(target.position)
                    if adjacent:
                        new_pos = random.choice(adjacent)
                        if not self.grid.get_entity_at(new_pos):
                            target.move(new_pos)

    def move_towards(self, hunter: Hunter, target: Position) -> None:
        """Move a hunter towards a target position."""
        try:
            current_pos = hunter.position
            best_move = None
            min_dist = float('inf')

            for new_pos in self.grid.get_adjacent_positions(current_pos):
                if self.grid.get_entity_at(new_pos):
                    continue
                dist = new_pos.distance_to(target)
                if dist < min_dist:
                    min_dist = dist
                    best_move = new_pos

            if best_move:
                # Remove hunter from current position
                if current_pos in self.grid.entities:
                    self.grid.entities.pop(current_pos)
                
                # Move hunter to new position
                hunter.move(best_move)
                self.grid.entities[best_move] = hunter
        except Exception as e:
            print(f"Error moving hunter from {current_pos} to {target}: {e}")

    def find_nearest_hideout(self, position: Position) -> Optional[Hideout]:
        """Find the nearest hideout to a position."""
        if not self.grid.hideouts:
            return None
        try:
            return min(self.grid.hideouts, key=lambda h: position.distance_to(h.position))
        except Exception as e:
            print(f"Error finding nearest hideout to {position}: {e}")
            return None

    def find_nearest_treasure(self, position: Position) -> Optional[Treasure]:
        """Find the nearest treasure to a position."""
        if not self.grid.treasures:
            return None
        try:
            return min(self.grid.treasures, key=lambda t: position.distance_to(t.position))
        except Exception as e:
            print(f"Error finding nearest treasure to {position}: {e}")
            return None

    def step(self) -> bool:
        """Perform one simulation step. Returns False if simulation should end."""
        try:
            self.step_count += 1

            # Update all entities
            self.update_treasures()
            self.update_hunters()

            # Validate state after updates
            if not self.validate_state():
                print("Invalid simulation state detected!")
                return False

            # Check end conditions
            if not self.grid.treasures:
                print("Simulation ended: No more treasures to collect")
                return False

            if not self.grid.hunters:
                print("Simulation ended: All hunters eliminated")
                return False

            return True
        except Exception as e:
            print(f"Error in simulation step {self.step_count}: {e}")
            return False

    def get_state(self) -> Dict[str, Any]:
        """Return current simulation state for visualization."""
        try:
            return {
                'grid_size': self.grid.size,
                'step_count': self.step_count,
                'total_treasure_collected': self.total_treasure_collected,
                'treasures': [(t.position.x, t.position.y, t.treasure_type.name, t.value) for t in self.grid.treasures],
                'hunters': [(h.position.x, h.position.y, h.stamina, h.is_collapsed) for h in self.grid.hunters],
                'hideouts': [(h.position.x, h.position.y, len(h.hunters), len(h.stored_treasures)) for h in self.grid.hideouts]
            }
        except Exception as e:
            print(f"Error getting simulation state: {e}")
            return {
                'grid_size': self.grid.size,
                'step_count': self.step_count,
                'total_treasure_collected': self.total_treasure_collected,
                'treasures': [],
                'hunters': [],
                'hideouts': []
            }

    def __repr__(self) -> str:
        return f"Simulation(grid={self.grid}, hunters={len(self.grid.hunters)}, treasures={len(self.grid.treasures)}, hideouts={len(self.grid.hideouts)})" 