from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, HunterSkill, HUNTER_STAMINA_LOSS_MOVEMENT
from utils.constants import HUNTER_STAMINA_GAIN_REST, HUNTER_CRITICAL_STAMINA, \
    HUNTER_COLLAPSE_COUNTDOWN
from ai.knowledge_base import KnowledgeBase
from ai.decision_making import decide_hunter_action
from ai.pathfinding import get_next_move
import random

from utils.helpers import calculate_wrapped_distance


class TreasureHunter(Entity):
    """Represents a treasure hunter in Eldoria."""

    def __init__(self, location: Location, skill: HunterSkill):
        super().__init__(location, EntityType.HUNTER)
        self.skill = skill
        self.stamina = 100.0
        self.carrying_treasure = None
        self.carrying_treasure_value = 0.0
        self.knowledge = KnowledgeBase()
        self.in_hideout = None  # This will be set when added to a hideout
        self.resting = False
        self.collapse_countdown = HUNTER_COLLAPSE_COUNTDOWN
        self.critical_stamina = HUNTER_CRITICAL_STAMINA

        # Properties for scanning radius based on skill
        self.scan_radius = 3
        if skill == HunterSkill.NAVIGATION:
            self.scan_radius = 4  # Better at scanning

        print(f"Created hunter with skill {skill} at {location}")

    def update(self, grid):
        """Update hunter state and behavior."""
        # If collapsed, countdown to removal
        if self.stamina <= 0:
            self.collapse_countdown -= 1
            if self.collapse_countdown <= 0:
                grid.remove_entity(self)
                if self.in_hideout:
                    self.in_hideout.remove_hunter(self)
            return

        # If resting, regain stamina
        if self.resting:
            self.stamina += HUNTER_STAMINA_GAIN_REST
            if self.stamina >= 100.0:
                self.stamina = 100.0
                self.resting = False
            return

        # Scan surroundings for entities
        self._scan_surroundings(grid)

        # If stamina is critically low, try to find a hideout to rest
        if self.stamina <= self.critical_stamina:
            if self.known_hideout_locations:
                # Find nearest hideout
                nearest = None
                min_distance = float('inf')

                for hideout_loc in self.known_hideout_locations:
                    # Verify it's still a hideout
                    entity = grid.get_entity_at(hideout_loc)
                    if not entity or entity.type != EntityType.HIDEOUT:
                        continue

                    distance = calculate_wrapped_distance(
                        self.location.x, self.location.y,
                        hideout_loc.x, hideout_loc.y,
                        grid.width, grid.height
                    )

                    if distance < min_distance:
                        min_distance = distance
                        nearest = hideout_loc

                if nearest:
                    # Move towards hideout
                    self._move_towards(grid, nearest)

                    # Check if we've reached the hideout
                    entity = grid.get_entity_at(self.location)
                    if entity and entity.type == EntityType.HIDEOUT:
                        self.resting = True
                        if self.in_hideout is None:
                            entity.add_hunter(self)
                        return
                else:
                    # No valid hideout known, just rest in place
                    self.resting = True
                    return
            else:
                # No hideout known, just rest in place
                self.resting = True
                return

        # If carrying treasure, try to deposit it at a hideout
        if self.carrying_treasure_value > 0:
            if self.known_hideout_locations:
                # Find nearest hideout
                nearest = None
                min_distance = float('inf')

                for hideout_loc in self.known_hideout_locations:
                    # Verify it's still a hideout
                    entity = grid.get_entity_at(hideout_loc)
                    if not entity or entity.type != EntityType.HIDEOUT:
                        continue

                    distance = calculate_wrapped_distance(
                        self.location.x, self.location.y,
                        hideout_loc.x, hideout_loc.y,
                        grid.width, grid.height
                    )

                    if distance < min_distance:
                        min_distance = distance
                        nearest = hideout_loc

                if nearest:
                    # Move towards hideout
                    self._move_towards(grid, nearest)

                    # Check if we've reached the hideout
                    entity = grid.get_entity_at(self.location)
                    if entity and entity.type == EntityType.HIDEOUT:
                        # Deposit treasure
                        entity.store_treasure(self.carrying_treasure_value)
                        self.carrying_treasure_value = 0
                        self.carrying_treasure = None
                        return
            else:
                # No hideout known, explore to find one
                self._explore_randomly(grid)

        # If not carrying treasure, look for some
        else:
            # Check if we know of any treasure locations
            if self.known_treasure_locations:
                # Find nearest treasure
                nearest = None
                min_distance = float('inf')

                for treasure_loc in list(self.known_treasure_locations):  # Create a copy to allow modification
                    # Verify it's still a treasure
                    entity = grid.get_entity_at(treasure_loc)
                    if not entity or entity.type != EntityType.TREASURE:
                        self.known_treasure_locations.remove(treasure_loc)
                        continue

                    distance = calculate_wrapped_distance(
                        self.location.x, self.location.y,
                        treasure_loc.x, treasure_loc.y,
                        grid.width, grid.height
                    )

                    if distance < min_distance:
                        min_distance = distance
                        nearest = treasure_loc

                if nearest:
                    # Move towards treasure
                    self._move_towards(grid, nearest)

                    # Check if we've reached the treasure
                    entity = grid.get_entity_at(self.location)
                    if entity and entity.type == EntityType.TREASURE:
                        # Collect the treasure
                        self.carrying_treasure = entity
                        self.carrying_treasure_value = entity.value
                        grid.remove_entity(entity)
                        # Remove from known locations
                        if self.location in self.known_treasure_locations:
                            self.known_treasure_locations.remove(self.location)
                        return
                else:
                    # No valid treasure known, explore
                    self._explore_randomly(grid)
            else:
                # No treasure known, explore
                self._explore_randomly(grid)

    def _scan_surroundings(self, grid):
        """Scan nearby cells for entities."""
        nearby_coords = grid.get_nearby_coords(self.location, self.scan_radius)
        for coord in nearby_coords:
            entity = grid.get_entity_at(coord)
            if entity:
                if entity.type == EntityType.TREASURE:
                    self.knowledge.add_treasure_location(coord)
                elif entity.type == EntityType.HIDEOUT:
                    self.knowledge.add_hideout_location(coord)
                elif entity.type == EntityType.KNIGHT:
                    self.knowledge.add_knight_location(coord)

    def _move_towards(self, grid, target_location):
        """Move towards a target location."""
        next_location = get_next_move(self.location, target_location, grid, grid.width, grid.height)

        if next_location:
            # Check if the new position is empty or contains a collectible entity
            entity = grid.get_entity_at(next_location)
            if entity is None or entity.type == EntityType.TREASURE or entity.type == EntityType.HIDEOUT:
                # Move to the new position
                if grid.move_entity(self, next_location):
                    # Reduce stamina based on skill
                    stamina_loss = HUNTER_STAMINA_LOSS_MOVEMENT
                    if self.skill == HunterSkill.ENDURANCE:
                        stamina_loss *= 0.5  # Less stamina loss for endurance hunters
                    self.stamina -= stamina_loss

    def _explore_randomly(self, grid):
        """Move in a random direction to explore."""
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
                    # Reduce stamina based on skill
                    stamina_loss = HUNTER_STAMINA_LOSS_MOVEMENT
                    if self.skill == HunterSkill.ENDURANCE:
                        stamina_loss *= 0.5  # Less stamina loss for endurance hunters
                    self.stamina -= stamina_loss
                    break

    @property
    def known_treasure_locations(self):
        """Property to access the knowledge base's treasure locations."""
        return self.knowledge.known_treasure_locations

    @property
    def known_hideout_locations(self):
        """Property to access the knowledge base's hideout locations."""
        return self.knowledge.known_hideout_locations

    @property
    def known_knight_locations(self):
        """Property to access the knowledge base's knight locations."""
        return self.knowledge.known_knight_locations

    @staticmethod
    def create_random(grid, hideouts, count_per_hideout: int):
        """Create random hunters at hideouts."""
        hunters = []

        # Ensure we have hideouts
        if not hideouts:
            print("No hideouts available to place hunters")
            return hunters

        print(f"Creating hunters at {len(hideouts)} hideouts, {count_per_hideout} per hideout")

        for hideout in hideouts:
            for i in range(count_per_hideout):
                # Make sure we don't exceed hideout capacity
                if len(hideout.hunters) >= hideout.max_capacity:
                    print(f"Hideout at {hideout.location} is at max capacity")
                    continue

                # Choose random skill
                skill = random.choice(list(HunterSkill))

                # Create hunter at hideout location
                hunter = TreasureHunter(
                    Location(hideout.location.x, hideout.location.y),
                    skill
                )

                # Add knowledge of this hideout
                hunter.knowledge.add_hideout_location(hideout.location)

                # Try to place on grid first
                if grid.place_entity(hunter):
                    # Only add to hideout if placement successful
                    hideout.add_hunter(hunter)
                    hunters.append(hunter)
                    print(f"Successfully created hunter at {hunter.location}, skill: {skill}")
                else:
                    print(f"Failed to place hunter at {hunter.location}")

        print(f"Created {len(hunters)} hunters total")
        return hunters