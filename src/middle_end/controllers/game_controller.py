# src/middle_end/controllers/game_controller.py

from src.backend.models.simulation import Simulation
from src.backend.services.game_service import GameService
from src.backend.services.movement_service import MovementService

class GameController:
    def __init__(self):
        self.simulation = Simulation()
        self.game_service = GameService(self.simulation)

    def start(self, steps: int = 1):
        self.game_service.start_game(steps)
        return {"message": f"Game ran for {steps} step(s)."}

    def reset(self):
        self.game_service.reset_game()
        return {"message": "Game has been reset."}

    def get_state(self):
        return self.game_service.get_game_state()

    def move(self, direction: str):
        if self.simulation.hunters:
            MovementService.move_hunter(self.simulation.hunters[0], direction, self.simulation.grid)
        return {"message": f"Hunter moved {direction}."}
