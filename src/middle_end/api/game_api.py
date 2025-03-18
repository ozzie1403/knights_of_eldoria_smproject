from flask import Flask, jsonify
from src.backend.services.game_service import GameService
from src.backend.models.simulation import Simulation

app = Flask(__name__)

# Initialize simulation and game service
simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
game_service = GameService(simulation)

@app.route('/start', methods=['GET'])
def start_game():
    """Starts the game simulation."""
    game_service.start_game(steps=100)
    return jsonify({"message": "Game simulation started."})

@app.route('/state', methods=['GET'])
def get_game_state():
    """Returns the current game state."""
    return jsonify(game_service.get_game_state())

if __name__ == '__main__':
    app.run(debug=True)
