from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, HunterSkill, KNIGHT_DETECTION_RADIUS
from utils.constants import KNIGHT_ENERGY_LOSS_CHASE, KNIGHT_ENERGY_LOSS_MOVEMENT
from utils.constants import KNIGHT_ENERGY_GAIN_REST, KNIGHT_CRITICAL_ENERGY
from utils.constants import KNIGHT_DETAIN_STAMINA_LOSS, KNIGHT_CHALLENGE_STAMINA_LOSS
from utils.constants import KNIGHT_DETAIN_PROBABILITY
from ai.pathfinding import get_next_move
import random


class Knight(Entity):
    """Represents a knight in Eldoria."""

    def __init__(self, location: Location):
        super().__init__(location, EntityType.KNIGHT)
        self.energy = 100.0
        self.detection_radius = KNIGHT_DETECTION_RADIUS
        self.target = None
        self.resting = False
        self.critical_energy = KNIGHT_CRITICAL_ENERGY
        self.in_garrison = None
        self.known_garrison_locations = set()

    def update(self, grid):
        """Update knight state and behavior."""
        # If resting, regain energy
        if self.resting:
            self.energy += KNIGHT_ENERGY_GAIN_REST
            if self.energy >= 100.0:
                self.energy = 100.0
                self.resting = False
            return

        # If energy is low, find a garrison to rest
        if self.energy <= self.critical_energy:
            # If already in a garrison, start resting
            if self.in_garrison:
                self.resting = True
                return

            # Try to find nearest garrison
            nearest_garrison = self._find_nearest_garrison(grid)
            if nearest_garrison:
                # Move towards the garrison
                next_location = get_next_move(
                    self.location,
                    nearest_garrison.location,
                    grid,
                    grid.width,
                    grid.height
                )

                if next_location:
                    # Try to move
                    entity = grid.get_entity_at(next_location)
                    if entity is None or entity.type == EntityType.GARRISON:
                        grid.move_entity(self, next_location)
                        self.energy -= KNIGHT_ENERGY_LOSS_MOVEMENT

                        # Check if reached garrison
                        if entity and entity.type == EntityType.GARRISON:
                            entity.add_knight(self)
                            self.resting = True
                return
            else:
                # No known garrison, just rest in place
                self.resting = True
                return

        # Check for hunters in detection radius
        hunters = grid.get_nearby_entities(self.location, self.detection_radius, EntityType.HUNTER)

        # Filter out stealth hunters (they have 50% chance to be undetected)
        detectable_hunters = []
        for hunter in hunters:
            if hunter.skill == HunterSkill.STEALTH:
                if random.random() < 0.5:  # 50% chance to detect stealth hunters
                    detectable_hunters.append(hunter)
            else:
                detectable_hunters.append(hunter)

        # If we have a target, continue pursuit
        if self.target:
            # Check if target still exists
            if self.target not in grid.entities:
                self.target = None
            else:
                # Calculate distance to target
                from utils.helpers import calculate_wrapped_distance
                distance = calculate_wrapped_distance(
                    self.location.x, self.location.y,
                    self.target.location.x, self.target.location.y,
                    grid.width, grid.height
                )

                # If we caught the target
                if distance < 1.5:  # Close enough to catch
                    self._handle_hunter_caught(grid)
                    return

                # Continue pursuit (costs energy)
                next_location = get_next_move(
                    self.location,
                    self.target.location,
                    grid,
                    grid.width,
                    grid.height
                )

                if next_location:
                    # Check if the next location has the hunter or is empty
                    entity = grid.get_entity_at(next_location)
                    if entity is None or entity == self.target:
                        grid.move_entity(self, next_location)
                        self.energy -= KNIGHT_ENERGY_LOSS_CHASE
                return

        # If no current target but hunters detected, choose one
        if detectable_hunters:
            self.target = random.choice(detectable_hunters)
            return

        # Look for garrisons as we patrol
        self._scan_for_garrisons(grid)

        # No hunters detected, patrol randomly
        self._patrol_randomly(grid)

    # When looking for nearest garrison, make sure they consider all garrisons
    def _find_nearest_garrison(self, grid):
        """Find the nearest garrison to rest in."""
        # If we already know some garrisons
        if self.known_garrison_locations:
            nearest = None
            min_distance = float('inf')

            for garrison_loc in self.known_garrison_locations:
                # Check if it's still a garrison
                entity = grid.get_entity_at(garrison_loc)
                if not entity or entity.type != EntityType.GARRISON:
                    continue

                # Calculate distance
                from utils.helpers import calculate_wrapped_distance
                distance = calculate_wrapped_distance(
                    self.location.x, self.location.y,
                    garrison_loc.x, garrison_loc.y,
                    grid.width, grid.height
                )

                if distance < min_distance:
                    min_distance = distance
                    nearest = entity

            return nearest

        # If we don't know any garrisons, look for all garrisons in the grid
        else:
            # Check all entities to find garrisons
            garrisons = []
            nearest = None
            min_distance = float('inf')

            for entity in grid.entities:
                if entity.type == EntityType.GARRISON:
                    # Add to known garrisons
                    self.known_garrison_locations.add(entity.location)

                    # Calculate distance
                    from utils.helpers import calculate_wrapped_distance
                    distance = calculate_wrapped_distance(
                        self.location.x, self.location.y,
                        entity.location.x, entity.location.y,
                        grid.width, grid.height
                    )

                    if distance < min_distance:
                        min_distance = distance
                        nearest = entity

            return nearest

    def _scan_for_garrisons(self, grid):
        """Scan surroundings for garrisons."""
        nearby = grid.get_nearby_coords(self.location, 2)  # Shorter scan range than hunters

        for loc in nearby:
            entity = grid.get_entity_at(loc)
            if entity and entity.type == EntityType.GARRISON:
                self.known_garrison_locations.add(loc)

    def _handle_hunter_caught(self, grid):
        """Handle interaction when a hunter is caught."""
        # Check if target is a hunter
        if self.target.type != EntityType.HUNTER:
            self.target = None
            return

        # Decide whether to detain or challenge the hunter
        if random.random() < KNIGHT_DETAIN_PROBABILITY:
            # Detain: reduce stamina by 5%
            self.target.stamina -= KNIGHT_DETAIN_STAMINA_LOSS
        else:
            # Challenge: reduce stamina by 20%
            self.target.stamina -= KNIGHT_CHALLENGE_STAMINA_LOSS

        # Make hunter drop treasure
        if self.target.carrying_treasure_value > 0:
            from models.treasure import Treasure, TreasureType

            # Determine treasure type based on value
            treasure_type = TreasureType.BRONZE
            if self.target.carrying_treasure_value >= 7.0:
                treasure_type = TreasureType.SILVER
            if self.target.carrying_treasure_value >= 13.0:
                treasure_type = TreasureType.GOLD

            # Create new treasure at hunter's position
            treasure = Treasure(
                Location(self.target.location.x, self.target.location.y),
                treasure_type
            )
            treasure.value = self.target.carrying_treasure_value
            grid.place_entity(treasure)

            # Hunter remembers where they lost the treasure
            self.target.knowledge.add_treasure_location(Location(self.target.location.x, self.target.location.y))

            # Reset hunter's treasure
            self.target.carrying_treasure_value = 0
            self.target.carrying_treasure = None

        # After interaction, clear target
        self.target = None

    def _patrol_randomly(self, grid):
        """Move in a random direction to patrol."""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = (self.location.x + dx) % grid.width
            new_y = (self.location.y + dy) % grid.height
            new_location = Location(new_x, new_y)

            # Check if the new position is empty
            entity = grid.get_entity_at(new_location)
            if entity is None:
                # Move to the new position
                if grid.move_entity(self, new_location):
                    # Patrolling uses less energy
                    self.energy -= KNIGHT_ENERGY_LOSS_MOVEMENT
                    break

    @staticmethod
    def create_random(grid, count: int, garrisons=None):
        """Create random knights in the grid."""
        knights = []

        # Create knights at garrisons if available
        if garrisons:
            # First place knights at garrisons
            placed_at_garrisons = 0
            for garrison in garrisons:
                if placed_at_garrisons >= count:
                    break

                # Add knight to garrison
                location = Location(garrison.location.x, garrison.location.y)
                knight = Knight(location)
                knight.known_garrison_locations.add(location)

                if grid.place_entity(knight):
                    garrison.add_knight(knight)
                    knights.append(knight)
                    placed_at_garrisons += 1

            # If we've placed all knights, return
            if placed_at_garrisons >= count:
                return knights

            # Otherwise place remaining knights randomly
            remaining = count - placed_at_garrisons
        else:
            remaining = count

        # Place remaining knights randomly
        for _ in range(remaining):
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