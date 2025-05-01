from abc import ABC, abstractmethod
from typing import Tuple

class Entity(ABC):
    """Abstract base class for all entities in the game."""
    
    def __init__(self, x: int, y: int):
        """
        Initialize an entity with its position.
        
        Args:
            x (int): The x-coordinate of the entity
            y (int): The y-coordinate of the entity
            
        Raises:
            TypeError: If x or y is not an integer
        """
        if not isinstance(x, int):
            raise TypeError(f"x must be an integer, got {type(x)}")
        if not isinstance(y, int):
            raise TypeError(f"y must be an integer, got {type(y)}")
            
        self.x = x
        self.y = y
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the current position of the entity.
        
        Returns:
            Tuple[int, int]: The (x, y) coordinates of the entity
        """
        return (self.x, self.y)
    
    @abstractmethod
    def move(self, grid) -> None:
        """
        Abstract method for moving the entity.
        
        Args:
            grid: The game grid containing all entities
        """
        pass
    
    @abstractmethod
    def update(self, grid) -> None:
        """
        Abstract method for updating the entity's state.
        
        Args:
            grid: The game grid containing all entities
        """
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """
        Abstract method for string representation of the entity.
        
        Returns:
            str: A string representation of the entity
        """
        pass 