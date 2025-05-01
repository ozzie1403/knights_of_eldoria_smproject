from models.location import Location
from utils.constants import EntityType
from typing import List, Dict, Optional, Any


class Grid:
    """Represents the 2D grid environment for the simulation."""

    def __init__(self, width: int, height: int):
        """
        Initialize a grid with given dimensions.

        Args:
            width: The width of the grid
            height: The height of the grid
        """
        self.width = width
        self.height = height
        self.entities = []  # List of all entities in the grid
        self.entity_map = {}  # Maps location hashes to entities for quick lookup

    def add_entity(self, entity) -> bool:
        """
        Add an entity to the grid at its specified location.

        Args:
            entity: The entity to add

        Returns:
            True if entity was added successfully, False otherwise
        """
        location = entity.location

        # Check if location is valid
        if not self._is_valid_location(location):
            return False

        # Check if location is already occupied
        loc_hash = self._hash_location(location)
        if loc_hash in self.entity_map:
            return False

        # Add entity to our collections
        self.entities.append(entity)
        self.entity_map[loc_hash] = entity
        return True

    def remove_entity(self, entity) -> bool:
        """
        Remove an entity from the grid.

        Args:
            entity: The entity to remove

        Returns:
            True if entity was removed successfully, False otherwise
        """
        # Check if entity exists in our collections
        if entity not in self.entities:
            return False

        # Remove entity from our collections
        self.entities.remove(entity)
        loc_hash = self._hash_location(entity.location)
        if loc_hash in self.entity_map:
            self.entity_map.pop(loc_hash)
        return True

    def move_entity(self, entity, new_location: Location):
        """Move an entity to a new location on the grid."""
        # Check if new location is valid and empty
        new_loc_hash = self._hash_location(new_location)
        entity_at_new = None

        if new_loc_hash in self.entity_map:
            entity_at_new = self.entity_map[new_loc_hash]
            # Check special cases - hunters can move onto treasures or hideouts
            if entity.type == EntityType.HUNTER:
                if entity_at_new.type not in [EntityType.TREASURE, EntityType.HIDEOUT]:
                    return False  # Can't move onto non-treasure, non-hideout entities
            else:
                return False  # Cell already occupied

        # Remove from old location
        old_loc_hash = self._hash_location(entity.location)
        if old_loc_hash in self.entity_map:
            self.entity_map.pop(old_loc_hash)

        # Update entity's location
        entity.location = new_location

        # Add to new location
        if entity_at_new and entity_at_new.type == EntityType.TREASURE:
            # Special case - hunter captures treasure
            self.entities.remove(entity_at_new)

        self.entity_map[new_loc_hash] = entity
        return True

    def get_entity_at(self, location: Location):
        """
        Get the entity at a specific location.

        Args:
            location: The location to check

        Returns:
            The entity at the location, or None if no entity is present
        """
        loc_hash = self._hash_location(location)
        return self.entity_map.get(loc_hash, None)

    def get_entities_by_type(self, entity_type: EntityType) -> List[Any]:
        """
        Get all entities of a specific type.

        Args:
            entity_type: The type of entities to retrieve

        Returns:
            List of entities of the specified type
        """
        return [entity for entity in self.entities if entity.type == entity_type]

    def get_entities_in_radius(self, center: Location, radius: int, entity_type: Optional[EntityType] = None) -> List[
        Any]:
        """
        Get all entities within a radius of a center location.

        Args:
            center: The center location
            radius: The radius to search within
            entity_type: Optional entity type to filter results

        Returns:
            List of entities within the radius (optionally filtered by type)
        """
        entities_in_radius = []

        for entity in self.entities:
            distance = self._calculate_distance(center, entity.location)
            if distance <= radius:
                if entity_type is None or entity.type == entity_type:
                    entities_in_radius.append(entity)

        return entities_in_radius

    def find_random_empty_location(self, existing_locations=None) -> Location:
        """
        Find a random empty location on the grid.

        Args:
            existing_locations: Optional list of locations to avoid

        Returns:
            A random empty Location
        """
        import random

        # Make sure existing_locations is a list
        if existing_locations is None:
            existing_locations = []
        if not isinstance(existing_locations, list):
            existing_locations = []

        # Convert existing locations to set of hashes for faster lookup
        existing_hashes = set()
        for loc in existing_locations:
            if isinstance(loc, Location):
                existing_hashes.add(self._hash_location(loc))

        # Get all occupied locations
        occupied_hashes = set(self.entity_map.keys()).union(existing_hashes)

        # Find all empty locations
        empty_locations = []
        for x in range(self.width):
            for y in range(self.height):
                loc = Location(x, y)
                loc_hash = self._hash_location(loc)
                if loc_hash not in occupied_hashes:
                    empty_locations.append(loc)

        if not empty_locations:
            # If no empty locations, just return a random location
            return Location(random.randint(0, self.width - 1), random.randint(0, self.height - 1))

        return random.choice(empty_locations)

    def _is_valid_location(self, location: Location) -> bool:
        """Check if a location is within the grid boundaries."""
        return 0 <= location.x < self.width and 0 <= location.y < self.height

    def _hash_location(self, location: Location) -> str:
        """Convert a location to a unique string hash."""
        return f"{location.x},{location.y}"

    def _calculate_distance(self, loc1: Location, loc2: Location) -> int:
        """
        Calculate the Manhattan distance between two locations, accounting for wrap-around edges.

        Args:
            loc1: First location
            loc2: Second location

        Returns:
            The Manhattan distance between the two locations
        """
        # Calculate x distance with wrap-around
        dx = min(abs(loc1.x - loc2.x), self.width - abs(loc1.x - loc2.x))

        # Calculate y distance with wrap-around
        dy = min(abs(loc1.y - loc2.y), self.height - abs(loc1.y - loc2.y))

        return dx + dy