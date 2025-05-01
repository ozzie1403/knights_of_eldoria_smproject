from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, GARRISON_MAX_CAPACITY
import random


class Garrison(Entity):
    """Represents a knight's garrison (resting place) in Eldoria."""

    def __init__(self, location: Location):
        super().__init__(location, EntityType.GARRISON)
        self.knights = []
        self.max_capacity = GARRISON_MAX_CAPACITY

    def update(self, grid):
        """Update garrison state."""
        pass  # Garrisons don't need to do anything on update

    def add_knight(self, knight):
        """Add a knight to this garrison if there's space."""
        if len(self.knights) < self.max_capacity:
            self.knights.append(knight)
            knight.in_garrison = self
            return True
        return False

    def remove_knight(self, knight):
        """Remove a knight from this garrison."""
        if knight in self.knights:
            self.knights.remove(knight)
            knight.in_garrison = None
            return True
        return False

    @staticmethod
    def create_random(grid, count: int):
        """Create random garrisons in the grid."""
        garrisons = []
        for _ in range(count):
            attempts = 0
            while attempts < 100:  # Limit attempts
                x = random.randint(0, grid.width - 1)
                y = random.randint(0, grid.height - 1)
                location = Location(x, y)

                if grid.get_entity_at(location) is None:
                    garrison = Garrison(location)
                    if grid.place_entity(garrison):
                        garrisons.append(garrison)
                        break

                attempts += 1

        return garrisons