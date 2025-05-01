from models.location import Location
from utils.constants import EntityType
from typing import List, Dict


class Hideout:
    """
    Represents a hideout where treasure hunters can rest, recover stamina,
    and share information about treasures and knights.
    """

    def __init__(self, location: Location, max_capacity: int = 5):
        """
        Initialize a hideout.

        Args:
            location: The location of the hideout on the grid
            max_capacity: Maximum number of hunters that can rest in the hideout at once
        """
        self.location = location
        self.type = EntityType.HIDEOUT
        self.hunters = []  # Hunters currently in the hideout
        self.max_capacity = max_capacity

        # Shared knowledge
        self.known_treasures = {}  # Map of location hash to treasure info
        self.known_knights = {}  # Map of location hash to knight info
        self.stored_treasures = []  # Treasures stored in the hideout
        self.stored_treasure_count = 0  # Number of treasure pieces stored
        self.stored_treasure_value = 0  # Total value of stored treasures

    def can_enter(self, hunter) -> bool:
        """
        Check if a hunter can enter the hideout.

        Args:
            hunter: The hunter trying to enter

        Returns:
            True if the hunter can enter, False otherwise
        """
        return len(self.hunters) < self.max_capacity

    def enter(self, hunter) -> bool:
        """
        Hunter enters the hideout to rest.

        Args:
            hunter: The hunter entering the hideout

        Returns:
            True if the hunter successfully entered, False otherwise
        """
        if not self.can_enter(hunter):
            return False

        # Add hunter to the hideout
        self.hunters.append(hunter)

        # Share hunter's knowledge with the hideout
        self._share_knowledge(hunter)

        # Store treasures the hunter is carrying
        if hunter.carrying_treasure_value > 0:
            self.stored_treasures.append({
                'value': hunter.carrying_treasure_value,
                'type': hunter.carrying_treasure_type
            })
            self.stored_treasure_count += 1
            self.stored_treasure_value += hunter.carrying_treasure_value

            # Reset hunter's carrying state
            hunter.carrying_treasure_value = 0
            hunter.carrying_treasure_type = None

        return True

    def exit(self, hunter) -> bool:
        """
        Hunter exits the hideout after resting.

        Args:
            hunter: The hunter exiting the hideout

        Returns:
            True if the hunter successfully exited, False otherwise
        """
        if hunter not in self.hunters:
            return False

        # Remove hunter from the hideout
        self.hunters.remove(hunter)

        # Share hideout's knowledge with the hunter
        self._share_hideout_knowledge(hunter)

        return True

    def update(self):
        """Update the hideout state for a simulation step."""
        # Restore stamina for all hunters in the hideout
        for hunter in self.hunters:
            # Restore 5% stamina per step
            hunter.stamina = min(100, hunter.stamina + 5)

    def _share_knowledge(self, hunter):
        """Share hunter's knowledge with the hideout."""
        # Share treasure knowledge
        for loc_hash, treasure_info in hunter.known_treasures.items():
            if loc_hash not in self.known_treasures or treasure_info['last_seen'] > self.known_treasures[loc_hash][
                'last_seen']:
                self.known_treasures[loc_hash] = treasure_info

        # Share knight knowledge
        for loc_hash, knight_info in hunter.known_knights.items():
            if loc_hash not in self.known_knights or knight_info['last_seen'] > self.known_knights[loc_hash][
                'last_seen']:
                self.known_knights[loc_hash] = knight_info

    def _share_hideout_knowledge(self, hunter):
        """Share hideout's knowledge with a hunter."""
        # Share treasure knowledge
        for loc_hash, treasure_info in self.known_treasures.items():
            if loc_hash not in hunter.known_treasures or treasure_info['last_seen'] > hunter.known_treasures[loc_hash][
                'last_seen']:
                hunter.known_treasures[loc_hash] = treasure_info

        # Share knight knowledge
        for loc_hash, knight_info in self.known_knights.items():
            if loc_hash not in hunter.known_knights or knight_info['last_seen'] > hunter.known_knights[loc_hash][
                'last_seen']:
                hunter.known_knights[loc_hash] = knight_info

    @classmethod
    def create_random(cls, grid, existing_locations=None):
        """
        Create a hideout at a random empty location on the grid.

        Args:
            grid: The simulation grid
            existing_locations: Optional list of locations to avoid

        Returns:
            A new Hideout instance, or None if no empty location could be found
        """
        # Find a random empty location
        location = grid.find_random_empty_location(existing_locations)
        if not location:
            return None

        # Create hideout
        hideout = cls(location)

        # Add to grid
        if grid.add_entity(hideout):  # Changed from place_entity to add_entity
            return hideout

        return None