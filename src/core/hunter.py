from dataclasses import dataclass
from typing import Optional
from .position import Position
from .treasure import Treasure

@dataclass
class Hunter:
    position: Position
    stamina: float = 100.0
    steps_since_collapse: int = 0
    carrying_treasure: Optional[Treasure] = None
    is_collapsed: bool = False

    def move(self, new_position: Position) -> None:
        """Move the hunter to a new position, reducing stamina."""
        if not self.is_collapsed:
            self.position = new_position
            self.stamina = max(0.0, self.stamina - 2.0)
            if self.stamina <= 0.0:
                self.is_collapsed = True

    def rest(self) -> None:
        """Rest in a hideout, recovering stamina."""
        if self.is_collapsed:
            self.steps_since_collapse += 1
        else:
            self.stamina = min(100.0, self.stamina + 1.0)

    def needs_rest(self) -> bool:
        """Check if the hunter needs to rest."""
        return self.stamina <= 6.0 or self.is_collapsed

    def can_move(self) -> bool:
        """Check if the hunter can move."""
        return not self.is_collapsed and self.stamina > 0.0

    def pick_up_treasure(self, treasure: Treasure) -> bool:
        """Attempt to pick up a treasure."""
        if not self.carrying_treasure and not self.is_collapsed:
            self.carrying_treasure = treasure
            return True
        return False

    def deposit_treasure(self) -> Optional[Treasure]:
        """Deposit the carried treasure."""
        treasure = self.carrying_treasure
        self.carrying_treasure = None
        return treasure 