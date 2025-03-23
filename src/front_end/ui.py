import tkinter as tk
from src.backend.models.simulation import Simulation
import requests

API_URL = "http://127.0.0.1:5000"

class GameUI:
    def __init__(self, master, simulation: Simulation):
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
        """Updates the UI with the latest game state."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_entities()
        if self.running:
            self.simulation.run_step()
            self.step_count += 1
        self.update_status()
        self.master.after(1000, self.update_ui)  # Refresh every second

    def draw_grid(self):
        """Draws the grid background."""
        cell_size = 25
        for i in range(0, 500, cell_size):
            self.canvas.create_line(i, 0, i, 500, fill="gray")
            self.canvas.create_line(0, i, 500, i, fill="gray")

    def draw_entities(self):
        """Draws hunters, knights, and treasures."""
        cell_size = 25
        for hunter in self.simulation.hunters:
            x, y = hunter.position
            self.canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="blue")

        for knight in self.simulation.knights:
            x, y = knight.position
            self.canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size,
                                         fill="red")

        for x in range(self.simulation.grid.size):
            for y in range(self.simulation.grid.size):
                treasure = self.simulation.grid.get_treasure_at(x, y)
                if treasure:
                    self.canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size,
                                            fill="gold")

    def update_status(self):
        """Updates the status panel with the current game state."""
        num_hunters = len(self.simulation.hunters)
        num_knights = len(self.simulation.knights)
        num_treasures = sum(1 for x in range(self.simulation.grid.size) for y in range(self.simulation.grid.size) if
                            self.simulation.grid.get_treasure_at(x, y))
        self.status_label.config(
            text=f"Step: {self.step_count} | Hunters: {num_hunters} | Knights: {num_knights} | Treasures: {num_treasures}")

    def start_simulation(self):
        """Starts the simulation."""
        self.running = True

    def pause_simulation(self):
        """Pauses the simulation."""
        self.running = False

    def reset_simulation(self):
        """Resets the simulation to its initial state."""
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
        self.running = False
        self.step_count = 0
