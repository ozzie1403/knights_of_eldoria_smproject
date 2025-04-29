import random
import math
from typing import List, Optional, Tuple, Dict, Set, Any
from dataclasses import dataclass
from src.backend.models.grid import Grid
from src.backend.models.entities import Position, Treasure, Hunter, Knight, Hideout, TreasureType, HunterSkill, KnightAction, CellType


class Simulation:
    def __init__(self, grid_size: int, num_hunters: int, num_knights: int, num_treasures: int, num_hideouts: int):
        self.grid = Grid(grid_size)
        self.initialize_simulation(num_hunters, num_knights, num_treasures, num_hideouts)
        self.step_count = 0
        self.total_treasure_collected = 0

    def initialize_simulation(self, num_hunters: int, num_knights: int, num_treasures: int, num_hideouts: int) -> None:
        # Place hideouts first
        for _ in range(num_hideouts):
            pos = self.grid.get_random_empty_position()
            if pos:
                self.grid.add_hideout(pos)

        # Place hunters in hideouts
        for _ in range(num_hunters):
            if self.grid.hideouts:
                hideout = random.choice(self.grid.hideouts)
                if hideout.can_accommodate():
                    hunter = self.grid.add_hunter(hideout.position, random.choice(list(HunterSkill)))
                    hideout.add_hunter(hunter)

        # Place knights
        for _ in range(num_knights):
            pos = self.grid.get_random_empty_position()
            if pos:
                self.grid.add_knight(pos)

        # Place treasures
        for _ in range(num_treasures):
            pos = self.grid.get_random_empty_position()
            if pos:
                treasure_type = random.choice(list(TreasureType))
                self.grid.add_treasure(pos, treasure_type)

    def update_treasures(self) -> None:
        for treasure in self.grid.treasures[:]:
            treasure.decay()
            if treasure.value <= 0:
                self.grid.remove_entity(treasure.position)

    def update_hunters(self) -> None:
        for hunter in self.grid.hunters[:]:
            if not hunter.can_move():
                if hunter.is_collapsed and hunter.steps_since_collapse >= 3:
                    self.grid.remove_entity(hunter.position)
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
            if hunter.carried_treasure:
                nearest_hideout = self.find_nearest_hideout(hunter.position)
                if nearest_hideout:
                    self.move_towards(hunter, nearest_hideout.position)
                    if hunter.position == nearest_hideout.position:
                        hideout = self.grid.position_to_entity[nearest_hideout.position]
                        hideout.stored_treasures.append(hunter.carried_treasure)
                        hunter.carried_treasure = None
                        self.total_treasure_collected += 1
            else:
                # Find nearest treasure using known positions
                nearest_treasure = self.find_nearest_known_treasure(hunter)
                if not nearest_treasure:
                    nearest_treasure = self.find_nearest_treasure(hunter.position)
                    if nearest_treasure:
                        hunter.known_treasures.append(nearest_treasure)

                if nearest_treasure:
                    self.move_towards(hunter, nearest_treasure)
                    if hunter.position == nearest_treasure:
                        treasure = self.grid.position_to_entity[nearest_treasure]
                        hunter.carried_treasure = treasure
                        self.grid.remove_entity(treasure.position)

            # Check for nearby knights
            nearby_knights = self.find_knights_in_range(hunter.position, 3)
            for knight_pos in nearby_knights:
                if knight_pos not in hunter.known_knights:
                    hunter.known_knights.append(knight_pos)

    def update_knights(self) -> None:
        for knight in self.grid.knights:
            if knight.needs_rest():
                nearest_hideout = self.find_nearest_hideout(knight.position)
                if nearest_hideout:
                    self.move_towards(knight, nearest_hideout.position)
                    if knight.position == nearest_hideout.position:
                        knight.rest()
                continue

            # Look for hunters in range
            nearby_hunters = self.find_hunters_in_range(knight.position, 3)
            if nearby_hunters:
                target_hunter = random.choice(nearby_hunters)
                knight.detect_hunter(target_hunter.position)
                self.move_towards(knight, target_hunter.position)
                if knight.position == target_hunter.position:
                    self.handle_knight_hunter_interaction(knight, target_hunter)
            else:
                # Patrol known hunter positions
                if knight.last_known_hunter_positions:
                    target_pos = random.choice(knight.last_known_hunter_positions)
                    self.move_towards(knight, target_pos)
                    if knight.position == target_pos:
                        knight.last_known_hunter_positions.remove(target_pos)

    def find_nearest_hideout(self, position: Position) -> Optional[Position]:
        nearest = None
        min_dist = float('inf')
        for hideout in self.grid.hideouts:
            dist = position.distance_to(hideout.position)
            if dist < min_dist:
                min_dist = dist
                nearest = hideout.position
        return nearest

    def find_nearest_treasure(self, position: Position) -> Optional[Position]:
        nearest = None
        min_dist = float('inf')
        for treasure in self.grid.treasures:
            dist = position.distance_to(treasure.position)
            if dist < min_dist:
                min_dist = dist
                nearest = treasure.position
        return nearest

    def find_nearest_known_treasure(self, hunter: Hunter) -> Optional[Position]:
        nearest = None
        min_dist = float('inf')
        for treasure_pos in hunter.known_treasures:
            if treasure_pos in self.grid.position_to_entity:
                dist = hunter.position.distance_to(treasure_pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest = treasure_pos
        return nearest

    def find_hunters_in_range(self, position: Position, radius: int) -> List[Hunter]:
        hunters = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                check_pos = self.grid.wrap_position(Position(position.x + dx, position.y + dy))
                if check_pos in self.grid.position_to_entity:
                    entity = self.grid.position_to_entity[check_pos]
                    if isinstance(entity, Hunter):
                        hunters.append(entity)
        return hunters

    def find_knights_in_range(self, position: Position, radius: int) -> List[Position]:
        knights = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                check_pos = self.grid.wrap_position(Position(position.x + dx, position.y + dy))
                if check_pos in self.grid.position_to_entity:
                    entity = self.grid.position_to_entity[check_pos]
                    if isinstance(entity, Knight):
                        knights.append(check_pos)
        return knights

    def move_towards(self, entity: Hunter | Knight, target: Position) -> None:
        current_pos = entity.position
        best_move = None
        min_dist = float('inf')

        for new_pos in self.grid.get_adjacent_positions(current_pos):
            dist = new_pos.distance_to(target)
            if dist < min_dist:
                min_dist = dist
                best_move = new_pos

        if best_move and self.grid.get_cell_type(best_move) == CellType.EMPTY:
            self.grid.set_cell_type(current_pos, CellType.EMPTY)
            entity.move(best_move)
            self.grid.set_cell_type(best_move, CellType.HUNTER if isinstance(entity, Hunter) else CellType.KNIGHT)
            self.grid.position_to_entity[best_move] = entity

    def handle_knight_hunter_interaction(self, knight: Knight, hunter: Hunter) -> None:
        action = knight.choose_action(hunter)
        if action == KnightAction.DETAIN:
            hunter.stamina = max(0, hunter.stamina - 5)
        elif action == KnightAction.CHALLENGE:
            hunter.stamina = max(0, hunter.stamina - 20)

        if hunter.carried_treasure:
            treasure_pos = hunter.carried_treasure.position
            hunter.known_treasures.append(treasure_pos)
            hunter.carried_treasure = None

        if hunter.stamina <= 0:
            hunter.collapse()

    def step(self) -> bool:
        """Perform one simulation step. Returns False if simulation should end."""
        self.step_count += 1

        # Update all entities
        self.update_treasures()
        self.update_hunters()
        self.update_knights()

        # Try to recruit new hunters
        for hideout in self.grid.hideouts:
            new_hunter = hideout.try_recruit_hunter(self.grid.size)
            if new_hunter:
                self.grid.add_hunter(new_hunter.position, new_hunter.skill)
                hideout.add_hunter(new_hunter)

        # Check end conditions
        if not self.grid.treasures:
            return False  # No more treasure to collect

        if not self.grid.hunters:
            return False  # All hunters eliminated

        return True

    def get_state(self) -> dict:
        """Return current simulation state for visualization."""
        return {
            'grid_size': self.grid.size,
            'step_count': self.step_count,
            'total_treasure_collected': self.total_treasure_collected,
            'treasures': [(t.position.x, t.position.y, t.treasure_type.name, t.value) for t in self.grid.treasures],
            'hunters': [(h.position.x, h.position.y, h.skill.name, h.stamina, h.is_collapsed) for h in self.grid.hunters],
            'knights': [(k.position.x, k.position.y, k.energy, k.is_resting) for k in self.grid.knights],
            'hideouts': [(h.position.x, h.position.y, len(h.hunters), len(h.stored_treasures)) for h in self.grid.hideouts]
        }