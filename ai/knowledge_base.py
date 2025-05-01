from typing import Set, List, Dict, Optional
from models.location import Location

class KnowledgeBase:
    """Manages an entity's knowledge of the world."""
    
    def __init__(self):
        self.known_treasure_locations: Set[Location] = set()
        self.known_hideout_locations: Set[Location] = set()
        self.known_knight_locations: Set[Location] = set()
        self.memory_capacity = 20  # Maximum locations to remember for each type
    
    def add_treasure_location(self, location: Location):
        """Remember a treasure location."""
        self._add_location(self.known_treasure_locations, location)
    
    def add_hideout_location(self, location: Location):
        """Remember a hideout location."""
        self._add_location(self.known_hideout_locations, location)
    
    def add_knight_location(self, location: Location):
        """Remember a knight location."""
        self._add_location(self.known_knight_locations, location)
    
    def remove_treasure_location(self, location: Location):
        """Forget a treasure location."""
        if location in self.known_treasure_locations:
            self.known_treasure_locations.remove(location)
    
    def _add_location(self, location_set: Set[Location], location: Location):
        """Add a location to a memory set, respecting capacity limits."""
        location_set.add(location)
        
        # Limit memory capacity
        if len(location_set) > self.memory_capacity:
            # Remove the oldest location (first item in set)
            location_set.remove(next(iter(location_set)))
    
    def merge_knowledge(self, other_kb):
        """Merge knowledge from another knowledge base."""
        for location in other_kb.known_treasure_locations:
            self._add_location(self.known_treasure_locations, location)
            
        for location in other_kb.known_hideout_locations:
            self._add_location(self.known_hideout_locations, location)
            
        for location in other_kb.known_knight_locations:
            self._add_location(self.known_knight_locations, location)