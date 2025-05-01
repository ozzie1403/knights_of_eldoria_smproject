from abc import ABC, abstractmethod
from models.location import Location
from utils.constants import EntityType

class Entity(ABC):
    """Base class for all entities in the simulation."""
    
    def __init__(self, location: Location, entity_type: EntityType):
        self.location = location
        self.type = entity_type
        
    @abstractmethod
    def update(self, grid):
        """Update the entity state based on the current simulation state."""
        pass