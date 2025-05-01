from typing import Tuple, List, Optional, Dict, Any, Set
import random
import math
from src.core.enums import EntityType, CellType, KnightSkill, KnightAction, KnightState
from src.core.hunter import TreasureHunter
from src.core.treasure import Treasure

class Knight:
    def __init__(self, position: Tuple[int, int], skill: KnightSkill = KnightSkill.NOVICE):
        self.position = position
        self.skill = skill
        self.cell_type = CellType.KNIGHT
        self.entity_type = EntityType.KNIGHT
        self.stamina = 100
        self.max_stamina = 100
        self.detection_radius = 3
        self.current_action = KnightAction.PATROL
        self.target: Optional[TreasureHunter] = None
        self.is_resting = False
        self.knowledge: Dict[str, Any] = {}
        self.id = 0
        self.patrol_route: Optional[List[Tuple[int, int]]] = []
        self.patrol_index = 0
        self.energy = 100.0
        self.state = KnightState.PATROLLING
        self.known_garrisons: Set[Tuple[int, int]] = set()
    
    @property
    def cell_type(self):
        return "KNIGHT"

    def __post_init__(self):
        if self.knowledge is None:
            self.knowledge = {}
        if self.patrol_route is None:
            self.patrol_route = []

    def perceive(self, environment: Any) -> None:
        """Perceive the environment and update internal knowledge."""
        # Example: see nearby hunters
        self.knowledge['visible_hunters'] = [h for h in environment['hunters'] if self.position.distance_to(Position(h[0], h[1])) <= 3]

    def act(self, environment: Any) -> str:
        """Decide and return the next action as a string (for now)."""
        # Rule-based: If tired, rest. If hunter nearby, pursue. Else, patrol.
        if self.needs_rest():
            return 'rest'
        if self.knowledge.get('visible_hunters'):
            return 'pursue_hunter'
        return 'patrol'

    def move(self, grid, target_position: Optional[Tuple[int, int]] = None) -> bool:
        """Move the knight towards a target position or patrol."""
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
            # Patrol movement
            adjacent = grid.get_adjacent_positions(self.position)
            if not adjacent:
                return False
            new_x, new_y = adjacent[0]  # Move in a consistent direction for patrol
            
        new_position = (new_x, new_y)
        if grid.move_entity(self.position, new_position):
            self.position = new_position
            self.stamina -= 1
            return True
        return False
    
    def detect_hunters(self, grid) -> Optional[TreasureHunter]:
        """Detect hunters within 3-cell radius."""
        if self.state != KnightState.PATROLLING:
            return None
            
        nearby_hunters = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue
                pos = grid.wrap_position(
                    self.position[0] + dx,
                    self.position[1] + dy
                )
                entity = grid.get_entity_at(pos)
                if entity and entity.entity_type == EntityType.HUNTER:
                    nearby_hunters.append(entity)
        
        return random.choice(nearby_hunters) if nearby_hunters else None
    
    def choose_action(self, hunter: TreasureHunter) -> KnightAction:
        """Choose between detain or challenge action."""
        if random.random() < 0.7:  # 70% chance to detain
            return KnightAction.DETAIN
        return KnightAction.CHALLENGE
    
    def catch_hunter(self, hunter: TreasureHunter) -> None:
        """Catch a hunter and perform an action."""
        action = self.choose_action(hunter)
        
        if action == KnightAction.DETAIN:
            hunter.stamina = max(0.0, hunter.stamina - 5.0)
        else:  # CHALLENGE
            hunter.stamina = max(0.0, hunter.stamina - 20.0)
        
        # Force treasure drop
        if hunter.carrying:
            treasure = hunter.carrying
            hunter.carrying = None
            # Place treasure at hunter's position
            grid = hunter.grid  # Assuming grid is accessible
            grid.add_entity(hunter.position, treasure)
    
    def find_nearest_garrison(self, grid) -> Optional[Tuple[int, int]]:
        """Find the nearest garrison to rest at."""
        if not self.known_garrisons:
            return None
            
        return min(
            self.known_garrisons,
            key=lambda pos: self._distance_to(pos, grid.size)
        )
    
    def move_towards(self, target: Tuple[int, int], grid) -> bool:
        """Move towards a target position."""
        possible_moves = grid.get_adjacent_positions(self.position)
        best_move = min(possible_moves, key=lambda pos: self._distance_to(target, grid.size))
        return grid.move_entity(self.position, best_move)
    
    def rest(self) -> None:
        """Rest to recover energy."""
        if self.state == KnightState.RESTING:
            self.energy = min(100.0, self.energy + 10.0)
            if self.energy >= 100.0:
                self.state = KnightState.PATROLLING
    
    def update(self, grid) -> None:
        """Update knight state for the current simulation step."""
        # Scan for garrisons
        for pos in grid.get_adjacent_positions(self.position):
            entity = grid.get_entity_at(pos)
            if entity and entity.entity_type == EntityType.GARRISON:
                self.known_garrisons.add(pos)
        
        if self.state == KnightState.RESTING:
            self.rest()
            return
            
        if self.state == KnightState.CHASING:
            if not self.target or self.target.state == HunterState.COLLAPSED:
                self.state = KnightState.PATROLLING
                self.target = None
                return
                
            # Move towards target
            if self.move_towards(self.target.position, grid):
                self.energy = max(0.0, self.energy - 20.0)
                
                # Check if caught up to hunter
                if self.position == self.target.position:
                    self.catch_hunter(self.target)
                    self.state = KnightState.PATROLLING
                    self.target = None
                
                if self.energy <= 20.0:
                    self.state = KnightState.RESTING
                    self.target = None
            return
            
        # PATROLLING state
        if self.energy <= 20.0:
            garrison = self.find_nearest_garrison(grid)
            if garrison:
                self.state = KnightState.RESTING
                self.move_towards(garrison, grid)
            return
            
        # Look for hunters
        hunter = self.detect_hunters(grid)
        if hunter:
            self.state = KnightState.CHASING
            self.target = hunter
            self.move_towards(hunter.position, grid)
            self.energy = max(0.0, self.energy - 20.0)
        else:
            # Random patrol movement
            possible_moves = grid.get_adjacent_positions(self.position)
            if possible_moves:
                grid.move_entity(self.position, random.choice(possible_moves))
    
    def _distance_to(self, target: Tuple[int, int], grid_size: int) -> float:
        """Calculate distance to target considering grid wrapping."""
        dx = min(abs(target[0] - self.position[0]),
                abs(target[0] - self.position[0] - grid_size),
                abs(target[0] - self.position[0] + grid_size))
        dy = min(abs(target[1] - self.position[1]),
                abs(target[1] - self.position[1] - grid_size),
                abs(target[1] - self.position[1] + grid_size))
        return (dx**2 + dy**2)**0.5
    
    def __repr__(self) -> str:
        return f"Knight(Position: {self.position}, Skill: {self.skill.name}, State: {self.state.name}, Energy: {self.energy:.1f}%)"

    def needs_rest(self) -> bool:
        """Check if the knight needs to rest."""
        return self.stamina <= 6.0 or self.is_resting

    def can_move(self) -> bool:
        """Check if the knight can move."""
        return not self.is_resting and self.stamina > 0.0

    def predict_hunter_move(self, hunters: list, grid) -> 'Position':
        """Predict the next move of the nearest hunter (adversarial search, 1-ply minimax)."""
        if not hunters:
            return self.position
        # Find nearest hunter
        nearest = min(hunters, key=lambda h: self.position.distance_to(h.position))
        # Predict their next move (assume they move toward their current target or randomly)
        adj = grid.get_adjacent_positions(nearest.position)
        # For simplicity, pick the adjacent cell farthest from this knight
        best_pos = nearest.position
        max_dist = self.position.distance_to(nearest.position)
        for pos in adj:
            dist = self.position.distance_to(pos)
            if dist > max_dist and not grid.get_entity_at(pos):
                best_pos = pos
                max_dist = dist
        return best_pos

    def generate_patrol_route(self, grid_size: int, length: int = 5):
        """Generate a random patrol route."""
        self.patrol_route = []
        current_x, current_y = self.position
        
        for _ in range(length):
            # Choose a random direction
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            
            # Calculate new position with wrapping
            new_x = (current_x + dx) % grid_size
            new_y = (current_y + dy) % grid_size
            
            self.patrol_route.append((new_x, new_y))
            current_x, current_y = new_x, new_y
    
    def next_patrol_position(self) -> Tuple[int, int]:
        """Get the next position in the patrol route."""
        if not self.patrol_route:
            return self.position
        
        next_pos = self.patrol_route[self.patrol_index]
        self.patrol_index = (self.patrol_index + 1) % len(self.patrol_route)
        return next_pos

    def can_capture(self, hunter_position: Tuple[int, int]) -> bool:
        """Check if the knight can capture a hunter at the given position."""
        # Knight can capture if hunter is in an adjacent cell
        dx = abs(self.position[0] - hunter_position[0])
        dy = abs(self.position[1] - hunter_position[1])
        return dx <= 1 and dy <= 1 