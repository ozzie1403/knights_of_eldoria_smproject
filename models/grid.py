from typing import List, Optional, Tuple
from models.entity import Entity
from models.location import Location
from utils.constants import EntityType


class Grid:
    """Represents the 2D grid of Eldoria."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.entities = []
        self.step_count = 0

    def place_entity(self, entity: Entity) -> bool:
        """Place an entity in the grid at its current location."""
        x, y = entity.location.get_wrapped_coords(self.width, self.height)
        if self.grid[y][x] is None:
            self.grid[y][x] = entity
            self.entities.append(entity)
            return True
        return False

    def remove_entity(self, entity: Entity) -> bool:
        """Remove an entity from the grid."""
        if entity in self.entities:
            x, y = entity.location.get_wrapped_coords(self.width, self.height)
            self.grid[y][x] = None
            self.entities.remove(entity)
            return True
        return False

    def move_entity(self, entity: Entity, new_location: Location) -> bool:
        """Move an entity to a new location in the grid."""
        if entity in self.entities:
            # Remove from old position
            old_x, old_y = entity.location.get_wrapped_coords(self.width, self.height)
            self.grid[old_y][old_x] = None

            # Update entity location
            entity.location = new_location

            # Add to new position
            new_x, new_y = new_location.get_wrapped_coords(self.width, self.height)

            # Only place if the position is empty
            if self.grid[new_y][new_x] is None:
                self.grid[new_y][new_x] = entity
                return True
            else:
                # Put back in original position if destination occupied
                self.grid[old_y][old_x] = entity
                return False
        return False

    def get_entity_at(self, location: Location) -> Optional[Entity]:
        """Get the entity at a specified location."""
        x, y = location.get_wrapped_coords(self.width, self.height)
        return self.grid[y][x]


    def get_nearby_coords(self, location: Location, radius: int) -> List[Location]:
        """Get all coordinates within specified radius of a location."""
        nearby = []
        x, y = location.get_wrapped_coords(self.width, self.height)

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                new_x = (x + dx) % self.width
                new_y = (y + dy) % self.height
                nearby.append(Location(new_x, new_y))

        return nearby

    def get_nearby_entities(self, location: Location, radius: int,
                            entity_type: Optional[EntityType] = None) -> List[Entity]:
        """Get all entities of specified type within radius of a location."""
        nearby_coords = self.get_nearby_coords(location, radius)
        entities = []

        for coord in nearby_coords:
            entity = self.get_entity_at(coord)
            if entity is not None and (entity_type is None or entity.type == entity_type):
                entities.append(entity)

        return entities

    def step(self):
        """Perform one step of the simulation."""
        # Create a copy to avoid modification during iteration
        entities_copy = self.entities.copy()

        # Update each entity
        for entity in entities_copy:
            if entity in self.entities:  # Check if entity still exists
                entity.update(self)

        self.step_count += 1

    def count_entities_by_type(self) -> dict:
        """Count the number of each type of entity in the grid."""
        counts = {entity_type: 0 for entity_type in EntityType}

        for entity in self.entities:
            counts[entity.type] += 1

        return counts

    def has_treasure(self) -> bool:
        """Check if there is any treasure left in the grid."""
        for entity in self.entities:
            if entity.type == EntityType.TREASURE:
                return True
        return False

    def has_hunters(self) -> bool:
        """Check if there are any hunters left in the grid."""
        for entity in self.entities:
            if entity.type == EntityType.HUNTER:
                return True
        return False