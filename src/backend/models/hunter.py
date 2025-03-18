import random
from typing import Optional
from src.backend.models.grid import Grid
from src.backend.models.treasure import Treasure


class TreasureHunter:
    def __init__(self, name: str, position: tuple[int, int], stamina: float = 100.0):
        self.name = name
        self.position = position
        self.stamina = stamina
        self.carrying_treasure: Optional[Treasure] = None

    def move(self, direction: str, grid: Grid):
        """Moves the hunter in a given direction if stamina allows."""
        if self.stamina <= 0:
            return

        x, y = self.position
        if direction == "up":
            y -= 1
        elif direction == "down":
            y += 1
        elif direction == "left":
            x -= 1
        elif direction == "right":
            x += 1

        self.position = grid.wrap_position(x, y)
        self.stamina = max(0, self.stamina - 2)  # Decrease stamina by 2% per move

    def pick_up_treasure(self, grid: Grid):
        """Picks up a treasure if available and not already carrying one."""
        if self.carrying_treasure is None:
            treasure = grid.get_treasure_at(*self.position)
            if treasure:
                self.carrying_treasure = treasure
                grid.cells[self.position[0]][self.position[1]] = None

    def drop_treasure(self):
        """Drops the carried treasure."""
        self.carrying_treasure = None

    def rest(self):
        """Regains stamina while resting in a hideout."""
        self.stamina = min(100, self.stamina + 1)

    def __repr__(self):
        return f"TreasureHunter({self.name}, Position: {self.position}, Stamina: {self.stamina})"
