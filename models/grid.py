from typing import List, Dict, Optional, Tuple
from models.entity import Entity, Position, EntityType
import random


class Grid:
    """
    Represents the 2D toroidal grid for the Knights of Eldoria simulation.
    The grid wraps around at the edges.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells: List[List[Optional[Entity]]] = [[None for _ in range(width)] for _ in range(height)]
        self.entity_positions: Dict[str, Position] = {}  # Maps entity IDs to positions

    def place_entity(self, entity: Entity) -> bool:
        """Place an entity on the grid."""
        if entity.position.x < 0 or entity.position.x >= self.width or \
                entity.position.y < 0 or entity.position.y >= self.height:
            return False

        # Check if the position is empty
        if self.cells[entity.position.y][entity.position.x] is not None:
            return False

        # Place the entity
        self.cells[entity.position.y][entity.position.x] = entity
        return True

    def remove_entity(self, entity: Entity) -> bool:
        """Remove an entity from the grid."""
        if entity.position.x < 0 or entity.position.x >= self.width or \
                entity.position.y < 0 or entity.position.y >= self.height:
            return False

        # Remove from the grid
        self.cells[entity.position.y][entity.position.x] = None
        return True

    def move_entity(self, entity: Entity, new_position: Position) -> bool:
        """Move an entity to a new position."""
        # Check if the new position is valid
        if new_position.x < 0 or new_position.x >= self.width or \
                new_position.y < 0 or new_position.y >= self.height:
            return False

        # Get the entity at the target position
        target_entity = self.cells[new_position.y][new_position.x]

        # Allow hunters to move onto treasure
        if target_entity is not None:
            if entity.type == EntityType.HUNTER and target_entity.type == EntityType.TREASURE:
                # First collect the treasure
                entity._collect_treasure(target_entity, self)
                # Then move the hunter
                self.cells[entity.position.y][entity.position.x] = None
                entity.position = new_position
                self.cells[new_position.y][new_position.x] = entity
                return True
            else:
                return False

        # Remove from old position
        self.cells[entity.position.y][entity.position.x] = None

        # Update entity's position
        entity.position = new_position

        # Place at new position
        self.cells[new_position.y][new_position.x] = entity
        return True

    def get_entity_at(self, position: Position) -> Optional[Entity]:
        """Get the entity at a specific position, or None if the cell is empty."""
        x, y = position.x % self.width, position.y % self.height
        return self.cells[y][x]

    def get_nearby_entities(self, position: Position, radius: int = 1) -> List[Entity]:
        """
        Get all entities within a certain radius of a position.
        Accounts for toroidal grid wrapping.
        """
        entities = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip the center position

                # Calculate position with wrapping
                nx = (position.x + dx) % self.width
                ny = (position.y + dy) % self.height

                # Add the entity if there is one
                entity = self.cells[ny][nx]
                if entity is not None:
                    entities.append(entity)

        return entities

    def find_empty_positions(self, count: int) -> List[Position]:
        """Find a specified number of random empty positions on the grid."""
        empty_positions = []

        # Get all empty positions
        all_empty = []
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] is None:
                    all_empty.append(Position(x, y))

        # Return random subset
        if len(all_empty) <= count:
            return all_empty

        return random.sample(all_empty, count)

    def find_path(self, start: Position, end: Position, max_steps: int = 100) -> List[Position]:
        """
        Find a path from start to end using A* algorithm.
        Accounts for toroidal grid wrapping.
        """
        # TODO: Implement A* pathfinding for navigation
        # For now, just return a simple path in the direction of the end
        path = [start]
        current = start

        for _ in range(max_steps):
            next_pos = current.get_next_step_towards(end, self.width, self.height)
            path.append(next_pos)
            current = next_pos

            if current.x == end.x and current.y == end.y:
                break

        return path[1:]  # Exclude the start position