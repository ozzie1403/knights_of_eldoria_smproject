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

    def move_towards(self, target_position: tuple[int, int], grid: Grid):
        """Moves the knight one step towards the target position if energy allows."""
        if self.energy <= 20:
            return  # Knights retreat when energy is low

        x, y = self.position
        tx, ty = target_position

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1

        self.position = grid.wrap_position(x, y)
        self.energy = max(0, self.energy - 10)  # Knights lose 10% energy per move

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
