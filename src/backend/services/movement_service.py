# src/backend/services/movement_service.py

from src.backend.models.grid import Grid
from src.backend.models.entities import Hunter
from typing import Tuple

class MovementService:
    @staticmethod
    def move_entity(entity: Hunter, direction: Tuple[int, int], grid: Grid) -> bool:
        """
        Move an entity in the specified direction.
        Returns True if the move was successful, False otherwise.
        """
        current_pos = entity.position
        new_x = (current_pos.x + direction[0]) % grid.size
        new_y = (current_pos.y + direction[1]) % grid.size
        new_pos = grid.wrap_position(current_pos)
        
        if grid.get_cell_type(new_pos) == grid.EMPTY:
            grid.set_cell_type(current_pos, grid.EMPTY)
            del grid.position_to_entity[current_pos]
            entity.move(new_pos)
            grid.set_cell_type(new_pos, grid.HUNTER)
            grid.position_to_entity[new_pos] = entity
            return True
        return False
