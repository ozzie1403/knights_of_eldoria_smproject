from typing import List, Tuple, Optional, Dict, Any
import random
from models.enums import CellType, TreasureType, HunterSkill, HunterState
from logic.game_logic import GameLogic

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
            TreasureType.BRONZE.value: 70.0,  # Bronze starts with 70 value
            TreasureType.SILVER.value: 80.0,  # Silver starts with 80 value
            TreasureType.GOLD.value: 99.0     # Gold starts with 99 value
        }
        # Value degradation rate per step
        self.treasure_degradation_rate = 0.001  # 0.1% degradation per step
    
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
            treasure_name = "Bronze" if treasure_type == TreasureType.BRONZE.value else \
                          "Silver" if treasure_type == TreasureType.SILVER.value else "Gold"
            print(f"[DEBUG][grid] {treasure_name} treasure at {pos} degrading: {current_value:.2f} -> {new_value:.2f}")
            
            if new_value <= 0:
                # Mark treasure for removal
                treasures_to_remove.append(pos)
                print(f"[DEBUG][grid] {treasure_name} treasure at {pos} has lost all value, removing from simulation")
            else:
                # Update treasure value
                self.treasure_values[pos] = (treasure_type, new_value)
        
        # Remove treasures that have lost all value
        for pos in treasures_to_remove:
            old_type = self.treasure_values[pos][0]
            treasure_name = "Bronze" if old_type == TreasureType.BRONZE.value else \
                          "Silver" if old_type == TreasureType.SILVER.value else "Gold"
            print(f"[DEBUG][grid] Removing {treasure_name} treasure at {pos} from grid")
            self.set_cell(pos[0], pos[1], CellType.EMPTY.value)
            self.treasure_values.pop(pos)
    
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
    
    def random_fill(self, reserved_positions=None) -> None:
        """
        Fill grid with random cell types, ensuring exactly 5 hunters, 1 hideout, and 12 treasures (4 bronze, 4 silver, 4 gold).
        If reserved_positions is provided, those cells are left untouched.
        """
        if reserved_positions is None:
            reserved_positions = set()
        # First clear the grid
        self.clear_grid()
        # Create a list of all possible positions, skipping reserved
        positions = [(x, y) for y in range(self.height) for x in range(self.width)
                     if (x, y) not in reserved_positions]
        random.shuffle(positions)
        # Place exactly 5 hunters
        for _ in range(5):
            if positions:
                x, y = positions.pop()
                self.set_cell(x, y, CellType.TREASURE_HUNTER.value)
        # Place exactly 1 hideout
        if positions:
            x, y = positions.pop()
            self.set_cell(x, y, CellType.HIDEOUT.value)
        # Place exactly 4 bronze, 4 silver, 4 gold treasures
        for _ in range(4):
            if positions:
                x, y = positions.pop()
                self.set_cell(x, y, CellType.TREASURE.value, TreasureType.BRONZE)
        for _ in range(4):
            if positions:
                x, y = positions.pop()
                self.set_cell(x, y, CellType.TREASURE.value, TreasureType.SILVER)
        for _ in range(4):
            if positions:
                x, y = positions.pop()
                self.set_cell(x, y, CellType.TREASURE.value, TreasureType.GOLD)
        # Fill remaining positions with empty
        for x, y in positions:
            self.set_cell(x, y, CellType.EMPTY.value)
    
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

    def get_hunter_stamina(self, x: int, y: int) -> Optional[float]:
        """
        Get the stamina of a hunter at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Optional[float]: Hunter's stamina if position contains a hunter, None otherwise
        """
        hunter = self.get_hunter_at(x, y)
        if hunter is not None:
            return hunter.get_stamina_percentage()
        return None

    def get_grid_contents(self, x: int, y: int) -> Dict[str, Any]:
        """
        Get the contents of a cell at the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Dict[str, Any]: Dictionary containing cell information
        """
        cell_type = self.get_cell(x, y)
        cell_info = {'type': cell_type}
        
        if cell_type == CellType.TREASURE_HUNTER.value:
            # Get hunter's stamina
            stamina = self.get_hunter_stamina(x, y)
            if stamina is not None:
                cell_info['stamina'] = stamina
                print(f"[DEBUG] Hunter at ({x},{y}) stamina: {stamina:.2f}")
            
            # Get hunter's state and check if carrying treasure
            hunter = self.get_hunter_at(x, y)
            if hunter is not None:
                cell_info['state'] = hunter.state
                cell_info['hunter_id'] = hunter.hunter_id
                if hunter.carried_treasure is not None:
                    cell_info['carrying'] = True
                    print(f"[DEBUG] Hunter at ({x},{y}) is carrying treasure")
                
                # Add wealth information
                wealth = self.get_hunter_wealth(x, y)
                if wealth is not None:
                    cell_info['wealth'] = wealth
                    print(f"[DEBUG][grid] Hunter at ({x},{y}) wealth: {wealth:.2f}")
        
        elif cell_type == CellType.TREASURE.value:
            treasure_data = self.get_treasure_value(x, y)
            if treasure_data:
                treasure_type, value = treasure_data
                cell_info['value'] = value
                cell_info['treasure_type'] = treasure_type
        
        return cell_info
    
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
            return '*'  # Or any symbol you want for treasures
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