import random
from enum import Enum
from .entity import EntityType, Entity, Position
from .treasure import TreasureType
from .ai_controllers import TreasureCollectorAI, HideoutReturnAI


class HunterState(Enum):
    EXPLORING = 1
    COLLECTING = 2
    RETURNING = 3
    RESTING = 4
    COLLAPSED = 5


class TreasureHunter(Entity):
    def __init__(self, name: str, position: Position, skill, grid_width: int, grid_height: int):
        super().__init__(name, EntityType.HUNTER, position)
        self.state = HunterState.EXPLORING
        self.memory = {'treasures': []}
        self.skill = skill
        self.hideout_position = position  # Initially set to spawn position
        self.stamina = 100
        self.carrying_treasure = None
        self.steps_without_rest = 0
        self.collapsed_steps = 0
        self.wealth = 0.0
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Statistics tracking
        self.treasures_collected = {
            TreasureType.GOLD: 0,
            TreasureType.SILVER: 0,
            TreasureType.BRONZE: 0
        }
        self.total_distance_traveled = 0
        self.times_collapsed = 0

        # Set visual properties
        self.icon = "H"  # Hunter icon
        self.color = "#FFA500"  # Orange color

        # Initialize AI controllers
        self.collector_ai = TreasureCollectorAI(self, grid_width, grid_height)
        self.return_ai = HideoutReturnAI(self, grid_width, grid_height)

    def get_report(self) -> str:
        """Generate a detailed report of the hunter's performance."""
        total_treasures = sum(self.treasures_collected.values())
        total_value = (
                self.treasures_collected[TreasureType.GOLD] * 3.0 +
                self.treasures_collected[TreasureType.SILVER] * 2.0 +
                self.treasures_collected[TreasureType.BRONZE] * 1.0
        )

        report = [
            f"\nHunter {self.id} Final Report:",
            f"Skill Level: {self.skill.name}",
            f"Final Wealth: {self.wealth:.1f}",
            f"Treasures Collected:",
            f"  - Gold: {self.treasures_collected[TreasureType.GOLD]}",
            f"  - Silver: {self.treasures_collected[TreasureType.SILVER]}",
            f"  - Bronze: {self.treasures_collected[TreasureType.BRONZE]}",
            f"Total Treasures: {total_treasures}",
            f"Total Value: {total_value:.1f}",
            f"Distance Traveled: {self.total_distance_traveled} tiles",
            f"Times Collapsed: {self.times_collapsed}",
            f"Final State: {self.state.name}",
            f"Final Stamina: {self.stamina}"
        ]

        return "\n".join(report)

    def isCollapsed(self) -> bool:
        return self.state == HunterState.COLLAPSED

    def drop_treasure(self) -> None:
        """Drop any treasure being carried."""
        if self.carrying_treasure:
            self.carrying_treasure = None
            self.state = HunterState.EXPLORING

    def act(self, grid, entities):
        if self.state == HunterState.COLLAPSED:
            self.collapsed_steps += 1
            if self.collapsed_steps >= 3:
                grid.remove_entity(self)
            return

        if self.stamina <= 0:
            self.state = HunterState.COLLAPSED
            self.collapsed_steps = 0
            return

        # Update memory with visible treasures and hideouts
        self.memory['treasures'] = [
            entity for entity in entities
            if entity.type == EntityType.TREASURE and
               self.toroidal_distance_to(entity, self.grid_width, self.grid_height) <= 5
        ]

        # Update hideout position if we see a better one
        visible_hideouts = [
            entity for entity in entities
            if entity.type == EntityType.HIDEOUT and
               self.toroidal_distance_to(entity, self.grid_width, self.grid_height) <= 10
        ]

        if visible_hideouts:
            # Find the best hideout based on wealth and distance
            best_hideout = max(
                visible_hideouts,
                key=lambda h: h.wealth - self.toroidal_distance_to(h, self.grid_width, self.grid_height)
            )
            self.hideout_position = best_hideout.position

        if self.state == HunterState.EXPLORING:
            treasure = self._find_best_treasure()
            if treasure:
                self.state = HunterState.COLLECTING
            else:
                self._explore(grid)
                self._decrease_stamina()

        elif self.state == HunterState.COLLECTING:
            self.collector_ai.update(grid, entities)

        elif self.state == HunterState.RETURNING:
            self.return_ai.update(grid, entities)

        elif self.state == HunterState.RESTING:
            self.stamina += 1
            if self.stamina > 6:
                self.state = HunterState.EXPLORING

    def _find_best_treasure(self):
        if not self.memory['treasures']:
            return None
        return sorted(
            self.memory['treasures'],
            key=lambda t: {
                TreasureType.GOLD: 3,
                TreasureType.SILVER: 2,
                TreasureType.BRONZE: 1
            }[t.treasure_type],
            reverse=True
        )[0]

    def _explore(self, grid):
        """Move randomly to explore the grid."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        new_x = (self.position.x + dx) % grid.width
        new_y = (self.position.y + dy) % grid.height
        new_position = Position(new_x, new_y)

        # Try to move to the new position
        if grid.move_entity(self, new_position):
            return

        # If blocked, try other directions
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = (self.position.x + dx) % grid.width
            new_y = (self.position.y + dy) % grid.height
            new_position = Position(new_x, new_y)
            if grid.move_entity(self, new_position):
                return

    def _move_towards_target(self, grid, target_position):
        """Move towards a target position."""
        # Get next step towards target
        next_position = self.position.get_next_step_towards(
            target_position, self.grid_width, self.grid_height)

        print(f"Hunter {self.id} current position: {self.position}, target: {target_position}, next: {next_position}")

        # Try to move to the next position
        if grid.move_entity(self, next_position):
            self.total_distance_traveled += 1
            print(f"Hunter {self.id} moved to {next_position}")
            return

        # If blocked, try adjacent positions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x = (self.position.x + dx) % self.grid_width
            new_y = (self.position.y + dy) % self.grid_height
            new_position = Position(new_x, new_y)
            if grid.move_entity(self, new_position):
                self.total_distance_traveled += 1
                print(f"Hunter {self.id} moved to adjacent position {new_position}")
                return

        print(f"Hunter {self.id} failed to move from {self.position}")
        # If we couldn't move, ensure we're still on the grid
        if not grid.get_entity_at(self.position):
            grid.place_entity(self)

    def _collect_treasure(self, treasure_entity, grid):
        """Collect treasure from the current position."""
        print(f"Hunter {self.id} collecting treasure {treasure_entity.id}")
        # Store the treasure entity
        self.carrying_treasure = treasure_entity
        # Remove the treasure from the grid
        grid.remove_entity(treasure_entity)
        # Remove the treasure from memory
        if treasure_entity in self.memory['treasures']:
            self.memory['treasures'].remove(treasure_entity)
        # Ensure the hunter is still on the grid
        if not grid.get_entity_at(self.position):
            grid.place_entity(self)
        # Clear the target treasure
        if hasattr(self, 'collector_ai'):
            self.collector_ai.target_treasure = None
        print(f"Hunter {self.id} now carrying treasure at position {self.position}")
        # Transition to RETURNING state
        self.state = HunterState.RETURNING

    def _deposit_treasure(self, grid):
        """Deposit treasure at the current hideout."""
        if self.carrying_treasure:
            print(f"Hunter {self.id} depositing treasure")
            # Add treasure value to wealth
            treasure_value = {
                TreasureType.GOLD: 3.0,
                TreasureType.SILVER: 2.0,
                TreasureType.BRONZE: 1.0
            }[self.carrying_treasure.treasure_type]
            self.wealth += treasure_value
            # Update statistics
            self.treasures_collected[self.carrying_treasure.treasure_type] += 1
            self.carrying_treasure = None
            # Clear the target hideout
            if hasattr(self, 'return_ai'):
                self.return_ai.target_hideout = None
            # Reset state to exploring
            self.state = HunterState.EXPLORING
            print(f"Hunter {self.id} deposited treasure, new wealth: {self.wealth}")

    def _decrease_stamina(self):
        self.stamina -= 2
        if self.stamina <= 0:
            self.state = HunterState.COLLAPSED
            self.collapsed_steps = 0
