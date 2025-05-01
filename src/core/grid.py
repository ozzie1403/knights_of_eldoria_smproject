from typing import List, Dict, Optional, Set, Any, Tuple
import random
import math
from src.core.position import Position
from src.core.treasure import Treasure
from src.core.hunter import Hunter
from src.core.hideout import Hideout
from src.core.enums import EntityType, TreasureType, HunterSkill, CellType
from dataclasses import dataclass
from src.core.knight import Knight
from src.core.garrison import Garrison
from enum import Enum

@dataclass
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class CellType(Enum):
    EMPTY = 0
    TREASURE = 1
    HUNTER = 2
    HIDEOUT = 3
    KNIGHT = 4
    GARRISON = 5

class Grid:
    MIN_SIZE = 20
    MAX_SIZE = 100

    def __init__(self, size: int = 20):
        if size < self.MIN_SIZE:
            raise ValueError(f"Grid size must be at least {self.MIN_SIZE}x{self.MIN_SIZE}")
        if size > self.MAX_SIZE:
            raise ValueError(f"Grid size cannot exceed {self.MAX_SIZE}x{self.MAX_SIZE}")
            
        self.size = size
        self.grid = [[CellType.EMPTY for _ in range(size)] for _ in range(size)]
        self.entities: Dict[Tuple[int, int], Any] = {}
        self.treasures: List[Any] = []
        self.hunters: List[Any] = []
        self.knights: List[Any] = []
        self.hideouts: List[Any] = []
        self.garrisons: List[Any] = []

    def add_entity(self, entity: Any) -> bool:
        """Add an entity to the grid."""
        if entity.position not in self.entities:
            self.entities[entity.position] = entity
            self.set_cell(entity.position[0], entity.position[1], entity.cell_type)

            if isinstance(entity, Treasure):
                self.treasures.append(entity)
            elif isinstance(entity, Hunter):
                self.hunters.append(entity)
            elif isinstance(entity, Knight):
                self.knights.append(entity)
            elif isinstance(entity, Hideout):
                self.hideouts.append(entity)
            elif isinstance(entity, Garrison):
                self.garrisons.append(entity)

            return True
        return False

    def remove_entity(self, position: Tuple[int, int]) -> bool:
        """Remove an entity from the grid."""
        if position in self.entities:
            entity = self.entities.pop(position)
            if isinstance(entity, Treasure):
                if entity in self.treasures:
                    self.treasures.remove(entity)
            elif isinstance(entity, Hunter):
                if entity in self.hunters:
                    self.hunters.remove(entity)
            elif isinstance(entity, Knight):
                if entity in self.knights:
                    self.knights.remove(entity)
            elif isinstance(entity, Hideout):
                if entity in self.hideouts:
                    self.hideouts.remove(entity)
            elif isinstance(entity, Garrison):
                if entity in self.garrisons:
                    self.garrisons.remove(entity)
            self.set_cell(position[0], position[1], CellType.EMPTY)
            return True
        return False

    def get_entity_at(self, position: Tuple[int, int]) -> Optional[Any]:
        """Get the entity at a specific position."""
        return self.entities.get(position)

    def get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all adjacent positions (including diagonals) with wrapping."""
        x, y = position
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = self.wrap_position(x + dx, y + dy)
                positions.append((new_x, new_y))
        return positions

    def get_random_empty_position(self) -> Optional[Tuple[int, int]]:
        """Get a random empty position on the grid."""
        empty_positions = [
            pos for pos in [(x, y) for x in range(self.size) for y in range(self.size)]
            if pos not in self.entities
        ]
        return random.choice(empty_positions) if empty_positions else None

    def wrap_position(self, x: int, y: int) -> Tuple[int, int]:
        """Wrap coordinates around the grid edges (toroidal)."""
        return (x % self.size, y % self.size)

    def get_cell(self, x: int, y: int) -> CellType:
        """Get the type of cell at the given position."""
        x, y = self.wrap_position(x, y)
        return self.grid[x][y]

    def set_cell(self, x: int, y: int, cell_type: CellType):
        """Set the type of cell at the given position."""
        x, y = self.wrap_position(x, y)
        self.grid[x][y] = cell_type

    def move_entity(self, old_position: Tuple[int, int], new_position: Tuple[int, int]) -> bool:
        """Move an entity from one position to another."""
        if old_position in self.entities and new_position not in self.entities:
            entity = self.entities.pop(old_position)
            entity.position = new_position
            self.entities[new_position] = entity
            self.set_cell(new_position[0], new_position[1], entity.cell_type)
            return True
        return False

    def get_empty_cell_count(self) -> int:
        """Get the number of empty cells in the grid."""
        return (self.size * self.size) - len(self.entities)

    def get_entity_count(self) -> Dict[str, int]:
        """Get the count of each entity type in the grid."""
        return {
            'treasures': len(self.treasures),
            'hunters': len(self.hunters),
            'knights': len(self.knights),
            'hideouts': len(self.hideouts),
            'garrisons': len(self.garrisons),
            'empty': self.get_empty_cell_count()
        }

    def get_entities_in_radius(self, position: Tuple[int, int], radius: int) -> List[Any]:
        """Get all entities within a certain radius of a position."""
        x, y = position
        entities = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                pos = self.wrap_position(x + dx, y + dy)
                entity = self.get_entity_at(pos)
                if entity:
                    entities.append(entity)
        return entities

    def __repr__(self) -> str:
        return f"Grid(Size: {self.size}x{self.size}, Treasures: {len(self.treasures)}, Hunters: {len(self.hunters)}, Knights: {len(self.knights)}, Hideouts: {len(self.hideouts)}, Garrisons: {len(self.garrisons)})"

class EldoriaGrid:
    def __init__(self, size: int, min_treasures: int = 5, max_treasures: int = 15):
        """
        Initialize a toroidal grid of given size with random treasures.
        
        Args:
            size (int): The size of the grid (size x size)
            min_treasures (int): Minimum number of treasures to place
            max_treasures (int): Maximum number of treasures to place
        """
        if size < 1:
            raise ValueError("Grid size must be positive")
        self.size = size
        self.grid: List[List[CellType]] = [[CellType.EMPTY for _ in range(size)] for _ in range(size)]
        self.entities: Dict[Tuple[int, int], Any] = {}
        self.treasures: List[Treasure] = []
        
        # Place random treasures
        self._place_random_treasures(min_treasures, max_treasures)
    
    def _place_random_treasures(self, min_treasures: int, max_treasures: int) -> None:
        """Place random treasures on the grid."""
        num_treasures = random.randint(min_treasures, max_treasures)
        for _ in range(num_treasures):
            pos = self.get_random_empty_position()
            if pos:
                treasure_type = random.choice(list(TreasureType))
                treasure = Treasure(pos, treasure_type)
                if self.add_entity(treasure):
                    self.treasures.append(treasure)
    
    def update_treasures(self) -> None:
        """Update all treasures (decay) and remove depleted ones."""
        for treasure in self.treasures[:]:  # Create a copy to allow removal
            if treasure.decay():
                self.remove_entity(treasure.position)
                self.treasures.remove(treasure)
    
    def wrap_position(self, x: int, y: int) -> Tuple[int, int]:
        """
        Wrap coordinates around the grid edges (toroidal).
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Tuple[int, int]: Wrapped coordinates
        """
        return (x % self.size, y % self.size)
    
    def get_cell(self, x: int, y: int) -> CellType:
        """
        Get the cell type at the given position with wrap-around.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            CellType: The type of cell at the position
        """
        x, y = self.wrap_position(x, y)
        return self.grid[x][y]
    
    def set_cell(self, x: int, y: int, cell_type: CellType) -> None:
        """
        Set the cell type at the given position with wrap-around.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            cell_type (CellType): The type to set the cell to
        """
        x, y = self.wrap_position(x, y)
        self.grid[x][y] = cell_type
    
    def add_entity(self, entity: Any) -> bool:
        """
        Add an entity to the grid.
        
        Args:
            entity (Any): The entity to add (must have position and cell_type attributes)
            
        Returns:
            bool: True if entity was added successfully, False otherwise
        """
        if entity.position not in self.entities:
            self.entities[entity.position] = entity
            self.set_cell(entity.position[0], entity.position[1], entity.cell_type)
            return True
        return False
    
    def remove_entity(self, position: Tuple[int, int]) -> bool:
        """
        Remove an entity from the grid.
        
        Args:
            position (Tuple[int, int]): The position to remove from
            
        Returns:
            bool: True if entity was removed successfully, False otherwise
        """
        if position in self.entities:
            entity = self.entities[position]
            if isinstance(entity, Treasure) and entity in self.treasures:
                self.treasures.remove(entity)
            del self.entities[position]
            self.set_cell(position[0], position[1], CellType.EMPTY)
            return True
        return False
    
    def get_entity_at(self, position: Tuple[int, int]) -> Optional[Any]:
        """
        Get the entity at a specific position.
        
        Args:
            position (Tuple[int, int]): The position to check
            
        Returns:
            Optional[Any]: The entity at the position, or None if empty
        """
        return self.entities.get(position)
    
    def move_entity(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Move an entity from one position to another.
        
        Args:
            from_pos (Tuple[int, int]): Current position
            to_pos (Tuple[int, int]): Target position
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        if from_pos in self.entities and to_pos not in self.entities:
            entity = self.entities.pop(from_pos)
            self.entities[to_pos] = entity
            self.set_cell(from_pos[0], from_pos[1], CellType.EMPTY)
            self.set_cell(to_pos[0], to_pos[1], entity.cell_type)
            return True
        return False
    
    def get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get all adjacent positions (including diagonals) with wrapping.
        
        Args:
            position (Tuple[int, int]): The center position
            
        Returns:
            List[Tuple[int, int]]: List of adjacent positions
        """
        x, y = position
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = self.wrap_position(x + dx, y + dy)
                positions.append((new_x, new_y))
        return positions
    
    def get_random_empty_position(self) -> Optional[Tuple[int, int]]:
        """
        Get a random empty position on the grid.
        
        Returns:
            Optional[Tuple[int, int]]: A random empty position, or None if grid is full
        """
        empty_positions = [
            (x, y) for x in range(self.size) for y in range(self.size)
            if self.get_cell(x, y) == CellType.EMPTY
        ]
        return random.choice(empty_positions) if empty_positions else None
    
    def display(self) -> None:
        """Display the current state of the grid."""
        for y in range(self.size):
            row = []
            for x in range(self.size):
                cell = self.get_cell(x, y)
                row.append(cell.value)
            print(" ".join(row))
        print()  # Empty line for readability
    
    def __repr__(self) -> str:
        return f"EldoriaGrid(Size: {self.size}x{self.size}, Entities: {len(self.entities)}, Treasures: {len(self.treasures)})"

    def place_hideouts(self, num_hideouts: int) -> None:
        """Place hideouts randomly on the grid."""
        for _ in range(num_hideouts):
            pos = self.get_random_empty_position()
            if pos:
                hideout = Hideout(pos)
                self.add_entity(hideout)

    def place_knights(self, num_knights: int) -> None:
        """Place knights randomly on the grid."""
        for _ in range(num_knights):
            pos = self.get_random_empty_position()
            if pos:
                knight = Knight(pos)
                self.add_entity(knight)

    def place_garrisons(self, num_garrisons: int) -> None:
        """Place garrisons randomly on the grid."""
        for _ in range(num_garrisons):
            pos = self.get_random_empty_position()
            if pos:
                garrison = Garrison(pos)
                self.add_entity(garrison)

    def update(self) -> None:
        """Update all entities in the grid."""
        # Update all garrisons first
        for entity in list(self.entities.values()):
            if entity.entity_type == EntityType.GARRISON:
                entity.update()
        
        # Update all hideouts
        for entity in list(self.entities.values()):
            if entity.entity_type == EntityType.HIDEOUT:
                entity.update()
        
        # Update all knights
        for entity in list(self.entities.values()):
            if entity.entity_type == EntityType.KNIGHT:
                entity.update(self)
        
        # Update all other entities
        for entity in list(self.entities.values()):
            if entity.entity_type not in [EntityType.GARRISON, EntityType.HIDEOUT, EntityType.KNIGHT]:
                entity.update(self) 