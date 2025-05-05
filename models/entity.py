from enum import Enum
from typing import Tuple, Optional, List, Dict
import math
import random
from abc import ABC, abstractmethod


class EntityType(Enum):
    """Enum for the different types of entities in the simulation."""
    EMPTY = 0
    KNIGHT = 1
    HUNTER = 2
    TREASURE = 3
    HIDEOUT = 4
    GARRISON = 5


class Position:
    """Represents a position on the grid."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def distance_to(self, other) -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def toroidal_distance(self, other, grid_width: int, grid_height: int) -> int:
        """Calculate Manhattan distance on a toroidal grid."""
        dx = min(abs(self.x - other.x), grid_width - abs(self.x - other.x))
        dy = min(abs(self.y - other.y), grid_height - abs(self.y - other.y))
        return dx + dy

    def get_next_step_towards(self, target, grid_width: int, grid_height: int) -> 'Position':
        """Get the next position one step towards the target on a toroidal grid."""
        # If we're adjacent to the target, move directly onto it
        if self.toroidal_distance(target, grid_width, grid_height) <= 1:
            return Position(target.x, target.y)

        # Calculate direct and wrapped distances for x
        direct_x = target.x - self.x
        wrapped_x = direct_x - grid_width if direct_x > 0 else direct_x + grid_width

        # Choose the shorter x path
        move_x = direct_x if abs(direct_x) <= abs(wrapped_x) else wrapped_x

        # Calculate direct and wrapped distances for y
        direct_y = target.y - self.y
        wrapped_y = direct_y - grid_height if direct_y > 0 else direct_y + grid_height

        # Choose the shorter y path
        move_y = direct_y if abs(direct_y) <= abs(wrapped_y) else wrapped_y

        # Decide whether to move in x or y direction based on which gets us closer
        if abs(move_x) >= abs(move_y) and move_x != 0:
            # Move in x direction
            step_x = 1 if move_x > 0 else -1
            new_x = self.x + step_x

            # Wrap around if needed
            if new_x < 0:
                new_x = grid_width - 1
            if new_x >= grid_width:
                new_x = 0

            return Position(new_x, self.y)
        elif move_y != 0:
            # Move in y direction
            step_y = 1 if move_y > 0 else -1
            new_y = self.y + step_y

            # Wrap around if needed
            if new_y < 0:
                new_y = grid_height - 1
            if new_y >= grid_height:
                new_y = 0

            return Position(self.x, new_y)

        # If we're already at the target, don't move
        return Position(self.x, self.y)


class Entity(ABC):
    """Base class for all entities in the simulation."""

    def __init__(self, entity_id: str, entity_type: EntityType, position: Position):
        self.id = entity_id
        self.type = entity_type
        self.position = position
        self.icon = "?"  # Default icon, to be overridden by subclasses
        self.color = "#000000"  # Default color, to be overridden by subclasses

    def __str__(self):
        return f"{self.type.name} at {self.position}"

    @abstractmethod
    def act(self, grid, entities: List['Entity']) -> None:
        """Perform the entity's action for this simulation step."""
        pass

    def distance_to(self, other: 'Entity') -> int:
        """Calculate Manhattan distance to another entity."""
        return self.position.distance_to(other.position)

    def toroidal_distance_to(self, other: 'Entity', grid_width: int, grid_height: int) -> int:
        """Calculate Manhattan distance on a toroidal grid."""
        return self.position.toroidal_distance(other.position, grid_width, grid_height)