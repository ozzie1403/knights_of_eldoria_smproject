import random
from models.location import Location
from utils.constants import EntityType, TreasureType


class Treasure:
    """
    Represents a treasure that can be collected by hunters.
    Treasures have different types (bronze, silver, gold) and values.
    """

    def __init__(self, location: Location, treasure_type: TreasureType = None, initial_value: float = None):
        """
        Initialize a treasure.

        Args:
            location: The location of the treasure on the grid
            treasure_type: The type of treasure (bronze, silver, gold)
            initial_value: The initial value of the treasure
        """
        self.location = location
        self.type = EntityType.TREASURE

        # Set treasure type randomly if not specified
        if treasure_type is None:
            # 60% bronze, 30% silver, 10% gold
            rand = random.random()
            if rand < 0.6:
                treasure_type = TreasureType.BRONZE
            elif rand < 0.9:
                treasure_type = TreasureType.SILVER
            else:
                treasure_type = TreasureType.GOLD

        self.treasure_type = treasure_type

        # Set initial value based on type if not specified
        if initial_value is None:
            if treasure_type == TreasureType.BRONZE:
                initial_value = 3.0  # 3% wealth increase
            elif treasure_type == TreasureType.SILVER:
                initial_value = 7.0  # 7% wealth increase
            else:  # GOLD
                initial_value = 13.0  # 13% wealth increase

        self.initial_value = initial_value
        self.value = initial_value

    def update(self):
        """Update the treasure state for a simulation step."""
        # Treasures lose 0.1% of their value per step
        self.value = max(0, self.value - (self.initial_value * 0.001))

    @classmethod
    def create_random(cls, grid, num_treasures, existing_locations=None):
        """
        Create multiple treasures at random empty locations on the grid.

        Args:
            grid: The simulation grid
            num_treasures: Number of treasures to create
            existing_locations: Optional list of locations to avoid

        Returns:
            List of created Treasure instances
        """
        treasures = []

        for _ in range(num_treasures):
            # Find a random empty location
            location = grid.find_random_empty_location(existing_locations)
            if not location:
                break

            # Create treasure with random type
            treasure = cls(location)

            # Add to grid
            if grid.add_entity(treasure):  # Changed from place_entity to add_entity
                treasures.append(treasure)

                # Add this location to existing locations to avoid
                if existing_locations is None:
                    existing_locations = []
                existing_locations.append(location)

        return treasures