from typing import List, Tuple, Optional, Dict
import random
from models.enums import CellType, TreasureType, HunterSkill

class Grid:
    def __init__(self, width: int, height: int):
        """
        Initialize a 2D grid for the simulation with wraparound edges.
        
        Args:
            width (int): Width of the grid
            height (int): Height of the grid
        """
        self.width = width
        self.height = height
        # Initialize grid with empty cells using list comprehension
        self.grid = [[CellType.EMPTY.value for _ in range(width)] for _ in range(height)]
        # Dictionary to store entity positions for quick lookup
        self.entity_positions: Dict[int, List[Tuple[int, int]]] = {
            CellType.TREASURE.value: [],
            CellType.TREASURE_HUNTER.value: [],
            CellType.HIDEOUT.value: [],
            CellType.KNIGHT.value: [],
            CellType.GARRISON.value: []
        }
        # Dictionary to store treasure values and their remaining value
        self.treasure_values: Dict[Tuple[int, int], Tuple[int, float]] = {}
        # Dictionary to store hunter wealth
        self.hunter_wealth: Dict[Tuple[int, int], float] = {}
        # Initial wealth for hunters
        self.initial_wealth = 100.0
        # Treasure value multipliers
        self.treasure_multipliers = {
            TreasureType.BRONZE.value: 0.03,  # 3%
            TreasureType.SILVER.value: 0.07,  # 7%
            TreasureType.GOLD.value: 0.13     # 13%
        }
        # Initial treasure values
        self.initial_treasure_values = {
            TreasureType.BRONZE.value: 50.0,  # Bronze starts with 50 value
            TreasureType.SILVER.value: 100.0, # Silver starts with 100 value
            TreasureType.GOLD.value: 200.0    # Gold starts with 200 value
        }
        # Value degradation rate per step
        self.treasure_degradation_rate = 0.1  # 10% degradation per step
    
    def wrap_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Wrap coordinates around the grid edges.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Tuple[int, int]: Wrapped coordinates
        """
        wrapped_x = x % self.width
        wrapped_y = y % self.height
        return wrapped_x, wrapped_y
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        All positions are valid due to wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: Always True due to wraparound
        """
        return True
    
    def get_cell(self, x: int, y: int) -> int:
        """
        Get the value at the specified cell with wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            int: Value at the cell
        """
        wrapped_x, wrapped_y = self.wrap_coordinates(x, y)
        return self.grid[wrapped_y][wrapped_x]
    
    def get_treasure_value(self, x: int, y: int) -> Optional[Tuple[int, float]]:
        """
        Get the treasure type and remaining value at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Optional[Tuple[int, float]]: (treasure_type, remaining_value) if position contains treasure, None otherwise
        """
        wrapped_x, wrapped_y = self.wrap_coordinates(x, y)
        return self.treasure_values.get((wrapped_x, wrapped_y))
    
    def get_hunter_wealth(self, x: int, y: int) -> Optional[float]:
        """
        Get the wealth of a hunter at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Optional[float]: Hunter's wealth if position contains a hunter, None otherwise
        """
        wrapped_x, wrapped_y = self.wrap_coordinates(x, y)
        return self.hunter_wealth.get((wrapped_x, wrapped_y))
    
    def collect_treasure(self, hunter_x: int, hunter_y: int) -> Optional[float]:
        """
        Collect treasure at the hunter's position and update their wealth.
        
        Args:
            hunter_x (int): Hunter's X coordinate
            hunter_y (int): Hunter's Y coordinate
            
        Returns:
            Optional[float]: New wealth if treasure was collected, None otherwise
        """
        wrapped_x, wrapped_y = self.wrap_coordinates(hunter_x, hunter_y)
        
        # Get treasure value and current wealth
        treasure_data = self.treasure_values.get((wrapped_x, wrapped_y))
        current_wealth = self.hunter_wealth.get((wrapped_x, wrapped_y), self.initial_wealth)
        
        if treasure_data is not None:
            treasure_type, remaining_value = treasure_data
            # Calculate wealth increase based on remaining value
            multiplier = self.treasure_multipliers[treasure_type]
            new_wealth = current_wealth * (1 + multiplier)
            
            # Update hunter's wealth
            self.hunter_wealth[(wrapped_x, wrapped_y)] = new_wealth
            
            # Remove the treasure and place hunter there
            self.set_cell(wrapped_x, wrapped_y, CellType.TREASURE_HUNTER.value)
            
            return new_wealth
        
        return None
    
    def degrade_treasures(self) -> None:
        """
        Degrade all treasures' values and remove those that have lost all value.
        """
        treasures_to_remove = []
        
        for pos, (treasure_type, current_value) in self.treasure_values.items():
            # Calculate new value after degradation
            new_value = current_value * (1 - self.treasure_degradation_rate)
            
            if new_value <= 0:
                # Mark treasure for removal
                treasures_to_remove.append(pos)
            else:
                # Update treasure value
                self.treasure_values[pos] = (treasure_type, new_value)
        
        # Remove treasures that have lost all value
        for pos in treasures_to_remove:
            self.set_cell(pos[0], pos[1], CellType.EMPTY.value)
    
    def set_cell(self, x: int, y: int, value: int, treasure_type: Optional[TreasureType] = None) -> bool:
        """
        Set the value at the specified cell with wraparound.
        Updates entity positions tracking, treasure values, and hunter wealth.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            value (int): Value to set
            treasure_type (Optional[TreasureType]): Type of treasure if setting a treasure cell
            
        Returns:
            bool: Always True due to wraparound
        """
        wrapped_x, wrapped_y = self.wrap_coordinates(x, y)
        old_value = self.grid[wrapped_y][wrapped_x]
        
        # Remove old position from entity tracking
        if old_value in self.entity_positions:
            pos = (wrapped_x, wrapped_y)
            if pos in self.entity_positions[old_value]:
                self.entity_positions[old_value].remove(pos)
        
        # Remove old treasure value if exists
        if old_value == CellType.TREASURE.value:
            self.treasure_values.pop((wrapped_x, wrapped_y), None)
        
        # Remove old hunter wealth if exists
        if old_value == CellType.TREASURE_HUNTER.value:
            self.hunter_wealth.pop((wrapped_x, wrapped_y), None)
        
        # Set new value
        self.grid[wrapped_y][wrapped_x] = value
        
        # Add new position to entity tracking
        if value in self.entity_positions:
            self.entity_positions[value].append((wrapped_x, wrapped_y))
        
        # Set treasure value if provided
        if value == CellType.TREASURE.value and treasure_type is not None:
            initial_value = self.initial_treasure_values[treasure_type.value]
            self.treasure_values[(wrapped_x, wrapped_y)] = (treasure_type.value, initial_value)
        
        # Initialize hunter wealth if placing a new hunter
        if value == CellType.TREASURE_HUNTER.value:
            self.hunter_wealth[(wrapped_x, wrapped_y)] = self.initial_wealth
        
        return True
    
    def clear_cell(self, x: int, y: int) -> bool:
        """
        Clear the value at the specified cell (set to EMPTY) with wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: Always True due to wraparound
        """
        return self.set_cell(x, y, CellType.EMPTY.value)
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get neighboring positions (up, down, left, right) with wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            List[Tuple[int, int]]: List of neighboring positions
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # up, right, down, left
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            wrapped_x, wrapped_y = self.wrap_coordinates(new_x, new_y)
            neighbors.append((wrapped_x, wrapped_y))
                
        return neighbors
    
    def get_diagonal_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get diagonal neighboring positions with wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            List[Tuple[int, int]]: List of diagonal neighboring positions
        """
        neighbors = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # diagonal directions
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            wrapped_x, wrapped_y = self.wrap_coordinates(new_x, new_y)
            neighbors.append((wrapped_x, wrapped_y))
                
        return neighbors
    
    def get_all_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all neighboring positions (including diagonals) with wraparound.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            List[Tuple[int, int]]: List of all neighboring positions
        """
        return self.get_neighbors(x, y) + self.get_diagonal_neighbors(x, y)
    
    def clear_grid(self) -> None:
        """
        Clear all cells in the grid (set to EMPTY).
        """
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = CellType.EMPTY.value
        # Clear entity positions
        for entity_type in self.entity_positions:
            self.entity_positions[entity_type] = []
        # Clear treasure values
        self.treasure_values.clear()
        # Clear hunter wealth
        self.hunter_wealth.clear()
    
    def random_fill(self) -> None:
        """
        Fill grid with random cell types, ensuring at least one of each entity type.
        """
        # First clear the grid
        self.clear_grid()
        
        # Create a list of all possible positions
        positions = [(x, y) for y in range(self.height) for x in range(self.width)]
        random.shuffle(positions)
        
        # Place one of each entity type
        entity_types = [CellType.TREASURE_HUNTER.value,
                       CellType.HIDEOUT.value,
                       CellType.KNIGHT.value]
        
        for entity_type in entity_types:
            if positions:
                x, y = positions.pop()
                self.set_cell(x, y, entity_type)
        
        # Place some treasures with random values
        num_treasures = min(len(positions) // 3, 5)  # Place up to 5 treasures or 1/3 of remaining positions
        for _ in range(num_treasures):
            if positions:
                x, y = positions.pop()
                treasure_type = random.choice(list(TreasureType))
                self.set_cell(x, y, CellType.TREASURE.value, treasure_type)
        
        # Fill remaining positions randomly
        for x, y in positions:
            value = random.choice([CellType.EMPTY.value] + entity_types)
            self.set_cell(x, y, value)
    
    def get_entity_positions(self, entity_type: int) -> List[Tuple[int, int]]:
        """
        Get all positions of a specific entity type.
        
        Args:
            entity_type (int): The type of entity to find
            
        Returns:
            List[Tuple[int, int]]: List of positions containing the entity
        """
        return self.entity_positions.get(entity_type, [])
    
    def get_treasure_positions(self) -> List[Tuple[Tuple[int, int], Tuple[int, float]]]:
        """
        Get all positions containing treasures and their values.
        
        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, float]]]: List of (position, (type, value)) tuples for treasures
        """
        return [(pos, value) for pos, value in self.treasure_values.items()]
    
    def get_hunter_positions(self) -> List[Tuple[Tuple[int, int], float]]:
        """
        Get all positions containing hunters and their wealth.
        
        Returns:
            List[Tuple[Tuple[int, int], float]]: List of (position, wealth) tuples for hunters
        """
        return [(pos, wealth) for pos, wealth in self.hunter_wealth.items()]
    
    def __str__(self) -> str:
        """
        Return a string representation of the grid.
        """
        return '\n'.join(' '.join(str(cell) for cell in row) for row in self.grid)

    def get_state(self) -> Dict:
        """
        Get the current state of the grid.
        
        Returns:
            Dict: Current grid state including:
                - Grid dimensions
                - Entity positions
                - Treasure values
                - Hunter wealth
        """
        return {
            'width': self.width,
            'height': self.height,
            'entity_positions': self.entity_positions,
            'treasure_values': self.treasure_values,
            'hunter_wealth': self.hunter_wealth
        }

    def get_grid_contents(self) -> List[List[Dict]]:
        """
        Get the contents of the grid in a format suitable for visualization.
        
        Returns:
            List[List[Dict]]: 2D array of cell contents, where each cell contains:
                - type: The cell type (EMPTY, TREASURE, TREASURE_HUNTER, etc.)
                - value: The treasure value if it's a treasure cell
                - wealth: The hunter's wealth if it's a hunter cell
                - symbol: A character representation of the cell type
        """
        contents = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell_type = self.grid[y][x]
                cell_info = {
                    'type': cell_type,
                    'symbol': self._get_cell_symbol(cell_type)
                }
                
                if cell_type == CellType.TREASURE.value:
                    treasure_data = self.get_treasure_value(x, y)
                    if treasure_data:
                        cell_info['value'] = treasure_data[1]
                        cell_info['treasure_type'] = treasure_data[0]
                elif cell_type == CellType.TREASURE_HUNTER.value:
                    cell_info['wealth'] = self.hunter_wealth.get((x, y), self.initial_wealth)
                
                row.append(cell_info)
            contents.append(row)
        return contents
    
    def _get_cell_symbol(self, cell_type: int) -> str:
        """
        Get a character symbol for a cell type.
        
        Args:
            cell_type (int): The cell type value
            
        Returns:
            str: A character representing the cell type
        """
        if cell_type == CellType.EMPTY.value:
            return '.'
        elif cell_type == CellType.TREASURE.value:
            return 'T'
        elif cell_type == CellType.TREASURE_HUNTER.value:
            return 'H'
        elif cell_type == CellType.HIDEOUT.value:
            return 'O'
        elif cell_type == CellType.KNIGHT.value:
            return 'K'
        elif cell_type == CellType.GARRISON.value:
            return 'G'
        return '?'

    def get_all_garrisons(self) -> List['Garrison']:
        """
        Get all garrisons in the grid.
        
        Returns:
            List[Garrison]: List of all garrison objects in the grid
        """
        # Import here to avoid circular imports
        from models.garrison import Garrison
        
        garrisons = []
        for x, y in self.entity_positions.get(CellType.GARRISON.value, []):
            garrison = Garrison(self, x, y)
            garrisons.append(garrison)
        return garrisons

    def get_hunter_at(self, x: int, y: int) -> Optional['TreasureHunter']:
        """
        Get the treasure hunter at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Optional[TreasureHunter]: The hunter at the position if one exists, None otherwise
        """
        # Check if there's a hunter at the position
        if self.get_cell(x, y) != CellType.TREASURE_HUNTER.value:
            return None
        
        # Import here to avoid circular imports
        from models.treasure_hunter import TreasureHunter
        
        # Create a new hunter instance with the position
        # Note: This is a temporary solution - in a real implementation,
        # we would maintain a list of actual hunter instances
        hunter = TreasureHunter(self, x, y, HunterSkill.NAVIGATION)  # Default skill
        return hunter

    def create_hunter(self, x: int, y: int, skill: HunterSkill) -> Optional['TreasureHunter']:
        """
        Create a new treasure hunter at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            skill (HunterSkill): The hunter's primary skill
            
        Returns:
            Optional[TreasureHunter]: The created hunter if successful, None otherwise
        """
        # Check if position is empty
        if self.get_cell(x, y) != CellType.EMPTY.value:
            return None
        
        # Create new hunter
        from models.treasure_hunter import TreasureHunter
        hunter = TreasureHunter(self, x, y, skill)
        
        # Place hunter on grid
        if self.set_cell(x, y, CellType.TREASURE_HUNTER.value):
            return hunter
        
        return None