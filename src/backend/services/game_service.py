# src/backend/services/game_service.py

from src.backend.models.simulation import Simulation

class GameService:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation

    def start_game(self, steps: int = 100):
        for _ in range(steps):
            self.simulation.run_step()

    def get_game_state(self) -> dict:
        return self.simulation.get_state()

    def reset_game(self):
        size = self.simulation.grid.size
        self.simulation = Simulation(
            grid_size=size,
            num_hunters=len(self.simulation.hunters),
            num_knights=len(self.simulation.knights),
            num_treasures=10,
            num_hideouts=len(self.simulation.hideouts)
        )
