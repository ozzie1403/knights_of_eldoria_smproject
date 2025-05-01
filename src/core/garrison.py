from typing import List, Tuple, Optional
import random
from src.core.knight import Knight
from src.core.enums import EntityType, CellType, KnightSkill

class Garrison:
    def __init__(self, position: Tuple[int, int], capacity: int = 5):
        self.position = position
        self.capacity = capacity
        self.knights: List[Knight] = []
        self.cell_type = CellType.GARRISON
        self.entity_type = EntityType.GARRISON
        self.max_knights = 3
        self.spawn_cooldown = 0
        self.max_cooldown = 10  # Number of steps between knight spawns
    
    @property
    def cell_type(self):
        return "GARRISON"
    
    def can_spawn_knight(self) -> bool:
        """Check if the garrison can spawn a new knight."""
        return len(self.knights) < self.max_knights and self.spawn_cooldown <= 0
    
    def spawn_knight(self, grid_size: int) -> Optional[Knight]:
        """Spawn a new knight if possible."""
        if not self.can_spawn_knight():
            return None
        
        # Create a new knight at the garrison's position
        knight = Knight(position=self.position)
        knight.generate_patrol_route(grid_size)
        self.knights.append(knight)
        self.spawn_cooldown = self.max_cooldown
        return knight
    
    def update(self):
        """Update the garrison's state."""
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
    
    def add_knight(self, knight: Knight) -> bool:
        """Add a knight to the garrison."""
        if len(self.knights) < self.capacity:
            self.knights.append(knight)
            return True
        return False
    
    def remove_knight(self, knight: Knight) -> bool:
        """Remove a knight from the garrison."""
        if knight in self.knights:
            self.knights.remove(knight)
            return True
        return False
    
    def get_knight_count(self) -> int:
        """Get the number of knights in the garrison."""
        return len(self.knights)
    
    def get_average_skill_level(self) -> float:
        """Calculate the average skill level of knights in the garrison."""
        if not self.knights:
            return 0
        return sum(knight.skill.value for knight in self.knights) / len(self.knights)
    
    def __repr__(self) -> str:
        return f"Garrison(Position: {self.position}, Knights: {len(self.knights)}/{self.capacity}, Avg Skill: {self.get_average_skill_level():.1f})" 