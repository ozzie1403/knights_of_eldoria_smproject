from typing import Optional, List, Set
from src.core.entities.position import Position
from src.core.entities.base import Entity
from src.core.entities.treasure import Treasure
from src.core.enums import EntityType, HunterSkill

class Hunter(Entity):
    def __init__(self, position: Position, skill: HunterSkill):
        super().__init__(position, EntityType.HUNTER)
        self.skill = skill
        self.carrying_treasure: Optional[Treasure] = None
        self.known_treasures: Set[Position] = set()
        self.known_hideouts: Set[Position] = set()
        self.known_knights: Set[Position] = set()
        self.steps_since_collapse: int = 0
        self.is_collapsed: bool = False
        self.stamina: float = 100.0  # Initialize with full stamina

    def move(self, new_position: Position) -> None:
        if not self.can_move():
            return
            
        self.position = new_position
        # Base stamina depletion is -2% per move
        base_depletion = 2.0
        
        # Skill-based stamina adjustment
        if self.skill == HunterSkill.ENDURANCE:
            # Endurance: 50% less stamina depletion
            self.stamina = max(0.0, self.stamina - (base_depletion * 0.5))
        else:
            self.stamina = max(0.0, self.stamina - base_depletion)

    def rest(self) -> None:
        # Base recovery is +1% per step
        base_recovery = 1.0
        
        if self.skill == HunterSkill.ENDURANCE:
            # Endurance: 50% faster recovery
            self.stamina = min(100.0, self.stamina + (base_recovery * 1.5))
        else:
            self.stamina = min(100.0, self.stamina + base_recovery)

    def can_move(self) -> bool:
        if self.is_collapsed:
            self.steps_since_collapse += 1
            if self.steps_since_collapse >= 3:
                return False
            return True
        return self.stamina > 0.0

    def needs_rest(self) -> bool:
        return self.stamina <= 6.0

    def collapse(self) -> None:
        if self.stamina <= 0.0 and not self.is_collapsed:
            self.is_collapsed = True
            self.steps_since_collapse = 0

    def get_skill_efficiency(self) -> float:
        """Get the efficiency multiplier based on skill."""
        if self.skill == HunterSkill.NAVIGATION:
            return 1.5  # 50% better pathfinding
        elif self.skill == HunterSkill.ENDURANCE:
            return 1.0  # Normal efficiency
        else:  # STEALTH
            return 0.7  # 30% harder to detect

    def update_memory(self, treasures: List[Position], hideouts: List[Position], knights: List[Position]) -> None:
        """Update the hunter's memory of known positions."""
        self.known_treasures.update(treasures)
        self.known_hideouts.update(hideouts)
        self.known_knights.update(knights)

    def prioritize_treasure(self, treasures: List[Treasure]) -> Optional[Treasure]:
        """Prioritize treasure based on value and type."""
        if not treasures:
            return None
            
        # Sort treasures by value and type
        sorted_treasures = sorted(treasures, 
                                key=lambda t: (t.value, t.treasure_type.value), 
                                reverse=True)
        return sorted_treasures[0]

    def __repr__(self) -> str:
        return f"Hunter(Skill: {self.skill.name}, Position: {self.position}, Stamina: {self.stamina:.1f}%)" 