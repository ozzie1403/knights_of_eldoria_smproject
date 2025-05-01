import tkinter as tk
from ui.display import SimulationDisplay

def main():
    """Main entry point for the Knights of Eldoria simulation."""
    root = tk.Tk()
    app = SimulationDisplay(root)
    root.mainloop()

if __name__ == "__main__":
    main()