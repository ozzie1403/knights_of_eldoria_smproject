from typing import Optional
from src.core.entities.position import Position
from src.core.entities.base import Entity
from src.core.enums import EntityType, TreasureType

class Treasure(Entity):
    def __init__(self, position: Position, treasure_type: TreasureType):
        super().__init__(position, EntityType.TREASURE)
        self.treasure_type = treasure_type
        self.value = self._get_initial_value()
        self.decay_rate = 0.1  # Fixed decay rate of -0.1% per step

    def _get_initial_value(self) -> float:
        """Get the initial value based on treasure type."""
        values = {
            TreasureType.BRONZE: 3.0,   # 3% value
            TreasureType.SILVER: 7.0,   # 7% value
            TreasureType.GOLD: 13.0     # 13% value
        }
        return values[self.treasure_type]

    def decay(self) -> None:
        """Reduce the treasure's value by 0.1% per step."""
        self.value = max(0.0, self.value - self.decay_rate)

    def is_depleted(self) -> bool:
        """Check if the treasure has been completely depleted (0%)."""
        return self.value <= 0.0

    def get_value_percentage(self) -> float:
        """Get the treasure's value as a percentage."""
        return self.value

    def __repr__(self) -> str:
        return f"Treasure({self.treasure_type.name}, Value: {self.value:.1f}%)" 