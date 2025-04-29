from typing import Tuple
from src.core.entities.base import Entity
from src.core.enums import EntityType, DragonSkill

class Dragon(Entity):
    def __init__(self, name: str, position: Tuple[int, int], skill: DragonSkill):
        super().__init__(name, position, EntityType.DRAGON)
        self.skill = skill

    def move_towards(self, target: Tuple[int, int]) -> bool:
        """Move towards a target position."""
        if not self.can_move():
            return False
            
        current_x, current_y = self.position
        target_x, target_y = target
        
        # Calculate direction to move
        dx = 1 if target_x > current_x else -1 if target_x < current_x else 0
        dy = 1 if target_y > current_y else -1 if target_y < current_y else 0
        
        # Move in the direction that reduces distance the most
        if abs(target_x - current_x) > abs(target_y - current_y):
            new_x = current_x + dx
            new_y = current_y
        else:
            new_x = current_x
            new_y = current_y + dy
            
        self.move((new_x, new_y))
        return True 