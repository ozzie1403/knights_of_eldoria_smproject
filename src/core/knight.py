from dataclasses import dataclass
from .position import Position
from typing import Dict, Any

@dataclass
class Knight:
    position: Position
    stamina: float = 100.0
    is_resting: bool = False
    knowledge: Dict[str, Any] = None  # For agent memory and perception
    id: int = 0  # Unique identifier for multi-agent systems

    def __post_init__(self):
        if self.knowledge is None:
            self.knowledge = {}

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

    def move(self, new_position: Position) -> None:
        """Move the knight to a new position, reducing stamina."""
        if not self.is_resting:
            self.position = new_position
            self.stamina = max(0.0, self.stamina - 2.0)
            if self.stamina <= 0.0:
                self.is_resting = True

    def rest(self) -> None:
        """Rest to recover stamina."""
        self.stamina = min(100.0, self.stamina + 1.0)
        if self.stamina >= 100.0:
            self.is_resting = False

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