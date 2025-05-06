from typing import Tuple, List
from .base_entity import BaseEntity, EntityType

class Knight(BaseEntity):
    def __init__(self, position: Tuple[int, int]):
        super().__init__(EntityType.KNIGHT, position)
        self.patrol_route: List[Tuple[int, int]] = []
        self.current_route_index = 0

    def set_patrol_route(self, route: List[Tuple[int, int]]) -> None:
        """Set the patrol route for the knight"""
        self.patrol_route = route
        self.current_route_index = 0

    def move_along_route(self, grid_size: Tuple[int, int]) -> Tuple[int, int]:
        """Move to the next position in the patrol route"""
        if not self.patrol_route:
            return self.position

        next_pos = self.patrol_route[self.current_route_index]
        self.current_route_index = (self.current_route_index + 1) % len(self.patrol_route)
        return self.move(next_pos, grid_size) 