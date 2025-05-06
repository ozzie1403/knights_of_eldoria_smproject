from typing import List, Tuple, Optional, Set
from enum import Enum
import random
from .base_entity import BaseEntity, EntityType
from .treasure import Treasure


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
        self.resting = False
        self.collapse_timer = 0
        self.status = "active"  # can be "active", "resting", or "collapsed"
        self.recruited_by: Optional[Tuple[int, int]] = None  # Position of hunter who recruited this one

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

    def move_towards(self, target: Tuple[int, int], grid_size: Tuple[int, int]) -> Tuple[int, int]:
        """Move one step in any direction (8-way) towards the target position."""
        current_x, current_y = self.position
        target_x, target_y = target
        grid_width, grid_height = grid_size
        dx = (target_x - current_x + grid_width) % grid_width
        dy = (target_y - current_y + grid_height) % grid_height
        # Choose best direction
        best_move = self.position
        min_dist = float('inf')
        for ddx, ddy in DIRECTIONS:
            nx = (current_x + ddx) % grid_width
            ny = (current_y + ddy) % grid_height
            dist = min(abs(nx - target_x), grid_width - abs(nx - target_x)) + min(abs(ny - target_y),
                                                                                  grid_height - abs(ny - target_y))
            if dist < min_dist:
                min_dist = dist
                best_move = (nx, ny)
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