from typing import List, Tuple, Optional, Dict, Set
from enum import Enum
from models.grid import Grid
from models.enums import CellType
from models.garrison import Garrison

class KnightState(Enum):
    """Enum for different states a knight can be in"""
    PATROLLING = 0    # Moving around the kingdom
    PURSUING = 1      # Actively pursuing a hunter
    RETURNING = 2     # Returning to patrol route
    RESTING = 3       # Taking a break at a safe location
    EXHAUSTED = 4     # Too tired to continue pursuit
    DETAINING = 5     # Detaining a caught hunter
    CHALLENGING = 6   # Challenging a caught hunter
    RETREATING = 7    # Retreating to nearest garrison

class KnightAction(Enum):
    """Enum for different actions a knight can take when catching a hunter"""
    DETAIN = 0    # Detain the hunter, drain stamina and force treasure drop
    CHALLENGE = 1 # Challenge the hunter to a duel, causing greater stamina drain

class Knight:
    """
    A knight in the Kingdom of Eldoria.
    Knights are responsible for protecting treasures and maintaining order.
    They patrol the kingdom and pursue treasure hunters within their detection radius.
    Each pursuit depletes their energy, limiting how far they can chase.
    When catching a hunter, they can either detain them (5% stamina drain) or
    challenge them to a duel (20% stamina drain). Hunters will remember where
    they lost their treasure, allowing them to attempt retrieval if they escape.
    Knights must retreat to garrisons when their energy falls below 20%.
    """
    def __init__(self, grid: Grid, x: int, y: int):
        """
        Initialize a knight with position and initial state.
        
        Args:
            grid (Grid): The game grid
            x (int): Initial X coordinate
            y (int): Initial Y coordinate
        """
        self.grid = grid
        self.x = x
        self.y = y
        self.state = KnightState.PATROLLING
        self.detection_radius = 3  # Number of cells the knight can detect hunters in
        self.current_target: Optional[Tuple[int, int]] = None  # Position of current target
        self.patrol_route: List[Tuple[int, int]] = []  # List of positions to patrol
        self.current_step = 0  # Current simulation step
        
        # Energy system
        self.max_energy = 100.0
        self.current_energy = self.max_energy
        self.energy_depletion_rate = 20.0  # 20% energy depletion per pursuit step
        self.min_energy_to_pursue = 20.0  # Minimum energy required to continue pursuit
        self.energy_restore_rate = 5.0  # 5% energy restoration per rest step
        self.retreat_threshold = 20.0  # Energy level at which knight must retreat
        
        # Hunter interaction system
        self.stamina_drain_rate = 5.0  # 5% stamina drain when detaining
        self.challenge_stamina_drain_rate = 20.0  # 20% stamina drain when challenging
        self.detainment_duration = 3  # Number of steps to complete detainment
        self.challenge_duration = 5  # Number of steps to complete challenge
        
        # Garrison system
        self.current_garrison: Optional[Garrison] = None
        
        # Ensure knight is placed in the grid
        self.grid.set_cell(x, y, CellType.KNIGHT.value)
    
    def get_energy(self) -> float:
        """
        Get the current energy level.
        
        Returns:
            float: Current energy (0.0 to 100.0)
        """
        return self.current_energy
    
    def get_energy_percentage(self) -> float:
        """
        Get the current energy as a percentage.
        
        Returns:
            float: Current energy percentage (0.0 to 100.0)
        """
        return (self.current_energy / self.max_energy) * 100.0
    
    def can_pursue(self) -> bool:
        """
        Check if the knight has enough energy to continue pursuit.
        
        Returns:
            bool: True if knight has enough energy to pursue
        """
        return self.current_energy >= self.min_energy_to_pursue
    
    def deplete_energy(self) -> None:
        """
        Deplete energy during pursuit.
        """
        self.current_energy = max(0.0, self.current_energy - self.energy_depletion_rate)
        if self.current_energy < self.min_energy_to_pursue:
            self.state = KnightState.EXHAUSTED
    
    def restore_energy(self) -> None:
        """
        Restore energy while resting.
        """
        if self.state == KnightState.RESTING:
            self.current_energy = min(self.max_energy, 
                                    self.current_energy + self.energy_restore_rate)
            if self.current_energy >= self.max_energy:
                self.state = KnightState.PATROLLING
    
    def scan_for_hunters(self) -> List[Tuple[int, int]]:
        """
        Scan the surrounding area for treasure hunters.
        
        Returns:
            List[Tuple[int, int]]: List of hunter positions found
        """
        hunters_found = []
        
        # Scan in a square pattern around the knight
        for dx in range(-self.detection_radius, self.detection_radius + 1):
            for dy in range(-self.detection_radius, self.detection_radius + 1):
                scan_x = self.x + dx
                scan_y = self.y + dy
                
                if self.grid.get_cell(scan_x, scan_y) == CellType.TREASURE_HUNTER.value:
                    hunters_found.append((scan_x, scan_y))
        
        return hunters_found
    
    def select_target(self, hunters: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        Select a target from the list of detected hunters.
        Currently selects the closest hunter.
        
        Args:
            hunters (List[Tuple[int, int]]): List of detected hunter positions
            
        Returns:
            Optional[Tuple[int, int]]: Selected target position, None if no hunters
        """
        if not hunters:
            return None
        
        # Calculate distances to all hunters
        distances = []
        for hunter_x, hunter_y in hunters:
            # Calculate Manhattan distance
            distance = abs(self.x - hunter_x) + abs(self.y - hunter_y)
            distances.append((distance, (hunter_x, hunter_y)))
        
        # Return position of closest hunter
        return min(distances, key=lambda x: x[0])[1]
    
    def move_towards(self, target_x: int, target_y: int) -> bool:
        """
        Move one step towards the target position.
        
        Args:
            target_x (int): Target X coordinate
            target_y (int): Target Y coordinate
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Normalize direction to one step
        if abs(dx) > abs(dy):
            new_x = self.x + (1 if dx > 0 else -1)
            new_y = self.y
        else:
            new_x = self.x
            new_y = self.y + (1 if dy > 0 else -1)
        
        return self.move(new_x, new_y)
    
    def move(self, new_x: int, new_y: int) -> bool:
        """
        Move the knight to a new position if it's adjacent to current position.
        
        Args:
            new_x (int): Target X coordinate
            new_y (int): Target Y coordinate
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Get all possible adjacent positions
        adjacent_positions = self.grid.get_all_neighbors(self.x, self.y)
        
        # Check if target position is adjacent
        if (new_x, new_y) not in adjacent_positions:
            return False
        
        # Check if target position is empty or contains a hunter
        cell_type = self.grid.get_cell(new_x, new_y)
        if cell_type not in [CellType.EMPTY.value, CellType.TREASURE_HUNTER.value]:
            return False
        
        # Move knight
        self.grid.set_cell(self.x, self.y, CellType.EMPTY.value)
        self.grid.set_cell(new_x, new_y, CellType.KNIGHT.value)
        self.x = new_x
        self.y = new_y
        
        # Deplete energy if pursuing
        if self.state == KnightState.PURSUING:
            self.deplete_energy()
        
        return True
    
    def force_treasure_drop(self, hunter_pos: Tuple[int, int], hunter) -> None:
        """
        Force a hunter to drop their treasure and remember its location.
        
        Args:
            hunter_pos (Tuple[int, int]): Position where treasure is dropped
            hunter: The hunter object that lost the treasure
        """
        if hunter.carried_treasure:
            # Get treasure details before dropping
            treasure_type, value = hunter.carried_treasure
            
            # Drop treasure at current position
            self.grid.set_cell(hunter_pos[0], hunter_pos[1], CellType.TREASURE.value)
            self.grid.set_treasure_value(hunter_pos[0], hunter_pos[1], treasure_type, value)
            
            # Make hunter remember the lost treasure
            hunter.remember_lost_treasure(hunter_pos[0], hunter_pos[1], treasure_type, value)
            
            # Clear carried treasure
            hunter.carried_treasure = None
    
    def detain_hunter(self, hunter_pos: Tuple[int, int]) -> bool:
        """
        Detain a caught hunter, draining their stamina and forcing them to drop treasure.
        
        Args:
            hunter_pos (Tuple[int, int]): Position of the hunter to detain
            
        Returns:
            bool: True if detainment was successful
        """
        hunter = self.grid.get_hunter_at(hunter_pos[0], hunter_pos[1])
        if not hunter:
            return False
        
        # Drain hunter's stamina
        current_stamina = hunter.get_stamina()
        new_stamina = max(0.0, current_stamina * (1 - self.stamina_drain_rate / 100.0))
        hunter.current_stamina = new_stamina
        
        # Force treasure drop and make hunter remember it
        self.force_treasure_drop(hunter_pos, hunter)
        
        return True
    
    def challenge_hunter(self, hunter_pos: Tuple[int, int]) -> bool:
        """
        Challenge a caught hunter to a duel, causing greater stamina drain.
        
        Args:
            hunter_pos (Tuple[int, int]): Position of the hunter to challenge
            
        Returns:
            bool: True if challenge was successful
        """
        hunter = self.grid.get_hunter_at(hunter_pos[0], hunter_pos[1])
        if not hunter:
            return False
        
        # Drain hunter's stamina more significantly
        current_stamina = hunter.get_stamina()
        new_stamina = max(0.0, current_stamina * (1 - self.challenge_stamina_drain_rate / 100.0))
        hunter.current_stamina = new_stamina
        
        # Force treasure drop and make hunter remember it
        self.force_treasure_drop(hunter_pos, hunter)
        
        return True
    
    def choose_action(self, hunter_pos: Tuple[int, int]) -> KnightAction:
        """
        Choose an action to take when catching a hunter.
        Currently defaults to detaining.
        
        Args:
            hunter_pos (Tuple[int, int]): Position of the caught hunter
            
        Returns:
            KnightAction: Chosen action
        """
        # For now, always choose to detain
        return KnightAction.DETAIN
    
    def handle_caught_hunter(self, hunter_pos: Tuple[int, int]) -> None:
        """
        Handle a caught hunter based on chosen action.
        
        Args:
            hunter_pos (Tuple[int, int]): Position of the caught hunter
        """
        action = self.choose_action(hunter_pos)
        
        if action == KnightAction.DETAIN:
            self.state = KnightState.DETAINING
            if self.detain_hunter(hunter_pos):
                # Detainment successful, return to resting
                self.state = KnightState.RESTING
            else:
                # Detainment failed, continue pursuit
                self.state = KnightState.PURSUING
        else:  # CHALLENGE
            self.state = KnightState.CHALLENGING
            if self.challenge_hunter(hunter_pos):
                # Challenge successful, return to resting
                self.state = KnightState.RESTING
            else:
                # Challenge failed, continue pursuit
                self.state = KnightState.PURSUING
    
    def find_nearest_garrison(self) -> Optional[Tuple[int, int]]:
        """
        Find the nearest garrison to retreat to.
        
        Returns:
            Optional[Tuple[int, int]]: Position of nearest garrison, None if none found
        """
        garrisons = self.grid.get_all_garrisons()
        if not garrisons:
            return None
        
        # Calculate distances to all garrisons
        distances = []
        for garrison in garrisons:
            garrison_pos = garrison.get_position()
            # Calculate Manhattan distance
            distance = abs(self.x - garrison_pos[0]) + abs(self.y - garrison_pos[1])
            distances.append((distance, garrison_pos))
        
        # Return position of closest garrison
        return min(distances, key=lambda x: x[0])[1]
    
    def needs_retreat(self) -> bool:
        """
        Check if the knight needs to retreat to a garrison.
        
        Returns:
            bool: True if knight's energy is below retreat threshold
        """
        return self.get_energy_percentage() <= self.retreat_threshold
    
    def retreat_to_garrison(self) -> None:
        """
        Begin retreat to the nearest garrison.
        """
        if self.state != KnightState.RETREATING:
            self.state = KnightState.RETREATING
            self.current_target = self.find_nearest_garrison()
    
    def update(self) -> None:
        """
        Update knight's state and perform appropriate actions.
        """
        self.current_step += 1
        
        # Check if knight needs to retreat
        if self.needs_retreat() and self.state != KnightState.RETREATING:
            self.retreat_to_garrison()
        
        # Handle exhausted state
        if self.state == KnightState.EXHAUSTED:
            self.state = KnightState.RETREATING
            self.current_target = self.find_nearest_garrison()
            return
        
        # Handle retreating state
        if self.state == KnightState.RETREATING:
            if self.current_target:
                self.move_towards(self.current_target[0], self.current_target[1])
                
                # Check if we've reached the garrison
                if self.x == self.current_target[0] and self.y == self.current_target[1]:
                    garrison = self.grid.get_garrison_at(self.x, self.y)
                    if garrison and garrison.accept_knight((self.x, self.y), self.current_energy):
                        self.current_garrison = garrison
                        self.state = KnightState.RESTING
                        self.current_target = None
            else:
                # No garrison found, try to find one
                self.current_target = self.find_nearest_garrison()
                if not self.current_target:
                    self.state = KnightState.RESTING
            return
        
        # Handle resting state
        if self.state == KnightState.RESTING:
            if self.current_garrison:
                # Let garrison handle energy restoration
                fully_recovered = self.current_garrison.update()
                
                # Check if this knight is fully recovered
                for knight_pos, final_energy in fully_recovered:
                    if knight_pos == (self.x, self.y):
                        self.current_energy = final_energy
                        self.current_garrison.release_knight((self.x, self.y))
                        self.current_garrison = None
                        self.state = KnightState.PATROLLING
                        break
            else:
                # Regular resting (5% energy restoration)
                self.restore_energy()
            return
        
        # Handle detaining state
        if self.state == KnightState.DETAINING:
            self.state = KnightState.RESTING
            return
        
        # Handle challenging state
        if self.state == KnightState.CHALLENGING:
            self.state = KnightState.RESTING
            return
        
        # Scan for hunters
        hunters = self.scan_for_hunters()
        
        if hunters and self.can_pursue():
            # Select a target if we don't have one
            if not self.current_target or self.current_target not in hunters:
                self.current_target = self.select_target(hunters)
                self.state = KnightState.PURSUING
            
            # Move towards target
            if self.current_target:
                self.move_towards(self.current_target[0], self.current_target[1])
                
                # Check if we've reached the target
                if self.x == self.current_target[0] and self.y == self.current_target[1]:
                    # Target has been caught, handle the hunter
                    self.handle_caught_hunter(self.current_target)
                    self.current_target = None
        else:
            # No hunters detected or too exhausted, return to patrolling
            self.current_target = None
            if self.state == KnightState.PURSUING:
                self.state = KnightState.RESTING
            else:
                self.state = KnightState.PATROLLING
    
    def get_state(self) -> KnightState:
        """
        Get the current state of the knight.
        
        Returns:
            KnightState: Current state
        """
        return self.state
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the current position of the knight.
        
        Returns:
            Tuple[int, int]: Current (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_target(self) -> Optional[Tuple[int, int]]:
        """
        Get the current target position.
        
        Returns:
            Optional[Tuple[int, int]]: Current target position, None if no target
        """
        return self.current_target 