import tkinter as tk
from simulation.simulation_manager import SimulationManager
from ui.simulation_ui import SimulationUI


def main():
    """
    Main entry point for the Knights of Eldoria simulation.
    Creates the simulation manager and UI, then starts the application.
    """
    # Create root window
    root = tk.Tk()
    root.title("Knights of Eldoria Simulation")
    root.geometry("1200x800")
    root.configure(bg="#f3e8c8")  # Light parchment background

    # Set icon and styling
    root.option_add("*Font", "Helvetica 10")

    # Create simulation manager with default settings
    simulation = SimulationManager(
        grid_width=20,
        grid_height=20,
        hunter_count=8,
        hideout_count=3,
        garrison_count=2,
        treasure_count=15
    )

    # Create and pack UI
    ui = SimulationUI(root, simulation)
    ui.pack(fill=tk.BOTH, expand=True)

    # Start UI main loop
    root.mainloop()


if __name__ == "__main__":
    main()