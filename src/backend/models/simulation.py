import random
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight
from src.backend.models.hideout import Hideout
from src.backend.services.ai_service import AIService


class Simulation:
    def __init__(self, grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2):
        """Initializes the simulation environment."""
        self.grid = Grid(grid_size)
        self.hunters = [
            TreasureHunter(f"Hunter{i + 1}", (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))) for i
            in range(num_hunters)]
        self.knights = [Knight((random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))) for _ in
                        range(num_knights)]
        self.hideouts = [Hideout(random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)) for _ in
                         range(num_hideouts)]
        self.grid.place_treasure(num_treasures)

    def run_step(self):
        """Runs one step of the simulation."""
        for hunter in self.hunters:
            AIService.move_hunter_towards_treasure(hunter, self.grid)
            hunter.pick_up_treasure(self.grid)
            for hideout in self.hideouts:
                if hunter.position == (hideout.x, hideout.y):
                    hunter.deposit_treasure(hideout)
                    hunter.rest()

        for knight in self.knights:
            AIService.move_knight_towards_hunter(knight, self.hunters, self.grid)
            for hunter in self.hunters:
                if knight.position == hunter.position:
                    knight.attack_hunter(hunter)

        self.grid.update_treasures()

    def run(self, steps=100):
        """Runs the simulation for a given number of steps."""
        for _ in range(steps):
            self.run_step()

    def __repr__(self):
        return f"Simulation(Grid Size: {self.grid.size}, Hunters: {len(self.hunters)}, Knights: {len(self.knights)})"
