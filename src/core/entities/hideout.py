from typing import List, Optional, Set
from src.core.entities.position import Position
from src.core.entities.base import Entity
from src.core.entities.treasure import Treasure
from src.core.entities.hunter import Hunter
from src.core.enums import EntityType, HunterSkill
import random

class Hideout(Entity):
    def __init__(self, position: Position):
        super().__init__(position, EntityType.HIDEOUT)
        self.hunters: List[Hunter] = []
        self.stored_treasures: List[Treasure] = []
        self.capacity = 5  # Maximum number of hunters that can be in the hideout

    def can_accommodate(self) -> bool:
        """Check if the hideout can accommodate more hunters."""
        return len(self.hunters) < self.capacity

    def add_hunter(self, hunter: Hunter) -> bool:
        """Add a hunter to the hideout if there's space."""
        if self.can_accommodate():
            self.hunters.append(hunter)
            # Share knowledge with the new hunter
            self.share_knowledge()
            return True
        return False

    def remove_hunter(self, hunter: Hunter) -> bool:
        """Remove a hunter from the hideout."""
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False

    def store_treasure(self, treasure: Treasure) -> None:
        """Store a treasure in the hideout."""
        self.stored_treasures.append(treasure)

    def share_knowledge(self) -> None:
        """Share knowledge between all hunters in the hideout."""
        if not self.hunters:
            return

        # Collect all known positions from all hunters
        all_treasures: Set[Position] = set()
        all_hideouts: Set[Position] = set()
        all_knights: Set[Position] = set()

        for hunter in self.hunters:
            all_treasures.update(hunter.known_treasures)
            all_hideouts.update(hunter.known_hideouts)
            all_knights.update(hunter.known_knights)

        # Share the combined knowledge with each hunter
        for hunter in self.hunters:
            hunter.update_memory(
                list(all_treasures),
                list(all_hideouts),
                list(all_knights)
            )

    def has_diverse_skills(self) -> bool:
        """Check if the hideout has hunters with diverse skills."""
        if len(self.hunters) < 2:
            return False

        skills = {hunter.skill for hunter in self.hunters}
        return len(skills) >= 2  # At least 2 different skills

    def try_recruit_hunter(self, grid_size: int) -> Optional[Hunter]:
        """Try to recruit a new hunter if conditions are met."""
        # Check recruitment conditions
        if not self.can_accommodate():
            return None
        if not self.has_diverse_skills():
            return None
        if random.random() > 0.2:  # 20% chance per step
            return None

        # Create a new hunter with a random existing skill
        existing_skills = [hunter.skill for hunter in self.hunters]
        new_skill = random.choice(existing_skills)
        new_hunter = Hunter(self.position, new_skill)
        
        # Share knowledge with the new hunter
        self.share_knowledge()
        
        return new_hunter

    def __repr__(self) -> str:
        return f"Hideout(Position: {self.position}, Hunters: {len(self.hunters)}/{self.capacity}, Stored Treasures: {len(self.stored_treasures)})" 