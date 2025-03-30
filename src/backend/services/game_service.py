from src.backend.models.simulation import Simulation

class GameService:
    def __init__(self, simulation: Simulation):
        """Initializes the game service with a simulation instance."""
        self.simulation = simulation

    def start_game(self, steps=100):
        """Runs the simulation for a given number of steps."""
        self.simulation.run(steps)

    def get_game_state(self):
        """Returns a snapshot of the game state."""
        return {
            "hunters": [
                {"name": h.name, "position": h.position, "stamina": h.stamina}
                for h in self.simulation.hunters
            ],
            "knights": [
                {"position": k.position, "energy": k.energy}
                for k in self.simulation.knights
            ],
            "treasures": [
                {"position": (x, y), "value": t.value}
                for x in range(self.simulation.grid.size)
                for y in range(self.simulation.grid.size)
                if (t := self.simulation.grid.get_treasure_at(x, y))
            ],
        }
