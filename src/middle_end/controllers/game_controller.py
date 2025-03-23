from src.backend.services.game_service import GameService
from src.backend.models.simulation import Simulation

class GameController:
    def __init__(self):
        """Initializes the game controller with a simulation instance."""
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
        self.game_service = GameService(self.simulation)

    def start_game(self, steps=100):
        """Starts the game simulation."""
        self.game_service.start_game(steps)

    def get_game_state(self):
        """Retrieves the current game state."""
        return self.game_service.get_game_state()

    def reset_game(self):
        """Resets the game to its initial state."""
        self.__init__()
