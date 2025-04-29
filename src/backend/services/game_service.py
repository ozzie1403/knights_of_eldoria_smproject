# src/backend/services/game_service.py

from src.backend.models.simulation import Simulation
from typing import Dict, Any

class GameService:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation

    def run_simulation_step(self) -> bool:
        """Run a single simulation step. Returns False if simulation should end."""
        return self.simulation.step()

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current state of the game."""
        return self.simulation.get_state()

    def reset_simulation(self, grid_size: int = 20, num_hunters: int = 3, 
                        num_knights: int = 2, num_treasures: int = 10, 
                        num_hideouts: int = 2) -> None:
        """Reset the simulation with new parameters."""
        self.simulation = Simulation(
            grid_size=grid_size,
            num_hunters=num_hunters,
            num_knights=num_knights,
            num_treasures=num_treasures,
            num_hideouts=num_hideouts
        )
