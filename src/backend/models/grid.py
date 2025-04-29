from typing import List, Optional, Tuple, Dict, Set, Any
import random
import math
from dataclasses import dataclass
from src.backend.models.entities import Position, Treasure, Hunter, Knight, Hideout, CellType, TreasureType, HunterSkill

class Grid:
    def __init__(self, size: int):
        self.size = size
        self.grid: List[List[CellType]] = [[CellType.EMPTY for _ in range(size)] for _ in range(size)]
        self.treasures: List[Treasure] = []
        self.hunters: List[Hunter] = []
        self.knights: List[Knight] = []
        self.hideouts: List[Hideout] = []
        self.position_to_entity: Dict[Position, object] = {}

    def wrap_position(self, position: Position) -> Position:
        """Wrap position around grid edges."""
        return Position(
            (position.x % self.size + self.size) % self.size,
            (position.y % self.size + self.size) % self.size
        )

    def get_adjacent_positions(self, position: Position) -> List[Position]:
        """Get all adjacent positions, including diagonals."""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_pos = self.wrap_position(Position(position.x + dx, position.y + dy))
                adjacent.append(new_pos)
        return adjacent

    def get_cell_type(self, position: Position) -> CellType:
        return self.grid[position.x][position.y]

    def set_cell_type(self, position: Position, cell_type: CellType) -> None:
        self.grid[position.x][position.y] = cell_type

    def add_treasure(self, position: Position, treasure_type: TreasureType) -> Treasure:
        treasure = Treasure(position, treasure_type)
        self.treasures.append(treasure)
        self.set_cell_type(position, CellType.TREASURE)
        self.position_to_entity[position] = treasure
        return treasure

    def add_hunter(self, position: Position, skill: HunterSkill) -> Hunter:
        hunter = Hunter(position, skill)
        self.hunters.append(hunter)
        self.set_cell_type(position, CellType.HUNTER)
        self.position_to_entity[position] = hunter
        return hunter

    def add_knight(self, position: Position) -> Knight:
        knight = Knight(position)
        self.knights.append(knight)
        self.set_cell_type(position, CellType.KNIGHT)
        self.position_to_entity[position] = knight
        return knight

    def add_hideout(self, position: Position) -> Hideout:
        hideout = Hideout(position)
        self.hideouts.append(hideout)
        self.set_cell_type(position, CellType.HIDEOUT)
        self.position_to_entity[position] = hideout
        return hideout

    def remove_entity(self, position: Position) -> None:
        entity = self.position_to_entity.get(position)
        if entity:
            if isinstance(entity, Treasure):
                self.treasures.remove(entity)
            elif isinstance(entity, Hunter):
                self.hunters.remove(entity)
            elif isinstance(entity, Knight):
                self.knights.remove(entity)
            elif isinstance(entity, Hideout):
                self.hideouts.remove(entity)
            self.set_cell_type(position, CellType.EMPTY)
            del self.position_to_entity[position]

    def get_entities_in_radius(self, position: Position, radius: int) -> List[Tuple[Position, object]]:
        """Get all entities within a given radius, including diagonals."""
        entities = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                check_pos = self.wrap_position(Position(position.x + dx, position.y + dy))
                if check_pos in self.position_to_entity:
                    entities.append((check_pos, self.position_to_entity[check_pos]))
        return entities

    def get_random_empty_position(self) -> Optional[Position]:
        """Get a random empty position on the grid."""
        empty_positions = []
        for x in range(self.size):
            for y in range(self.size):
                pos = Position(x, y)
                if self.get_cell_type(pos) == CellType.EMPTY:
                    empty_positions.append(pos)
        return random.choice(empty_positions) if empty_positions else None

    def is_position_valid(self, position: Position) -> bool:
        """Check if a position is within grid bounds."""
        return 0 <= position.x < self.size and 0 <= position.y < self.size

    def get_entity_at(self, position: Position) -> Optional[object]:
        """Get entity at a specific position."""
        return self.position_to_entity.get(position)

    def get_empty_positions(self) -> List[Position]:
        """Get all empty positions on the grid."""
        empty_positions = []
        for x in range(self.size):
            for y in range(self.size):
                pos = Position(x, y)
                if self.get_cell_type(pos) == CellType.EMPTY:
                    empty_positions.append(pos)
        return empty_positions