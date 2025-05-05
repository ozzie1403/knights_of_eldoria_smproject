import random
from typing import List, Optional
from models.entity import Entity, EntityType, Position
from models.types import KnightState


class Knight(Entity):
    """
    Represents a knight in the simulation. Knights patrol the grid,
    detect and pursue hunters, and challenge them when caught.
    """

    def __init__(self, entity_id: str, position: Position):
        super().__init__(entity_id, EntityType.KNIGHT, position)
        self.state = KnightState.PATROLLING
        self.energy = 100.0  # Full energy
        self.detection_radius = 3  # Detect hunters within this radius
        self.target_id = None  # ID of hunter being pursued
        self.patrol_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.rest_threshold = 20.0  # Rest when energy <= 20%
        self.energy_recovery_rate = 10.0  # Recover 10% per step when resting
        self.pursuit_energy_cost = 20.0  # Cost 20% energy to chase

        # Set visual properties
        self.icon = "K"
        self.color = "#8B0000"  # Dark red

    def act(self, grid, entities: List[Entity]) -> None:
        """Perform the knight's action for this simulation step."""
        if self.state == KnightState.RESTING:
            self._rest()
            if self.energy >= 80.0:  # Fully rested
                self.state = KnightState.PATROLLING

        elif self.state == KnightState.PATROLLING:
            # Check for nearby hunters
            hunters = self._detect_hunters(grid, entities)
            if hunters:
                # Choose a target and pursue
                target = random.choice(hunters)
                self.target_id = target.id
                self.state = KnightState.PURSUING
                self.energy -= self.pursuit_energy_cost  # Energy cost to start pursuit
            else:
                # Continue patrolling
                self._patrol(grid)

        elif self.state == KnightState.PURSUING:
            # Check if we need to rest
            if self.energy <= self.rest_threshold:
                self._seek_garrison(grid, entities)
                return

            # Find the target
            target = next((e for e in entities if e.id == self.target_id), None)
            if not target:
                # Target lost or no longer exists
                self.state = KnightState.PATROLLING
                self.target_id = None
                return

            # Move towards the target
            self._pursue_target(grid, target)

            # Check if we caught the target
            if self.position.x == target.position.x and self.position.y == target.position.y:
                self._challenge_hunter(target)
                self.state = KnightState.PATROLLING
                self.target_id = None

    def _detect_hunters(self, grid, entities: List[Entity]) -> List[Entity]:
        """Detect hunters within the detection radius."""
        hunters = []
        for entity in entities:
            if entity.type == EntityType.HUNTER:
                distance = self.toroidal_distance_to(entity, grid.width, grid.height)
                if distance <= self.detection_radius:
                    # TODO: Apply stealth skill modifier
                    hunters.append(entity)
        return hunters

    def _patrol(self, grid) -> None:
        """Move in the patrol direction, changing direction randomly."""
        # Randomly change direction sometimes
        if random.random() < 0.2:  # 20% chance to change direction
            self.patrol_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

        # Move in the patrol direction
        dx, dy = self.patrol_direction
        new_x = (self.position.x + dx) % grid.width
        new_y = (self.position.y + dy) % grid.height
        new_position = Position(new_x, new_y)

        # If the cell is occupied, try a different direction
        if not grid.move_entity(self, new_position):
            self.patrol_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

    def _pursue_target(self, grid, target: Entity) -> None:
        """Move towards the target hunter."""
        # Get next step towards target
        next_position = self.position.get_next_step_towards(
            target.position, grid.width, grid.height)

        # Try to move to the next position
        if not grid.move_entity(self, next_position):
            # If blocked, try a different approach
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                new_x = (self.position.x + dx) % grid.width
                new_y = (self.position.y + dy) % grid.height
                new_position = Position(new_x, new_y)
                if grid.move_entity(self, new_position):
                    break

    def _challenge_hunter(self, hunter) -> None:
        """Challenge a hunter that has been caught."""
        self.state = KnightState.CHALLENGING

        # Decide on challenge type
        if random.random() < 0.4:  # 40% chance for a severe challenge
            # Severe challenge (20% stamina loss)
            hunter.lose_stamina(20.0)
        else:
            # Mild challenge (5% stamina loss)
            hunter.lose_stamina(5.0)

        # Hunter drops treasure
        hunter.drop_treasure()

    def _seek_garrison(self, grid, entities: List[Entity]) -> None:
        """Find and move towards the nearest garrison to rest."""
        # Find all garrisons
        garrisons = [e for e in entities if e.type == EntityType.GARRISON]
        if not garrisons:
            # No garrisons, just rest in place
            self.state = KnightState.RESTING
            return

        # Find the nearest garrison
        nearest = min(garrisons, key=lambda g:
        self.toroidal_distance_to(g, grid.width, grid.height))

        # Move towards the garrison
        next_position = self.position.get_next_step_towards(
            nearest.position, grid.width, grid.height)

        # Try to move to the next position
        if grid.move_entity(self, next_position):
            # If we reached the garrison, start resting
            if self.position.x == nearest.position.x and self.position.y == nearest.position.y:
                self.state = KnightState.RESTING
        else:
            # If blocked, just rest in place
            self.state = KnightState.RESTING

    def _rest(self) -> None:
        """Recover energy while resting."""
        self.energy = min(100.0, self.energy + self.energy_recovery_rate)