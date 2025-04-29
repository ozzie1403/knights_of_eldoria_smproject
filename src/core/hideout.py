from dataclasses import dataclass, field
from typing import List
from src.core.position import Position
from src.core.treasure import Treasure
from src.core.hunter import Hunter

@dataclass
class Hideout:
    position: Position
    max_hunters: int = 5
    hunters: List[Hunter] = field(default_factory=list)
    stored_treasures: List[Treasure] = field(default_factory=list)

    def can_accommodate(self) -> bool:
        """Check if the hideout can accommodate more hunters."""
        return len(self.hunters) < self.max_hunters

    def add_hunter(self, hunter: Hunter) -> bool:
        """Add a hunter to the hideout if there's space."""
        if self.can_accommodate():
            self.hunters.append(hunter)
            return True
        return False

    def remove_hunter(self, hunter: Hunter) -> bool:
        """Remove a hunter from the hideout."""
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False

    def store_treasure(self, treasure: Treasure) -> None:
        """Store a treasure in the hideout."""
        self.stored_treasures.append(treasure)

    def get_stored_treasure_count(self) -> int:
        """Get the count of stored treasures."""
        return len(self.stored_treasures) 