# src/backend/models/treasure.py

from enum import Enum

class TreasureType(Enum):
    BRONZE = 3   # Adds 3% wealth
    SILVER = 7   # Adds 7% wealth
    GOLD = 13    # Adds 13% wealth


class Treasure:
    def __init__(self, treasure_type: TreasureType, position: tuple[int, int]):
        """Initialize a treasure with type and position."""
        self.treasure_type = treasure_type
        self.value = treasure_type.value  # percentage value
        self.position = position

    def decay(self):
        """Treasure loses 0.1% value per tick."""
        self.value = max(0, self.value - 0.1)

    def is_depleted(self) -> bool:
        """Check if treasure is fully decayed."""
        return self.value <= 0

    def __repr__(self):
        return f"Treasure({self.treasure_type.name}, Value: {self.value:.1f}%, Position: {self.position})"
