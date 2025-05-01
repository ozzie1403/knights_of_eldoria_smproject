from typing import List, Dict, Set, Tuple, Optional
from src.models.entity import Entity
from src.core.enums import EntityType, HunterSkill
from src.core.hunter import TreasureHunter
import random

class Hideout(Entity):
    """A hideout where hunters can rest, store treasure, and share information."""
    
    def __init__(self, x: int, y: int):
        """
        Initialize a hideout at the specified position.
        
        Args:
            x (int): The x-coordinate of the hideout
            y (int): The y-coordinate of the hideout
            
        Raises:
            ValueError: If capacity is not a positive integer
        """
        super().__init__(x, y)
        
        # Validate capacity
        capacity = 5  # Default capacity
        if not isinstance(capacity, int):
            raise ValueError(f"Capacity must be an integer, got {type(capacity)}")
        if capacity < 0:
            raise ValueError(f"Capacity must be positive, got {capacity}")
            
        self.capacity = capacity
        self.stored_treasure: List[Treasure] = []
        self.hunters: List[TreasureHunter] = []  # Initialize empty list
        self.known_info: Dict[str, Set[Tuple[int, int]]] = {
            'treasures': set(),
            'knights': set(),
            'hideouts': set()
        }
        self.entity_type = EntityType.HIDEOUT
    
    def can_enter(self, hunter: TreasureHunter) -> bool:
        """
        Check if a hunter can enter the hideout.
        
        Args:
            hunter (TreasureHunter): The hunter attempting to enter
            
        Returns:
            bool: True if the hunter can enter, False otherwise
        """
        return len(self.hunters) < self.capacity  # Use capacity attribute
    
    def enter(self, hunter: TreasureHunter) -> bool:
        """
        Allow a hunter to enter the hideout.
        
        Args:
            hunter (TreasureHunter): The hunter entering
            
        Returns:
            bool: True if entry was successful, False otherwise
        """
        if self.can_enter(hunter):
            self.hunters.append(hunter)
            self._share_memory(hunter)
            return True
        return False
    
    def leave(self, hunter: TreasureHunter) -> None:
        """
        Remove a hunter from the hideout.
        
        Args:
            hunter (TreasureHunter): The hunter leaving
        """
        if hunter in self.hunters:
            self.hunters.remove(hunter)
    
    def deposit_treasure(self, treasure: Treasure) -> None:
        """
        Store treasure in the hideout.
        
        Args:
            treasure (Treasure): The treasure to store
        """
        self.stored_treasure.append(treasure)
    
    def _share_memory(self, hunter: TreasureHunter) -> None:
        """
        Share known information with a hunter.
        
        Args:
            hunter (TreasureHunter): The hunter to share information with
        """
        # Share treasure locations
        hunter.memory['treasures'].update(self.known_info['treasures'])
        # Share knight locations
        hunter.memory['knights'].update(self.known_info['knights'])
        # Share hideout locations
        hunter.memory['hideouts'].update(self.known_info['hideouts'])
        
        # Update hideout's knowledge with hunter's knowledge
        self.known_info['treasures'].update(hunter.memory['treasures'])
        self.known_info['knights'].update(hunter.memory['knights'])
        self.known_info['hideouts'].update(hunter.memory['hideouts'])
    
    def try_recruit(self) -> Optional[TreasureHunter]:
        """
        Attempt to recruit a new hunter based on existing skills.
        
        Returns:
            Optional[TreasureHunter]: The new hunter if recruitment was successful, None otherwise
        """
        if len(self.hunters) >= self.capacity:  # Maximum capacity reached
            return None
            
        # Check for skill diversity
        existing_skills = {hunter.skill for hunter in self.hunters}
        if len(existing_skills) < 3:  # If not all skills are represented
            # Choose a missing skill
            missing_skills = set(HunterSkill) - existing_skills
            if missing_skills:
                new_skill = random.choice(list(missing_skills))
                new_hunter = TreasureHunter(self.get_position())
                new_hunter.skill = new_skill
                return new_hunter
        return None
    
    def move(self, grid) -> None:
        """
        Hideouts do not move, so this method does nothing.
        
        Args:
            grid: The game grid (unused)
        """
        pass
    
    def update(self, grid) -> None:
        """
        Update the hideout's state.
        
        Args:
            grid: The game grid containing all entities
        """
        # Allow hunters to rest
        for hunter in self.hunters:
            if hunter.stamina < 100:
                hunter.stamina = min(100, hunter.stamina + 5)  # Restore 5% stamina per step
        
        # Attempt recruitment (20% chance)
        if random.random() < 0.2:
            new_hunter = self.try_recruit()
            if new_hunter:
                self.enter(new_hunter)
    
    def add_hunter(self, hunter: TreasureHunter) -> None:
        """
        Add a hunter to the hideout.
        
        Args:
            hunter (TreasureHunter): The hunter to add to the hideout
            
        Raises:
            TypeError: If hunter is not an instance of TreasureHunter
            Exception: If the hideout is at full capacity
        """
        # Check if hunter is an instance of TreasureHunter
        if not isinstance(hunter, TreasureHunter):
            raise TypeError(f"Hunter must be an instance of TreasureHunter, got {type(hunter)}")
            
        # Check if hideout is full
        if len(self.hunters) >= self.capacity:
            raise Exception(f"Hideout is at full capacity ({self.capacity} hunters)")
            
        # Add hunter to the list
        self.hunters.append(hunter)
        self._share_memory(hunter)  # Share information with the new hunter
    
    def __repr__(self) -> str:
        """
        Get a string representation of the hideout.
        
        Returns:
            str: A string describing the hideout
        """
        return f"Hideout({self.x}, {self.y}, hunters={len(self.hunters)}, treasure={len(self.stored_treasure)})" 