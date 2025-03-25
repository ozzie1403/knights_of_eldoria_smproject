from typing import List
from src.backend.models.treasure import Treasure
from src.backend.models.hunter import TreasureHunter

class Hideout:
    MAX_CAPACITY = 5  # Maximum number of hunters allowed

    def __init__(self, x: int, y: int):
        """Initializes a hideout at (x, y) location."""
        self.x = x
        self.y = y
        self.hunters: List[TreasureHunter] = []  # Hunters currently resting
        self.stored_treasures: List[Treasure] = []  # Treasures stored in the hideout

    def add_hunter(self, hunter: TreasureHunter) -> bool:
        """Adds a hunter if there's space."""
        if len(self.hunters) < Hideout.MAX_CAPACITY:
            self.hunters.append(hunter)
            return True
        return False  # Hideout is full

    def remove_hunter(self, hunter: TreasureHunter):
        """Removes a hunter when they leave."""
        if hunter in self.hunters:
            self.hunters.remove(hunter)

    def store_treasure(self, treasure: Treasure):
        """Stores treasure inside the hideout."""
        self.stored_treasures.append(treasure)

    def rest_hunters(self):
        """Recovers stamina of all hunters resting in the hideout."""
        for hunter in self.hunters:
            hunter.rest()

    def share_information(self):
        """Hunters share knowledge about treasure & knights."""
        known_locations = []
        for hunter in self.hunters:
            known_locations.extend(hunter.known_treasures)
        return set(known_locations)  # Remove duplicates

    def __repr__(self):
        return f"Hideout({self.x}, {self.y}, Hunters: {len(self.hunters)})"