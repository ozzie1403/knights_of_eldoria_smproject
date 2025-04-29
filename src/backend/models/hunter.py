# src/backend/models/hunter.py

import random
from typing import Optional, TYPE_CHECKING
from src.backend.models.grid import Grid
from src.backend.models.entities import Treasure, HunterSkill

if TYPE_CHECKING:
    from src.backend.models.hideout import Hideout

class TreasureHunter:
    def __init__(self, name: str, position: tuple[int, int], skill: HunterSkill, stamina: float = 100.0):
        self.name = name
        self.position = position
        self.skill = skill
        self.stamina = stamina
        self.carrying_treasure: Optional[Treasure] = None
        self.known_treasures = []

    def move(self, direction: str, grid: Grid):
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
        self.stamina = max(0, self.stamina - 2)

    def pick_up_treasure(self, grid: Grid):
        if self.carrying_treasure is None:
            x, y = self.position
            treasure = grid.get_treasure_at(x, y)
            if treasure:
                self.known_treasures.append((x, y))
                self.carrying_treasure = treasure
                grid.cells[x][y] = None

    def drop_treasure(self):
        self.carrying_treasure = None

    def rest(self):
        self.stamina = min(100, self.stamina + 1)

    def deposit_treasure(self, hideout: "Hideout"):
        if self.carrying_treasure:
            hideout.store_treasure(self.carrying_treasure)
            self.drop_treasure()

    def __repr__(self):
        return f"TreasureHunter({self.name}, Position: {self.position}, Stamina: {self.stamina}, Carrying: {self.carrying_treasure})"
