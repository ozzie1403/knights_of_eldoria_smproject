import random
from enum import Enum
from typing import List, Optional
import tkinter as tk


class TreasureType(Enum):
    BRONZE = 3  # Increases wealth by 3%
    SILVER = 7  # Increases wealth by 7%
    GOLD = 13  # Increases wealth by 13%


class Treasure:
    def __init__(self, treasure_type: TreasureType, position: tuple[int, int]):
        self.treasure_type = treasure_type
        self.value = treasure_type.value  # Percentage value increase
        self.position = position

    def decay(self):
        """Treasure loses 0.1% of its value per step."""
        self.value = max(0, self.value - 0.1)

    def is_depleted(self) -> bool:
        """Returns True if the treasure has lost all its value."""
        return self.value <= 0


class Grid:
    def __init__(self, size: int = 20):
        self.size = size
        self.cells = [[None for _ in range(size)] for _ in range(size)]

    def wrap_position(self, x: int, y: int) -> tuple[int, int]:
        """Ensures grid wraps around edges."""
        return x % self.size, y % self.size

    def place_treasure(self, count: int = 10):
        """Randomly place treasures in the grid."""
        for _ in range(count):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            treasure_type = random.choice(list(TreasureType))
            self.cells[x][y] = Treasure(treasure_type, (x, y))

    def get_treasure_at(self, x: int, y: int) -> Optional[Treasure]:
        """Returns the treasure at the given position, if any."""
        return self.cells[x][y] if isinstance(self.cells[x][y], Treasure) else None

    def update_treasures(self):
        """Decays all treasures and removes depleted ones."""
        for x in range(self.size):
            for y in range(self.size):
                treasure = self.get_treasure_at(x, y)
                if treasure:
                    treasure.decay()
                    if treasure.is_depleted():
                        self.cells[x][y] = None


class GameUI:
    def __init__(self, master, simulation):
        self.master = master
        self.simulation = simulation
        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack()
        self.master.after(1000, self.update_ui)

    def update_ui(self):
        """Updates the UI with the latest game state."""
        self.canvas.delete("all")
        for hunter in self.simulation.hunters:
            x, y = hunter.position
            self.canvas.create_oval(x * 25, y * 25, (x + 1) * 25, (y + 1) * 25, fill="blue")
        for knight in self.simulation.knights:
            x, y = knight.position
            self.canvas.create_rectangle(x * 25, y * 25, (x + 1) * 25, (y + 1) * 25, fill="red")
        for x in range(self.simulation.grid.size):
            for y in range(self.simulation.grid.size):
                treasure = self.simulation.grid.get_treasure_at(x, y)
                if treasure:
                    self.canvas.create_oval(x * 25, y * 25, (x + 1) * 25, (y + 1) * 25, fill="gold")
        self.master.after(1000, self.update_ui)


if __name__ == "__main__":
    from src.backend.models.grid import Grid
    from src.backend.models.hunter import TreasureHunter
    from src.backend.models.knight import Knight
    from src.backend.models.simulation import Simulation

    root = tk.Tk()
    root.title("Knights of Eldoria")

    simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10)
    ui = GameUI(root, simulation)

    root.mainloop()
