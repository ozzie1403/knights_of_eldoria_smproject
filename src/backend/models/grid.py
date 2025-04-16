# src/backend/models/grid.py

import random
from enum import Enum
from typing import Optional
from src.backend.models.treasure import Treasure, TreasureType


class Grid:
    def __init__(self, size: int = 20):
        """Initializes a grid with the given size."""
        self.size = size
        self.cells = [[[] for _ in range(size)] for _ in range(size)]  # List of treasures

    def wrap_position(self, x: int, y: int) -> tuple[int, int]:
        """Ensures the grid wraps around the edges."""
        return x % self.size, y % self.size

    def place_treasure(self, treasure: Optional[Treasure] = None, count: int = 10):
        """Places treasures on the grid, randomly or at given location."""
        if treasure:
            x, y = treasure.position
            self.cells[x][y].append(treasure)
        else:
            for _ in range(count):
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                t_type = random.choice(list(TreasureType))
                self.cells[x][y].append(Treasure(t_type, (x, y)))

    def get_treasure_at(self, x: int, y: int) -> list[Treasure]:
        """Returns list of treasures at (x, y), if any."""
        if 0 <= x < self.size and 0 <= y < self.size:
            return [t for t in self.cells[x][y] if not t.is_depleted()]
        return []

    def remove_treasure_at(self, x: int, y: int, treasure: Treasure):
        """Removes a specific treasure object from (x, y)."""
        if treasure in self.cells[x][y]:
            self.cells[x][y].remove(treasure)

    def update_treasures(self):
        """Decay and cleanup depleted treasures."""
        for x in range(self.size):
            for y in range(self.size):
                for treasure in self.cells[x][y][:]:  # Copy to avoid iteration issues
                    treasure.decay()
                    if treasure.is_depleted():
                        self.cells[x][y].remove(treasure)

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def __repr__(self):
        return f"Grid(Size: {self.size}x{self.size})"
