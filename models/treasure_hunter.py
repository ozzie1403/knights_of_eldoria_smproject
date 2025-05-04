from typing import List, Tuple, Optional, Dict, Set
from enum import Enum
import random
from models.grid import Grid
from models.enums import CellType, TreasureType, HunterSkill, HunterState

class TreasureMemory:
    """Class to store information about discovered treasures"""
    def __init__(self, x: int, y: int, treasure_type: int, initial_value: float):
        self.x = x
        self.y = y
        self.treasure_type = treasure_type
        self.initial_value = initial_value
        self.last_known_value = initial_value
        self.is_collected = False
        self.collection_time = None  # Can be used to track when it was collected
        self.discovered_by: Optional[Tuple[int, int]] = None  # Position of hunter who discovered it

class TeamMember:
    """Class to store information about team members"""
    def __init__(self, x: int, y: int, last_seen: int, skill: HunterSkill):
        self.x = x
        self.y = y
        self.last_seen = last_seen
        self.known_treasures: List[Tuple[int, int, float]] = []  # Treasures known by this member
        self.is_carrying_treasure = False
        self.last_known_stamina = 100.0
        self.skill = skill

class TreasureHunter:
    def __init__(self, grid: Grid, x: int, y: int, skill: HunterSkill):
        """
        Initialize a treasure hunter with position and initial state.
        
        Args:
            grid (Grid): The game grid
            x (int): Initial X coordinate
            y (int): Initial Y coordinate
            skill (HunterSkill): The hunter's primary skill
        """
        self.grid = grid
        self.x = x
        self.y = y
        self.skill = skill
        self.state = HunterState.EXPLORING
        self.carried_treasure: Optional[Tuple[int, float]] = None  # (type, value)
        self.known_treasures: List[Tuple[int, int, float]] = []  # (x, y, value)
        self.known_hideouts: List[Tuple[int, int]] = []  # (x, y)
        
        # Assign unique hunter ID
        if not hasattr(grid, 'next_hunter_id'):
            grid.next_hunter_id = 1
        self.hunter_id = grid.next_hunter_id
        grid.next_hunter_id += 1
        
        # Skill-based attributes
        if skill == HunterSkill.NAVIGATION:
            self.scan_range = 3  # Increased scan range
            self.team_share_radius = 4  # Increased sharing range
            self.path_memory: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}  # Remembered paths
            self.stamina_depletion_rate = 0.2  # 20% depletion per movement (for debug)
            self.stamina_restore_rate = 0.01  # 1% restoration per step
        elif skill == HunterSkill.ENDURANCE:
            self.scan_range = 2
            self.team_share_radius = 3
            self.stamina_depletion_rate = 0.2  # 20% depletion per movement (for debug)
            self.stamina_restore_rate = 0.015  # 1.5% restoration per step
        else:  # STEALTH
            self.scan_range = 2
            self.team_share_radius = 3
            self.stealth_level = 0.8  # 80% chance to avoid detection
            self.stamina_depletion_rate = 0.2  # 20% depletion per movement (for debug)
            self.stamina_restore_rate = 0.01  # 1% restoration per step
        
        # Minimum value threshold for collecting treasures
        self.min_treasure_value = 20.0  # Won't collect treasures below this value
        
        # Memory systems
        self.treasure_memory: Dict[Tuple[int, int], TreasureMemory] = {}  # Maps positions to treasure memory
        self.hideout_memory: Set[Tuple[int, int]] = set()  # Set of all discovered hideout positions
        self.explored_positions: Set[Tuple[int, int]] = set()  # Set of all explored positions
        
        # Stamina system
        self.max_stamina = 100.0
        self.current_stamina = self.max_stamina  # Start with full stamina instead of 20.0
        self.min_stamina_to_move = 10.0  # Minimum stamina required to move
        self.critical_stamina_threshold = 6.0  # Critical stamina level (6%)
        
        # Survival system
        self.survival_steps_remaining = 0  # Steps remaining before collapse
        self.max_survival_steps = 3  # Maximum steps to survive at 0% stamina
        
        # Team system
        self.team_members: Dict[Tuple[int, int], TeamMember] = {}  # Maps positions to team members
        self.current_step = 0  # Current simulation step
        
        self.deposit_pause = 0  # Steps to pause when depositing
        self.just_deposited = False  # Flag to track if just deposited
        self.happy = False  # (legacy, not used for display)
        self.carrying_display_steps = 0  # Show 'T' for this many steps after pickup
    
    def get_skill(self) -> HunterSkill:
        """
        Get the hunter's skill.
        
        Returns:
            HunterSkill: The hunter's primary skill
        """
        return self.skill
    
    def get_skill_benefits(self) -> Dict[str, float]:
        """
        Get the benefits provided by the hunter's skill.
        
        Returns:
            Dict[str, float]: Dictionary of skill benefits
        """
        benefits = {}
        if self.skill == HunterSkill.NAVIGATION:
            benefits = {
                "scan_range": self.scan_range,
                "share_radius": self.team_share_radius,
                "path_memory": len(self.path_memory)
            }
        elif self.skill == HunterSkill.ENDURANCE:
            benefits = {
                "stamina_restore": self.stamina_restore_rate,
                "stamina_depletion": self.stamina_depletion_rate,
                "max_stamina": self.max_stamina
            }
        else:  # STEALTH
            benefits = {
                "stealth_level": self.stealth_level,
                "detection_chance": 1 - self.stealth_level
            }
        return benefits
    
    def move(self, new_x: int, new_y: int) -> bool:
        """
        Move the hunter to a new position if it's adjacent to current position.
        Allows moving onto a treasure cell and collects it immediately.
        
        Args:
            new_x (int): Target X coordinate
            new_y (int): Target Y coordinate
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Check if hunter is collapsed
        if self.state == HunterState.COLLAPSED:
            return False
        
        # Check if hunter has enough stamina to move
        if self.current_stamina < self.min_stamina_to_move:
            return False
        
        # Get all possible adjacent positions
        adjacent_positions = self.grid.get_all_neighbors(self.x, self.y)
        
        # Check if target position is adjacent
        if (new_x, new_y) not in adjacent_positions:
            return False
        
        target_cell = self.grid.get_cell(new_x, new_y)
        # Allow moving to empty or treasure cell
        if target_cell not in [CellType.EMPTY.value, CellType.TREASURE.value]:
            return False
        
        # Stealth check for STEALTH skill
        if self.skill == HunterSkill.STEALTH:
            if random.random() > self.stealth_level:
                return False  # Failed stealth check
        
        # Move hunter
        self.grid.set_cell(self.x, self.y, CellType.EMPTY.value)
        success = self.grid.set_cell(new_x, new_y, CellType.TREASURE_HUNTER.value)
        
        if success:
            self.x = new_x
            self.y = new_y
            
            # Deplete stamina by 2% of max stamina per move
            old_stamina = self.current_stamina
            self.current_stamina = max(0.0, self.current_stamina - (self.max_stamina * 0.02))
            print(f"[DEBUG] Hunter moved to ({new_x},{new_y}), stamina: {old_stamina:.2f} -> {self.current_stamina:.2f} (max: {self.max_stamina})")
            
            # Add position to explored positions
            self.explored_positions.add((new_x, new_y))
            
            # Update path memory for NAVIGATION skill
            if self.skill == HunterSkill.NAVIGATION:
                current_path = self.path_memory.get((self.x, self.y), [])
                current_path.append((new_x, new_y))
                self.path_memory[(self.x, self.y)] = current_path
            
            # If moved onto a treasure, collect it immediately
            if target_cell == CellType.TREASURE.value:
                self.collect_treasure()
            
            return True
        
        return False
    
    def rest(self) -> None:
        """
        Rest to restore stamina. Can only rest at hideouts.
        Restores stamina by 1% per step.
        """
        if self.grid.get_cell(self.x, self.y) == CellType.HIDEOUT.value:
            self.state = HunterState.RESTING
            # Restore stamina by 1% per step
            old_stamina = self.current_stamina
            self.current_stamina = min(self.max_stamina, self.current_stamina + (self.max_stamina * 0.01))
            print(f"[DEBUG] Hunter resting at ({self.x},{self.y}), stamina: {old_stamina:.2f} -> {self.current_stamina:.2f}")
            # Reset survival steps if stamina is restored
            if self.current_stamina > 0:
                self.survival_steps_remaining = 0
    
    def is_at_critical_stamina(self) -> bool:
        """
        Check if the hunter's stamina is at a critical level.
        
        Returns:
            bool: True if stamina is at or below critical threshold
        """
        return self.current_stamina <= self.critical_stamina_threshold
    
    def is_exhausted(self) -> bool:
        """
        Check if the hunter has collapsed from exhaustion.
        
        Returns:
            bool: True if hunter has collapsed
        """
        return self.state == HunterState.COLLAPSED
    
    def get_survival_steps_remaining(self) -> int:
        """
        Get the number of steps remaining before collapse.
        
        Returns:
            int: Steps remaining before collapse
        """
        return self.survival_steps_remaining
    
    def scan_area(self) -> None:
        """
        Scan the surrounding area for treasures and hideouts.
        Updates known_treasures, known_hideouts, and memory systems.
        """
        # Clear current scan results
        self.known_treasures.clear()
        self.known_hideouts.clear()
        
        # Scan in a square pattern around the hunter
        for dx in range(-self.scan_range, self.scan_range + 1):
            for dy in range(-self.scan_range, self.scan_range + 1):
                scan_x = self.x + dx
                scan_y = self.y + dy
                scan_pos = (scan_x, scan_y)
                
                # Add to explored positions
                self.explored_positions.add(scan_pos)
                
                # Get cell content
                cell_type = self.grid.get_cell(scan_x, scan_y)
                
                if cell_type == CellType.TREASURE.value:
                    # Get treasure value
                    treasure_data = self.grid.get_treasure_value(scan_x, scan_y)
                    if treasure_data is not None:
                        treasure_type, value = treasure_data
                        # Update treasure memory
                        if scan_pos not in self.treasure_memory:
                            self.treasure_memory[scan_pos] = TreasureMemory(
                                scan_x, scan_y, treasure_type, value
                            )
                        else:
                            self.treasure_memory[scan_pos].last_known_value = value
                        
                        # Only add to known treasures if above minimum value
                        if value >= self.min_treasure_value:
                            self.known_treasures.append((scan_x, scan_y, value))
                
                elif cell_type == CellType.HIDEOUT.value:
                    # Add to hideout memory
                    self.hideout_memory.add(scan_pos)
                    self.known_hideouts.append(scan_pos)
    
    def collect_treasure(self) -> bool:
        """
        Collect treasure from current position if available.
        
        Returns:
            bool: True if treasure was collected, False otherwise
        """
        # Get treasure data
        treasure_data = self.grid.get_treasure_value(self.x, self.y)
        if treasure_data is None:
            return False
        
        treasure_type, value = treasure_data
        
        # Only collect if value is above minimum threshold
        if value < self.min_treasure_value:
            return False
        
        # Update treasure memory
        pos = (self.x, self.y)
        if pos in self.treasure_memory:
            self.treasure_memory[pos].is_collected = True
            self.treasure_memory[pos].last_known_value = value
        
        # Collect treasure and update grid
        new_wealth = self.grid.collect_treasure(self.x, self.y)
        if new_wealth is not None:
            self.carried_treasure = treasure_data
            self.state = HunterState.CARRYING
            self.carrying_display_steps = 1  # Show 'T' for one step
            return True
        
        return False
    
    def find_nearest_hideout(self) -> Optional[Tuple[int, int]]:
        """
        Find the nearest hideout from known hideouts.
        
        Returns:
            Optional[Tuple[int, int]]: Coordinates of nearest hideout, None if no hideouts known
        """
        if not self.hideout_memory:
            return None
        
        # Calculate distances to all known hideouts
        distances = []
        for hideout_x, hideout_y in self.hideout_memory:
            # Calculate Manhattan distance
            distance = abs(self.x - hideout_x) + abs(self.y - hideout_y)
            distances.append((distance, (hideout_x, hideout_y)))
        
        # Return coordinates of nearest hideout
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
        # Check if hunter has enough stamina to move
        if self.current_stamina < self.min_stamina_to_move:
            return False
        
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
    
    def deposit_treasure(self) -> bool:
        """
        Deposit carried treasure at a hideout.
        
        Returns:
            bool: True if treasure was deposited, False otherwise
        """
        if self.state != HunterState.CARRYING or self.carried_treasure is None:
            return False
        
        # Check if hunter is at a hideout
        if self.grid.get_cell(self.x, self.y) != CellType.HIDEOUT.value:
            return False
        
        # Deposit treasure (update hunter's wealth)
        treasure_type, value = self.carried_treasure
        self.grid.collect_treasure(self.x, self.y)
        
        # Reset state
        self.carried_treasure = None
        self.state = HunterState.EXPLORING
        
        return True
    
    def find_most_valuable_treasure(self) -> Optional[Tuple[int, int, float]]:
        """
        Find the most valuable treasure from known treasures.
        
        Returns:
            Optional[Tuple[int, int, float]]: (x, y, value) of most valuable treasure, None if no treasures known
        """
        if not self.known_treasures:
            return None
        
        # Sort treasures by value in descending order
        sorted_treasures = sorted(self.known_treasures, key=lambda t: t[2], reverse=True)
        return sorted_treasures[0]
    
    def get_treasure_history(self) -> List[TreasureMemory]:
        """
        Get the history of all discovered treasures.
        
        Returns:
            List[TreasureMemory]: List of all treasure memories
        """
        return list(self.treasure_memory.values())
    
    def get_explored_positions(self) -> Set[Tuple[int, int]]:
        """
        Get all positions that have been explored.
        
        Returns:
            Set[Tuple[int, int]]: Set of explored positions
        """
        return self.explored_positions.copy()
    
    def get_hideout_history(self) -> Set[Tuple[int, int]]:
        """
        Get all discovered hideout positions.
        
        Returns:
            Set[Tuple[int, int]]: Set of hideout positions
        """
        return self.hideout_memory.copy()
    
    def get_stamina(self) -> float:
        """
        Get the current stamina level.
        
        Returns:
            float: Current stamina (0.0 to 100.0)
        """
        return self.current_stamina
    
    def get_stamina_percentage(self) -> float:
        """
        Get the current stamina as a percentage.
        
        Returns:
            float: Current stamina percentage (0.0 to 100.0)
        """
        return (self.current_stamina / self.max_stamina) * 100.0
    
    def get_rest_time_estimate(self) -> int:
        """
        Estimate the number of simulation steps needed to fully restore stamina.
        
        Returns:
            int: Number of steps needed to reach max stamina
        """
        if self.current_stamina >= self.max_stamina:
            return 0
        
        remaining_stamina = self.max_stamina - self.current_stamina
        steps_needed = int(remaining_stamina / (self.max_stamina * self.stamina_restore_rate))
        return steps_needed
    
    def scan_for_team_members(self) -> None:
        """
        Scan for nearby team members and update team information.
        """
        for dx in range(-self.team_share_radius, self.team_share_radius + 1):
            for dy in range(-self.team_share_radius, self.team_share_radius + 1):
                scan_x = self.x + dx
                scan_y = self.y + dy
                
                if self.grid.get_cell(scan_x, scan_y) == CellType.TREASURE_HUNTER.value:
                    member_pos = (scan_x, scan_y)
                    if member_pos not in self.team_members:
                        # Create new team member with random skill
                        skill = random.choice(list(HunterSkill))
                        self.team_members[member_pos] = TeamMember(scan_x, scan_y, self.current_step, skill)
                    else:
                        self.team_members[member_pos].last_seen = self.current_step
                        self.team_members[member_pos].x = scan_x
                        self.team_members[member_pos].y = scan_y
    
    def share_information(self) -> None:
        """
        Share information with nearby team members.
        """
        for member_pos, member in self.team_members.items():
            if abs(self.x - member.x) + abs(self.y - member.y) <= self.team_share_radius:
                # Share treasure information
                for treasure in self.known_treasures:
                    if treasure not in member.known_treasures:
                        member.known_treasures.append(treasure)
                
                # Share hideout information
                for hideout in self.hideout_memory:
                    if hideout not in member.known_treasures:
                        member.known_treasures.append(hideout)
    
    def coordinate_exploration(self) -> None:
        """
        Coordinate exploration efforts with team members.
        """
        if not self.team_members:
            return
        
        # Find unexplored areas
        unexplored_areas = []
        for dx in range(-self.scan_range, self.scan_range + 1):
            for dy in range(-self.scan_range, self.scan_range + 1):
                scan_x = self.x + dx
                scan_y = self.y + dy
                if (scan_x, scan_y) not in self.explored_positions:
                    unexplored_areas.append((scan_x, scan_y))
        
        if unexplored_areas:
            # Assign areas to team members
            for i, area in enumerate(unexplored_areas):
                member_pos = list(self.team_members.keys())[i % len(self.team_members)]
                self.team_members[member_pos].known_treasures.append(area)
    
    def share_treasure(self, other_hunter_pos: Tuple[int, int]) -> bool:
        """
        Share carried treasure with another hunter.
        
        Args:
            other_hunter_pos (Tuple[int, int]): Position of the other hunter
            
        Returns:
            bool: True if treasure was shared successfully
        """
        if not self.carried_treasure or other_hunter_pos not in self.team_members:
            return False
        
        # Check if other hunter is within sharing range
        other_x, other_y = other_hunter_pos
        if abs(self.x - other_x) + abs(self.y - other_y) > 1:
            return False
        
        # Share treasure
        self.team_members[other_hunter_pos].is_carrying_treasure = True
        self.carried_treasure = None
        self.state = HunterState.EXPLORING
        return True
    
    def get_optimal_path(self, target_x: int, target_y: int) -> Optional[List[Tuple[int, int]]]:
        """
        Get the optimal path to a target position using remembered paths.
        Only available for hunters with NAVIGATION skill.
        
        Args:
            target_x (int): Target X coordinate
            target_y (int): Target Y coordinate
            
        Returns:
            Optional[List[Tuple[int, int]]]: List of positions forming the path, or None if no path found
        """
        if self.skill != HunterSkill.NAVIGATION:
            return None
        
        # Check if we have a remembered path to the target
        target_pos = (target_x, target_y)
        if target_pos in self.path_memory:
            return self.path_memory[target_pos]
        
        # If no remembered path, return None
        return None
    
    def update(self) -> None:
        """
        Update hunter's state and perform appropriate actions.
        """
        self.current_step += 1
        print(f"[DEBUG][hunter] Hunter at ({self.x},{self.y}) stamina: {self.current_stamina:.2f}")
        
        # Decrement carrying_display_steps if > 0
        if self.carrying_display_steps > 0:
            self.carrying_display_steps -= 1
        
        # If hunter is in deposit pause, skip this step
        if self.deposit_pause > 0:
            self.deposit_pause -= 1
            if self.deposit_pause == 0:
                # Respawn hunter adjacent to hideout
                if self.just_deposited and hasattr(self, 'last_hideout_pos'):
                    hideout_x, hideout_y = self.last_hideout_pos
                    adjacent = self.grid.get_all_neighbors(hideout_x, hideout_y)
                    empty_adjacent = [pos for pos in adjacent if self.grid.get_cell(pos[0], pos[1]) == CellType.EMPTY.value]
                    if empty_adjacent:
                        new_x, new_y = random.choice(empty_adjacent)
                        self.x, self.y = new_x, new_y
                        self.grid.set_cell(new_x, new_y, CellType.TREASURE_HUNTER.value)
                        self.state = HunterState.EXPLORING
                        self.just_deposited = False
                        self.happy = True  # Set happy flag for one step
            return
        
        # If carrying (happy) flag is set, reset after one step
        if self.happy:
            self.happy = False
        
        # Check if hunter is collapsed
        if self.state == HunterState.COLLAPSED:
            return
        
        # Check if stamina is at 0%
        if self.current_stamina <= 0:
            if self.survival_steps_remaining == 0:
                self.survival_steps_remaining = 3  # 3 steps to survive at 0%
            else:
                self.survival_steps_remaining -= 1
                if self.survival_steps_remaining <= 0:
                    self.state = HunterState.COLLAPSED
                    print(f"[DEBUG][hunter] Hunter at ({self.x},{self.y}) COLLAPSED!")
                    return
        
        # Scan area for treasures and hideouts
        self.scan_area()
        
        # Check if hunter needs to rest due to critical stamina
        if self.is_at_critical_stamina():
            if self.grid.get_cell(self.x, self.y) == CellType.HIDEOUT.value:
                self.rest()
            else:
                # Try to find nearest hideout to rest
                nearest_hideout = self.find_nearest_hideout()
                if nearest_hideout:
                    self.state = HunterState.RETURNING
                    self.move_towards(nearest_hideout[0], nearest_hideout[1])
            return
        
        # Check if hunter needs to rest due to low stamina
        if self.current_stamina < self.min_stamina_to_move:
            if self.grid.get_cell(self.x, self.y) == CellType.HIDEOUT.value:
                self.rest()
            else:
                # Try to find nearest hideout to rest
                nearest_hideout = self.find_nearest_hideout()
                if nearest_hideout:
                    self.state = HunterState.RETURNING
                    self.move_towards(nearest_hideout[0], nearest_hideout[1])
            return
        
        if self.state == HunterState.EXPLORING:
            # First check if we're adjacent to a treasure
            adjacent_positions = self.grid.get_all_neighbors(self.x, self.y)
            for adj_x, adj_y in adjacent_positions:
                if self.grid.get_cell(adj_x, adj_y) == CellType.TREASURE.value:
                    # Move to the treasure
                    if self.move(adj_x, adj_y):
                        # Try to collect it
                        if self.collect_treasure():
                            # After collecting, immediately start returning to hideout
                            self.state = HunterState.CARRYING
                            nearest_hideout = self.find_nearest_hideout()
                            if nearest_hideout:
                                self.move_towards(nearest_hideout[0], nearest_hideout[1])
                    return
            
            # If not adjacent to a treasure, look for known treasures
            if self.known_treasures:
                # Find most valuable treasure
                most_valuable = self.find_most_valuable_treasure()
                if most_valuable:
                    # Move towards most valuable treasure
                    self.move_towards(most_valuable[0], most_valuable[1])
            else:
                # If no known treasures, explore randomly
                empty_positions = [pos for pos in adjacent_positions 
                                 if self.grid.get_cell(pos[0], pos[1]) == CellType.EMPTY.value]
                if empty_positions:
                    next_pos = random.choice(empty_positions)
                    print(f"[DEBUG][hunter] Moving randomly to {next_pos}")
                    self.move(next_pos[0], next_pos[1])
        
        elif self.state == HunterState.CARRYING:
            # Find nearest hideout
            nearest_hideout = self.find_nearest_hideout()
            if nearest_hideout:
                # Check if adjacent to hideout
                if (abs(self.x - nearest_hideout[0]) + abs(self.y - nearest_hideout[1])) == 1:
                    # Deposit treasure and update wealth
                    treasure_type, value = self.carried_treasure
                    print(f"[DEBUG][hunter] Depositing {treasure_type} treasure with value {value:.2f} at hideout {nearest_hideout}")
                    
                    # Update hunter's wealth based on treasure type
                    if treasure_type == TreasureType.BRONZE.value:
                        wealth_increase = 0.03  # 3% increase
                    elif treasure_type == TreasureType.SILVER.value:
                        wealth_increase = 0.07  # 7% increase
                    else:  # GOLD
                        wealth_increase = 0.13  # 13% increase
                    
                    # Get current wealth and update it
                    current_wealth = self.grid.get_hunter_wealth(self.x, self.y)
                    if current_wealth is not None:
                        new_wealth = current_wealth * (1 + wealth_increase)
                        self.grid.hunter_wealth[(self.x, self.y)] = new_wealth
                        print(f"[DEBUG][hunter] Wealth increased: {current_wealth:.2f} -> {new_wealth:.2f}")
                    
                    # Reset state and treasure
                    self.carried_treasure = None
                    self.state = HunterState.EXPLORING
                    
                    # Increment collected counter
                    if hasattr(self.grid, 'simulation') and hasattr(self.grid.simulation, 'increment_collected_treasure'):
                        self.grid.simulation.increment_collected_treasure()
                    return
                else:
                    # Move towards hideout
                    self.move_towards(nearest_hideout[0], nearest_hideout[1])
        
        elif self.state == HunterState.RESTING:
            # Rest until stamina is restored
            if self.current_stamina < self.max_stamina:
                self.rest()
            else:
                self.state = HunterState.EXPLORING
        
        elif self.state == HunterState.RETURNING:
            # Continue moving towards hideout
            nearest_hideout = self.find_nearest_hideout()
            if nearest_hideout:
                self.move_towards(nearest_hideout[0], nearest_hideout[1])
                
                # If reached hideout, start resting
                if self.x == nearest_hideout[0] and self.y == nearest_hideout[1]:
                    self.state = HunterState.RESTING
                    self.rest()
            else:
                # If no hideout found, go back to exploring
                self.state = HunterState.EXPLORING
    
    def get_team_size(self) -> int:
        """
        Get the current size of the team.
        
        Returns:
            int: Number of team members
        """
        return len(self.team_members)
    
    def get_team_member_positions(self) -> List[Tuple[int, int]]:
        """
        Get the positions of all team members.
        
        Returns:
            List[Tuple[int, int]]: List of team member positions
        """
        return list(self.team_members.keys())
    
    def get_shared_treasures(self) -> List[Tuple[int, int, float]]:
        """
        Get all treasures known by the team.
        
        Returns:
            List[Tuple[int, int, float]]: List of shared treasures
        """
        shared_treasures = set()
        for member in self.team_members.values():
            shared_treasures.update(member.known_treasures)
        return list(shared_treasures)
    
    def get_state(self) -> HunterState:
        """
        Get the current state of the hunter.
        
        Returns:
            HunterState: Current state
        """
        return self.state
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the current position of the hunter.
        
        Returns:
            Tuple[int, int]: Current (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_carried_treasure(self) -> Optional[Tuple[int, float]]:
        """
        Get the currently carried treasure.
        
        Returns:
            Optional[Tuple[int, float]]: (type, value) of carried treasure, None if not carrying
        """
        return self.carried_treasure
    
    def is_active(self) -> bool:
        """
        Check if the hunter is active (not collapsed).
        
        Returns:
            bool: True if hunter is active, False if collapsed
        """
        return self.state != HunterState.COLLAPSED
    
    def is_happy(self) -> bool:
        """Return True if the hunter is happy (just deposited treasure)."""
        return self.happy 