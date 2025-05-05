import random
from typing import List, Dict, Optional
import uuid

from models.entity import Entity, EntityType, Position
from models.knight import Knight
from models.hunter import TreasureHunter
from models.hideout import Hideout
from models.garrison import Garrison
from models.treasure import Treasure
from models.types import TreasureType, HunterSkill


class EntityFactory:
    """Factory for creating simulation entities."""

    @staticmethod
    def create_entity(entity_type: EntityType, position: Position, **kwargs) -> Optional[Entity]:
        """Create an entity of the specified type at the given position."""
        entity_id = kwargs.get('entity_id', f"{entity_type.name.lower()}_{uuid.uuid4().hex[:8]}")

        if entity_type == EntityType.KNIGHT:
            return Knight(entity_id, position)

        elif entity_type == EntityType.HUNTER:
            skill = kwargs.get('skill', random.choice(list(HunterSkill)))
            return TreasureHunter(entity_id, position, skill)

        elif entity_type == EntityType.HIDEOUT:
            return Hideout(entity_id, position)

        elif entity_type == EntityType.GARRISON:
            return Garrison(entity_id, position)

        elif entity_type == EntityType.TREASURE:
            treasure_type = kwargs.get('treasure_type', random.choice(list(TreasureType)))
            return Treasure(entity_id, position, treasure_type)

        return None

    @staticmethod
    def create_random_distribution(grid_width: int, grid_height: int,
                                   knight_count: int, hunter_count: int,
                                   hideout_count: int, garrison_count: int,
                                   treasure_count: int) -> List[Entity]:
        """Create a random distribution of entities for the simulation."""
        entities = []
        positions = []

        # Generate random positions
        all_positions = []
        for y in range(grid_height):
            for x in range(grid_width):
                all_positions.append(Position(x, y))

        # Shuffle and take the required number
        random.shuffle(all_positions)
        available_positions = all_positions[:knight_count + hunter_count +
                                             hideout_count + garrison_count +
                                             treasure_count]

        # Create hideouts
        for i in range(hideout_count):
            position = available_positions.pop()
            hideout = EntityFactory.create_entity(
                EntityType.HIDEOUT, position, entity_id=f"hideout_{i}")
            entities.append(hideout)

        # Create garrisons
        for i in range(garrison_count):
            position = available_positions.pop()
            garrison = EntityFactory.create_entity(
                EntityType.GARRISON, position, entity_id=f"garrison_{i}")
            entities.append(garrison)

        # Create knights
        for i in range(knight_count):
            position = available_positions.pop()
            knight = EntityFactory.create_entity(
                EntityType.KNIGHT, position, entity_id=f"knight_{i}")
            entities.append(knight)

        # Create hunters with balanced skills
        skills = list(HunterSkill)
        for i in range(hunter_count):
            position = available_positions.pop()
            skill = skills[i % len(skills)]  # Distribute skills evenly
            hunter = EntityFactory.create_entity(
                EntityType.HUNTER, position, entity_id=f"hunter_{i}", skill=skill)
            entities.append(hunter)

        # Create treasures with distribution
        bronze_count = int(treasure_count * 0.5)  # 50% bronze
        silver_count = int(treasure_count * 0.3)  # 30% silver
        gold_count = treasure_count - bronze_count - silver_count  # Remainder gold

        treasure_types = ([TreasureType.BRONZE] * bronze_count +
                          [TreasureType.SILVER] * silver_count +
                          [TreasureType.GOLD] * gold_count)
        random.shuffle(treasure_types)

        for i in range(treasure_count):
            position = available_positions.pop()
            treasure_type = treasure_types[i]
            treasure = EntityFactory.create_entity(
                EntityType.TREASURE, position, entity_id=f"treasure_{i}",
                treasure_type=treasure_type)
            entities.append(treasure)

        return entities