from models.location import Location
from utils.constants import EntityType

class Entity:
    """Base class for all entities in the simulation."""

    def __init__(self, location: Location, entity_type: EntityType):
        self.location = location
        self.type = entity_type

    def update(self, grid):
        """Update the entity's state. To be implemented by subclasses."""
        pass

    def __repr__(self):
        return f"{self.type.name}({self.location.x}, {self.location.y})"