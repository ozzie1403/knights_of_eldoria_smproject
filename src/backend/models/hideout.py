# src/backend/models/hideout.py

from src.backend.models.treasure import Treasure

class Hideout:
    def __init__(self, x: int, y: int):
        self.position = (x, y)
        self.stored_treasures: list[Treasure] = []

    def store_treasure(self, treasure: Treasure):
        self.stored_treasures.append(treasure)

    def __repr__(self):
        return f"Hideout(Position: {self.position}, Stored: {len(self.stored_treasures)} treasures)"
