from typing import TYPE_CHECKING
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter

if TYPE_CHECKING:
    from src.backend.models.hunter import TreasureHunter


class Knight:
    def __init__(self, position: tuple[int, int], energy: float = 100.0):
        """Initializes a knight with a position and energy level."""
        self.position = position
        self.energy = energy

    def move_towards(self, target_position, grid):
        x, y = self.position
        tx, ty = target_position

        # Generate possible knight moves (L-shape)
        possible_moves = [
            (x + 2, y + 1), (x + 2, y - 1),
            (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2),
            (x - 1, y + 2), (x - 1, y - 2),
        ]

        # Filter out moves that are out of bounds
        valid_moves = [(nx, ny) for nx, ny in possible_moves if grid.is_within_bounds(nx, ny)]

        # Select the move that gets closest to the target
        valid_moves.sort(key=lambda pos: abs(pos[0] - tx) + abs(pos[1] - ty))

        if valid_moves:
            self.position = valid_moves[0]  # Move to the best valid position

    def attack_hunter(self, hunter: "TreasureHunter"):
        """Knights attack a hunter, reducing stamina and forcing treasure drop."""
        if self.energy > 0:
            hunter.stamina = max(0, hunter.stamina - 20)  # Reduces hunter stamina
            hunter.drop_treasure()  # Forces hunter to drop treasure

    def rest(self):
        """Recovers knight's energy."""
        self.energy = min(100, self.energy + 10)

    def __repr__(self):
        return f"Knight(Position: {self.position}, Energy: {self.energy})"
