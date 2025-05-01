import tkinter as tk
from src.core.simulation import Simulation
from src.front_end.ui import GameUI


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Knights of Eldoria")

    # Initialize simulation with default parameters
    simulation = Simulation(
        grid_size=20,      # 20x20 grid
        num_hunters=3,     # 3 hunters
        num_knights=2,     # 2 knights
        num_treasures=10,  # 10 treasures
        num_hideouts=2,    # 2 hideouts
        num_garrisons=2    # 2 garrisons
    )

    # Create and start the game UI
    GameUI(root, simulation)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()