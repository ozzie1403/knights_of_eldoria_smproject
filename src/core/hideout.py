from typing import List, Dict, Set, Tuple, Optional
import random
from src.core.enums import EntityType, CellType, HunterSkill
from src.core.treasure import Treasure
from src.core.hunter import TreasureHunter

class Hideout:
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.cell_type = CellType.HIDEOUT
        self.entity_type = EntityType.HIDEOUT
        self.stored_treasure: List[Treasure] = []
        self.hunters: List[TreasureHunter] = []
        self.known_info = {
            'treasures': {},  # position -> value
            'knights': set(),  # positions
            'hideouts': set()  # positions
        }
        self.max_hunters = 5
    
    def can_enter(self) -> bool:
        """Check if there's space for another hunter."""
        return len(self.hunters) < self.max_hunters
    
    def enter(self, hunter: TreasureHunter) -> bool:
        """Allow a hunter to enter the hideout."""
        if self.can_enter():
            self.hunters.append(hunter)
            self._share_memory(hunter)
            return True
        return False
    
    def leave(self, hunter: TreasureHunter) -> bool:
        """Remove a hunter from the hideout."""
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False
    
    def deposit_treasure(self, hunter: TreasureHunter) -> bool:
        """Accept treasure from a hunter."""
        if hunter in self.hunters and hunter.carrying:
            self.stored_treasure.append(hunter.carrying)
            hunter.carrying = None
            return True
        return False
    
    def _share_memory(self, hunter: TreasureHunter) -> None:
        """Share memory between all hunters in the hideout."""
        # Share treasure locations
        for pos, value in hunter.memory.items():
            if pos not in self.known_info['treasures'] or value > self.known_info['treasures'][pos]:
                self.known_info['treasures'][pos] = value
        
        # Share hideout locations
        self.known_info['hideouts'].update(hunter.known_hideouts)
        
        # Update all hunters' memory
        for h in self.hunters:
            h.memory.update(self.known_info['treasures'])
            h.known_hideouts.update(self.known_info['hideouts'])
    
    def try_recruit(self) -> Optional[TreasureHunter]:
        """Attempt to recruit a new hunter based on existing skills."""
        if not self.can_enter() or len(self.hunters) < 2:
            return None
            
        # Check if there's a mix of skills
        skills = {h.skill for h in self.hunters}
        if len(skills) < 2:
            return None
            
        # 20% chance to recruit
        if random.random() < 0.2:
            # Choose a random skill from existing hunters
            new_skill = random.choice(list(skills))
            new_hunter = TreasureHunter(self.position)
            new_hunter.skill = new_skill
            return new_hunter
        return None
    
    def update(self) -> None:
        """Update hideout state for the current simulation step."""
        # Rest all hunters
        for hunter in self.hunters:
            hunter.rest()
        
        # Try to recruit new hunter
        new_hunter = self.try_recruit()
        if new_hunter:
            self.enter(new_hunter)
    
    def __repr__(self) -> str:
        return f"Hideout(Position: {self.position}, Hunters: {len(self.hunters)}, Treasure: {len(self.stored_treasure)})" 