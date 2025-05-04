from typing import List, Tuple, Optional, Dict
from enum import Enum
from models.grid import Grid
from models.enums import CellType

class GarrisonState(Enum):
    """Enum for different states a garrison can be in"""
    ACTIVE = 0      # Garrison is active and can receive knights
    FULL = 1        # Garrison is at maximum capacity
    INACTIVE = 2    # Garrison is temporarily inactive

class Garrison:
    """
    A garrison in the Kingdom of Eldoria.
    Garrisons serve as recovery points for knights, providing them with
    a safe place to rest and restore their energy. Each garrison has a
    limited capacity for knights and provides energy restoration at a rate
    of 10% per simulation step until knights are fully recovered.
    """
    def __init__(self, grid: Grid, x: int, y: int, max_knights: int = 3):
        """
        Initialize a garrison with position and capacity.
        
        Args:
            grid (Grid): The game grid
            x (int): X coordinate
            y (int): Y coordinate
            max_knights (int): Maximum number of knights the garrison can hold
        """
        self.grid = grid
        self.x = x
        self.y = y
        self.max_knights = max_knights
        self.current_knights: Dict[Tuple[int, int], float] = {}  # Dict of knight positions to their energy levels
        self.state = GarrisonState.ACTIVE
        self.energy_restore_rate = 10.0  # 10% energy restoration per step
        
        # Ensure garrison is placed in the grid
        self.grid.set_cell(x, y, CellType.GARRISON.value)
    
    def can_accept_knight(self) -> bool:
        """
        Check if the garrison can accept another knight.
        
        Returns:
            bool: True if garrison can accept another knight
        """
        return (self.state == GarrisonState.ACTIVE and 
                len(self.current_knights) < self.max_knights)
    
    def accept_knight(self, knight_pos: Tuple[int, int], current_energy: float) -> bool:
        """
        Accept a knight into the garrison for recovery.
        
        Args:
            knight_pos (Tuple[int, int]): Position of the knight to accept
            current_energy (float): Current energy level of the knight
            
        Returns:
            bool: True if knight was accepted
        """
        if not self.can_accept_knight():
            return False
        
        self.current_knights[knight_pos] = current_energy
        
        # Update state if garrison becomes full
        if len(self.current_knights) >= self.max_knights:
            self.state = GarrisonState.FULL
        
        return True
    
    def release_knight(self, knight_pos: Tuple[int, int]) -> Optional[float]:
        """
        Release a knight from the garrison.
        
        Args:
            knight_pos (Tuple[int, int]): Position of the knight to release
            
        Returns:
            Optional[float]: Final energy level of the knight, None if knight wasn't in garrison
        """
        if knight_pos in self.current_knights:
            final_energy = self.current_knights.pop(knight_pos)
            
            # Update state if garrison was full
            if self.state == GarrisonState.FULL:
                self.state = GarrisonState.ACTIVE
            
            return final_energy
        return None
    
    def get_available_slots(self) -> int:
        """
        Get the number of available slots in the garrison.
        
        Returns:
            int: Number of available slots
        """
        return self.max_knights - len(self.current_knights)
    
    def get_energy_restore_rate(self) -> float:
        """
        Get the energy restoration rate for knights in this garrison.
        
        Returns:
            float: Energy restoration rate per step (10%)
        """
        return self.energy_restore_rate
    
    def update(self) -> List[Tuple[Tuple[int, int], float]]:
        """
        Update garrison state and handle knight recovery.
        Restores 10% energy per step for each knight until they are fully recovered.
        
        Returns:
            List[Tuple[Tuple[int, int], float]]: List of knights that are fully recovered
            and ready to be released, with their final energy levels
        """
        fully_recovered_knights = []
        
        # Update energy for each knight
        for knight_pos, current_energy in list(self.current_knights.items()):
            # Restore 10% of max energy (100.0)
            new_energy = min(100.0, current_energy + self.energy_restore_rate)
            self.current_knights[knight_pos] = new_energy
            
            # Check if knight is fully recovered
            if new_energy >= 100.0:
                fully_recovered_knights.append((knight_pos, new_energy))
        
        # Update state based on current capacity
        if len(self.current_knights) >= self.max_knights:
            self.state = GarrisonState.FULL
        elif self.state == GarrisonState.FULL:
            self.state = GarrisonState.ACTIVE
        
        return fully_recovered_knights
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the garrison's position.
        
        Returns:
            Tuple[int, int]: (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_state(self) -> GarrisonState:
        """
        Get the current state of the garrison.
        
        Returns:
            GarrisonState: Current state
        """
        return self.state
    
    def get_knight_energy(self, knight_pos: Tuple[int, int]) -> Optional[float]:
        """
        Get the current energy level of a knight in the garrison.
        
        Args:
            knight_pos (Tuple[int, int]): Position of the knight
            
        Returns:
            Optional[float]: Current energy level, None if knight not in garrison
        """
        return self.current_knights.get(knight_pos) 