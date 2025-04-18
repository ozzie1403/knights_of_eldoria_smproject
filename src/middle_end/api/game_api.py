# src/middle_end/api/game_api.py

from flask import Flask, request, jsonify
from src.backend.models.simulation import Simulation
from src.backend.services.game_service import GameService
from src.backend.services.movement_service import MovementService

app = Flask(__name__)

simulation = Simulation()
game_service = GameService(simulation)

@app.route("/start", methods=["POST"])
def start_game():
    steps = request.json.get("steps", 1)
    game_service.start_game(steps=steps)
    return jsonify({"message": f"Game advanced by {steps} steps."})

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(game_service.get_game_state())

@app.route("/reset", methods=["POST"])
def reset_game():
    game_service.reset_game()
    return jsonify({"message": "Game reset."})

@app.route("/move", methods=["POST"])
def move_hunter():
    direction = request.json.get("direction")
    if simulation.hunters:
        MovementService.move_hunter(simulation.hunters[0], direction, simulation.grid)
    return jsonify({"message": f"Hunter moved {direction}."})

if __name__ == '__main__':
    app.run(debug=True)
