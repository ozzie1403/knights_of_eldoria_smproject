# src/backend/models/hideout.py

from src.backend.models.grid import Treasure

class Hideout:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.stored_treasures: list[Treasure] = []

    def store_treasure(self, treasure: Treasure):
        self.stored_treasures.append(treasure)

    def __repr__(self):
        return f"Hideout(Position: ({self.x}, {self.y}), Treasures Stored: {len(self.stored_treasures)})"
