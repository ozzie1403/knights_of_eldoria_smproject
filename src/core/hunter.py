from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from src.core.position import Position
from src.core.treasure import Treasure

@dataclass
class Hunter:
    position: Position
    stamina: float = 100.0
    steps_since_collapse: int = 0
    carrying_treasure: Optional[Treasure] = None
    is_collapsed: bool = False
    knowledge: Dict[str, Any] = None  # For agent memory and communication
    id: int = 0  # Unique identifier for multi-agent systems
    strategy: list = None  # For genetic algorithm (e.g., weights for decision-making)

    def __post_init__(self):
        if self.knowledge is None:
            self.knowledge = {}
        if self.strategy is None:
            # Example: [rest_weight, hideout_weight, avoid_weight, treasure_weight, swarm_weight, explore_weight]
            self.strategy = [1, 1, 1, 1, 1, 1]

    def fuzzy_tiredness(self) -> float:
        """Return a fuzzy tiredness value between 0 (not tired) and 1 (very tired)."""
        return max(0, min(1, (100 - self.stamina) / 100))

    def perceive(self, environment: Any) -> None:
        """Perceive the environment and update internal knowledge."""
        # Example: see nearby treasures, knights, hideouts
        self.knowledge['visible_treasures'] = [t for t in environment['treasures'] if self.position.distance_to(Position(t[0], t[1])) <= 3]
        self.knowledge['visible_knights'] = [k for k in environment['knights'] if self.position.distance_to(Position(k[0], k[1])) <= 3]
        self.knowledge['visible_hideouts'] = [h for h in environment['hideouts'] if self.position.distance_to(Position(h[0], h[1])) <= 3]

    def swarm_target(self, all_hunters: list) -> Optional[Position]:
        """Return the average position of all other hunters (for swarm behavior)."""
        if not all_hunters or len(all_hunters) == 1:
            return None
        x = sum(h.position.x for h in all_hunters if h.id != self.id) / (len(all_hunters) - 1)
        y = sum(h.position.y for h in all_hunters if h.id != self.id) / (len(all_hunters) - 1)
        return Position(int(round(x)), int(round(y)))

    def act(self, environment: Any) -> str:
        """Decide and return the next action as a string (for now)."""
        # Fuzzy logic: rest if tiredness > 0.7
        if self.fuzzy_tiredness() > 0.7:
            return 'rest'
        if self.carrying_treasure:
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

    def move(self, new_position: Position) -> None:
        """Move the hunter to a new position, reducing stamina."""
        if not self.is_collapsed:
            self.position = new_position
            self.stamina = max(0.0, self.stamina - 2.0)
            if self.stamina <= 0.0:
                self.is_collapsed = True

    def rest(self) -> None:
        """Rest in a hideout, recovering stamina."""
        if self.is_collapsed:
            self.steps_since_collapse += 1
        else:
            self.stamina = min(100.0, self.stamina + 1.0)

    def needs_rest(self) -> bool:
        """Check if the hunter needs to rest."""
        return self.stamina <= 6.0 or self.is_collapsed

    def can_move(self) -> bool:
        """Check if the hunter can move."""
        return not self.is_collapsed and self.stamina > 0.0

    def pick_up_treasure(self, treasure: Treasure) -> bool:
        """Attempt to pick up a treasure."""
        if not self.carrying_treasure and not self.is_collapsed:
            self.carrying_treasure = treasure
            return True
        return False

    def deposit_treasure(self) -> Optional[Treasure]:
        """Deposit the carried treasure."""
        treasure = self.carrying_treasure
        self.carrying_treasure = None
        return treasure

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
        self.knowledge['belief_map'][self.position.x][self.position.y] = 0.0

    def plan_path(self, target: Position, grid, max_steps=10) -> list:
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