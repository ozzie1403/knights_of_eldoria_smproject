import random
from typing import List, Optional
from .entity import Entity, Position, EntityType
from .types import TreasureType, HunterState


class TreasureCollectorAI:
    """AI controller for hunters in COLLECTING state."""

    def __init__(self, hunter, grid_width: int, grid_height: int):
        self.hunter = hunter
        self.target_treasure = None
        self.grid_width = grid_width
        self.grid_height = grid_height

    def update(self, grid, entities) -> None:
        """Update the hunter's collecting behavior."""
        # If already carrying treasure, transition to returning
        if self.hunter.carrying_treasure:
            print(f"Hunter {self.hunter.id} already carrying treasure, transitioning to RETURNING")
            self.hunter.state = HunterState.RETURNING
            return

        # Check if we're at a treasure position
        entity_at_position = grid.get_entity_at(self.hunter.position)
        if entity_at_position and entity_at_position.type == EntityType.TREASURE:
            print(f"Hunter {self.hunter.id} at treasure position, collecting")
            self.hunter._collect_treasure(entity_at_position, grid)
            self.hunter.state = HunterState.RETURNING
            return

        # Find best treasure if we don't have a target
        if not self.target_treasure:
            self.target_treasure = self._find_best_treasure(entities)
            if not self.target_treasure:
                print(f"Hunter {self.hunter.id} no treasure found, transitioning to EXPLORING")
                self.hunter.state = HunterState.EXPLORING
                return

        # Move towards treasure
        print(f"Hunter {self.hunter.id} moving towards treasure at {self.target_treasure.position}")
        self.hunter._move_towards_target(grid, self.target_treasure.position)
        self.hunter._decrease_stamina()

    def _find_best_treasure(self, entities) -> Optional[Entity]:
        """Find the best treasure to collect."""
        visible_treasures = [
            entity for entity in entities
            if entity.type == EntityType.TREASURE and
               self.hunter.toroidal_distance_to(entity, self.grid_width, self.grid_height) <= 5
        ]

        if not visible_treasures:
            return None

        return sorted(
            visible_treasures,
            key=lambda t: {
                TreasureType.GOLD: 3,
                TreasureType.SILVER: 2,
                TreasureType.BRONZE: 1
            }[t.treasure_type],
            reverse=True
        )[0]


class HideoutReturnAI:
    """AI controller for hunters in RETURNING state."""

    def __init__(self, hunter, grid_width: int, grid_height: int):
        self.hunter = hunter
        self.target_hideout = None
        self.grid_width = grid_width
        self.grid_height = grid_height

    def update(self, grid, entities) -> None:
        """Update the hunter's returning behavior."""
        # Find hideout if we don't have a target
        if not self.target_hideout:
            self.target_hideout = self._find_hideout(entities)
            if not self.target_hideout:
                print(f"Hunter {self.hunter.id} no hideout found, transitioning to EXPLORING")
                self.hunter.state = HunterState.EXPLORING
                return

        # If at hideout position, deposit treasure
        if self.hunter.position == self.target_hideout.position:
            print(f"Hunter {self.hunter.id} at hideout position, depositing treasure")
            self.hunter._deposit_treasure(grid)
            if self.hunter.stamina <= 6:
                print(f"Hunter {self.hunter.id} low stamina, transitioning to RESTING")
                self.hunter.state = HunterState.RESTING
            else:
                print(f"Hunter {self.hunter.id} transitioning to EXPLORING")
                self.hunter.state = HunterState.EXPLORING
        else:
            # Move towards hideout
            print(f"Hunter {self.hunter.id} moving towards hideout at {self.target_hideout.position}")
            self.hunter._move_towards_target(grid, self.target_hideout.position)
            self.hunter._decrease_stamina()

    def _find_hideout(self, entities) -> Optional[Entity]:
        """Find the best hideout to return to."""
        hideouts = [e for e in entities if e.type == EntityType.HIDEOUT]
        if not hideouts:
            return None

        # Find the hideout with the most wealth and within range
        best_hideout = None
        best_score = float('-inf')

        for hideout in hideouts:
            # Calculate distance to hideout
            distance = self.hunter.toroidal_distance_to(hideout, self.grid_width, self.grid_height)

            # Calculate score based on wealth and distance
            # Higher wealth and closer distance = better score
            score = hideout.wealth - distance

            if score > best_score:
                best_score = score
                best_hideout = hideout

        if best_hideout:
            print(
                f"Hunter {self.hunter.id} selected hideout with wealth {best_hideout.wealth} at distance {best_score}")

        return best_hideout


class HideoutAI:
    """AI controller for hideouts to attract hunters."""

    def __init__(self, hideout, grid_width: int, grid_height: int):
        self.hideout = hideout
        self.attraction_radius = 10  # Radius within which hunters can sense the hideout
        self.attraction_strength = 1.0  # Base attraction strength
        self.grid_width = grid_width
        self.grid_height = grid_height

    def update(self, grid, entities) -> None:
        """Update the hideout's attraction behavior."""
        # Calculate attraction strength based on collected treasure
        current_attraction = self.attraction_strength * (1 + self.hideout.wealth / 100.0)

        # Find hunters within attraction radius
        nearby_hunters = [
            entity for entity in entities
            if entity.type == EntityType.HUNTER and
               self.hideout.toroidal_distance_to(entity, self.grid_width, self.grid_height) <= self.attraction_radius
        ]

        # Influence hunters to return to this hideout
        for hunter in nearby_hunters:
            if hunter.state == HunterState.RETURNING:
                # If hunter is already returning, increase chance of choosing this hideout
                if random.random() < 0.3:  # 30% chance to switch to this hideout
                    hunter.hideout_position = self.hideout.position
            elif hunter.state == HunterState.COLLECTING and hunter.carrying_treasure:
                # If hunter has treasure, increase chance of choosing this hideout
                if random.random() < 0.2:  # 20% chance to switch to this hideout
                    hunter.hideout_position = self.hideout.position
                    hunter.state = HunterState.RETURNING