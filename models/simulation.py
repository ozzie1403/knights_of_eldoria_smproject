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
    INITIALIZED = 0       # Simulation is initialized but not running
    RUNNING = 1        # Simulation is actively running
    PAUSED = 2        # Simulation is paused
    TREASURE_DEPLETED = 3  # All treasure has been collected or lost
    HUNTERS_ELIMINATED = 4 # All hunters eliminated and no recruitment possible
    COMPLETED = 5     # Simulation completed successfully

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
        Initialize the simulation with a grid of specified size.
        
        Args:
            size (int): Size of the grid (width and height)
        """
        self.size = size
        self.grid = Grid(size, size)
        self.current_step = 0
        self.state = SimulationState.INITIALIZED
        self.hunters = []
        self.total_treasure_value = 0.0
        self.collected_treasure_value = 0.0
        self.lost_treasure_value = 0.0  # Track treasure lost (e.g., to knights)
        self.deposited_treasure = {'bronze': 0, 'silver': 0, 'gold': 0}
        self.eliminated_hunters = 0
        self.max_hunters = 10  # Maximum number of hunters allowed
        self.recruitment_cost = 50.0  # Cost to recruit a new hunter
        self.min_treasure_for_recruitment = 100.0  # Minimum treasure value needed to recruit
        
        # Reserve center and adjacent cells for hideout and hunters
        center_x = self.size // 2
        center_y = self.size // 2
        reserved_positions = set()
        reserved_positions.add((center_x, center_y))
        adjacent_positions = self.grid.get_all_neighbors(center_x, center_y)
        # Pick up to 3 adjacent positions for hunters
        hunter_positions = []
        for pos in adjacent_positions:
            if len(hunter_positions) < 3:
                reserved_positions.add(pos)
                hunter_positions.append(pos)
        if len(hunter_positions) < 3:
            raise ValueError("Not enough space around hideout to place 3 hunters")

        # Mark reserved cells as empty (in case random_fill tries to fill them)
        for x, y in reserved_positions:
            self.grid.set_cell(x, y, CellType.EMPTY.value)

        # Now fill the rest of the grid randomly, avoiding reserved positions
        self.grid.random_fill(reserved_positions=reserved_positions)
        
        # Place hideout in the center
        hideout = Hideout(self.grid, center_x, center_y)
        self.hideouts = [hideout]
        self.treasure_hunters = []
        self.hunters = []
        available_skills = list(HunterSkill)
        # Scan the grid for all hunter cells and create TreasureHunter objects for each
        hunter_positions = self.grid.get_entity_positions(CellType.TREASURE_HUNTER.value)
        for i, (hx, hy) in enumerate(hunter_positions):
            skill = available_skills[i % len(available_skills)]
            hunter = TreasureHunter(self.grid, hx, hy, skill)
            self.treasure_hunters.append(hunter)
            self.hunters.append(hunter)
            # Optionally, add to hideout if adjacent
            if abs(hx - center_x) <= 1 and abs(hy - center_y) <= 1:
                hideout.add_hunter(hx, hy)

        self.active_hunters = len(self.hunters)
        
        # Calculate initial total treasure value
        for pos, (treasure_type, value) in self.grid.treasure_values.items():
            self.total_treasure_value += value
        
        # Simulation state
        self.remaining_treasure_count = 0
        
        # Hunter tracking
        self.captured_hunters = 0
        self.hunter_history: List[Dict] = []
        
        # Calculate entity counts based on grid size
        self._calculate_entity_distribution()
        
        # Initialize the simulation
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
        Perform one step of the simulation.
        Updates all entities and checks for simulation end conditions.
        """
        if self.state != SimulationState.RUNNING:
            return
        
        self.current_step += 1
        print(f"[DEBUG][simulation] Running step {self.current_step}")
        
        # Update all hunters
        for hunter in self.hunters[:]:  # Copy list to allow removal during iteration
            if hunter.is_active():
                hunter.update()
            else:
                self.eliminated_hunters += 1
                self.hunters.remove(hunter)
                print(f"[DEBUG][simulation] Hunter eliminated at step {self.current_step}")
        
        # Degrade treasures
        self.grid.degrade_treasures()
        
        # Try to recruit new hunters if possible
        self.try_recruit_hunters()
        
        # Check end conditions
        self.check_end_conditions()
    
    def try_recruit_hunters(self) -> None:
        """
        Attempt to recruit new hunters if conditions are met, but never allow more than 3 hunters.
        """
        if len(self.hunters) >= 3:
            return
        # Check if we have enough treasure value to recruit
        if self.collected_treasure_value >= self.recruitment_cost:
            # Find empty positions adjacent to hideouts
            hideout_positions = self.grid.get_entity_positions(CellType.HIDEOUT.value)
            for hideout_x, hideout_y in hideout_positions:
                adjacent = self.grid.get_all_neighbors(hideout_x, hideout_y)
                empty_adjacent = [pos for pos in adjacent 
                                if self.grid.get_cell(pos[0], pos[1]) == CellType.EMPTY.value]
                if empty_adjacent:
                    # Recruit a new hunter
                    new_x, new_y = random.choice(empty_adjacent)
                    skill = random.choice(list(HunterSkill))
                    hunter = self.grid.create_hunter(new_x, new_y, skill)
                    if hunter:
                        self.hunters.append(hunter)
                        self.collected_treasure_value -= self.recruitment_cost
                        print(f"[DEBUG][simulation] Recruited new hunter with {skill.name} skill at ({new_x}, {new_y})")
                        break
    
    def check_end_conditions(self) -> None:
        """
        Check if the simulation should end based on treasure and hunter conditions.
        """
        # Check if all treasures are gone
        if not self.grid.treasure_values:
            self.state = SimulationState.TREASURE_DEPLETED
            print("[DEBUG][simulation] All treasures have been collected or degraded")
            return
        
        # Check if all hunters are eliminated and can't recruit more
        if not self.hunters and self.collected_treasure_value < self.recruitment_cost:
            self.state = SimulationState.HUNTERS_ELIMINATED
            print("[DEBUG][simulation] All hunters eliminated and cannot recruit more")
            return
    
    def get_simulation_state(self) -> Dict:
        """
        Get the current state of the simulation.
        
        Returns:
            Dict: Current simulation state
        """
        return {
            'step': self.current_step,
            'active_hunters': len(self.hunters),
            'eliminated_hunters': self.eliminated_hunters,
            'total_treasure': self.total_treasure_value,
            'collected_treasure': self.collected_treasure_value,
            'state': self.state
        }
    
    def get_success_metrics(self) -> Dict:
        """
        Calculate success metrics for the simulation.
        
        Returns:
            Dict: Success metrics including efficiency and survival rates
        """
        total_hunters = len(self.hunters) + self.eliminated_hunters
        collection_efficiency = (self.collected_treasure_value / self.total_treasure_value * 100) if self.total_treasure_value > 0 else 0
        survival_rate = ((total_hunters - self.eliminated_hunters) / total_hunters * 100) if total_hunters > 0 else 0
        
        return {
            'total_treasure': self.total_treasure_value,
            'collected_treasure': self.collected_treasure_value,
            'collection_efficiency': collection_efficiency,
            'hunter_survival_rate': survival_rate,
            'avg_treasure_per_hunter': self.collected_treasure_value / total_hunters if total_hunters > 0 else 0,
            'deposited_treasure': self.deposited_treasure
        }
    
    def increment_collected_treasure(self, treasure_type: int, value: float) -> None:
        """
        Increment the collected treasure counter and update deposited treasure counts.
        
        Args:
            treasure_type (int): Type of treasure collected
            value (float): Value of the collected treasure
        """
        self.collected_treasure_value += value
        if treasure_type == TreasureType.BRONZE.value:
            self.deposited_treasure['bronze'] += 1
        elif treasure_type == TreasureType.SILVER.value:
            self.deposited_treasure['silver'] += 1
        else:  # GOLD
            self.deposited_treasure['gold'] += 1
    
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