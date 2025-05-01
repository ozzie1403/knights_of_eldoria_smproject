from models.location import Location
from utils.constants import EntityType
from typing import List


class Garrison:
    """
    Represents a garrison where knights are stationed and can patrol from.
    """

    def __init__(self, location: Location):
        """
        Initialize a garrison.

        Args:
            location: The location of the garrison on the grid
        """
        self.location = location
        self.type = EntityType.GARRISON
        self.knights = []  # Knights stationed at this garrison

    def update(self):
        """Update the garrison state for a simulation step."""
        # Knights in the garrison regain energy
        for knight in self.knights:
            # Restore 5% energy per step
            knight.energy = min(100, knight.energy + 5)

    def station_knight(self, knight) -> bool:
        """
        Station a knight at this garrison.

        Args:
            knight: The knight to station

        Returns:
            True if the knight was successfully stationed, False otherwise
        """
        if knight in self.knights:
            return False

        self.knights.append(knight)
        knight.garrison = self
        return True

    @classmethod
    def create_random(cls, grid, existing_locations=None):
        """
        Create a garrison at a random empty location on the grid.

        Args:
            grid: The simulation grid
            existing_locations: Optional list of locations to avoid

        Returns:
            A new Garrison instance, or None if no empty location could be found
        """
        # Find a random empty location
        location = grid.find_random_empty_location(existing_locations)
        if not location:
            return None

        # Create garrison
        garrison = cls(location)

        # Add to grid
        if grid.add_entity(garrison):  # Changed from place_entity to add_entity
            return garrison

        return None