from typing import List, Tuple, Optional, Dict
import random
from entities.base_entity import BaseEntity, EntityType
from entities.treasure import Treasure, TreasureType
from entities.hunter import Hunter
from entities.hideout import Hideout
from entities.knight import Knight
from entities.garrison import Garrison

class EldoriaGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[List[BaseEntity]]] = [[[] for _ in range(width)] for _ in range(height)]
        self.entities: Dict[EntityType, List[BaseEntity]] = {
            EntityType.TREASURE: [],
            EntityType.HUNTER: [],
            EntityType.HIDEOUT: [],
            EntityType.KNIGHT: [],
            EntityType.GARRISON: []
        }

    def add_entity(self, entity: BaseEntity) -> None:
        """Add an entity to the grid"""
        x, y = entity.position
        self.grid[y][x].append(entity)
        if entity.entity_type != EntityType.EMPTY:
            self.entities[entity.entity_type].append(entity)

    def remove_entity(self, entity: BaseEntity) -> None:
        """Remove an entity from the grid"""
        x, y = entity.position
        if entity in self.grid[y][x]:
            self.grid[y][x].remove(entity)
            if entity.entity_type != EntityType.EMPTY:
                self.entities[entity.entity_type].remove(entity)

    def move_entity(self, entity: BaseEntity, new_position: Tuple[int, int]) -> None:
        """Move an entity to a new position"""
        self.remove_entity(entity)
        entity.position = new_position
        self.add_entity(entity)

    def get_entities_at(self, position: Tuple[int, int]) -> List[BaseEntity]:
        """Get all entities at a specific position"""
        x, y = position
        return self.grid[y][x]

    def is_position_empty(self, position: Tuple[int, int]) -> bool:
        """Check if a position is empty"""
        return len(self.get_entities_at(position)) == 0

    def generate_random_treasure(self, count: int) -> None:
        """Generate random treasures on the grid"""
        for _ in range(count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            treasure_type = random.choice(list(TreasureType))
            treasure = Treasure((x, y), treasure_type)
            self.add_entity(treasure)

    def __str__(self) -> str:
        """String representation of the grid"""
        result = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                entities = self.grid[y][x]
                if not entities:
                    row.append(".")
                else:
                    # Show the first entity at this position
                    row.append(str(entities[0]))
            result.append(" ".join(row))
        return "\n".join(result)