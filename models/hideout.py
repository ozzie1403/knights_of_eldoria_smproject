from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, HunterSkill, HIDEOUT_MAX_CAPACITY, HIDEOUT_RECRUIT_PROBABILITY
import random
from typing import List, Set

class Hideout(Entity):
    """Represents a hideout in Eldoria."""
    
    def __init__(self, location: Location):
        super().__init__(location, EntityType.HIDEOUT)
        self.hunters = []
        self.stored_treasure = 0
        self.max_capacity = HIDEOUT_MAX_CAPACITY
        self.known_treasure_locations = set()
        self.known_hideout_locations = set()
        self.known_knight_locations = set()
    
    def update(self, grid):
        """Update hideout state, sharing information and possibly recruiting."""
        # Share information between hunters in this hideout
        self._share_information()
        
        # Check if we can recruit a new hunter
        self._try_recruit_new_hunter(grid)
    
    def _share_information(self):
        """Share knowledge between all hunters in the hideout."""
        if len(self.hunters) <= 1:
            return
        
        # Collect all known information
        all_treasure_locations = set()
        all_hideout_locations = set()
        all_knight_locations = set()
        
        for hunter in self.hunters:
            all_treasure_locations.update(hunter.known_treasure_locations)
            all_hideout_locations.update(hunter.known_hideout_locations)
            all_knight_locations.update(hunter.known_knight_locations)
        
        # Update hideout knowledge
        self.known_treasure_locations.update(all_treasure_locations)
        self.known_hideout_locations.update(all_hideout_locations)
        self.known_knight_locations.update(all_knight_locations)
        
        # Share with all hunters
        for hunter in self.hunters:
            hunter.known_treasure_locations.update(all_treasure_locations)
            hunter.known_hideout_locations.update(all_hideout_locations)
            hunter.known_knight_locations.update(all_knight_locations)
    
    def _try_recruit_new_hunter(self, grid):
        """Try to recruit a new hunter if conditions are met."""
        # Check if we have space and a diverse skill set
        if len(self.hunters) >= self.max_capacity or len(self.hunters) == 0:
            return
        
        # Check for diverse skills
        skills = set(hunter.skill for hunter in self.hunters)
        if len(skills) < len(self.hunters):
            # 20% chance to recruit a new hunter if we have diverse skills
            if random.random() < HIDEOUT_RECRUIT_PROBABILITY:
                from models.treasure_hunter import TreasureHunter
                
                # Choose a random skill from existing hunters
                skill = random.choice([hunter.skill for hunter in self.hunters])
                
                # Create and add the new hunter
                new_hunter = TreasureHunter(
                    Location(self.location.x, self.location.y), 
                    skill
                )
                
                # Add knowledge of this hideout
                new_hunter.known_hideout_locations.add(self.location)
                new_hunter.in_hideout = self
                
                if grid.place_entity(new_hunter):
                    self.hunters.append(new_hunter)
    
    def add_hunter(self, hunter):
        """Add a hunter to this hideout if there's space."""
        if len(self.hunters) < self.max_capacity:
            self.hunters.append(hunter)
            hunter.in_hideout = self
            return True
        return False
    
    def remove_hunter(self, hunter):
        """Remove a hunter from this hideout."""
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            hunter.in_hideout = None
            return True
        return False
    
    def store_treasure(self, value: float):
        """Store treasure in the hideout."""
        self.stored_treasure += value
    
    @staticmethod
    def create_random(grid, count: int):
        """Create random hideouts in the grid."""
        hideouts = []
        for _ in range(count):
            attempts = 0
            while attempts < 100:  # Limit attempts
                x = random.randint(0, grid.width - 1)
                y = random.randint(0, grid.height - 1)
                location = Location(x, y)
                
                if grid.get_entity_at(location) is None:
                    hideout = Hideout(location)
                    if grid.place_entity(hideout):
                        hideouts.append(hideout)
                        break
                
                attempts += 1
        
        return hideouts