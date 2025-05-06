from enum import Enum
from typing import Tuple
from .base_entity import BaseEntity, EntityType

class TreasureType(Enum):
    BRONZE = 1
    SILVER = 2
    GOLD = 3

    @property
    def gain_percentage(self) -> float:
        """Returns the gain percentage for each treasure type"""
        return {
            TreasureType.BRONZE: 0.03,  # 3%
            TreasureType.SILVER: 0.07,  # 7%
            TreasureType.GOLD: 0.13     # 13%
        }[self]

class Treasure(BaseEntity):
    def __init__(self, position: Tuple[int, int], treasure_type: TreasureType):
        super().__init__(EntityType.TREASURE, position)
        self.treasure_type = treasure_type
        self.base_value = treasure_type.value * 100  # Bronze: 100, Silver: 200, Gold: 300
        self.current_value = self.base_value
        self.gain_percentage = treasure_type.gain_percentage

    def decay_value(self) -> bool:
        """Decay the treasure value by 0.1% and return True if value is depleted"""
        self.current_value *= 0.999  # 0.1% decay
        return self.current_value < 1  # Consider treasure depleted if value < 1

    def get_collection_value(self) -> float:
        """Get the value when collected, including the gain percentage"""
        return self.current_value * (1 + self.gain_percentage)

    def __str__(self) -> str:
        return f"{self.entity_type.value}{self.treasure_type.value}" 