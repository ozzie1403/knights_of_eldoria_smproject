from enum import Enum
from dataclasses import dataclass
from .position import Position

class TreasureType(Enum):
    BRONZE = 3.0  # 3% value
    SILVER = 7.0  # 7% value
    GOLD = 13.0   # 13% value

@dataclass
class Treasure:
    position: Position
    treasure_type: TreasureType
    value: float = 100.0  # Initial value is 100%

    def decay(self) -> None:
        """Decay the treasure's value by 0.1% per tick."""
        self.value = max(0.0, self.value - 0.1)

    def is_depleted(self) -> bool:
        """Check if the treasure is depleted (value <= 0%)."""
        return self.value <= 0.0

    def get_value_percentage(self) -> float:
        """Get the current value as a percentage of the treasure type's base value."""
        return self.value * self.treasure_type.value / 100.0 