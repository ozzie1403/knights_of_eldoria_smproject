import random
import time
from typing import List, Dict, Optional, Tuple
import uuid

from models.entity import Entity, EntityType, Position
from models.grid import Grid
from models.hunter import TreasureHunter
from models.hideout import Hideout
from models.garrison import Garrison
from models.treasure import Treasure
from models.types import TreasureType, HunterSkill, HunterState


class SimulationManager:
    """
    Manages the Knights of Eldoria simulation, including entity creation,
    simulation step processing, statistics tracking, and simulation control.
    """

    def __init__(self, grid_width: int = 20, grid_height: int = 20,
                 hunter_count: int = 5,
                 hideout_count: int = 3, garrison_count: int = 2,
                 treasure_count: int = 15):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = Grid(grid_width, grid_height)
        self.entities: List[Entity] = []
        self.step_count = 0
        self.is_running = False
        self.is_complete = False
        self.completion_reason = ""

        # Entity counts
        self.hunter_count = hunter_count
        self.hideout_count = hideout_count
        self.garrison_count = garrison_count
        self.treasure_count = treasure_count

        # Treasure distribution
        self.treasure_distribution = {
            TreasureType.BRONZE: 0.5,  # 50% bronze
            TreasureType.SILVER: 0.3,  # 30% silver
            TreasureType.GOLD: 0.2  # 20% gold
        }

        # Statistics
        self.stats = {
            'treasure_collected': {
                TreasureType.BRONZE: 0.0,
                TreasureType.SILVER: 0.0,
                TreasureType.GOLD: 0.0,
                'total': 0.0
            },
            'hunters_lost': 0,
            'hunters_recruited': 0,
            'average_hunter_stamina': 0.0,
            'remaining_treasures': 0,
            'remaining_hunters': 0
        }

        # Initialize simulation
        self.initialize()

    def initialize(self) -> None:
        """Initialize the simulation by creating the grid and entities."""
        # Clear existing state
        self.grid = Grid(self.grid_width, self.grid_height)
        self.entities = []
        self.step_count = 0
        self.is_running = False
        self.is_complete = False
        self.completion_reason = ""

        # Reset statistics
        self.stats = {
            'treasure_collected': {
                TreasureType.BRONZE: 0.0,
                TreasureType.SILVER: 0.0,
                TreasureType.GOLD: 0.0,
                'total': 0.0
            },
            'hunters_lost': 0,
            'hunters_recruited': 0,
            'average_hunter_stamina': 0.0,
            'remaining_treasures': 0,
            'remaining_hunters': 0
        }

        # Create entities
        self._create_hideouts()
        self._create_garrisons()
        self._create_hunters()
        self._create_treasures()

        # Update statistics
        self._update_statistics()

    def _get_random_empty_position(self) -> Position:
        """Get a random empty position on the grid."""
        while True:
            x = random.randint(0, self.grid.width - 1)
            y = random.randint(0, self.grid.height - 1)
            position = Position(x, y)
            if self.grid.get_entity_at(position) is None:
                return position

    def _create_hideouts(self) -> None:
        """Create hideout entities and place them on the grid."""
        for i in range(self.hideout_count):
            position = self._get_random_empty_position()
            hideout = Hideout(
                f"Hideout-{i}",
                position,
                self.grid.width,
                self.grid.height
            )
            self.entities.append(hideout)
            self.grid.place_entity(hideout)

    def _create_garrisons(self) -> None:
        """Create garrison entities and place them on the grid."""
        empty_positions = self.grid.find_empty_positions(self.garrison_count)
        for i, position in enumerate(empty_positions):
            garrison = Garrison(f"garrison_{i}", position)
            self.entities.append(garrison)
            self.grid.place_entity(garrison)

    def _create_hunters(self) -> None:
        """Create hunter entities and place them at hideouts."""
        for i in range(self.hunter_count):
            position = self._get_random_empty_position()
            hunter = TreasureHunter(
                f"Hunter-{i}",
                position,
                random.choice(list(HunterSkill)),
                self.grid.width,
                self.grid.height
            )
            self.entities.append(hunter)
            self.grid.place_entity(hunter)

    def _create_treasures(self) -> None:
        """Create treasure entities and place them on the grid."""
        empty_positions = self.grid.find_empty_positions(self.treasure_count)
        for i, position in enumerate(empty_positions):
            # Determine treasure type based on distribution
            treasure_type = self._select_treasure_type()
            treasure = Treasure(f"treasure_{i}", position, treasure_type)
            self.entities.append(treasure)
            self.grid.place_entity(treasure)

    def _select_treasure_type(self) -> TreasureType:
        """Select a treasure type based on the distribution."""
        r = random.random()
        if r < self.treasure_distribution[TreasureType.BRONZE]:
            return TreasureType.BRONZE
        elif r < self.treasure_distribution[TreasureType.BRONZE] + self.treasure_distribution[TreasureType.SILVER]:
            return TreasureType.SILVER
        else:
            return TreasureType.GOLD

    def step(self) -> None:
        """Process one step of the simulation."""
        if self.is_complete:
            return

        self.step_count += 1

        # Update entity knowledge of the current step
        self._update_entity_step_knowledge()

        # Process all entity actions
        self._process_entity_actions()

        # Remove depleted treasures and collapsed hunters
        self._remove_depleted_entities()

        # Handle hideout recruitment
        self._process_recruitment()

        # Update statistics
        self._update_statistics()

        # Check for simulation completion
        self._check_completion()

    def _update_entity_step_knowledge(self) -> None:
        """Update entities with knowledge of the current step."""
        for entity in self.entities:
            if hasattr(entity, '_get_current_step'):
                entity._current_step = self.step_count

    def _process_entity_actions(self) -> None:
        """Process actions for all entities."""
        # Copy the entities list to avoid modification issues during iteration
        current_entities = list(self.entities)

        # Process each entity
        for entity in current_entities:
            if entity in self.entities:  # Entity might have been removed
                entity.act(self.grid, self.entities)

    def _remove_depleted_entities(self) -> None:
        """Remove depleted treasures and collapsed hunters."""
        # Find entities to remove
        to_remove = []

        for entity in self.entities:
            if entity.type == EntityType.TREASURE:
                if entity.is_fully_depleted():
                    to_remove.append(entity)
            elif entity.type == EntityType.HUNTER:
                if entity.isCollapsed():
                    to_remove.append(entity)
                    self.stats['hunters_lost'] += 1

        # Remove entities
        for entity in to_remove:
            self.grid.remove_entity(entity)
            self.entities.remove(entity)

    def _process_recruitment(self) -> None:
        """Process recruitment of new hunters by hideouts."""
        # Count current hunters
        current_hunters = len([e for e in self.entities if e.type == EntityType.HUNTER])

        # If we're at or above the limit, remove any excess hunters
        if current_hunters >= self.hunter_count:
            # Find excess hunters
            hunters = [e for e in self.entities if e.type == EntityType.HUNTER]
            excess = current_hunters - self.hunter_count
            if excess > 0:
                # Remove the most recently recruited hunters
                for hunter in hunters[-excess:]:
                    self.grid.remove_entity(hunter)
                    self.entities.remove(hunter)
            return

        hideouts = [e for e in self.entities if e.type == EntityType.HIDEOUT]

        for hideout in hideouts:
            # Check if this hideout can recruit
            if len(hideout.occupants) >= hideout.max_occupants:
                continue

            if hideout.treasure_collected < 100.0:
                continue

            # Try to recruit (20% chance)
            if random.random() < 0.2:
                # Create a new hunter
                new_id = f"hunter_{uuid.uuid4().hex[:8]}"
                skill = random.choice(list(HunterSkill))

                # Find an empty position near the hideout
                near_positions = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue  # Skip the hideout's position

                        nx = (hideout.position.x + dx) % self.grid_width
                        ny = (hideout.position.y + dy) % self.grid_height
                        pos = Position(nx, ny)

                        if self.grid.get_entity_at(pos) is None:
                            near_positions.append(pos)

                if near_positions:
                    # Choose a random nearby empty position
                    spawn_pos = random.choice(near_positions)

                    # Create and place the new hunter
                    hunter = TreasureHunter(new_id, spawn_pos, skill)
                    self.entities.append(hunter)
                    self.grid.place_entity(hunter)
                    self.stats['hunters_recruited'] += 1

                    # Check if we've reached the maximum number of hunters
                    current_hunters = len([e for e in self.entities if e.type == EntityType.HUNTER])
                    if current_hunters >= self.hunter_count:
                        break

    def _update_statistics(self) -> None:
        """Update simulation statistics."""
        # Count entities by type
        hunters = [e for e in self.entities if e.type == EntityType.HUNTER]
        treasures = [e for e in self.entities if e.type == EntityType.TREASURE]
        hideouts = [e for e in self.entities if e.type == EntityType.HIDEOUT]

        # Update counts
        self.stats['remaining_treasures'] = len(treasures)
        self.stats['remaining_hunters'] = len(hunters)

        # Calculate averages
        if hunters:
            total_stamina = sum(h.stamina for h in hunters)
            self.stats['average_hunter_stamina'] = total_stamina / len(hunters)
        else:
            self.stats['average_hunter_stamina'] = 0

        # Update treasure collection (from hideouts)
        total_collected = 0
        for hideout in hideouts:
            total_collected += hideout.treasure_collected

        self.stats['treasure_collected']['total'] = total_collected

    def _check_completion(self) -> None:
        """Check if the simulation is complete."""
        # Check if all treasure is gone
        if self.stats['remaining_treasures'] == 0:
            self.is_complete = True
            self.completion_reason = "All treasure has been collected or depleted"
            self._print_final_reports()
            return

        # Check if all hunters are gone and cannot be replaced
        if self.stats['remaining_hunters'] == 0:
            # Check if hunters can be recruited
            hideouts = [e for e in self.entities if e.type == EntityType.HIDEOUT]
            can_recruit_more = any(len(h.occupants) < 5 for h in hideouts)

            if not can_recruit_more:
                self.is_complete = True
                self.completion_reason = "All hunters have been eliminated and cannot be replaced"
                self._print_final_reports()
                return

    def _print_final_reports(self) -> None:
        """Print final reports for all hunters."""
        print("\n=== SIMULATION COMPLETE ===")
        print(f"Reason: {self.completion_reason}")
        print(f"Total Steps: {self.step_count}")
        print("\n=== FINAL STATISTICS ===")
        print(f"Total Treasure Collected: {self.stats['treasure_collected']['total']:.1f}")
        print(f"Hunters Lost: {self.stats['hunters_lost']}")
        print(f"Hunters Recruited: {self.stats['hunters_recruited']}")

        # Get all hunters (including those that were removed)
        all_hunters = [e for e in self.entities if e.type == EntityType.HUNTER]
        if all_hunters:
            print("\n=== HUNTER REPORTS ===")
            # Sort hunters by wealth
            sorted_hunters = sorted(all_hunters, key=lambda h: h.wealth, reverse=True)
            for hunter in sorted_hunters:
                print(hunter.get_report())
        else:
            print("\nNo surviving hunters to report on.")

    def start(self) -> None:
        """Start the simulation."""
        self.is_running = True

    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False

    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        self.initialize()

    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        """Get the entity at the specified position."""
        position = Position(x, y)
        return self.grid.get_entity_at(position)

    def get_statistics(self) -> Dict:
        """Get the current simulation statistics."""
        return self.stats

    def is_simulation_complete(self) -> bool:
        """Check if the simulation is complete."""
        return self.is_complete

    def get_completion_reason(self) -> str:
        """Get the reason for simulation completion."""
        return self.completion_reason