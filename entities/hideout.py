from typing import List, Tuple, Set
from .base_entity import BaseEntity, EntityType
from .treasure import Treasure
from .hunter import Hunter


class Hideout(BaseEntity):
    def __init__(self, position: Tuple[int, int], grid=None):
        super().__init__(EntityType.HIDEOUT, position)
        self.stored_treasure: List[Treasure] = []
        self.total_value = 0.0
        self.max_capacity = 5
        self.known_treasures: Set[Tuple[int, int]] = set()
        self.known_hideouts: Set[Tuple[int, int]] = set()
        self.grid = grid

    def can_accommodate(self) -> bool:
        """Check if hideout has space for more hunters"""
        return len(self.get_current_hunters()) < self.max_capacity

    def get_current_hunters(self) -> List[Hunter]:
        """Get list of hunters currently at this hideout"""
        if not self.grid:
            return []
        return [h for h in self.grid.entities[EntityType.HUNTER] if h.position == self.position]

    def share_knowledge(self, hunter):
        """Share knowledge about treasures and hideouts with a hunter"""
        # Share treasure locations
        for treasure_info in self.known_treasures:
            if not any(m[0] == treasure_info[0] and m[1] == treasure_info[1] for m in hunter.memory):
                hunter.memory.append(treasure_info)
                print(
                    f"Hideout at {self.position} shared treasure location at {treasure_info[0:2]} with hunter at {hunter.position}")

        # Share hideout locations
        for hideout_pos in self.known_hideouts:
            if hideout_pos != self.position:  # Don't share own position
                hunter.memory_hideouts.add(hideout_pos)
                print(
                    f"Hideout at {self.position} shared hideout location at {hideout_pos} with hunter at {hunter.position}")

    def deposit_treasure(self, treasure_list: List[Treasure]) -> None:
        """Deposit a list of treasures into the hideout"""
        self.stored_treasure.extend(treasure_list)
        self.total_value = sum(treasure.get_collection_value() for treasure in self.stored_treasure)

    def get_total_value(self) -> float:
        """Get the total value of all stored treasure"""
        return self.total_value

    def __str__(self) -> str:
        hunters = len(self.get_current_hunters())
        return f"{self.entity_type.value}{hunters}"  # Shows number of hunters at hideout 