from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, TreasureType, TREASURE_VALUES, TREASURE_VALUE_DECAY
import random

class Treasure(Entity):
    """Represents a treasure in Eldoria."""
    
    def __init__(self, location: Location, treasure_type: TreasureType):
        super().__init__(location, EntityType.TREASURE)
        self.treasure_type = treasure_type
        self.value = TREASURE_VALUES[treasure_type]
    
    def update(self, grid):
        """Update treasure state, decreasing value over time."""
        self.value -= self.value * TREASURE_VALUE_DECAY
        
        # If value drops to zero or below, remove it
        if self.value <= 0:
            grid.remove_entity(self)
    
    @staticmethod
    def create_random(grid, count: int):
        """Create random treasures in the grid."""
        treasures = []
        for _ in range(count):
            # Try to place treasure in an empty cell
            attempts = 0
            while attempts < 100:  # Limit attempts
                x = random.randint(0, grid.width - 1)
                y = random.randint(0, grid.height - 1)
                location = Location(x, y)
                
                if grid.get_entity_at(location) is None:
                    # Choose random treasure type
                    treasure_type = random.choice(list(TreasureType))
                    treasure = Treasure(location, treasure_type)
                    
                    if grid.place_entity(treasure):
                        treasures.append(treasure)
                        break
                
                attempts += 1
        
        return treasures