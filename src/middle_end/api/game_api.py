from flask import Flask, jsonify, request
from src.backend.services.game_service import GameService
from src.backend.models.simulation import Simulation

app = Flask(__name__)

# Initialize simulation and game service
simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
game_service = GameService(simulation)

@app.route('/start', methods=['POST'])
def start_game():
    """Starts the game simulation with optional step count."""
    steps = request.json.get("steps", 100)
    game_service.start_game(steps)
    return jsonify({"message": "Game simulation started.", "steps": steps})

@app.route('/state', methods=['GET'])
def get_game_state():
    """Returns the current game state."""
    return jsonify(game_service.get_game_state())

@app.route('/reset', methods=['POST'])
def reset_game():
    """Resets the game to its initial state."""
    global simulation, game_service
    simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
    game_service = GameService(simulation)
    return jsonify({"message": "Game reset successfully."})

if __name__ == '__main__':
    app.run(debug=True)
