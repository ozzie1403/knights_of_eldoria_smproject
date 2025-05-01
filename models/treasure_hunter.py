from models.entity import Entity
from models.location import Location
from utils.constants import EntityType, HunterSkill, HUNTER_STAMINA_LOSS_MOVEMENT
from utils.constants import HUNTER_STAMINA_GAIN_REST, HUNTER_CRITICAL_STAMINA, \
    HUNTER_COLLAPSE_COUNTDOWN
from ai.knowledge_base import KnowledgeBase
from ai.decision_making import decide_hunter_action
from ai.pathfinding import get_next_move
import random


class TreasureHunter(Entity):
    """Represents a treasure hunter in Eldoria."""

    def __init__(self, location: Location, skill: HunterSkill):
        super().__init__(location, EntityType.HUNTER)
        self.skill = skill
        self.stamina = 100.0
        self.carrying_treasure = None
        self.carrying_treasure_value = 0.0
        self.knowledge = KnowledgeBase()
        self.in_hideout = None
        self.resting = False
        self.collapse_countdown = HUNTER_COLLAPSE_COUNTDOWN
        self.critical_stamina = HUNTER_CRITICAL_STAMINA

        # Properties for scanning radius based on skill
        self.scan_radius = 3
        if skill == HunterSkill.NAVIGATION:
            self.scan_radius = 4  # Better at scanning

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

        # Use AI to decide next action
        action, target = decide_hunter_action(self, grid)

        if action == "rest":
            if self.in_hideout:
                self.resting = True
            elif target:
                self._move_towards(grid, target)
                # Check if we've reached the hideout
                if self.location == target:
                    entity = grid.get_entity_at(target)
                    if entity and entity.type == EntityType.HIDEOUT:
                        self.in_hideout = entity
                        entity.add_hunter(self)
                        self.resting = True

        elif action == "deposit" and target:
            self._move_towards(grid, target)
            # Check if we've reached the hideout
            if self.location == target:
                entity = grid.get_entity_at(target)
                if entity and entity.type == EntityType.HIDEOUT:
                    # Deposit treasure
                    entity.store_treasure(self.carrying_treasure_value)
                    self.carrying_treasure_value = 0
                    self.carrying_treasure = None
                    # Join the hideout
                    if self.in_hideout is None:
                        entity.add_hunter(self)

        elif action == "collect" and target:
            self._move_towards(grid, target)
            # Check if we've reached the treasure
            if self.location == target:
                entity = grid.get_entity_at(target)
                if entity and entity.type == EntityType.TREASURE:
                    # Collect the treasure
                    self.carrying_treasure = entity
                    self.carrying_treasure_value = entity.value
                    grid.remove_entity(entity)
                    # Remove from known locations
                    self.knowledge.remove_treasure_location(target)

        elif action == "explore":
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
        for hideout in hideouts:
            for _ in range(count_per_hideout):
                if len(hideout.hunters) >= hideout.max_capacity:
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

                # Add hunter to hideout
                hideout.add_hunter(hunter)

                # Place on grid
                if grid.place_entity(hunter):
                    hunters.append(hunter)

        return hunters