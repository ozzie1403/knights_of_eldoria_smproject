from typing import List, Optional, Dict, Set, Any, Union, Tuple
import random
import math
from src.core.grid import Grid, CellType, EldoriaGrid
from src.core.treasure import Treasure, TreasureType
from src.core.hunter import Hunter, HunterSkill, TreasureHunter
from src.core.hideout import Hideout
from src.core.enums import EntityType, TreasureType, HunterSkill, KnightAction, KnightSkill
from src.core.knight import Knight
from src.core.garrison import Garrison

class Simulation:
    def __init__(self, grid_size: int = 20, num_hunters: int = 3, num_knights: int = 2, 
                 num_treasures: int = 10, num_hideouts: int = 2, num_garrisons: int = 2):
        """Initialize the simulation with a grid of given size and entity counts."""
        self.grid = EldoriaGrid(grid_size)
        self.step_count = 0
        self.is_running = True
        self.stats = {
            'treasures': 0,
            'hunters': 0,
            'knights': 0,
            'hideouts': 0,
            'garrisons': 0
        }
        self.num_hunters = num_hunters
        self.num_knights = num_knights
        self.num_treasures = num_treasures
        self.num_hideouts = num_hideouts
        self.num_garrisons = num_garrisons
        self.total_treasure_collected = 0.0  # Track total treasure collected
        self.initial_treasure_value = 0.0    # Track initial total treasure value
    
    def initialize(self) -> None:
        """Set up the initial state of the simulation."""
        # Place hideouts
        self.grid.place_hideouts(self.num_hideouts)
        self.stats['hideouts'] = self.num_hideouts
        
        # Place garrisons
        self.grid.place_garrisons(self.num_garrisons)
        self.stats['garrisons'] = self.num_garrisons
        
        # Place treasures
        for _ in range(self.num_treasures):
            pos = self.grid.get_random_empty_position()
            if pos:
                treasure_type = random.choice(list(TreasureType))
                treasure = Treasure(pos, treasure_type)
                self.grid.add_entity(pos, treasure)
                self.initial_treasure_value += treasure.base_value
        self.stats['treasures'] = self.num_treasures
        
        # Place knights
        self.grid.place_knights(self.num_knights)
        self.stats['knights'] = self.num_knights
        
        # Place hunters in hideouts
        hunters_per_hideout = self.num_hunters // self.num_hideouts
        remaining_hunters = self.num_hunters % self.num_hideouts
        
        for entity in self.grid.entities.values():
            if entity.entity_type == EntityType.HIDEOUT:
                num_hunters = hunters_per_hideout + (1 if remaining_hunters > 0 else 0)
                remaining_hunters -= 1
                for _ in range(num_hunters):
                    hunter = TreasureHunter(entity.position)
                    entity.enter(hunter)
                    self.stats['hunters'] += 1
    
    def update_stats(self) -> None:
        """Update simulation statistics."""
        self.stats['treasures'] = sum(1 for e in self.grid.entities.values() 
                                    if e.entity_type == EntityType.TREASURE)
        self.stats['hunters'] = sum(1 for e in self.grid.entities.values() 
                                  if e.entity_type == EntityType.HUNTER)
        self.stats['knights'] = sum(1 for e in self.grid.entities.values() 
                                  if e.entity_type == EntityType.KNIGHT)
        self.stats['hideouts'] = sum(1 for e in self.grid.entities.values() 
                                   if e.entity_type == EntityType.HIDEOUT)
        self.stats['garrisons'] = sum(1 for e in self.grid.entities.values() 
                                    if e.entity_type == EntityType.GARRISON)
        
        # Update total treasure collected from hideouts
        self.total_treasure_collected = sum(
            sum(treasure.current_value for treasure in hideout.stored_treasure)
            for hideout in self.grid.entities.values()
            if isinstance(hideout, Hideout)
        )
    
    def check_termination(self) -> bool:
        """Check if simulation should end."""
        # End if no treasures left
        if self.stats['treasures'] == 0:
            return True
            
        # End if no hunters and no hideouts to recruit from
        if self.stats['hunters'] == 0 and self.stats['hideouts'] == 0:
            return True
            
        return False
    
    def print_stats(self) -> None:
        """Print current simulation statistics."""
        print(f"\nStep {self.step_count}:")
        print(f"Treasures: {self.stats['treasures']}")
        print(f"Hunters: {self.stats['hunters']}")
        print(f"Knights: {self.stats['knights']}")
        print(f"Hideouts: {self.stats['hideouts']}")
        print(f"Garrisons: {self.stats['garrisons']}")
        
        # Print additional details
        active_hunters = sum(1 for e in self.grid.entities.values() 
                           if e.entity_type == EntityType.HUNTER and e.state != HunterState.COLLAPSED)
        chasing_knights = sum(1 for e in self.grid.entities.values() 
                            if e.entity_type == EntityType.KNIGHT and e.state == KnightState.CHASING)
        print(f"Active Hunters: {active_hunters}")
        print(f"Chasing Knights: {chasing_knights}")
    
    def step(self) -> None:
        """Perform one simulation step."""
        self.step_count += 1
        
        # Update all entities
        self.grid.update()
        
        # Update statistics
        self.update_stats()
        
        # Print current state
        self.print_stats()
        
        # Check termination conditions
        if self.check_termination():
            self.is_running = False
            print("\nSimulation ended!")
            if self.stats['treasures'] == 0:
                print("All treasures have been collected or decayed.")
            else:
                print("All hunters have been eliminated.")
    
    def run(self, max_steps: Optional[int] = None) -> None:
        """Run the simulation until termination or max steps reached."""
        self.initialize()
        print("Simulation started!")
        self.print_stats()
        
        while self.is_running:
            self.step()
            if max_steps and self.step_count >= max_steps:
                print(f"\nSimulation reached maximum steps ({max_steps})")
                break

    def get_stats(self) -> Dict[str, int]:
        """Get current simulation statistics."""
        return {
            'step': self.step_count,
            'hunters': len(self.grid.hunters),
            'knights': len(self.grid.knights),
            'treasures': len(self.grid.treasures),
            'hideouts': len(self.grid.hideouts),
            'garrisons': len(self.grid.garrisons)
        }
    
    def __repr__(self) -> str:
        return f"Simulation(Step: {self.step_count}, {self.grid})"

    def validate_state(self) -> bool:
        # All entities in the grid must be in exactly one list
        all_entities = set(self.grid.entities.values())
        all_listed = set(self.grid.hunters + self.grid.knights + self.grid.treasures + self.grid.hideouts + self.grid.garrisons)
        
        # Check for missing or extra entities
        if all_entities != all_listed:
            print("Entity mismatch:", all_entities.symmetric_difference(all_listed))
            return False
            
        # Check for duplicates in lists
        for lst in [self.grid.hunters, self.grid.knights, self.grid.treasures, self.grid.hideouts, self.grid.garrisons]:
            if len(lst) != len(set(lst)):
                print("Duplicate entity in list detected")
                return False
                
        return True

    def evolve_hunters(self):
        """Evolve hunter strategies using a simple genetic algorithm (placeholder)."""
        # Select top-performing hunters (e.g., those who collected treasure)
        top_hunters = sorted(self.grid.hunters, key=lambda h: h.stamina, reverse=True)[:max(1, len(self.grid.hunters)//2)]
        # Crossover and mutate to create new strategies
        new_strategies = []
        for _ in range(len(self.grid.hunters)):
            parent1 = random.choice(top_hunters).strategy
            parent2 = random.choice(top_hunters).strategy
            # Single-point crossover
            point = random.randint(1, len(parent1)-1)
            child = parent1[:point] + parent2[point:]
            # Mutation
            if random.random() < 0.2:
                idx = random.randint(0, len(child)-1)
                child[idx] += random.choice([-1, 1])
                child[idx] = max(1, child[idx])
            new_strategies.append(child)
        # Assign new strategies
        for h, strat in zip(self.grid.hunters, new_strategies):
            h.strategy = strat 