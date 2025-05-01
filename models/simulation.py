from models.grid import Grid
from models.hideout import Hideout
from models.treasure_hunter import TreasureHunter
from models.treasure import Treasure
from models.knight import Knight
from models.garrison import Garrison
from models.location import Location
from utils.constants import EntityType, HunterSkill, DEFAULT_GRID_SIZE
from utils.helpers import calculate_wrapped_distance
import random


class Simulation:
    """Main simulation class for Knights of Eldoria."""

    def __init__(self, grid_size=DEFAULT_GRID_SIZE):
        self.grid = Grid(grid_size, grid_size)
        self.step_count = 0
        self.running = False
        self.setup_complete = False

        # Store references to entity groups
        self.hideouts = []
        self.hunters = []
        self.treasures = []
        self.knights = []
        self.garrisons = []

    def setup(self, num_hideouts: int = 3, num_hunters_per_hideout: int = 2,
              num_treasures: int = 30, num_knights: int = 2, num_garrisons: int = 2):
        """Set up the simulation with initial entities."""
        # Create hideouts
        self.hideouts = Hideout.create_random(self.grid, num_hideouts)

        # Create garrisons
        self.garrisons = Garrison.create_random(self.grid, num_garrisons)

        # Create treasures
        self.treasures = Treasure.create_random(self.grid, num_treasures)

        # Create knights
        self.knights = Knight.create_random(self.grid, num_knights, self.garrisons)

        # Create hunters - directly create hunters on empty cells
        self.hunters = []
        total_hunters = num_hideouts * num_hunters_per_hideout
        attempts = 0
        created = 0

        while created < total_hunters and attempts < 100:
            # Find an empty cell
            x = random.randint(0, self.grid.width - 1)
            y = random.randint(0, self.grid.height - 1)
            location = Location(x, y)

            # Check if cell is empty
            if self.grid.get_entity_at(location) is None:
                # Choose random skill
                skill = random.choice(list(HunterSkill))

                # Create hunter
                hunter = TreasureHunter(location, skill)

                # Place on grid
                if self.grid.place_entity(hunter):
                    self.hunters.append(hunter)
                    created += 1

                    # Find nearest hideout and add to knowledge
                    nearest_hideout = None
                    min_distance = float('inf')

                    for hideout in self.hideouts:
                        distance = calculate_wrapped_distance(
                            hunter.location.x, hunter.location.y,
                            hideout.location.x, hideout.location.y,
                            self.grid.width, self.grid.height
                        )

                        if distance < min_distance:
                            min_distance = distance
                            nearest_hideout = hideout

                    if nearest_hideout:
                        hunter.knowledge.add_hideout_location(nearest_hideout.location)

            attempts += 1

        self.setup_complete = True
        self.running = True  # Set as running immediately after setup

    def step(self):
        """Perform one step of the simulation."""
        if not self.running:
            return

        # Update hideouts first to handle knowledge sharing
        for hideout in self.hideouts:
            hideout.update(self.grid)

        # Then update all other entities
        for entity in list(self.grid.entities):  # Create a copy to avoid modification during iteration
            if entity.type != EntityType.HIDEOUT:  # Skip hideouts as they're already updated
                entity.update(self.grid)

        self.step_count += 1

        # Update entity lists
        self._update_entity_lists()

        # Check stopping conditions
        if (not self.grid.has_treasure()) and (not self.grid.has_hunters()):
            self.running = False

    def _update_entity_lists(self):
        """Update the entity lists to reflect the current state of the grid."""
        self.hideouts = [e for e in self.grid.entities if e.type == EntityType.HIDEOUT]
        self.hunters = [e for e in self.grid.entities if e.type == EntityType.HUNTER]
        self.treasures = [e for e in self.grid.entities if e.type == EntityType.TREASURE]
        self.knights = [e for e in self.grid.entities if e.type == EntityType.KNIGHT]
        self.garrisons = [e for e in self.grid.entities if e.type == EntityType.GARRISON]

    def get_stats(self):
        """Get current simulation statistics."""
        # Count entities
        entity_counts = self.grid.count_entities_by_type()

        # Calculate total treasure stored in hideouts
        total_stored_value = sum(hideout.stored_treasure for hideout in self.hideouts)
        total_stored_count = sum(hideout.stored_treasure_count for hideout in self.hideouts)

        # Calculate total hunter wealth
        total_hunter_wealth = sum(hunter.wealth for hunter in self.hunters)

        # Return statistics
        return {
            "step_count": self.step_count,
            "hunters": entity_counts[EntityType.HUNTER],
            "treasures": entity_counts[EntityType.TREASURE],
            "knights": entity_counts[EntityType.KNIGHT],
            "hideouts": entity_counts[EntityType.HIDEOUT],
            "garrisons": entity_counts[EntityType.GARRISON],
            "total_treasure_collected": total_stored_value,
            "total_treasure_pieces_collected": total_stored_count,
            "total_hunter_wealth": total_hunter_wealth
        }