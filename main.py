import tkinter as tk
from ui.display import SimulationDisplay


def main():
    """Run the Knights of Eldoria simulation."""
    # Create the main window
    root = tk.Tk()

    # Create the simulation display
    simulation_display = SimulationDisplay(root)

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()