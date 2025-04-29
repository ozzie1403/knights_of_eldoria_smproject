from typing import Optional, List
from src.core.entities.position import Position
from src.core.enums import EntityType

class Entity:
    def __init__(self, position: Position, entity_type: EntityType):
        self.position = position
        self.entity_type = entity_type
        self.stamina: float = 100.0
        self.is_active: bool = True

    def move(self, new_position: Position) -> None:
        """Move the entity to a new position."""
        if not self.can_move():
            return
        self.position = new_position
        self.stamina = max(0, self.stamina - 2)  # 2% stamina loss per move

    def rest(self) -> None:
        """Rest to regain stamina."""
        if self.stamina <= 6:  # Critical stamina level
            self.stamina = min(100, self.stamina + 1)  # 1% stamina gain per step while resting

    def can_move(self) -> bool:
        """Check if the entity has enough stamina to move."""
        return self.stamina > 0 and self.is_active

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(Position: {self.position}, Stamina: {self.stamina}%)" 