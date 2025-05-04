from typing import List, Tuple, Optional, Dict
import random
from models.grid import Grid
from models.enums import CellType, HunterSkill, TreasureType
from models.treasure_hunter import TreasureHunter
from models.knight import Knight
from models.garrison import Garrison
from models.hideout import Hideout
from enum import Enum

class SimulationState(Enum):
    """Enum for different states the simulation can be in"""
    RUNNING = 0       # Simulation is actively running
    PAUSED = 1        # Simulation is paused
    TREASURE_DEPLETED = 2  # All treasure has been collected or lost
    HUNTERS_ELIMINATED = 3 # All hunters eliminated and no recruitment possible
    COMPLETED = 4     # Simulation completed successfully

class Simulation:
    """
    The main simulation class for the Kingdom of Eldoria.
    This class manages the overall simulation state, including the grid,
    treasure hunters, knights, and garrisons. It coordinates their interactions
    and updates their states over time. The goal is to maximize treasure collection
    by hunters while minimizing losses to knights. The simulation ends when either
    all treasure is collected/lost or all hunters are eliminated without possibility
    of recruitment. Supports uniform grids of different sizes (minimum 20x20).
    """
    def __init__(self, size: int = 20):
        """
        Initialize the Eldoria simulation with a uniform grid of specified size.
        
        Args:
            size (int): Size of the grid (both width and height), minimum 20
        """
        # Ensure minimum grid size of 20x20
        self.size = max(20, size)
        
        # Initialize the grid
        self.grid = Grid(self.size, self.size)
        
        # Initialize collections for entities
        self.treasure_hunters: List[TreasureHunter] = []
        self.hideouts: List[Hideout] = []
        
        # Simulation state
        self.current_step = 0
        self.state = SimulationState.PAUSED
        
        # Treasure tracking
        self.total_treasure_value = 0
        self.collected_treasure_value = 0
        self.lost_treasure_value = 0
        self.treasure_collection_history: List[Dict] = []
        self.remaining_treasure_count = 0
        
        # Hunter tracking
        self.active_hunters = 0
        self.captured_hunters = 0
        self.hunter_history: List[Dict] = []
        
        # Calculate entity counts based on grid size
        self._calculate_entity_distribution()
        
        # Initialize the simulation
        self._initialize_hideouts()
        self._initialize_remaining_cells()
        self._initialize_treasure_tracking()

    def _calculate_entity_distribution(self) -> None:
        """
        Calculate the number of entities to place based on grid size.
        Scales entity counts proportionally with grid size while maintaining
        reasonable gameplay balance. Fixed number of 3 hunters.
        """
        total_cells = self.size * self.size
        
        # Base numbers for 20x20 grid
        base_size = 400  # 20x20
        base_hideouts = (1, 1)  # Only one hideout for 3 hunters
        base_hunters_per_hideout = (3, 3)  # Fixed 3 hunters
        base_treasure_ratio = 0.3  # 30% of remaining cells
        
        # Scale factors based on grid size
        scale_factor = total_cells / base_size
        
        # Calculate scaled entity numbers
        self.min_hideouts = 1  # Fixed one hideout
        self.max_hideouts = 1  # Fixed one hideout
        self.min_hunters_per_hideout = 3  # Fixed 3 hunters
        self.max_hunters_per_hideout = 3  # Fixed 3 hunters
        
        # Adjust ratios for larger grids to maintain balance
        self.treasure_ratio = base_treasure_ratio * (0.8 + (0.2 * (base_size / total_cells) ** 0.5))

    def _initialize_hideouts(self) -> None:
        """
        Initialize hideout in the grid with exactly 3 hunters.
        Places hideout in the center of the grid.
        """
        # Place one hideout in the center
        center_x = self.size // 2
        center_y = self.size // 2
        
        # Create and place hideout
        hideout = Hideout(self.grid, center_x, center_y)
        self.hideouts.append(hideout)
        
        # Get adjacent empty positions for hunters
        adjacent_positions = self.grid.get_all_neighbors(center_x, center_y)
        empty_positions = [pos for pos in adjacent_positions 
                         if self.grid.get_cell(pos[0], pos[1]) == CellType.EMPTY.value]
        
        # Ensure we have exactly 3 hunters
        if len(empty_positions) >= 3:
            # Ensure skill diversity by assigning different skills
            available_skills = list(HunterSkill)
            random.shuffle(empty_positions)  # Randomize hunter positions
            
            for i in range(3):  # Place exactly 3 hunters
                # Get position for new hunter
                hunter_x, hunter_y = empty_positions[i]
                
                # Cycle through skills to ensure diversity
                skill = available_skills[i % len(available_skills)]
                
                # Create hunter and add to grid
                hunter = TreasureHunter(self.grid, hunter_x, hunter_y, skill)
                self.treasure_hunters.append(hunter)
                
                # Add hunter to hideout's tracking
                hideout.add_hunter(hunter_x, hunter_y)
                
                # Update active hunters count
                self.active_hunters += 1
        else:
            raise ValueError("Not enough space around hideout to place 3 hunters")
    
    def _initialize_remaining_cells(self) -> None:
        """
        Initialize the remaining grid cells with exactly 3 treasures and empty spaces.
        """
        # Place exactly 3 treasures
        num_treasures = 3
        
        # Place treasures
        for _ in range(num_treasures):
            attempts = 0
            while attempts < 100:  # Prevent infinite loops
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                
                if self.grid.get_cell(x, y) == CellType.EMPTY.value:
                    # Scale treasure value based on grid size
                    base_value = random.randint(50, 100)
                    treasure_value = int(base_value * (1 + (self.size - 20) * 0.02))
                    # Choose a random treasure type
                    treasure_type = random.choice(list(TreasureType))
                    self.grid.set_cell(x, y, CellType.TREASURE.value, treasure_type)
                    break
                
                attempts += 1
    
    def _initialize_treasure_tracking(self) -> None:
        """
        Initialize treasure tracking by counting total treasure value in the grid.
        """
        for x in range(self.size):
            for y in range(self.size):
                if self.grid.get_cell(x, y) == CellType.TREASURE.value:
                    treasure_value = self.grid.get_treasure_value(x, y)
                    if treasure_value:
                        self.total_treasure_value += treasure_value[1]
    
    def _track_treasure_collection(self, hunter: TreasureHunter, value: float) -> None:
        """
        Track treasure collection by a hunter.
        
        Args:
            hunter (TreasureHunter): The hunter who collected the treasure
            value (float): Value of the collected treasure
        """
        self.collected_treasure_value += value
        self.treasure_collection_history.append({
            'step': self.current_step,
            'hunter_id': id(hunter),
            'value': value,
            'total_collected': self.collected_treasure_value
        })
    
    def _track_treasure_loss(self, value: float) -> None:
        """
        Track treasure lost to knights.
        
        Args:
            value (float): Value of the lost treasure
        """
        self.lost_treasure_value += value
    
    def _track_hunter_capture(self, hunter: TreasureHunter) -> None:
        """
        Track when a hunter is captured by a knight.
        
        Args:
            hunter (TreasureHunter): The captured hunter
        """
        self.captured_hunters += 1
        self.active_hunters -= 1
        self.hunter_history.append({
            'step': self.current_step,
            'hunter_id': id(hunter),
            'treasure_lost': hunter.get_carried_treasure_value() if hunter.carried_treasure else 0
        })
    
    def _check_simulation_end(self) -> bool:
        """
        Check if the simulation should end based on treasure depletion or hunter elimination.
        
        Returns:
            bool: True if simulation should end, False otherwise
        """
        # Check if all treasure is collected or lost
        remaining_value = self.total_treasure_value - (self.collected_treasure_value + self.lost_treasure_value)
        if remaining_value <= 0:
            self.state = SimulationState.TREASURE_DEPLETED
            return True
        
        # Check if all hunters are eliminated and no recruitment is possible
        if self.active_hunters == 0:
            can_recruit = False
            for hideout in self.hideouts:
                if hideout.can_recruit():
                    can_recruit = True
                    break
            
            if not can_recruit:
                self.state = SimulationState.HUNTERS_ELIMINATED
                return True
        
        return False
    
    def step(self) -> None:
        """
        Perform one step of the simulation, updating all entities.
        This includes:
        - Treasure hunters moving, collecting treasure, and managing stamina
        - Hideouts managing their hunters and treasures
        
        The simulation will stop if:
        - All treasure has been collected
        - All hunters have been eliminated and no recruitment is possible
        """
        # Check if simulation can continue
        if self.state != SimulationState.RUNNING:
            return
        
        # Update simulation step counter
        self.current_step += 1
        print(f"[DEBUG][simulation] Step {self.current_step}")
        
        # Degrade treasures each step
        self.grid.degrade_treasures()
        
        # Reset active hunters count for this step
        self.active_hunters = 0
        
        # Update all hideouts
        for hideout in self.hideouts:
            hideout.update()
        
        # Update all treasure hunters
        for hunter in self.treasure_hunters:
            if hunter.is_active():
                self.active_hunters += 1
                print(f"[DEBUG][simulation] Updating hunter at ({hunter.x},{hunter.y})")
                hunter.update()
        
        # Check if simulation should end
        if self._check_simulation_end():
            self.state = SimulationState.COMPLETED
    
    def run(self, steps: Optional[int] = None) -> None:
        """
        Run the simulation until completion or for a specified number of steps.
        
        Args:
            steps (Optional[int]): Number of steps to run, or None to run until completion
        """
        self.state = SimulationState.RUNNING
        
        if steps is None:
            # Run until simulation ends
            while self.state == SimulationState.RUNNING:
                self.step()
        else:
            # Run for specified number of steps
            for _ in range(steps):
                if self.state != SimulationState.RUNNING:
                    break
                self.step()
    
    def get_final_report(self) -> Dict:
        """
        Get a comprehensive report of the simulation results.
        
        Returns:
            Dict: Final simulation report including:
                - Simulation state
                - Total steps run
                - Success metrics
                - Hunter statistics
                - Treasure statistics
                - Reason for completion
        """
        metrics = self.get_success_metrics()
        
        completion_reason = {
            SimulationState.TREASURE_DEPLETED: "All treasure collected or lost",
            SimulationState.HUNTERS_ELIMINATED: "All hunters eliminated without recruitment possibility",
            SimulationState.COMPLETED: "Simulation completed successfully"
        }.get(self.state, "Unknown")
        
        return {
            'state': self.state.name,
            'total_steps': self.current_step,
            'completion_reason': completion_reason,
            'success_metrics': metrics,
            'hunter_stats': {
                'total': len(self.treasure_hunters),
                'active': self.active_hunters,
                'captured': self.captured_hunters
            },
            'treasure_stats': {
                'total': self.total_treasure_value,
                'collected': self.collected_treasure_value,
                'lost': self.lost_treasure_value,
                'remaining': self.total_treasure_value - (self.collected_treasure_value + self.lost_treasure_value)
            }
        }
    
    def get_success_metrics(self) -> Dict:
        """
        Get metrics about the simulation's success in treasure collection.
        
        Returns:
            Dict: Success metrics including:
                - Total treasure value
                - Collected treasure value
                - Lost treasure value
                - Collection efficiency
                - Hunter survival rate
                - Average treasure per hunter
        """
        total_hunters = len(self.treasure_hunters)
        if total_hunters == 0:
            return {
                'total_treasure': self.total_treasure_value,
                'collected_treasure': self.collected_treasure_value,
                'lost_treasure': self.lost_treasure_value,
                'collection_efficiency': 0.0,
                'hunter_survival_rate': 0.0,
                'avg_treasure_per_hunter': 0.0
            }
        
        return {
            'total_treasure': self.total_treasure_value,
            'collected_treasure': self.collected_treasure_value,
            'lost_treasure': self.lost_treasure_value,
            'collection_efficiency': (self.collected_treasure_value / self.total_treasure_value) * 100,
            'hunter_survival_rate': ((total_hunters - self.captured_hunters) / total_hunters) * 100,
            'avg_treasure_per_hunter': self.collected_treasure_value / total_hunters
        }
    
    def get_simulation_state(self) -> Dict:
        """
        Get the current state of the simulation.
        
        Returns:
            Dict: Current simulation state including:
                - Current step
                - Number of active hunters
                - Number of hideouts
                - Grid state
                - Treasure collection metrics
        """
        state = {
            'step': self.current_step,
            'active_hunters': self.active_hunters,
            'hideouts': len(self.hideouts),
            'grid_state': self.grid.get_state(),
            'grid_contents': self.grid.get_grid_contents(),
            'treasure_metrics': {
                'total': self.total_treasure_value,
                'collected': self.collected_treasure_value,
                'lost': self.lost_treasure_value
            }
        }
        return state 