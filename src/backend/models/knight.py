# src/backend/models/knight.py

from typing import Tuple
from src.backend.models.grid import Grid

class Knight:
    def __init__(self, name: str, position: Tuple[int, int], skill: KnightSkill, energy: float = 100.0):
        self.name = name
        self.position = position
        self.skill = skill
        self.energy = energy

    def move_towards(self, target: Tuple[int, int], grid: Grid) -> bool:
        if self.energy <= 0:
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
            
        # Update position and energy
        self.position = grid.wrap_position(new_x, new_y)
        self.energy = max(0, self.energy - 10)
        return True

    def rest(self):
        self.energy = min(100, self.energy + 5)

    def __repr__(self):
        return f"Knight({self.name}, Position: {self.position}, Energy: {self.energy})"
