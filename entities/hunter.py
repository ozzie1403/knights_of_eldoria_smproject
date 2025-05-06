from typing import List, Tuple, Optional, Set, Dict
from enum import Enum
import random
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from .base_entity import BaseEntity, EntityType
from .treasure import Treasure, TreasureType


class HunterSkill(Enum):
    NAVIGATION = 'navigation'
    STEALTH = 'stealth'
    ENDURANCE = 'endurance'


DIRECTIONS = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1)
]


class Hunter(BaseEntity):
    def __init__(self, position: Tuple[int, int], skill: Optional[HunterSkill] = None):
        super().__init__(EntityType.HUNTER, position)
        self.carrying_treasure: Optional[Treasure] = None
        self.capacity = 1  # Only one treasure at a time
        self.total_value_collected = 0.0
        self.stamina = 100.0  # percent
        self.skill = skill if skill else random.choice(list(HunterSkill))
        self.memory: List[Tuple[int, int, TreasureType, int]] = []  # (x, y, treasure_type, timestamp)
        self.memory_hideouts: Set[Tuple[int, int]] = set()
        self.lost_treasures: Dict[
            Tuple[int, int], Tuple[TreasureType, int]] = {}  # (x, y) -> (treasure_type, step_lost)
        self.resting = False
        self.collapse_timer = 0
        self.status = "active"  # can be "active", "resting", or "collapsed"
        self.recruited_by: Optional[Tuple[int, int]] = None  # Position of hunter who recruited this one
        self.retrieval_attempts: Dict[Tuple[int, int], int] = {}  # Track attempts to retrieve lost treasures

        # Machine learning components
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        self.scaler = StandardScaler()
        self.behavior_patterns = []  # Store successful behavior patterns
        self.pattern_weights = []  # Weights for each pattern based on success rate

        # Initialize with some default patterns to fit the scaler
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize with some default patterns to fit the scaler"""
        # Create initial features for fitting
        initial_features = [
            [0.0, 0.0, 0.0, 100.0],  # position_x, position_y, treasure_value, stamina
            [0.1, 0.1, 50.0, 75.0],
            [0.2, 0.2, 100.0, 50.0]
        ]

        # Fit the scaler with initial features
        self.scaler.fit(initial_features)

        # Initialize default patterns
        default_patterns = [
            {'position': (0, 0), 'treasure_value': 0.0, 'stamina': 100.0, 'next_position': (0, 0), 'success': True,
             'success_rate': 1.0},
            {'position': (1, 1), 'treasure_value': 50.0, 'stamina': 75.0, 'next_position': (1, 1), 'success': True,
             'success_rate': 1.0},
            {'position': (2, 2), 'treasure_value': 100.0, 'stamina': 50.0, 'next_position': (2, 2), 'success': True,
             'success_rate': 1.0}
        ]
        self.behavior_patterns.extend(default_patterns)

        # Fit KMeans with initial features
        self.kmeans.fit(self.scaler.transform(initial_features))

    def analyze_behavior_patterns(self, grid, grid_size: Tuple[int, int]):
        """Analyze and learn from successful behavior patterns"""
        if len(self.behavior_patterns) < 10:  # Need enough data to analyze
            return

        # Convert patterns to features
        features = []
        for pattern in self.behavior_patterns:
            # Extract features from pattern (position, treasure value, stamina, etc.)
            pos_x, pos_y = pattern['position']
            features.append([
                pos_x / grid_size[0],  # Normalized x position
                pos_y / grid_size[1],  # Normalized y position
                pattern['treasure_value'] / 100.0,  # Normalized treasure value
                pattern['stamina'] / 100.0,  # Normalized stamina
                1 if pattern['success'] else 0  # Binary success indicator
            ])

        # Scale features and fit KMeans
        scaled_features = self.scaler.fit_transform(features)
        self.kmeans.fit(scaled_features)

        # Update pattern weights based on success rate
        self.pattern_weights = []
        for i in range(self.kmeans.n_clusters):
            cluster_patterns = [p for j, p in enumerate(self.behavior_patterns)
                                if self.kmeans.labels_[j] == i]
            success_rate = sum(1 for p in cluster_patterns if p['success']) / len(cluster_patterns)
            self.pattern_weights.append(success_rate)

    def choose_best_action(self, grid, grid_size: Tuple[int, int], current_step: int) -> Tuple[int, int]:
        """Use machine learning to choose the best action"""
        if not self.behavior_patterns:
            return self.position

        # Get current state features
        current_features = [
            self.position[0] / grid_size[0],
            self.position[1] / grid_size[1],
            self.carrying_treasure.current_value / 100.0 if self.carrying_treasure else 0.0,
            self.stamina / 100.0
        ]

        try:
            # Scale features
            scaled_features = self.scaler.transform([current_features])

            # Predict cluster
            cluster = self.kmeans.predict(scaled_features)[0]

            # Get successful patterns from this cluster
            cluster_patterns = [p for i, p in enumerate(self.behavior_patterns)
                                if self.kmeans.labels_[i] == cluster and p['success']]

            if cluster_patterns:
                # Choose pattern with highest success rate
                best_pattern = max(cluster_patterns, key=lambda p: p['success_rate'])
                # Ensure the next position is within one step
                next_pos = best_pattern['next_position']
                dx = next_pos[0] - self.position[0]
                dy = next_pos[1] - self.position[1]
                if abs(dx) <= 1 and abs(dy) <= 1:
                    return next_pos
        except Exception as e:
            print(f"ML prediction failed: {e}")

        return self.position

    def record_behavior_pattern(self, position: Tuple[int, int], treasure_value: float,
                                stamina: float, next_position: Tuple[int, int], success: bool):
        """Record a behavior pattern for learning"""
        pattern = {
            'position': position,
            'treasure_value': treasure_value,
            'stamina': stamina,
            'next_position': next_position,
            'success': success,
            'success_rate': 1.0 if success else 0.0
        }
        self.behavior_patterns.append(pattern)

        # Keep only recent patterns
        if len(self.behavior_patterns) > 100:
            self.behavior_patterns = self.behavior_patterns[-100:]

    def scan_for_treasure(self, grid, grid_size: Tuple[int, int], current_step: int) -> List[Treasure]:
        """Scan all adjacent cells for treasure, memorize their locations."""
        if self.carrying_treasure is not None:
            return []  # Ignore if already carrying treasure

        treasures_found = []
        # First check current position
        for entity in grid.get_entities_at(self.position):
            if entity.entity_type == EntityType.TREASURE:
                treasures_found.append(entity)
                # Add to memory if not already there
                if not any(m[0] == self.position[0] and m[1] == self.position[1] for m in self.memory):
                    self.memory.append((self.position[0], self.position[1], entity.treasure_type, current_step))
                    print(f"Hunter at {self.position} found treasure at current position")
                return treasures_found  # Return immediately if found treasure at current position

        # Then check adjacent cells
        for dx, dy in DIRECTIONS:
            nx = (self.position[0] + dx) % grid_size[0]
            ny = (self.position[1] + dy) % grid_size[1]
            for entity in grid.get_entities_at((nx, ny)):
                if entity.entity_type == EntityType.TREASURE:
                    treasures_found.append(entity)
                    # Add to memory if not already there
                    if not any(m[0] == nx and m[1] == ny for m in self.memory):
                        self.memory.append((nx, ny, entity.treasure_type, current_step))
                        print(
                            f"Hunter at {self.position} remembers treasure at ({nx}, {ny}) seen at step {current_step}")
        return treasures_found

    def update_memory(self, current_step: int):
        """Remove old memories after 20 simulation steps"""
        self.memory = [m for m in self.memory if current_step - m[3] <= 20]
        # Limit memory size to 10 entries
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]

    def share_memory(self, other_hunter: 'Hunter'):
        """Share memory with another hunter"""
        if not other_hunter.carrying_treasure and not other_hunter.resting and not other_hunter.memory:
            other_hunter.memory = list(self.memory)
            other_hunter.recruited_by = self.position
            print(f"Hunter at {self.position} recruited Hunter at {other_hunter.position}")

    def scan_for_hideouts(self, grid, grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Scan all adjacent cells for hideouts, memorize their locations."""
        hideouts_found = []
        for dx, dy in DIRECTIONS:
            nx = (self.position[0] + dx) % grid_size[0]
            ny = (self.position[1] + dy) % grid_size[1]
            for entity in grid.get_entities_at((nx, ny)):
                if entity.entity_type == EntityType.HIDEOUT:
                    hideouts_found.append((nx, ny))
                    self.memory_hideouts.add((nx, ny))
        return hideouts_found

    def collect_treasure(self, treasure: Treasure) -> bool:
        """Attempt to collect a treasure. Returns True if successful."""
        if self.carrying_treasure is None and treasure is not None:
            self.carrying_treasure = treasure
            self.total_value_collected += treasure.get_collection_value()
            print(f"Hunter at {self.position} picked up {treasure.treasure_type.name} treasure at {treasure.position}")
            return True
        return False

    def drop_treasure(self) -> List[Treasure]:
        """Drop the currently carried treasure and return it."""
        if self.carrying_treasure:
            dropped = [self.carrying_treasure]
            self.carrying_treasure = None
            return dropped
        return []

    def get_total_value(self) -> float:
        return self.total_value_collected

    def move_towards(self, target: Tuple[int, int], grid_size: Tuple[int, int], grid) -> Tuple[int, int]:
        """Move one step in any direction (8-way) towards the target position."""
        current_x, current_y = self.position
        target_x, target_y = target
        grid_width, grid_height = grid_size

        # Calculate the shortest path considering grid wrapping
        dx = (target_x - current_x + grid_width) % grid_width
        dy = (target_y - current_y + grid_height) % grid_height

        # Choose best direction (only move one step)
        best_move = self.position
        min_dist = float('inf')
        for ddx, ddy in DIRECTIONS:
            nx = (current_x + ddx) % grid_width
            ny = (current_y + ddy) % grid_height
            dist = min(abs(nx - target_x), grid_width - abs(nx - target_x)) + min(abs(ny - target_y),
                                                                                  grid_height - abs(ny - target_y))
            if dist < min_dist:
                # Check if the new position has a garrison
                has_garrison = False
                for entity in grid.get_entities_at((nx, ny)):
                    if entity.entity_type == EntityType.GARRISON:
                        has_garrison = True
                        break
                if not has_garrison:
                    min_dist = dist
                    best_move = (nx, ny)

        # Record the movement pattern
        self.record_behavior_pattern(
            self.position,
            self.carrying_treasure.current_value if self.carrying_treasure else 0.0,
            self.stamina,
            best_move,
            True  # Assume success for now, will be updated if collision occurs
        )

        return best_move

    def update_stamina(self, moving: bool = True, resting: bool = False):
        """Update stamina based on movement and resting status"""
        if moving:
            self.stamina -= 2.0
        if resting:
            self.stamina = min(100.0, self.stamina + 1.0)
        if self.stamina < 0:
            self.stamina = 0.0
        print(f"Hunter at {self.position} stamina: {self.stamina:.1f}%")

    def should_rest(self) -> bool:
        """Check if hunter should rest"""
        return self.stamina <= 6.0

    def is_collapsed(self) -> bool:
        """Check if hunter has collapsed"""
        return self.status == "collapsed"

    def step_collapse(self):
        """Handle collapse countdown"""
        if self.stamina <= 0.0:
            self.collapse_timer -= 1
            if self.collapse_timer <= 0:
                self.status = "collapsed"
                print(f"Hunter at {self.position} has collapsed")
        else:
            self.collapse_timer = 3  # Reset collapse timer if stamina is above 0

    def start_resting(self):
        """Start resting at a hideout"""
        self.resting = True
        self.status = "resting"
        print(f"Hunter at {self.position} is resting at hideout")

    def stop_resting(self):
        """Stop resting when stamina is full"""
        self.resting = False
        self.status = "active"

    def remember_lost_treasure(self, treasure: Treasure, current_step: int):
        """Remember where a treasure was lost"""
        self.lost_treasures[treasure.position] = (treasure.treasure_type, current_step)
        print(
            f"Hunter at {self.position} remembers losing {treasure.treasure_type.name} treasure at {treasure.position}")

    def attempt_retrieval(self, grid, grid_size: Tuple[int, int], current_step: int) -> bool:
        """Attempt to retrieve a lost treasure if conditions are right"""
        if self.carrying_treasure or not self.lost_treasures:
            return False

        # Find the most recently lost treasure that hasn't been attempted too many times
        valid_treasures = [
            (pos, data) for pos, data in self.lost_treasures.items()
            if self.retrieval_attempts.get(pos, 0) < 3  # Max 3 attempts per treasure
        ]

        if not valid_treasures:
            return False

        # Sort by most recent loss
        valid_treasures.sort(key=lambda x: x[1][1], reverse=True)
        target_pos, (treasure_type, _) = valid_treasures[0]

        # Check if we're at the target position
        if self.position == target_pos:
            # Check if treasure is still there
            for entity in grid.get_entities_at(target_pos):
                if entity.entity_type == EntityType.TREASURE:
                    if self.collect_treasure(entity):
                        print(f"Hunter at {self.position} successfully retrieved lost treasure")
                        del self.lost_treasures[target_pos]
                        del self.retrieval_attempts[target_pos]
                        return True
            # Treasure not found, increment attempt counter
            self.retrieval_attempts[target_pos] = self.retrieval_attempts.get(target_pos, 0) + 1
            print(
                f"Hunter at {self.position} failed to retrieve treasure at {target_pos} (attempt {self.retrieval_attempts[target_pos]})")
            return False

        # Move towards the target
        new_pos = self.move_towards(target_pos, grid_size, grid)
        return True

    def share_knowledge(self, hideouts: List['Hideout']) -> None:
        """Share knowledge with hideouts"""
        for hideout in hideouts:
            if hideout.position == self.position:
                hideout.share_knowledge(self)

    def deposit_treasure(self, hideouts: List['Hideout']) -> bool:
        """Attempt to deposit treasure at a hideout"""
        if not self.carrying_treasure:
            return False

        for hideout in hideouts:
            if hideout.position == self.position:
                hideout.deposit_treasure([self.carrying_treasure])
                self.carrying_treasure = None
                print(f"Hunter at {self.position} deposited treasure at hideout")
                return True

        return False