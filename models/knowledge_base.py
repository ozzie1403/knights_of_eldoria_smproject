from models.location import Location
from typing import Set


class KnowledgeBase:
    """Stores knowledge about the environment for a treasure hunter."""

    def __init__(self):
        self.known_treasure_locations: Set[Location] = set()
        self.known_hideout_locations: Set[Location] = set()
        self.known_knight_locations: Set[Location] = set()

    def add_treasure_location(self, location: Location):
        """Add a treasure location to knowledge base."""
        self.known_treasure_locations.add(location)

    def add_hideout_location(self, location: Location):
        """Add a hideout location to knowledge base."""
        self.known_hideout_locations.add(location)

    def add_knight_location(self, location: Location):
        """Add a knight location to knowledge base."""
        self.known_knight_locations.add(location)

    def remove_treasure_location(self, location: Location):
        """Remove a treasure location from knowledge base."""
        if location in self.known_treasure_locations:
            self.known_treasure_locations.remove(location)

    def remove_knight_location(self, location: Location):
        """Remove a knight location from knowledge base."""
        if location in self.known_knight_locations:
            self.known_knight_locations.remove(location)

    def merge_with(self, other):
        """Merge knowledge from another knowledge base."""
        self.known_treasure_locations.update(other.known_treasure_locations)
        self.known_hideout_locations.update(other.known_hideout_locations)
        self.known_knight_locations.update(other.known_knight_locations)