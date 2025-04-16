import tkinter as tk
import requests
from src.backend.models.simulation import Simulation

API_URL = "http://192.168.0.116"

class GameUI:
    def __init__(self, master, simulation):
        """Initializes the game UI with controls and a status panel."""
        self.master = master
        self.simulation = simulation
        self.running = False
        self.step_count = 0

        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack()

        self.control_frame = tk.Frame(master)
        self.control_frame.pack()

        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(master, text="Step: 0 | Hunters: 0 | Knights: 0 | Treasures: 0")
        self.status_label.pack()

        self.update_ui()

    def update_ui(self):
        """Fetches game state from API and updates UI."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_entities()
        self.update_status()
        self.master.after(1000, self.update_ui)  # Refresh every second

    def draw_grid(self):
        """Draws the grid background."""
        cell_size = 25
        for i in range(0, 500, cell_size):
            self.canvas.create_line(i, 0, i, 500, fill="gray")
            self.canvas.create_line(0, i, 500, i, fill="gray")

    def draw_entities(self):
        """Fetches game state and draws hunters, knights, and treasures."""
        game_state = {}  # Ensure `game_state` is always initialized

        try:
            response = requests.get(f"{API_URL}/state")
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            game_state = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game state: {e}")  # Log the actual error

        print("DEBUG: Game State ->", game_state)  # Ensure debug output always works

        if not game_state:  # If game_state is empty, do not attempt to draw entities
            return

        cell_size = 25
        self.canvas.delete("all")  # Clear previous drawings

        for hunter in game_state.get("hunters", []):
            x, y = hunter["position"]
            self.canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="blue")

        for knight in game_state.get("knights", []):
            x, y = knight["position"]
            self.canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size,
                                         fill="red")

        for treasure in game_state.get("treasures", []):
            x, y = treasure["position"]
            self.canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="gold")

    def update_status(self):
        """Updates the status panel with the latest game state."""
        try:
            response = requests.get(f"{API_URL}/state")
            game_state = response.json()
            self.status_label.config(
                text=f"Step: {self.step_count} | Hunters: {len(game_state['hunters'])} | Knights: {len(game_state['knights'])} | Treasures: {len(game_state['treasures'])}"
            )
        except requests.exceptions.RequestException:
            self.status_label.config(text="Error fetching game state.")

    def start_simulation(self):
        """Starts the simulation via API call."""
        requests.post(f"{API_URL}/start", json={"steps": 100})

    def pause_simulation(self):
        """Pauses the simulation."""
        self.running = False  # No API pause yet, implemented locally

    def reset_simulation(self):
        """Resets the simulation via API call."""
        requests.post(f"{API_URL}/reset")
        self.step_count = 0

    def fetch_game_state(self):
        try:
            response = requests.get(f"{API_URL}/state", timeout=5)  # Set a timeout to avoid hanging
            response.raise_for_status()  # Raise error if HTTP request failed
            print("DEBUG: API Response ->", response.json())  # Log response
            return response.json()
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to the API. Is the server running?")
        except requests.exceptions.Timeout:
            print("ERROR: API request timed out.")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: {e}")
        return None