import random
from enum import Enum
from typing import Optional

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


class Grid:
    def __init__(self, size: int = 20):
        """Initializes a grid with the given size."""
        self.size = size
        self.cells = [[None for _ in range(size)] for _ in range(size)]

    def wrap_position(self, x: int, y: int) -> tuple[int, int]:
        """Ensures grid wraps around edges."""
        return x % self.size, y % self.size

    def place_treasure(self, count: int = 10):
        """Randomly places treasures on the grid."""
        for _ in range(count):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            treasure_type = random.choice(list(TreasureType))
            self.cells[x][y] = Treasure(treasure_type, (x, y))

    def get_treasure_at(self, x: int, y: int) -> Optional[Treasure]:
        """Returns the treasure at the given position, if any."""
        return self.cells[x][y] if isinstance(self.cells[x][y], Treasure) else None

    def update_treasures(self):
        """Decays all treasures and removes depleted ones."""
        for x in range(self.size):
            for y in range(self.size):
                treasure = self.get_treasure_at(x, y)
                if treasure:
                    treasure.decay()
                    if treasure.is_depleted():
                        self.cells[x][y] = None

    def __repr__(self):
        return f"Grid(Size: {self.size}x{self.size})"
