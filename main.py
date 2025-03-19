import tkinter as tk
from src.backend.models.simulation import Simulation
from src.front_end.ui import GameUI

def main():
    """Initializes and runs the game simulation with UI."""
    root = tk.Tk()
    root.title("Knights of Eldoria")

    simulation = Simulation(grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2)
    ui = GameUI(root, simulation)

    root.mainloop()


if __name__ == "__main__":
    main()
