from typing import Tuple, Optional
from src.core.enums import EntityType, CellType, TreasureType

class Treasure:
    def __init__(self, position: Tuple[int, int], treasure_type: TreasureType = TreasureType.BRONZE):
        self.position = position
        self.treasure_type = treasure_type
        self.base_value = self._get_base_value()
        self.current_value = self.base_value
        self.decay_rate = 0.001  # 0.1% decay per step
        self.cell_type = CellType.TREASURE
        self.entity_type = EntityType.TREASURE
        self.should_remove = False
    
    def _get_base_value(self) -> float:
        """Get the base value based on treasure type."""
        if self.treasure_type == TreasureType.BRONZE:
            return 100.0
        elif self.treasure_type == TreasureType.SILVER:
            return 250.0
        else:  # GOLD
            return 500.0
    
    def decay(self) -> None:
        """Reduce the treasure's value by decay rate."""
        self.current_value *= (1 - self.decay_rate)
        if self.current_value < 0.01:  # Remove if value becomes negligible
            self.should_remove = True
    
    def update(self, grid) -> None:
        """Update the treasure's state each simulation step."""
        self.decay()
        if self.should_remove:
            grid.remove_entity(self.position)
    
    def __repr__(self) -> str:
        return f"Treasure({self.position}, {self.treasure_type}, value={self.current_value:.2f})" 