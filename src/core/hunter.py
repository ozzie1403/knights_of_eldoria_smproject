from typing import List, Tuple, Optional, Dict, Any, Set
import random
import math
from src.core.enums import HunterSkill, EntityType, CellType, HunterState
from src.core.position import Position
from src.core.treasure import Treasure

class Hunter:
    def __init__(self, position: Tuple[int, int], skills: List[HunterSkill] = None):
        self.position = position
        self.cell_type = CellType.HUNTER
        self.entity_type = EntityType.HUNTER
        self.skills = skills or []
        self.wealth = 0
        self.stamina = 100
        self.max_stamina = 100
        self.stealth = 50
        self.detected = False
        self.steps_since_collapse = 0
        self.carried_treasure = None
        self.is_collapsed = False
        self.knowledge: Dict[str, Any] = {}
        self.id = 0
        self.strategy = [1, 1, 1, 1, 1, 1]  # For genetic algorithm
        self.known_treasures: Dict[Tuple[int, int], Any] = {}
        self.known_hideouts: List[Tuple[int, int]] = []
        self.known_knights: Dict[Tuple[int, int], Any] = {}
        self.memory: Dict[Tuple[int, int], float] = {}  # Position -> value
        self.skill = random.choice(list(HunterSkill))
        self.state = HunterState.SEARCHING
        self.collapsed_steps = 0
    
    @property
    def cell_type(self):
        return "HUNTER"
    
    def fuzzy_tiredness(self) -> float:
        """Return a fuzzy tiredness value between 0 (not tired) and 1 (very tired)."""
        return max(0, min(1, (100 - self.stamina) / 100))

    def perceive(self, environment: Any) -> None:
        """Perceive the environment and update internal knowledge."""
        # Example: see nearby treasures, knights, hideouts
        self.knowledge['visible_treasures'] = [t for t in environment['treasures'] if self._distance_to(t[:2]) <= 3]
        self.knowledge['visible_knights'] = [k for k in environment['knights'] if self._distance_to(k[:2]) <= 3]
        self.knowledge['visible_hideouts'] = [h for h in environment['hideouts'] if self._distance_to(h[:2]) <= 3]

    def swarm_target(self, all_hunters: list) -> Optional[Tuple[int, int]]:
        """Return the average position of all other hunters (for swarm behavior)."""
        if not all_hunters or len(all_hunters) == 1:
            return None
        x = sum(h.position[0] for h in all_hunters if h.id != self.id) / (len(all_hunters) - 1)
        y = sum(h.position[1] for h in all_hunters if h.id != self.id) / (len(all_hunters) - 1)
        return (int(round(x)), int(round(y)))

    def act(self, environment: Any) -> str:
        """Decide and return the next action as a string (for now)."""
        # Fuzzy logic: rest if tiredness > 0.7
        if self.fuzzy_tiredness() > 0.7:
            return 'rest'
        if self.carried_treasure:
            return 'go_hideout'
        if self.knowledge.get('visible_knights'):
            return 'avoid_knight'
        if self.knowledge.get('visible_treasures'):
            return 'go_treasure'
        # Swarm: if not doing anything else, move toward the average position of other hunters
        all_hunters = environment.get('all_hunters', [])
        if all_hunters and len(all_hunters) > 1:
            swarm_pos = self.swarm_target(all_hunters)
            if swarm_pos:
                self.knowledge['swarm_target'] = swarm_pos
                return 'swarm'
        return 'explore'

    def move(self, grid, target_position: Optional[Tuple[int, int]] = None) -> bool:
        """Move the hunter towards a target position or randomly."""
        if self.stamina <= 0:
            return False
            
        if target_position:
            # Move towards target
            dx = target_position[0] - self.position[0]
            dy = target_position[1] - self.position[1]
            
            # Handle toroidal wrapping
            if abs(dx) > grid.size // 2:
                dx = -dx // abs(dx) * (grid.size - abs(dx))
            if abs(dy) > grid.size // 2:
                dy = -dy // abs(dy) * (grid.size - abs(dy))
                
            new_x = self.position[0] + (dx // abs(dx) if dx != 0 else 0)
            new_y = self.position[1] + (dy // abs(dy) if dy != 0 else 0)
        else:
            # Random movement
            adjacent = grid.get_adjacent_positions(self.position)
            if not adjacent:
                return False
            new_x, new_y = random.choice(adjacent)
            
        new_position = (new_x, new_y)
        if grid.move_entity(self.position, new_position):
            self.position = new_position
            self.stamina -= 1
            return True
        return False

    def collect_treasure(self, treasure) -> bool:
        """Collect treasure and increase wealth."""
        if treasure and treasure.entity_type == EntityType.TREASURE:
            self.wealth += treasure.value
            return True
        return False

    def rest(self) -> None:
        """Rest to recover stamina."""
        self.stamina = min(self.max_stamina, self.stamina + 5)

    def update_stealth(self) -> None:
        """Update stealth level based on skills and current state."""
        base_stealth = 50
        skill_bonus = sum(10 for skill in self.skills if skill == HunterSkill.STEALTH)
        self.stealth = base_stealth + skill_bonus - (10 if self.detected else 0)

    def needs_rest(self) -> bool:
        """Check if hunter needs to rest."""
        return self.stamina <= 6.0 or self.is_collapsed

    def is_exhausted(self) -> bool:
        """Check if hunter is exhausted."""
        return self.stamina <= 0.0

    def deposit_treasure(self):
        """Deposit carried treasure in a hideout."""
        if self.carried_treasure:
            self.carried_treasure = None
            return True
        return False

    def communicate(self, all_hunters: list) -> None:
        """Broadcast warnings about knights and hints about treasures to other hunters."""
        # If a knight is visible, broadcast its position
        for h in all_hunters:
            if h.id != self.id:
                if self.knowledge.get('visible_knights'):
                    h.knowledge.setdefault('warnings', set()).update(self.knowledge['visible_knights'])
                if self.knowledge.get('visible_treasures'):
                    h.knowledge.setdefault('treasure_hints', set()).update(self.knowledge['visible_treasures'])

    def update_belief_map(self, grid_size: int) -> None:
        """Update a simple belief map for treasure probability using Bayesian reasoning."""
        if 'belief_map' not in self.knowledge:
            # Initialize uniform prior
            self.knowledge['belief_map'] = [[0.1 for _ in range(grid_size)] for _ in range(grid_size)]
        # Increase probability for cells with hints
        for hint in self.knowledge.get('treasure_hints', []):
            x, y = hint[0], hint[1]
            self.knowledge['belief_map'][x][y] = min(1.0, self.knowledge['belief_map'][x][y] + 0.2)
        # Decrease probability for visited cells
        self.knowledge['belief_map'][self.position[0]][self.position[1]] = 0.0

    def plan_path(self, target: Tuple[int, int], grid, max_steps=10) -> list:
        """Plan a path to the target using BFS (returns a list of positions)."""
        from collections import deque
        visited = set()
        queue = deque([(self.position, [])])
        while queue:
            pos, path = queue.popleft()
            if pos == target:
                return path + [pos]
            if len(path) >= max_steps:
                continue
            for adj in grid.get_adjacent_positions(pos):
                if adj not in visited and not grid.get_entity_at(adj):
                    visited.add(adj)
                    queue.append((adj, path + [pos]))
        return []

    def scan_area(self, grid: 'Grid', radius: int = 2):
        """Scan the surrounding area for treasures, hideouts, and knights."""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = grid.wrap_position(self.position[0] + dx, self.position[1] + dy)
                entity = grid.get_entity_at((x, y))
                if entity:
                    if isinstance(entity, Treasure):
                        self.known_treasures[(x, y)] = entity
                    elif entity.cell_type == "HIDEOUT":
                        if (x, y) not in self.known_hideouts:
                            self.known_hideouts.append((x, y))
                    elif entity.cell_type == "KNIGHT":
                        self.known_knights[(x, y)] = entity

    def choose_next_move(self, grid: 'Grid') -> Optional[Tuple[int, int]]:
        """AI decision making for next move."""
        if self.is_exhausted():
            return None
        
        if self.needs_rest():
            # Find nearest hideout
            if self.known_hideouts:
                nearest_hideout = min(
                    self.known_hideouts,
                    key=lambda pos: self._distance_to(pos, grid.size)
                )
                return self._move_towards(nearest_hideout, grid)
        
        if self.carried_treasure:
            # Find nearest hideout to deposit treasure
            if self.known_hideouts:
                nearest_hideout = min(
                    self.known_hideouts,
                    key=lambda pos: self._distance_to(pos, grid.size)
                )
                return self._move_towards(nearest_hideout, grid)
        
        # Find nearest known treasure
        if self.known_treasures:
            nearest_treasure = min(
                self.known_treasures.keys(),
                key=lambda pos: self._distance_to(pos, grid.size)
            )
            return self._move_towards(nearest_treasure, grid)
        
        # Explore randomly
        return self._explore_randomly(grid)
    
    def _distance_to(self, target: Tuple[int, int], grid_size: int) -> float:
        """Calculate distance to target considering grid wrapping."""
        dx = min(abs(target[0] - self.position[0]),
                abs(target[0] - self.position[0] - grid_size),
                abs(target[0] - self.position[0] + grid_size))
        dy = min(abs(target[1] - self.position[1]),
                abs(target[1] - self.position[1] - grid_size),
                abs(target[1] - self.position[1] + grid_size))
        return (dx**2 + dy**2)**0.5
    
    def _move_towards(self, target: Tuple[int, int], grid: 'Grid') -> Tuple[int, int]:
        """Move towards a target position."""
        possible_moves = grid.get_adjacent_positions(self.position)
        best_move = min(possible_moves, key=lambda pos: self._distance_to(target, grid.size))
        return best_move
    
    def _explore_randomly(self, grid: 'Grid') -> Tuple[int, int]:
        """Choose a random adjacent cell to explore."""
        possible_moves = grid.get_adjacent_positions(self.position)
        return random.choice(possible_moves)

    def __repr__(self) -> str:
        return f"Hunter(Position: {self.position}, Wealth: {self.wealth}, Stamina: {self.stamina}, Stealth: {self.stealth})"

class TreasureHunter:
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.cell_type = CellType.HUNTER
        self.entity_type = EntityType.HUNTER
        self.stamina = 100.0
        self.carrying: Optional[Treasure] = None
        self.memory: Dict[Tuple[int, int], float] = {}  # Position -> value
        self.known_hideouts: Set[Tuple[int, int]] = set()
        self.skill = random.choice(list(HunterSkill))
        self.state = HunterState.SEARCHING
        self.collapsed_steps = 0
    
    def scan_area(self, grid) -> None:
        """Scan adjacent cells for treasures and hideouts."""
        for pos in grid.get_adjacent_positions(self.position):
            entity = grid.get_entity_at(pos)
            if entity:
                if entity.entity_type == EntityType.TREASURE:
                    self.memory[pos] = entity.current_value
                elif entity.entity_type == EntityType.HIDEOUT:
                    self.known_hideouts.add(pos)
    
    def choose_next_move(self, grid) -> Optional[Tuple[int, int]]:
        """Choose the next position to move to based on current state."""
        if self.state == HunterState.COLLAPSED:
            return None
            
        if self.state == HunterState.RESTING:
            # Stay in place while resting
            return self.position
            
        if self.stamina <= 6.0:
            # Find nearest hideout to rest
            if self.known_hideouts:
                nearest = min(
                    self.known_hideouts,
                    key=lambda pos: self._distance_to(pos, grid.size)
                )
                return self._move_towards(nearest, grid)
            return None
            
        if self.carrying:
            # Return to nearest hideout
            if self.known_hideouts:
                nearest = min(
                    self.known_hideouts,
                    key=lambda pos: self._distance_to(pos, grid.size)
                )
                return self._move_towards(nearest, grid)
            return None
            
        # Search for highest value treasure in memory
        if self.memory:
            best_pos = max(self.memory.items(), key=lambda x: x[1])[0]
            return self._move_towards(best_pos, grid)
            
        # Random exploration
        return self._explore_randomly(grid)
    
    def move(self, grid, new_position: Tuple[int, int]) -> bool:
        """Move to a new position and update stamina."""
        if self.state == HunterState.COLLAPSED:
            return False
            
        if grid.move_entity(self.position, new_position):
            self.position = new_position
            stamina_loss = 2.0
            if self.skill == HunterSkill.ENDURANCE:
                stamina_loss *= 0.8  # 20% less stamina loss
            self.stamina = max(0.0, self.stamina - stamina_loss)
            
            if self.stamina <= 0.0:
                self.state = HunterState.COLLAPSED
                self.collapsed_steps = 0
            return True
        return False
    
    def collect_treasure(self, treasure: Treasure) -> bool:
        """Collect a treasure if not already carrying one."""
        if not self.carrying:
            self.carrying = treasure
            self.state = HunterState.CARRYING
            return True
        return False
    
    def deposit_treasure(self) -> bool:
        """Deposit carried treasure in a hideout."""
        if self.carrying:
            self.carrying = None
            self.state = HunterState.SEARCHING
            return True
        return False
    
    def rest(self) -> None:
        """Rest to recover stamina."""
        if self.state == HunterState.RESTING:
            self.stamina = min(100.0, self.stamina + 1.0)
            if self.stamina >= 100.0:
                self.state = HunterState.SEARCHING
    
    def update(self, grid) -> None:
        """Update hunter state for the current simulation step."""
        if self.state == HunterState.COLLAPSED:
            self.collapsed_steps += 1
            if self.collapsed_steps >= 3:
                grid.remove_entity(self.position)
            return
            
        # Scan area for treasures and hideouts
        self.scan_area(grid)
        
        # Remove invalid treasure locations from memory
        for pos in list(self.memory.keys()):
            entity = grid.get_entity_at(pos)
            if not entity or entity.entity_type != EntityType.TREASURE:
                del self.memory[pos]
        
        # Check if we're in a hideout
        current_entity = grid.get_entity_at(self.position)
        if current_entity and current_entity.entity_type == EntityType.HIDEOUT:
            hideout = current_entity
            if self not in hideout.hunters:
                hideout.enter(self)
            if self.carrying:
                hideout.deposit_treasure(self)
            if self.stamina <= 6.0:
                self.state = HunterState.RESTING
        else:
            # If we were in a hideout, leave it
            for entity in grid.entities.values():
                if entity.entity_type == EntityType.HIDEOUT and self in entity.hunters:
                    entity.leave(self)
            
            # Choose and execute next move
            next_pos = self.choose_next_move(grid)
            if next_pos:
                self.move(grid, next_pos)
                
                # Check for treasure collection
                entity = grid.get_entity_at(next_pos)
                if entity and entity.entity_type == EntityType.TREASURE:
                    self.collect_treasure(entity)
                    grid.remove_entity(next_pos)
        
        # Rest if in hideout
        if self.state == HunterState.RESTING:
            self.rest()
    
    def _distance_to(self, target: Tuple[int, int], grid_size: int) -> float:
        """Calculate distance to target considering grid wrapping."""
        dx = min(abs(target[0] - self.position[0]),
                abs(target[0] - self.position[0] - grid_size),
                abs(target[0] - self.position[0] + grid_size))
        dy = min(abs(target[1] - self.position[1]),
                abs(target[1] - self.position[1] - grid_size),
                abs(target[1] - self.position[1] + grid_size))
        return (dx**2 + dy**2)**0.5
    
    def _move_towards(self, target: Tuple[int, int], grid) -> Tuple[int, int]:
        """Move towards a target position."""
        possible_moves = grid.get_adjacent_positions(self.position)
        best_move = min(possible_moves, key=lambda pos: self._distance_to(target, grid.size))
        return best_move
    
    def _explore_randomly(self, grid) -> Tuple[int, int]:
        """Choose a random adjacent cell to explore."""
        possible_moves = grid.get_adjacent_positions(self.position)
        return random.choice(possible_moves)
    
    def __repr__(self) -> str:
        return f"TreasureHunter(Position: {self.position}, State: {self.state.name}, Stamina: {self.stamina:.1f}%, Carrying: {bool(self.carrying)})" 