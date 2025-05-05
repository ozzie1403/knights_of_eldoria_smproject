import random
from models.entity import Entity, EntityType, Position
from models.types import TreasureType


class Treasure(Entity):
    """
    Represents a treasure in the simulation. Treasures have types, values,
    and decay over time.
    """

    def __init__(self, entity_id: str, position: Position, treasure_type: TreasureType):
        super().__init__(entity_id, EntityType.TREASURE, position)
        self.treasure_type = treasure_type
        self.initial_value = self._get_initial_value()
        self.current_value = self.initial_value
        self.decay_rate = 0.001  # 0.1% per step
        self.fully_depleted = False

        # Set visual properties
        self._set_visual_properties()

    def _get_initial_value(self) -> float:
        """Get the initial value based on treasure type."""
        if self.treasure_type == TreasureType.BRONZE:
            return 30.0  # 3% wealth increase
        elif self.treasure_type == TreasureType.SILVER:
            return 70.0  # 7% wealth increase
        elif self.treasure_type == TreasureType.GOLD:
            return 130.0  # 13% wealth increase
        return 10.0  # Default

    def _set_visual_properties(self) -> None:
        """Set the icon and color based on treasure type."""
        if self.treasure_type == TreasureType.BRONZE:
            self.icon = "B"
            self.color = "#CD7F32"  # Bronze
        elif self.treasure_type == TreasureType.SILVER:
            self.icon = "S"
            self.color = "#C0C0C0"  # Silver
        elif self.treasure_type == TreasureType.GOLD:
            self.icon = "G"
            self.color = "#FFD700"  # Gold

    def act(self, grid, entities) -> None:
        """Decay the treasure's value over time."""
        self.decay()

    def decay(self) -> None:
        """Reduce the treasure's value by the decay rate."""
        if not self.fully_depleted:
            self.current_value *= (1 - self.decay_rate)

            # Check if the treasure is fully depleted
            if self.current_value < 0.1:  # Threshold for depletion
                self.fully_depleted = True

    def is_fully_depleted(self) -> bool:
        """Check if the treasure is fully depleted."""
        return self.fully_depleted

    def get_collection_value(self) -> float:
        """Get the value of collecting this treasure."""
        return self.current_value

    def __str__(self) -> str:
        return f"{self.treasure_type.name} Treasure at {self.position} (Value: {self.current_value:.2f})"