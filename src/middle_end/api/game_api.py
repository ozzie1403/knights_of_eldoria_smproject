import json
import os
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

from src.backend.services.game_service import GameService
from src.backend.models.simulation import Simulation

class GameAPI:
    """Manages game state using file-based storage instead of Flask."""

    def __init__(self):
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
        self.game_service = GameService(self.simulation)
        self.state_file = "game_state.json"

    def start_game(self, steps=100):
        """Starts the game simulation and saves state."""
        self.game_service.start_game(steps)
        self.save_state()

    def get_game_state(self):
        """Returns the current game state."""
        return self.game_service.get_game_state()

    def reset_game(self):
        """Resets the game and saves the new state."""
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

# ✅ Instantiate the game API globally
game_api = GameAPI()

@app.route('/', methods=['GET'])
def home():
    """Home route to confirm API is running."""
    return jsonify({"message": "Welcome to the Game API", "endpoints": ["/state"]})

@app.route('/state', methods=['GET'])
def fetch_game_state():
    """Flask route to fetch game state."""
    try:
        state = game_api.get_game_state()
        return jsonify({"status": "success", "game_state": state})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_game_state():
    global game_state
    if "hunters" not in game_state:  # Ensure key exists
        game_state["hunters"] = []   # Set to empty list if missing
    return jsonify(game_state)

if __name__ == "__main__":
    app.run(debug=True)