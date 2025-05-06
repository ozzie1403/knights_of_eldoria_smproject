from typing import List, Tuple, Set, TYPE_CHECKING
from .base_entity import BaseEntity, EntityType

if TYPE_CHECKING:
    from .knight import Knight

class Garrison(BaseEntity):
    def __init__(self, position: Tuple[int, int]):
        super().__init__(EntityType.GARRISON, position)
        self.max_capacity = 3
        self.current_knights: Set['Knight'] = set()

    def can_accommodate(self) -> bool:
        """Check if garrison has space for more knights"""
        return len(self.current_knights) < self.max_capacity

    def add_knight(self, knight: 'Knight') -> bool:
        """Add a knight to the garrison for rest"""
        if self.can_accommodate():
            self.current_knights.add(knight)
            print(f"Knight at {knight.position} entered garrison at {self.position}")
            return True
        return False

    def remove_knight(self, knight: 'Knight') -> None:
        """Remove a knight from the garrison"""
        if knight in self.current_knights:
            self.current_knights.remove(knight)
            print(f"Knight at {knight.position} left garrison at {self.position}")

    def recover_knights(self) -> None:
        """Recover energy for all knights in the garrison"""
        # Create a copy of the set to avoid modification during iteration
        knights_to_recover = list(self.current_knights)
        for knight in knights_to_recover:
            if knight.energy < 100.0:
                knight.energy = min(100.0, knight.energy + 10.0)  # Recover 10% energy per step
                if knight.energy >= 100.0:
                    # Knight is fully recovered, remove from garrison
                    self.current_knights.remove(knight)
                    print(f"Knight at {knight.position} fully recovered and left garrison")

    def __str__(self) -> str:
        return f"{self.entity_type.value}{len(self.current_knights)}"  # Shows number of knights in garrison