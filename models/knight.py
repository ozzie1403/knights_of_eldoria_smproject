from models.entity import Entity
from models.location import Location
from utils.constants import (
    EntityType, KNIGHT_DETECTION_RADIUS,
    KNIGHT_ENERGY_LOSS_MOVE, KNIGHT_ENERGY_GAIN_REST,
    KNIGHT_LOW_ENERGY
)
from utils.helpers import calculate_wrapped_distance, calculate_wrapped_direction
import random


class Knight(Entity):
    """Represents a knight in Eldoria."""

    def __init__(self, location: Location, garrison=None):
        super().__init__(location, EntityType.KNIGHT)
        self.energy = 100.0
        self.in_garrison = garrison
        self.resting = False
        self.chasing_hunter = None

        if garrison:
            garrison.add_knight(self)

    def update(self, grid):
        """Update knight state and behavior."""
        # If resting, regain energy
        if self.resting:
            self.energy += KNIGHT_ENERGY_GAIN_REST
            if self.energy >= 100.0:
                self.energy = 100.0
                self.resting = False
            return

        # If energy is low, try to return to garrison
        if self.energy <= KNIGHT_LOW_ENERGY:
            if self.in_garrison:
                self.resting = True
                return

            # Try to find nearest garrison
            if self._move_towards_nearest_garrison(grid):
                return

        # Look for hunters to chase
        nearby_entities = grid.get_nearby_entities(self.location, KNIGHT_DETECTION_RADIUS)
        nearby_hunters = [e for e in nearby_entities if e.type == EntityType.HUNTER]

        if nearby_hunters:
            # Choose a hunter to chase
            target_hunter = nearby_hunters[0]  # Simply choose the first one found
            self.chasing_hunter = target_hunter

            # Move towards the hunter
            self._move_towards_hunter(grid, target_hunter)
        else:
            # No hunters nearby, patrol randomly
            self._patrol_randomly(grid)

    def _move_towards_hunter(self, grid, hunter):
        """Move towards a hunter."""
        # Calculate direction to hunter
        dx, dy = calculate_wrapped_direction(
            self.location.x, self.location.y,
            hunter.location.x, hunter.location.y,
            grid.width, grid.height
        )

        # Determine which way to move
        if abs(dx) > abs(dy):
            new_x = (self.location.x + (1 if dx > 0 else -1)) % grid.width
            new_y = self.location.y
        else:
            new_x = self.location.x
            new_y = (self.location.y + (1 if dy > 0 else -1)) % grid.height

        # Create new location and try to move
        new_location = grid.get_wrapped_location(new_x, new_y)

        # Check if the new location has another knight
        entity_at_new = grid.get_entity_at(new_location)
        if entity_at_new and entity_at_new.type == EntityType.KNIGHT:
            return  # Don't move if there's another knight

        if grid.move_entity(self, new_location):
            # Moving uses energy
            self.energy -= KNIGHT_ENERGY_LOSS_MOVE
            if self.energy < 0:
                self.energy = 0

            # Check if we've caught a hunter
            entity_at_new = grid.get_entity_at(new_location)
            if entity_at_new and entity_at_new.type == EntityType.HUNTER:
                # We've caught a hunter!
                # Make the hunter drop any treasure it's carrying
                if hasattr(entity_at_new, 'carrying_treasure_value') and entity_at_new.carrying_treasure_value > 0:
                    # Drop the treasure at the hunter's location
                    from models.treasure import Treasure, TreasureType

                    # Create a new treasure of an appropriate type
                    treasure_type = TreasureType.BRONZE
                    if entity_at_new.carrying_treasure_value >= 10.0:
                        treasure_type = TreasureType.GOLD
                    elif entity_at_new.carrying_treasure_value >= 5.0:
                        treasure_type = TreasureType.SILVER

                    # Remove the hunter first
                    grid.remove_entity(entity_at_new)

                    # Then place the treasure
                    treasure = Treasure(Location(new_location.x, new_location.y), treasure_type)
                    grid.place_entity(treasure)
                else:
                    # Just remove the hunter
                    grid.remove_entity(entity_at_new)

                # Stop chasing
                self.chasing_hunter = None

    def _move_towards_nearest_garrison(self, grid):
        """Move towards the nearest garrison."""
        # Find all garrisons
        garrisons = [e for e in grid.entities if e.type == EntityType.GARRISON]

        if not garrisons:
            return False

        # Find nearest garrison
        nearest_garrison = None
        min_distance = float('inf')

        for garrison in garrisons:
            distance = calculate_wrapped_distance(
                self.location.x, self.location.y,
                garrison.location.x, garrison.location.y,
                grid.width, grid.height
            )

            if distance < min_distance:
                min_distance = distance
                nearest_garrison = garrison

        if nearest_garrison:
            # Calculate direction to garrison
            dx, dy = calculate_wrapped_direction(
                self.location.x, self.location.y,
                nearest_garrison.location.x, nearest_garrison.location.y,
                grid.width, grid.height
            )

            # Determine which way to move
            if abs(dx) > abs(dy):
                new_x = (self.location.x + (1 if dx > 0 else -1)) % grid.width
                new_y = self.location.y
            else:
                new_x = self.location.x
                new_y = (self.location.y + (1 if dy > 0 else -1)) % grid.height

            # Create new location and try to move
            new_location = grid.get_wrapped_location(new_x, new_y)

            # Check if the new location is the garrison
            entity_at_new = grid.get_entity_at(new_location)
            if entity_at_new and entity_at_new.type == EntityType.GARRISON:
                # We've reached a garrison
                entity_at_new.add_knight(self)
                self.resting = True
                return True

            # Move towards the garrison
            if not entity_at_new or entity_at_new.type == EntityType.GARRISON:
                if grid.move_entity(self, new_location):
                    # Moving uses energy
                    self.energy -= KNIGHT_ENERGY_LOSS_MOVE
                    if self.energy < 0:
                        self.energy = 0
                    return True

        return False

    def _patrol_randomly(self, grid):
        """Patrol in a random direction."""
        # Choose a random direction
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = random.choice(directions)

        # Calculate new location with wrap-around
        new_x = (self.location.x + dx) % grid.width
        new_y = (self.location.y + dy) % grid.height
        new_location = Location(new_x, new_y)

        # Check if the new location is empty
        entity_at_new = grid.get_entity_at(new_location)
        if not entity_at_new or entity_at_new.type == EntityType.GARRISON:
            if grid.move_entity(self, new_location):
                # Moving uses energy
                self.energy -= KNIGHT_ENERGY_LOSS_MOVE
                if self.energy < 0:
                    self.energy = 0

                # Check if we've entered a garrison
                entity_at_new = grid.get_entity_at(new_location)
                if entity_at_new and entity_at_new.type == EntityType.GARRISON:
                    entity_at_new.add_knight(self)

    @staticmethod
    def create_random(grid, count: int, garrisons=None):
        """Create random knights in the grid. If garrisons are provided, place them near garrisons."""
        knights = []
        for _ in range(count):
            # Choose location
            if garrisons and random.random() < 0.8:  # 80% chance to start at a garrison
                garrison = random.choice(garrisons)
                knight = Knight(Location(garrison.location.x, garrison.location.y), garrison)
                if grid.place_entity(knight):
                    knights.append(knight)
                    continue

            # Fallback to random placement
            attempts = 0
            while attempts < 100:  # Limit attempts
                x = random.randint(0, grid.width - 1)
                y = random.randint(0, grid.height - 1)
                location = Location(x, y)

                if grid.get_entity_at(location) is None:
                    knight = Knight(location)
                    if grid.place_entity(knight):
                        knights.append(knight)
                        break

                attempts += 1

        return knights