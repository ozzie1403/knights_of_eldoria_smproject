import tkinter as tk
from src.backend.models.simulation import Simulation

class GameUI:
    def __init__(self, master, simulation: Simulation):
        """Initializes the game UI."""
        self.master = master
        self.simulation = simulation
        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack()
        self.update_ui()

    def update_ui(self):
        """Updates the UI with the latest game state."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_entities()
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