from models.entity import Entity
from models.location import Location
from models.knowledge_base import KnowledgeBase
from utils.constants import (
    EntityType, HunterSkill,
    HUNTER_STAMINA_LOSS_MOVE, HUNTER_STAMINA_GAIN_REST,
    HUNTER_CRITICAL_STAMINA, HUNTER_COLLAPSE_COUNTDOWN
)
from utils.helpers import calculate_wrapped_distance, calculate_wrapped_direction
import random


class TreasureHunter(Entity):
    """Represents a treasure hunter in Eldoria."""

    def __init__(self, location: Location, skill: HunterSkill):
        super().__init__(location, EntityType.HUNTER)
        self.skill = skill
        self.stamina = 100.0
        self.carrying_treasure = None
        self.carrying_treasure_value = 0.0
        self.wealth = 0.0  # Track hunter's total wealth
        self.knowledge = KnowledgeBase()
        self.in_hideout = None
        self.resting = False
        self.collapse_countdown = HUNTER_COLLAPSE_COUNTDOWN
        self.critical_stamina = HUNTER_CRITICAL_STAMINA

        # Properties for scanning radius based on skill
        self.scan_radius = 3
        if skill == HunterSkill.PERCEPTION:
            self.scan_radius = 4  # Better at scanning

        # Properties for stealth based on skill
        self.stealth_chance = 0.2  # 20% chance to avoid detection
        if skill == HunterSkill.STEALTH:
            self.stealth_chance = 0.5  # 50% chance with stealth skill

        # Properties for movement speed based on skill
        self.speed_multiplier = 1.0
        if skill == HunterSkill.SPEED:
            self.speed_multiplier = 1.5  # 50% faster movement

        # Properties for navigation skill
        self.navigation_knowledge_bonus = 1
        if skill == HunterSkill.NAVIGATION:
            self.navigation_knowledge_bonus = 2  # Double knowledge radius

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

            # While resting in a hideout, share knowledge
            if self.in_hideout:
                # Hideout sharing happens in the hideout's update method
                pass

            if self.stamina >= 100.0:
                self.stamina = 100.0
                self.resting = False
            return

        # Scan surroundings for entities
        self._scan_surroundings(grid)

        # If stamina is critically low, try to find a hideout to rest
        if self.stamina <= self.critical_stamina:
            if self.in_hideout:
                # Already in a hideout, start resting
                self.resting = True
                return

            if self.knowledge.known_hideout_locations:
                # Find nearest hideout
                nearest = None
                min_distance = float('inf')

                for hideout_loc in list(self.knowledge.known_hideout_locations):
                    # Verify it's still a hideout
                    entity = grid.get_entity_at(hideout_loc)
                    if not entity or entity.type != EntityType.HIDEOUT:
                        self.knowledge.known_hideout_locations.remove(hideout_loc)
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
                        # Try to enter the hideout
                        if entity.add_hunter(self):
                            self.resting = True
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
            if self.knowledge.known_hideout_locations:
                # Find nearest hideout
                nearest = None
                min_distance = float('inf')

                for hideout_loc in list(self.knowledge.known_hideout_locations):
                    # Verify it's still a hideout
                    entity = grid.get_entity_at(hideout_loc)
                    if not entity or entity.type != EntityType.HIDEOUT:
                        self.knowledge.known_hideout_locations.remove(hideout_loc)
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
            if self.knowledge.known_treasure_locations:
                # Find nearest treasure
                nearest = None
                min_distance = float('inf')

                for treasure_loc in list(self.knowledge.known_treasure_locations):
                    # Verify it's still a treasure
                    entity = grid.get_entity_at(treasure_loc)
                    if not entity or entity.type != EntityType.TREASURE:
                        self.knowledge.known_treasure_locations.remove(treasure_loc)
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

                        # Increase wealth based on treasure type
                        wealth_increase = entity.get_wealth_increase()
                        self.wealth += wealth_increase

                        grid.remove_entity(entity)
                        # Remove from known locations
                        if self.location in self.knowledge.known_treasure_locations:
                            self.knowledge.known_treasure_locations.remove(self.location)
                        return
                else:
                    # No valid treasure known, explore
                    self._explore_randomly(grid)
            else:
                # No treasure known, explore
                self._explore_randomly(grid)

    def _scan_surroundings(self, grid):
        """Scan surroundings for entities and update knowledge."""
        # Adjust scan radius based on navigation skill
        scan_radius = self.scan_radius
        if self.skill == HunterSkill.NAVIGATION:
            scan_radius += self.navigation_knowledge_bonus

        nearby = grid.get_nearby_entities(self.location, scan_radius)

        for entity in nearby:
            if entity == self:  # Skip self
                continue

            if entity.type == EntityType.TREASURE:
                self.knowledge.add_treasure_location(entity.location)
            elif entity.type == EntityType.HIDEOUT:
                self.knowledge.add_hideout_location(entity.location)
            elif entity.type == EntityType.KNIGHT:
                self.knowledge.add_knight_location(entity.location)

    def _move_towards(self, grid, target_location: Location):
        """Move towards a target location."""
        # Check if already at target
        if self.location.x == target_location.x and self.location.y == target_location.y:
            return

        # Calculate direction to move
        dx, dy = calculate_wrapped_direction(
            self.location.x, self.location.y,
            target_location.x, target_location.y,
            grid.width, grid.height
        )

        # Prioritize the dimension with larger difference
        if abs(dx) > abs(dy):
            new_x = (self.location.x + (1 if dx > 0 else -1)) % grid.width
            new_y = self.location.y
        else:
            new_x = self.location.x
            new_y = (self.location.y + (1 if dy > 0 else -1)) % grid.height

        # Create new location and try to move
        new_location = grid.get_wrapped_location(new_x, new_y)

        # Check if the new location has a knight
        entity_at_new = grid.get_entity_at(new_location)
        if entity_at_new and entity_at_new.type == EntityType.KNIGHT:
            # Check stealth to see if we can evade the knight
            if random.random() < self.stealth_chance:
                # Successfully evaded, continue with move
                pass
            else:
                # Failed to evade, don't move
                return

        # If the cell is empty or a treasure/hideout, try to move
        if not entity_at_new or entity_at_new.type in [EntityType.TREASURE, EntityType.HIDEOUT]:
            if grid.move_entity(self, new_location):
                # Decrease stamina due to movement
                stamina_loss = HUNTER_STAMINA_LOSS_MOVE
                if self.skill == HunterSkill.SPEED:
                    stamina_loss *= 1.5  # Speed hunters use more stamina

                self.stamina -= stamina_loss
                if self.stamina < 0:
                    self.stamina = 0

    def _explore_randomly(self, grid):
        """Explore in a random direction."""
        # Choose a random direction
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = random.choice(directions)

        # Calculate new location with wrap-around
        new_x = (self.location.x + dx) % grid.width
        new_y = (self.location.y + dy) % grid.height
        new_location = Location(new_x, new_y)

        # Check if the new location has a knight
        entity_at_new = grid.get_entity_at(new_location)
        if entity_at_new and entity_at_new.type == EntityType.KNIGHT:
            # Check stealth to see if we can evade the knight
            if random.random() < self.stealth_chance:
                # Successfully evaded, continue with move
                pass
            else:
                # Failed to evade, don't move
                return

        # If the cell is empty or a treasure/hideout, try to move
        if not entity_at_new or entity_at_new.type in [EntityType.TREASURE, EntityType.HIDEOUT]:
            if grid.move_entity(self, new_location):
                # Decrease stamina due to movement
                stamina_loss = HUNTER_STAMINA_LOSS_MOVE
                if self.skill == HunterSkill.SPEED:
                    stamina_loss *= 1.5  # Speed hunters use more stamina

                self.stamina -= stamina_loss
                if self.stamina < 0:
                    self.stamina = 0