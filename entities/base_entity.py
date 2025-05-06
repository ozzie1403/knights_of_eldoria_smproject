from enum import Enum
from typing import Tuple

class EntityType(Enum):
    EMPTY = " "
    TREASURE = "T"
    HUNTER = "H"
    HIDEOUT = "O"
    KNIGHT = "K"
    GARRISON = "G"

class BaseEntity:
    def __init__(self, entity_type: EntityType, position: Tuple[int, int]):
        self.entity_type = entity_type
        self.position = position

    def __str__(self) -> str:
        return self.entity_type.value

    def move(self, new_position: Tuple[int, int], grid_size: Tuple[int, int]) -> Tuple[int, int]:
        """Move the entity to a new position with grid wrapping"""
        x, y = new_position
        grid_width, grid_height = grid_size
        return (x % grid_width, y % grid_height)