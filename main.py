import tkinter as tk
from src.front_end.ui import GameUI

def main():
    """Initializes and runs the game UI."""
    root = tk.Tk()
    root.title("Knights of Eldoria")

    ui = GameUI(root)  # Only pass `root`, as GameUI fetches data from API

    root.mainloop()

if __name__ == "__main__":
    main()
