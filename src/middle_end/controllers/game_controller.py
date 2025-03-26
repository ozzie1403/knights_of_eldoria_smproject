import os
import json
from src.backend.services.game_service import GameService
from src.backend.models.simulation import Simulation


class GameController:
    """Manages game logic and state using file storage."""

    def __init__(self):
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
        self.game_service = GameService(self.simulation)
        self.state_file = "game_state.json"

    def start_game(self, steps=100):
        """Starts the game simulation and saves the state."""
        self.game_service.start_game(steps)
        self.save_state()

    def get_game_state(self):
        """Returns the current game state."""
        return self.game_service.get_game_state()

    def reset_game(self):
        """Resets the game to its initial state and saves it."""
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
        self.game_service = GameService(self.simulation)
        self.save_state()

    def save_state(self):
        """Saves the game state to a file."""
        with open(self.state_file, "w") as f:
            json.dump(self.get_game_state(), f)

    def load_state(self):
        """Loads the game state from a file if it exists."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return None