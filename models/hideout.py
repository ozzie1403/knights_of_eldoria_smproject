from typing import List, Tuple, Dict, Optional, Set
from enum import Enum
import random
from models.grid import Grid
from models.enums import CellType, TreasureType, HunterSkill

class HideoutState(Enum):
    """Enum for different states a hideout can be in"""
    ACTIVE = 0      # Hideout is active and can accept hunters
    FULL = 1        # Hideout is at maximum capacity
    INACTIVE = 2    # Hideout is temporarily inactive

class StoredTreasure:
    """Class to store information about treasures stored in the hideout"""
    def __init__(self, treasure_type: int, value: float, collection_time: int):
        self.treasure_type = treasure_type
        self.value = value
        self.collection_time = collection_time

class Hideout:
    def __init__(self, grid: Grid, x: int, y: int):
        """
        Initialize a hideout with position and storage capacity.
        
        Args:
            grid (Grid): The game grid
            x (int): X coordinate
            y (int): Y coordinate
        """
        self.grid = grid
        self.x = x
        self.y = y
        self.state = HideoutState.ACTIVE
        self.max_capacity = 5  # Maximum number of treasures that can be stored
        self.stored_treasures: List[StoredTreasure] = []
        self.current_hunters: List[Tuple[int, int]] = []  # List of hunter positions
        self.max_hunters = 5  # Maximum number of hunters that can rest here (updated to 5)
        self.total_value_stored = 0.0  # Total value of all stored treasures
        self.current_step = 0  # Current simulation step
        self.recruitment_cooldown = 0  # Cooldown for recruitment attempts
        self.recruitment_cooldown_steps = 10  # Steps between recruitment attempts
        
        # Ensure the hideout is placed in the grid
        self.grid.set_cell(x, y, CellType.HIDEOUT.value)
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the hideout's position.
        
        Returns:
            Tuple[int, int]: (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_state(self) -> HideoutState:
        """
        Get the current state of the hideout.
        
        Returns:
            HideoutState: Current state
        """
        return self.state
    
    def get_stored_treasures(self) -> List[StoredTreasure]:
        """
        Get all treasures stored in the hideout.
        
        Returns:
            List[StoredTreasure]: List of stored treasures
        """
        return self.stored_treasures.copy()
    
    def get_current_hunters(self) -> List[Tuple[int, int]]:
        """
        Get positions of all hunters currently in the hideout.
        
        Returns:
            List[Tuple[int, int]]: List of hunter positions
        """
        return self.current_hunters.copy()
    
    def get_hunters(self) -> List[Tuple[int, int]]:
        """
        Get positions of all hunters currently in the hideout.
        This is an alias for get_current_hunters for compatibility.
        
        Returns:
            List[Tuple[int, int]]: List of hunter positions
        """
        return self.get_current_hunters()
    
    def get_total_value(self) -> float:
        """
        Get the total value of all stored treasures.
        
        Returns:
            float: Total value
        """
        return self.total_value_stored
    
    def can_accept_hunter(self) -> bool:
        """
        Check if the hideout can accept another hunter.
        
        Returns:
            bool: True if hideout can accept another hunter
        """
        return (self.state == HideoutState.ACTIVE and 
                len(self.current_hunters) < self.max_hunters)
    
    def can_store_treasure(self) -> bool:
        """
        Check if the hideout can store another treasure.
        
        Returns:
            bool: True if hideout can store another treasure
        """
        return (self.state == HideoutState.ACTIVE and 
                len(self.stored_treasures) < self.max_capacity)
    
    def add_hunter(self, hunter_x: int, hunter_y: int) -> bool:
        """
        Add a hunter to the hideout.
        
        Args:
            hunter_x (int): Hunter's X coordinate
            hunter_y (int): Hunter's Y coordinate
            
        Returns:
            bool: True if hunter was added successfully
        """
        if not self.can_accept_hunter():
            return False
        
        hunter_pos = (hunter_x, hunter_y)
        if hunter_pos not in self.current_hunters:
            self.current_hunters.append(hunter_pos)
            self.update_state()
            return True
        return False
    
    def remove_hunter(self, hunter_x: int, hunter_y: int) -> bool:
        """
        Remove a hunter from the hideout.
        
        Args:
            hunter_x (int): Hunter's X coordinate
            hunter_y (int): Hunter's Y coordinate
            
        Returns:
            bool: True if hunter was removed successfully
        """
        hunter_pos = (hunter_x, hunter_y)
        if hunter_pos in self.current_hunters:
            self.current_hunters.remove(hunter_pos)
            self.update_state()
            return True
        return False
    
    def store_treasure(self, treasure_type: int, value: float, collection_time: int) -> bool:
        """
        Store a treasure in the hideout.
        
        Args:
            treasure_type (int): Type of treasure
            value (float): Value of treasure
            collection_time (int): Time when treasure was collected
            
        Returns:
            bool: True if treasure was stored successfully
        """
        if not self.can_store_treasure():
            return False
        
        treasure = StoredTreasure(treasure_type, value, collection_time)
        self.stored_treasures.append(treasure)
        self.total_value_stored += value
        self.update_state()
        return True
    
    def remove_treasure(self, index: int) -> Optional[StoredTreasure]:
        """
        Remove a treasure from the hideout.
        
        Args:
            index (int): Index of treasure to remove
            
        Returns:
            Optional[StoredTreasure]: Removed treasure if successful, None otherwise
        """
        if 0 <= index < len(self.stored_treasures):
            treasure = self.stored_treasures.pop(index)
            self.total_value_stored -= treasure.value
            self.update_state()
            return treasure
        return None
    
    def update_state(self) -> None:
        """
        Update the hideout's state based on current conditions.
        """
        if len(self.stored_treasures) >= self.max_capacity:
            self.state = HideoutState.FULL
        elif len(self.current_hunters) >= self.max_hunters:
            self.state = HideoutState.FULL
        else:
            self.state = HideoutState.ACTIVE
    
    def get_treasure_summary(self) -> Dict[int, int]:
        """
        Get a summary of stored treasures by type.
        
        Returns:
            Dict[int, int]: Dictionary mapping treasure types to counts
        """
        summary = {treasure_type.value: 0 for treasure_type in TreasureType}
        for treasure in self.stored_treasures:
            summary[treasure.treasure_type] += 1
        return summary
    
    def get_average_treasure_value(self) -> float:
        """
        Get the average value of stored treasures.
        
        Returns:
            float: Average value, or 0.0 if no treasures
        """
        if not self.stored_treasures:
            return 0.0
        return self.total_value_stored / len(self.stored_treasures)
    
    def is_at_position(self, x: int, y: int) -> bool:
        """
        Check if the hideout is at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if hideout is at the position
        """
        return self.x == x and self.y == y
    
    def get_hunter_count(self) -> int:
        """
        Get the current number of hunters in the hideout.
        
        Returns:
            int: Number of hunters
        """
        return len(self.current_hunters)
    
    def get_available_hunter_slots(self) -> int:
        """
        Get the number of available hunter slots.
        
        Returns:
            int: Number of available slots
        """
        return self.max_hunters - len(self.current_hunters)
    
    def get_hunter_skills(self) -> List[HunterSkill]:
        """
        Get the skills of all hunters in the hideout.
        
        Returns:
            List[HunterSkill]: List of hunter skills
        """
        skills = []
        for hunter_pos in self.current_hunters:
            # Get hunter from grid
            hunter = self.grid.get_hunter_at(hunter_pos[0], hunter_pos[1])
            if hunter:
                skills.append(hunter.get_skill())
        return skills
    
    def has_skill_diversity(self) -> bool:
        """
        Check if the hideout has a diverse mix of skills.
        
        Returns:
            bool: True if there are at least 2 different skills present
        """
        skills = self.get_hunter_skills()
        return len(set(skills)) >= 2
    
    def can_recruit(self) -> bool:
        """
        Check if the hideout can attempt to recruit a new hunter.
        
        Returns:
            bool: True if recruitment is possible
        """
        return (self.state == HideoutState.ACTIVE and
                len(self.current_hunters) < self.max_hunters and
                self.recruitment_cooldown == 0 and
                self.has_skill_diversity())
    
    def attempt_recruitment(self) -> bool:
        """
        Attempt to recruit a new hunter.
        Has a 20% chance of success if conditions are met.
        
        Returns:
            bool: True if recruitment was successful
        """
        if not self.can_recruit():
            return False
        
        # 20% chance of successful recruitment
        if random.random() < 0.2:
            # Get existing skills
            existing_skills = self.get_hunter_skills()
            # Choose a random skill from existing hunters
            new_skill = random.choice(existing_skills)
            
            # Find an empty adjacent cell for the new hunter
            adjacent_positions = self.grid.get_all_neighbors(self.x, self.y)
            empty_positions = [pos for pos in adjacent_positions 
                             if self.grid.get_cell(pos[0], pos[1]) == CellType.EMPTY.value]
            
            if empty_positions:
                # Create new hunter at random empty position
                new_pos = random.choice(empty_positions)
                new_hunter = self.grid.create_hunter(new_pos[0], new_pos[1], new_skill)
                if new_hunter:
                    self.add_hunter(new_pos[0], new_pos[1])
                    self.recruitment_cooldown = self.recruitment_cooldown_steps
                    return True
        
        return False
    
    def update(self) -> None:
        """
        Update the hideout's state and attempt recruitment if possible.
        """
        self.current_step += 1
        
        # Update recruitment cooldown
        if self.recruitment_cooldown > 0:
            self.recruitment_cooldown -= 1
        
        # Attempt recruitment
        self.attempt_recruitment()
    
    def get_skill_distribution(self) -> Dict[HunterSkill, int]:
        """
        Get the distribution of skills among hunters in the hideout.
        
        Returns:
            Dict[HunterSkill, int]: Dictionary mapping skills to their count
        """
        distribution = {skill: 0 for skill in HunterSkill}
        for skill in self.get_hunter_skills():
            distribution[skill] += 1
        return distribution 