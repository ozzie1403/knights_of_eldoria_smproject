from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def distance_to(self, other: 'Position') -> float:
        """Calculate the distance between two positions."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y) 