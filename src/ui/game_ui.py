import tkinter as tk
from typing import Dict, Tuple
from src.core.simulation import Simulation
from src.core.entities.hunter import Hunter
from src.core.entities.treasure import Treasure
from src.core.entities.hideout import Hideout
from src.core.enums import TreasureType

class GameUI:
    CELL_SIZE = 30
    COLORS = {
        'empty': 'white',
        'hunter': 'blue',
        'treasure': {
            TreasureType.BRONZE: 'brown',
            TreasureType.SILVER: 'gray',
            TreasureType.GOLD: 'gold'
        },
        'hideout': 'green'
    }

    def __init__(self, root: tk.Tk, simulation: Simulation):
        self.root = root
        self.simulation = simulation
        self.canvas = tk.Canvas(
            root,
            width=simulation.grid.size * self.CELL_SIZE,
            height=simulation.grid.size * self.CELL_SIZE
        )
        self.canvas.pack()

        # Add control buttons
        self.controls = tk.Frame(root)
        self.controls.pack()
        
        self.start_button = tk.Button(self.controls, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT)
        
        self.stop_button = tk.Button(self.controls, text="Stop", command=self.stop_simulation)
        self.stop_button.pack(side=tk.LEFT)
        
        self.step_button = tk.Button(self.controls, text="Step", command=self.step_simulation)
        self.step_button.pack(side=tk.LEFT)

        # Add status label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        self.running = False
        self.draw_grid()

    def draw_grid(self):
        """Draw the grid and all entities."""
        self.canvas.delete("all")
        
        # Draw grid lines
        for i in range(self.simulation.grid.size + 1):
            # Vertical lines
            self.canvas.create_line(
                i * self.CELL_SIZE, 0,
                i * self.CELL_SIZE, self.simulation.grid.size * self.CELL_SIZE
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * self.CELL_SIZE,
                self.simulation.grid.size * self.CELL_SIZE, i * self.CELL_SIZE
            )

        # Draw hideouts
        for hideout in self.simulation.hideouts:
            x, y = hideout.position
            self.canvas.create_rectangle(
                x * self.CELL_SIZE, y * self.CELL_SIZE,
                (x + 1) * self.CELL_SIZE, (y + 1) * self.CELL_SIZE,
                fill=self.COLORS['hideout']
            )

        # Draw treasures
        for treasure in self.simulation.treasures:
            x, y = treasure.position
            self.canvas.create_rectangle(
                x * self.CELL_SIZE, y * self.CELL_SIZE,
                (x + 1) * self.CELL_SIZE, (y + 1) * self.CELL_SIZE,
                fill=self.COLORS['treasure'][treasure.treasure_type]
            )

        # Draw hunters
        for hunter in self.simulation.hunters:
            x, y = hunter.position
            self.canvas.create_oval(
                x * self.CELL_SIZE, y * self.CELL_SIZE,
                (x + 1) * self.CELL_SIZE, (y + 1) * self.CELL_SIZE,
                fill=self.COLORS['hunter']
            )
            # Add stamina indicator
            stamina_color = 'green' if hunter.stamina > 50 else 'yellow' if hunter.stamina > 20 else 'red'
            self.canvas.create_rectangle(
                x * self.CELL_SIZE, (y + 1) * self.CELL_SIZE - 5,
                (x + hunter.stamina/100) * self.CELL_SIZE, (y + 1) * self.CELL_SIZE,
                fill=stamina_color
            )

        # Update status
        self.status_label.config(
            text=f"Hunters: {len(self.simulation.hunters)} | "
                 f"Treasures: {len(self.simulation.treasures)} | "
                 f"Hideouts: {len(self.simulation.hideouts)}"
        )

    def start_simulation(self):
        """Start the simulation."""
        if not self.running:
            self.running = True
            self.update_simulation()

    def stop_simulation(self):
        """Stop the simulation."""
        self.running = False

    def step_simulation(self):
        """Step the simulation one tick."""
        self.simulation.update()
        self.draw_grid()

    def update_simulation(self):
        """Update the simulation and redraw the grid."""
        if self.running:
            self.step_simulation()
            self.root.after(500, self.update_simulation)  # Update every 500ms 