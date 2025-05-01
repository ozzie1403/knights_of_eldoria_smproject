import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Any, List, Tuple
from src.core.simulation import Simulation

class GameUI:
    def __init__(self, root: tk.Tk, simulation: Simulation):
        self.root = root
        self.simulation = simulation
        self.cell_size = 30
        self.running = False
        self.colors = {
            'TREASURE': {
                'BRONZE': '#CD7F32',  # Bronze color
                'SILVER': '#C0C0C0',  # Silver color
                'GOLD': '#FFD700'     # Gold color
            },
            'HUNTER': {
                'SCOUT': '#00FF00',   # Green
                'ENDURANCE': '#0000FF', # Blue
                'STRENGTH': '#FF0000'  # Red
            },
            'KNIGHT': '#808080',      # Gray
            'HIDEOUT': '#8B4513',     # Brown
            'GARRISON': '#000000'     # Black
        }
        self.setup_ui()

    def setup_ui(self) -> None:
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Game canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.simulation.grid.size * self.cell_size,
            height=self.simulation.grid.size * self.cell_size,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, padx=5, pady=5)

        # Legend frame
        self.legend_frame = ttk.LabelFrame(self.main_frame, text="Legend", padding="10")
        self.legend_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Add legend items
        self._add_legend_item("Treasures", [
            ("Bronze", self.colors['TREASURE']['BRONZE']),
            ("Silver", self.colors['TREASURE']['SILVER']),
            ("Gold", self.colors['TREASURE']['GOLD'])
        ])

        self._add_legend_item("Hunters", [
            ("Scout", self.colors['HUNTER']['SCOUT']),
            ("Endurance", self.colors['HUNTER']['ENDURANCE']),
            ("Strength", self.colors['HUNTER']['STRENGTH'])
        ])

        self._add_legend_item("Other", [
            ("Knight", self.colors['KNIGHT']),
            ("Hideout", self.colors['HIDEOUT']),
            ("Garrison", self.colors['GARRISON'])
        ])

        # Controls frame
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.grid(row=1, column=0, columnspan=2, pady=5)

        # Add control buttons
        self.start_button = ttk.Button(self.controls_frame, text="Start", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop_simulation)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.step_button = ttk.Button(self.controls_frame, text="Step", command=self.step_simulation)
        self.step_button.grid(row=0, column=2, padx=5)

        self.reset_button = ttk.Button(self.controls_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=3, padx=5)

        # Status label
        self.status_label = ttk.Label(self.controls_frame, text="")
        self.status_label.grid(row=0, column=4, padx=5)

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def _add_legend_item(self, title: str, items: List[Tuple[str, str]]) -> None:
        """Add a group of legend items with a title."""
        frame = ttk.Frame(self.legend_frame)
        frame.pack(fill="x", pady=5)

        title_label = ttk.Label(frame, text=title, font=("Arial", 10, "bold"))
        title_label.pack(anchor="w")

        for name, color in items:
            item_frame = ttk.Frame(frame)
            item_frame.pack(fill="x", pady=2)

            color_box = tk.Canvas(item_frame, width=20, height=20, bg=color, highlightthickness=1)
            color_box.pack(side="left", padx=5)

            name_label = ttk.Label(item_frame, text=name)
            name_label.pack(side="left", padx=5)

    def draw_grid(self) -> None:
        self.canvas.delete("all")
        state = self.simulation.get_state()
        
        # Draw grid lines
        cell_size = self.cell_size
        for i in range(state['grid_size'] + 1):
            # Vertical lines
            self.canvas.create_line(
                i * cell_size, 0,
                i * cell_size, state['grid_size'] * cell_size,
                fill="gray"
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * cell_size,
                state['grid_size'] * cell_size, i * cell_size,
                fill="gray"
            )
        
        # Draw entities
        # Draw garrisons first (background)
        for x, y, num_knights, cooldown in state['garrisons']:
            self.canvas.create_rectangle(
                x * cell_size, y * cell_size,
                (x + 1) * cell_size, (y + 1) * cell_size,
                fill="darkred",
                outline="black"
            )
            # Draw number of knights
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.3) * cell_size,
                text=f"K:{num_knights}",
                fill="white"
            )
            # Draw cooldown
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.7) * cell_size,
                text=f"C:{cooldown}",
                fill="white"
            )
        
        # Draw hideouts
        for x, y, num_hunters, num_treasures in state['hideouts']:
            self.canvas.create_rectangle(
                x * cell_size, y * cell_size,
                (x + 1) * cell_size, (y + 1) * cell_size,
                fill="brown",
                outline="black"
            )
            # Draw number of hunters and treasures
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.3) * cell_size,
                text=f"H:{num_hunters}",
                fill="white"
            )
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.7) * cell_size,
                text=f"T:{num_treasures}",
                fill="white"
            )
        
        # Draw treasures
        for x, y, treasure_type, value in state['treasures']:
            color = {
                "BRONZE": "brown",
                "SILVER": "silver",
                "GOLD": "gold"
            }.get(treasure_type, "gray")
            self.canvas.create_oval(
                x * cell_size + 2, y * cell_size + 2,
                (x + 1) * cell_size - 2, (y + 1) * cell_size - 2,
                fill=color,
                outline="black"
            )
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.5) * cell_size,
                text=f"{value:.1f}",
                fill="black"
            )
        
        # Draw hunters
        for x, y, skill, stamina, is_collapsed in state['hunters']:
            color = "red" if is_collapsed else "green"
            self.canvas.create_oval(
                x * cell_size + 2, y * cell_size + 2,
                (x + 1) * cell_size - 2, (y + 1) * cell_size - 2,
                fill=color,
                outline="black"
            )
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.5) * cell_size,
                text=f"{skill[0]}:{stamina:.0f}",
                fill="black"
            )
        
        # Draw knights
        for x, y, stamina, is_resting in state['knights']:
            color = "blue" if is_resting else "darkblue"
            self.canvas.create_rectangle(
                x * cell_size + 2, y * cell_size + 2,
                (x + 1) * cell_size - 2, (y + 1) * cell_size - 2,
                fill=color,
                outline="black"
            )
            self.canvas.create_text(
                (x + 0.5) * cell_size,
                (y + 0.5) * cell_size,
                text=f"{stamina:.0f}",
                fill="white"
            )
        
        # Update legend
        self.status_label.config(text=f"Step: {state['step_count']}\nTreasures: {len(state['treasures'])}\nHunters: {len(state['hunters'])}\nKnights: {len(state['knights'])}\nHideouts: {len(state['hideouts'])}\nGarrisons: {len(state['garrisons'])}\nTotal Treasure Collected: {state['total_treasure_collected']}")

    def draw_cell(self, x: int, y: int, entity_type: str, subtype: str = None) -> None:
        # Wrap coordinates around grid edges
        x = x % self.simulation.grid.size
        y = y % self.simulation.grid.size

        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        if entity_type == 'TREASURE':
            color = self.colors['TREASURE'][subtype]
        elif entity_type == 'HUNTER':
            color = self.colors['HUNTER'][subtype]
        else:
            color = self.colors[entity_type]

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')

    def draw_stamina_indicator(self, x: int, y: int, stamina: float) -> None:
        x1 = x * self.cell_size + 2
        y1 = y * self.cell_size + self.cell_size - 5
        x2 = x1 + (self.cell_size - 4) * (stamina / 100)
        y2 = y1 + 3
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='green', outline='')

    def draw_energy_indicator(self, x: int, y: int, energy: float) -> None:
        x1 = x * self.cell_size + 2
        y1 = y * self.cell_size + 2
        x2 = x1 + (self.cell_size - 4) * (energy / 100)
        y2 = y1 + 3
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='')

    def draw_hunter_count(self, x: int, y: int, count: int) -> None:
        center_x = x * self.cell_size + self.cell_size // 2
        center_y = y * self.cell_size + self.cell_size // 2
        self.canvas.create_text(center_x, center_y, text=str(count), fill='white')

    def start_simulation(self) -> None:
        if not self.running:
            self.running = True
            self.run_simulation()

    def stop_simulation(self) -> None:
        self.running = False

    def step_simulation(self) -> None:
        if self.simulation.step():
            self.draw_grid()
        else:
            self.stop_simulation()
            self.show_game_over()

    def run_simulation(self) -> None:
        if self.running:
            self.step_simulation()
            self.root.after(500, self.run_simulation)  # Update every 500ms

    def show_game_over(self) -> None:
        game_over = tk.Toplevel(self.root)
        game_over.title("Game Over")
        game_over.geometry("200x100")

        ttk.Label(game_over, text="Game Over!").pack(pady=10)
        ttk.Label(game_over, text=f"Total Treasure Collected: {self.simulation.total_treasure_collected}").pack()
        ttk.Button(game_over, text="OK", command=game_over.destroy).pack(pady=10)

    def reset_simulation(self) -> None:
        """Reset the simulation to its initial state."""
        # Stop the simulation if it's running
        self.stop_simulation()
        
        # Store the initial parameters
        grid_size = self.simulation.grid.size
        num_hunters = len(self.simulation.hunters)
        num_knights = len(self.simulation.knights)
        num_treasures = len(self.simulation.treasures)
        num_hideouts = len(self.simulation.hideouts)
        
        # Create a new simulation with the same parameters
        self.simulation = Simulation(
            grid_size=grid_size,
            num_hunters=num_hunters,
            num_knights=num_knights,
            num_treasures=num_treasures,
            num_hideouts=num_hideouts
        )
        
        # Redraw the grid
        self.draw_grid()
        
        # Update the status label
        self.status_label.config(text="Simulation reset!")