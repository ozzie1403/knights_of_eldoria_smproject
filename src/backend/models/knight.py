# src/backend/models/knight.py

import random
from src.backend.models.grid import Grid

class Knight:
    def __init__(self, position: tuple[int, int], energy: float = 100.0):
        self.position = position
        self.energy = energy

    def move_towards(self, target: tuple[int, int], grid: Grid):
        if self.energy <= 0:
            return

        x, y = self.position
        tx, ty = target

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1

        self.position = grid.wrap_position(x, y)
        self.energy = max(0, self.energy - 10)

    def attack(self, hunter) -> bool:
        if self.energy <= 0:
            return False

        if self.position == hunter.position:
            if hunter.carrying_treasure:
                hunter.drop_treasure()
            hunter.stamina = max(0, hunter.stamina - 20)
            self.energy = max(0, self.energy - 5)
            return True
        return False

    def rest(self):
        self.energy = min(100, self.energy + 1)

    def __repr__(self):
        return f"Knight(Position: {self.position}, Energy: {self.energy})"
