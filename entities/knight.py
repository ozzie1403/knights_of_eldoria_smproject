from typing import Tuple, List, Optional, Set, TYPE_CHECKING
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from .base_entity import BaseEntity, EntityType
from .hunter import Hunter
from .treasure import Treasure
from .garrison import Garrison

if TYPE_CHECKING:
    from .garrison import Garrison

import random

# Define possible movement directions (8-way movement)
DIRECTIONS = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1)
]


class Knight(BaseEntity):
    def __init__(self, position: Tuple[int, int]):
        super().__init__(EntityType.KNIGHT, position)
        self.patrol_route: List[Tuple[int, int]] = []
        self.current_route_index = 0
        self.target_hunter: Optional[Hunter] = None
        self.detection_radius = 3
        self.energy = 100.0  # Energy level (0-100)
        self.is_resting = False
        self.resting_timer = 0
        self.aggression = random.uniform(0.0, 1.0)  # Random aggression level
        self.current_garrison: Optional['Garrison'] = None
        self.known_garrisons: Set[Tuple[int, int]] = set()

        # Machine learning components
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.hunter_patterns = []  # Store successful hunter capture patterns
        self.patrol_patterns = []  # Store successful patrol patterns

        # Initialize with some default patterns to fit the scaler
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize with some default patterns to fit the scaler"""
        # Create initial features for fitting
        initial_features = [
            [0.0, 0.0, 0.1, 0.1, 1.0, 0.5, 0.2, 1],
            # pos_x, pos_y, hunter_x, hunter_y, energy, aggression, distance, success
            [0.1, 0.1, 0.2, 0.2, 0.75, 0.7, 0.2, 1],
            [0.2, 0.2, 0.3, 0.3, 0.5, 0.3, 0.2, 0]
        ]

        # Fit the scaler with initial features
        self.scaler.fit(initial_features)

        # Initialize default patterns
        default_patterns = [
            {
                'position': (0, 0),
                'hunter_position': (1, 1),
                'energy': 100.0,
                'aggression': 0.5,
                'distance': 2.0,
                'success': True
            },
            {
                'position': (1, 1),
                'hunter_position': (2, 2),
                'energy': 75.0,
                'aggression': 0.7,
                'distance': 2.0,
                'success': True
            },
            {
                'position': (2, 2),
                'hunter_position': (3, 3),
                'energy': 50.0,
                'aggression': 0.3,
                'distance': 2.0,
                'success': False
            }
        ]
        self.hunter_patterns.extend(default_patterns)

        # Fit RandomForest with initial features
        X = self.scaler.transform(initial_features)
        y = [f[-1] for f in initial_features]  # Extract success labels
        self.rf_classifier.fit(X, y)

    def set_patrol_route(self, route: List[Tuple[int, int]]) -> None:
        """Set the patrol route for the knight"""
        self.patrol_route = route
        self.current_route_index = 0

    def _calculate_target_priority(self, hunter: Hunter, grid_size: Tuple[int, int]) -> float:
        """Calculate priority score for a hunter target"""
        priority = 0.0

        # Base priority for hunters with treasure
        if hunter.carrying_treasure:
            priority += 100.0

        # Consider distance - closer hunters get higher priority
        distance = self._distance_to(hunter.position, grid_size)
        priority += (self.detection_radius - distance) * 10.0

        # Consider hunter's stamina - lower stamina means easier target
        priority += (100.0 - hunter.stamina) * 0.5

        # Consider if hunter is resting - resting hunters are easier targets
        if hunter.resting:
            priority += 50.0

        return priority

    def _distance_to(self, pos: Tuple[int, int], grid_size: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between knight and position, considering grid wrapping"""
        x1, y1 = self.position
        x2, y2 = pos
        grid_width, grid_height = grid_size

        dx = min(abs(x1 - x2), grid_width - abs(x1 - x2))
        dy = min(abs(y1 - y2), grid_height - abs(y1 - y2))

        return dx + dy

    def analyze_hunter_patterns(self, grid, grid_size: Tuple[int, int]):
        """Analyze and learn from successful hunter capture patterns"""
        if len(self.hunter_patterns) < 10:  # Need enough data to analyze
            return

        # Convert patterns to features
        features = []
        targets = []
        for pattern in self.hunter_patterns:
            # Extract features from pattern
            pos_x, pos_y = pattern['position']
            hunter_x, hunter_y = pattern['hunter_position']
            features.append([
                pos_x / grid_size[0],  # Normalized x position
                pos_y / grid_size[1],  # Normalized y position
                hunter_x / grid_size[0],  # Normalized hunter x position
                hunter_y / grid_size[1],  # Normalized hunter y position
                pattern['energy'] / 100.0,  # Normalized energy
                pattern['aggression'],  # Aggression level
                pattern['distance'] / max(grid_size),  # Normalized distance
                1 if pattern['success'] else 0  # Binary success indicator
            ])
            targets.append(1 if pattern['success'] else 0)

        # Scale features and fit classifier
        scaled_features = self.scaler.fit_transform(features)
        self.rf_classifier.fit(scaled_features, targets)

    def predict_hunter_capture(self, hunter: Hunter, grid_size: Tuple[int, int]) -> bool:
        """Predict likelihood of successful hunter capture"""
        if not self.hunter_patterns:
            return True  # Default to aggressive behavior if no data

        # Get current state features
        current_features = [
            self.position[0] / grid_size[0],
            self.position[1] / grid_size[1],
            hunter.position[0] / grid_size[0],
            hunter.position[1] / grid_size[1],
            self.energy / 100.0,
            self.aggression,
            self._distance_to(hunter.position, grid_size) / max(grid_size)
        ]

        try:
            # Scale features
            scaled_features = self.scaler.transform([current_features])

            # Predict success probability
            success_prob = self.rf_classifier.predict_proba(scaled_features)[0][1]
            return success_prob > 0.5  # Return True if probability > 50%
        except Exception as e:
            print(f"ML prediction failed: {e}")
            # Fall back to default behavior if ML fails
            return self.aggression > 0.7 or hunter.stamina < 30.0

    def record_hunter_pattern(self, hunter: Hunter, success: bool):
        """Record a hunter capture pattern for learning"""
        pattern = {
            'position': self.position,
            'hunter_position': hunter.position,
            'energy': self.energy,
            'aggression': self.aggression,
            'distance': self._distance_to(hunter.position, (self.grid.width, self.grid.height)),
            'success': success
        }
        self.hunter_patterns.append(pattern)

        # Keep only recent patterns
        if len(self.hunter_patterns) > 100:
            self.hunter_patterns = self.hunter_patterns[-100:]

    def handle_caught_hunter(self, hunter: Hunter) -> Tuple[bool, List[Treasure]]:
        """
        Handle interaction with a caught hunter.
        Returns a tuple of (hunter_removed, dropped_treasures)
        """
        # Use ML to predict success of capture
        success = self.predict_hunter_capture(hunter, (self.grid.width, self.grid.height))

        # Record the pattern
        self.record_hunter_pattern(hunter, success)

        if success:
            # Challenge the hunter
            hunter.stamina = max(0.0, hunter.stamina - 20.0)
            print(
                f"Knight at {self.position} challenges hunter at {hunter.position}, reducing stamina to {hunter.stamina:.1f}%")
            if hunter.stamina <= 0.0:
                print(f"Hunter at {hunter.position} collapses from the challenge")
                return True, hunter.drop_treasure()
        else:
            # Detain the hunter
            hunter.stamina = max(0.0, hunter.stamina - 5.0)
            print(
                f"Knight at {self.position} detains hunter at {hunter.position}, reducing stamina to {hunter.stamina:.1f}%")
            if hunter.stamina <= 0.0:
                print(f"Hunter at {hunter.position} collapses from detention")
                return True, hunter.drop_treasure()

        # If hunter didn't collapse, just drop their treasure
        return False, hunter.drop_treasure()

    def scan_for_hunters(self, grid, grid_size: Tuple[int, int]) -> Optional[Hunter]:
        """Scan for hunters within detection radius and select the best target"""
        # Don't scan if resting or too tired
        if self.is_resting or self.energy < 20.0:
            return None

        hunters_in_range = []

        # Check current position
        for entity in grid.get_entities_at(self.position):
            if isinstance(entity, Hunter) and not entity.resting:
                hunters_in_range.append(entity)

        # Check surrounding cells up to detection radius
        for dx in range(-self.detection_radius, self.detection_radius + 1):
            for dy in range(-self.detection_radius, self.detection_radius + 1):
                if dx == 0 and dy == 0:  # Skip current position
                    continue

                nx = (self.position[0] + dx) % grid_size[0]
                ny = (self.position[1] + dy) % grid_size[1]

                for entity in grid.get_entities_at((nx, ny)):
                    if isinstance(entity, Hunter) and not entity.resting:
                        hunters_in_range.append(entity)

        if hunters_in_range:
            # Calculate priority for each hunter and select the highest priority target
            hunters_with_priority = [(h, self._calculate_target_priority(h, grid_size)) for h in hunters_in_range]
            best_hunter = max(hunters_with_priority, key=lambda x: x[1])[0]
            print(
                f"Knight at {self.position} selected hunter at {best_hunter.position} with priority score {max(hunters_with_priority, key=lambda x: x[1])[1]:.1f}")
            return best_hunter
        return None

    def scan_for_garrisons(self, grid, grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Scan for garrisons within detection radius"""
        garrisons_found = []
        for dx in range(-self.detection_radius, self.detection_radius + 1):
            for dy in range(-self.detection_radius, self.detection_radius + 1):
                nx = (self.position[0] + dx) % grid_size[0]
                ny = (self.position[1] + dy) % grid_size[1]
                for entity in grid.get_entities_at((nx, ny)):
                    if entity.entity_type == EntityType.GARRISON:
                        garrisons_found.append((nx, ny))
                        self.known_garrisons.add((nx, ny))
        return garrisons_found

    def should_retreat(self) -> bool:
        """Check if knight should retreat to garrison"""
        return self.energy <= 20.0 and not self.is_resting

    def retreat_to_garrison(self, grid, grid_size: Tuple[int, int]) -> bool:
        """Attempt to retreat to the nearest garrison"""
        if not self.known_garrisons:
            # Scan for garrisons if none are known
            self.scan_for_garrisons(grid, grid_size)
            if not self.known_garrisons:
                return False

        # Find nearest garrison
        nearest_garrison = None
        min_distance = float('inf')
        for garrison_pos in self.known_garrisons:
            distance = self._distance_to(garrison_pos, grid_size)
            if distance < min_distance:
                min_distance = distance
                nearest_garrison = garrison_pos

        if nearest_garrison:
            # Move towards garrison
            if self.position == nearest_garrison:
                # Try to enter garrison
                for entity in grid.get_entities_at(nearest_garrison):
                    if isinstance(entity, Garrison):
                        if entity.add_knight(self):
                            self.current_garrison = entity
                            self.is_resting = True
                            print(f"Knight at {self.position} has entered garrison to rest")
                            return True
            else:
                # Move towards garrison
                new_pos = self.move_towards(nearest_garrison, grid_size, grid)
                if new_pos != self.position:
                    grid.move_entity(self, new_pos)
                    print(f"Knight at {self.position} is retreating to garrison at {nearest_garrison}")
                return True
        return False

    def move_towards(self, target: Tuple[int, int], grid_size: Tuple[int, int], grid) -> Tuple[int, int]:
        """Move one step towards the target position"""
        # Deduct energy for pursuit
        self.energy = max(0.0, self.energy - 5.0)
        print(f"Knight at {self.position} energy depleted to {self.energy:.1f}%")

        current_x, current_y = self.position
        target_x, target_y = target
        grid_width, grid_height = grid_size

        # Calculate the shortest path considering grid wrapping
        dx = (target_x - current_x + grid_width) % grid_width
        dy = (target_y - current_y + grid_height) % grid_height

        # Choose the best move
        if abs(dx) > abs(dy):
            new_x = (current_x + (1 if dx > 0 else -1)) % grid_width
            new_y = current_y
        else:
            new_x = current_x
            new_y = (current_y + (1 if dy > 0 else -1)) % grid_height

        # Check if the new position has a hideout
        for entity in grid.get_entities_at((new_x, new_y)):
            if entity.entity_type == EntityType.HIDEOUT:
                print(f"Knight at {self.position} cannot enter hideout at {new_x}, {new_y}")
                return self.position

        return (new_x, new_y)

    def move_along_route(self, grid_size: Tuple[int, int], grid) -> Tuple[int, int]:
        """Move along the patrol route, avoiding obstacles"""
        if not self.patrol_route:
            return self.position

        # Get next position in route
        next_index = (self.current_route_index + 1) % len(self.patrol_route)
        next_pos = self.patrol_route[next_index]

        # Check if next position is blocked
        for entity in grid.get_entities_at(next_pos):
            if entity.entity_type == EntityType.HIDEOUT:
                # Find alternative path
                for dx, dy in DIRECTIONS:
                    alt_x = (next_pos[0] + dx) % grid_size[0]
                    alt_y = (next_pos[1] + dy) % grid_size[1]
                    alt_pos = (alt_x, alt_y)
                    if not any(e.entity_type == EntityType.HIDEOUT for e in grid.get_entities_at(alt_pos)):
                        next_pos = alt_pos
                        break

        # Move towards next position
        new_pos = self.move_towards(next_pos, grid_size, grid)

        # Update route index if reached next position
        if new_pos == next_pos:
            self.current_route_index = next_index

        return new_pos