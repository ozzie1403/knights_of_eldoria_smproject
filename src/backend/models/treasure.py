from enum import Enum


class TreasureType(Enum):
    BRONZE = 3  # Increases wealth by 3%
    SILVER = 7  # Increases wealth by 7%
    GOLD = 13  # Increases wealth by 13%


class Treasure:
    def __init__(self, treasure_type: TreasureType, position: tuple[int, int]):
        """Initializes a treasure with a type and position on the grid."""
        self.treasure_type = treasure_type
        self.value = treasure_type.value  # Percentage value increase
        self.position = position

    def decay(self):
        """Treasure loses 0.1% of its value per step."""
        self.value = max(0, self.value - 0.1)

    def is_depleted(self) -> bool:
        """Returns True if the treasure has lost all its value."""
        return self.value <= 0

    def __repr__(self):
        return f"Treasure({self.treasure_type.name}, Value: {self.value:.1f}%, Position: {self.position})"