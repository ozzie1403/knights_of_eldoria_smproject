from models.grid import Grid
from models.hideout import Hideout
from models.treasure_hunter import TreasureHunter
from models.treasure import Treasure
from models.knight import Knight
from models.garrison import Garrison
from utils.constants import EntityType, DEFAULT_GRID_SIZE
import random


class Simulation:
    """Main simulation class for Knights of Eldoria."""

    def __init__(self, grid_size: int = DEFAULT_GRID_SIZE):
        self.grid = Grid(grid_size, grid_size)
        self.running = False
        self.setup_complete = False
        self.total_treasure_collected = 0
        self.total_hunters_lost = 0
        self.step_count = 0

    def setup(self, num_hideouts: int = 3, num_hunters_per_hideout: int = 2,
              num_treasures: int = 30, num_knights: int = 2, num_garrisons: int = 2):
        """Set up the simulation with initial entities."""
        # Create hideouts
        self.hideouts = Hideout.create_random(self.grid, num_hideouts)

        # Create garrisons
        self.garrisons = Garrison.create_random(self.grid, num_garrisons)

        # Create hunters
        self.hunters = TreasureHunter.create_random(self.grid, self.hideouts, num_hunters_per_hideout)

        # Create treasures
        self.treasures = Treasure.create_random(self.grid, num_treasures)

        # Create knights
        self.knights = Knight.create_random(self.grid, num_knights, self.garrisons)

        self.setup_complete = True

    def start(self):
        """Start the simulation."""
        if not self.setup_complete:
            raise RuntimeError("Simulation setup must be completed before starting")

        self.running = True

    def stop(self):
        """Stop the simulation."""
        self.running = False

    def step(self):
        """Perform one step of the simulation."""
        if not self.running:
            return

        # Perform grid step (updates all entities)
        self.grid.step()
        self.step_count += 1

        # Check stopping conditions - only stop if all treasure is gone AND no hunters remain
        if (not self.grid.has_treasure()) and (not self.grid.has_hunters()):
            self.running = False

    def get_stats(self):
        """Get current simulation statistics."""
        # Count entities
        entity_counts = self.grid.count_entities_by_type()

        # Calculate total treasure stored in hideouts
        total_stored = sum(hideout.stored_treasure for hideout in self.hideouts)

        # Return statistics
        return {
            "step_count": self.step_count,
            "hunters": entity_counts[EntityType.HUNTER],
            "treasures": entity_counts[EntityType.TREASURE],
            "knights": entity_counts[EntityType.KNIGHT],
            "hideouts": entity_counts[EntityType.HIDEOUT],
            "garrisons": entity_counts[EntityType.GARRISON],
            "total_treasure_collected": total_stored
        }

    def reset(self):
        """Reset the simulation."""
        grid_size = self.grid.width  # Preserve grid size
        self.__init__(grid_size)