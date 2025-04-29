from typing import List, Dict, Optional, Set, Any
import random
from src.core.entities.position import Position
from src.core.entities.base import Entity
from src.core.entities.treasure import Treasure
from src.core.entities.hunter import Hunter
from src.core.entities.knight import Knight
from src.core.entities.hideout import Hideout
from src.core.enums import EntityType, TreasureType, HunterSkill
from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Grid:
    MIN_SIZE = 20
    MAX_SIZE = 100

    def __init__(self, size: int = 20):
        if size < self.MIN_SIZE:
            raise ValueError(f"Grid size must be at least {self.MIN_SIZE}x{self.MIN_SIZE}")
        if size > self.MAX_SIZE:
            raise ValueError(f"Grid size cannot exceed {self.MAX_SIZE}x{self.MAX_SIZE}")
            
        self.size = size
        self.entities: Dict[Position, Any] = {}
        self.treasures: List[Any] = []
        self.hunters: List[Any] = []
        self.knights: List[Any] = []
        self.hideouts: List[Any] = []

    def add_entity(self, entity: Any) -> bool:
        """Add an entity to the grid."""
        pos = self.wrap_position(entity.position)
        if pos in self.entities:
            return False
        self.entities[pos] = entity
        entity.position = pos
        
        if hasattr(entity, 'treasure_type'):
            self.treasures.append(entity)
        elif hasattr(entity, 'stamina'):
            self.hunters.append(entity)
        elif hasattr(entity, 'max_hunters'):
            self.hideouts.append(entity)
        
        return True

    def remove_entity(self, pos: Position) -> None:
        """Remove an entity from the grid."""
        wrapped_pos = self.wrap_position(pos)
        if wrapped_pos in self.entities:
            entity = self.entities.pop(wrapped_pos)
            if hasattr(entity, 'treasure_type'):
                self.treasures.remove(entity)
            elif hasattr(entity, 'stamina'):
                self.hunters.remove(entity)
            elif hasattr(entity, 'max_hunters'):
                self.hideouts.remove(entity)

    def get_entity_at(self, pos: Position) -> Optional[Any]:
        """Get the entity at a position."""
        wrapped_pos = self.wrap_position(pos)
        return self.entities.get(wrapped_pos)

    def get_adjacent_positions(self, pos: Position) -> List[Position]:
        """Get all adjacent positions (N, S, E, W)."""
        wrapped_pos = self.wrap_position(pos)
        return [
            self.wrap_position(Position(wrapped_pos.x, wrapped_pos.y - 1)),  # North
            self.wrap_position(Position(wrapped_pos.x, wrapped_pos.y + 1)),  # South
            self.wrap_position(Position(wrapped_pos.x + 1, wrapped_pos.y)),  # East
            self.wrap_position(Position(wrapped_pos.x - 1, wrapped_pos.y)),  # West
        ]

    def get_random_empty_position(self) -> Optional[Position]:
        """Get a random empty position on the grid."""
        empty_positions = []
        for x in range(self.size):
            for y in range(self.size):
                pos = Position(x, y)
                if pos not in self.entities:
                    empty_positions.append(pos)
        return empty_positions[0] if empty_positions else None

    def wrap_position(self, pos: Position) -> Position:
        """Wrap a position around the grid edges."""
        return Position(
            pos.x % self.size,
            pos.y % self.size
        )

    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is valid for this grid."""
        return (
            isinstance(position, Position) and
            isinstance(position.x, int) and
            isinstance(position.y, int)
        )

    def get_empty_cell_count(self) -> int:
        """Get the number of empty cells in the grid."""
        return (self.size * self.size) - len(self.entities)

    def get_entity_count(self) -> Dict[str, int]:
        """Get the count of each entity type in the grid."""
        return {
            'treasures': len(self.treasures),
            'hunters': len(self.hunters),
            'knights': len(self.knights),
            'hideouts': len(self.hideouts),
            'empty': self.get_empty_cell_count()
        }

    def __repr__(self) -> str:
        return f"Grid(Size: {self.size}x{self.size}, Treasures: {len(self.treasures)}, Hunters: {len(self.hunters)}, Knights: {len(self.knights)}, Hideouts: {len(self.hideouts)})" 