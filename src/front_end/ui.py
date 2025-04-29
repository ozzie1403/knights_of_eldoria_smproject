import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Any
from src.core.simulation import Simulation

class GameUI:
    def __init__(self, root: tk.Tk, simulation: Simulation):
        self.root = root
        self.simulation = simulation
        self.cell_size = 30
        self.colors = {
            'EMPTY': 'white',
            'TREASURE': {
                'BRONZE': '#CD7F32',  # Bronze color
                'SILVER': '#C0C0C0',  # Silver color
                'GOLD': '#FFD700'     # Gold color
            },
            'HUNTER': {
                'NAVIGATION': '#4169E1',  # Royal Blue
                'ENDURANCE': '#32CD32',   # Lime Green
                'STEALTH': '#4B0082'      # Indigo
            },
            'KNIGHT': '#FF0000',          # Red
            'HIDEOUT': '#8B4513'          # Saddle Brown
        }

        self.setup_ui()
        self.running = False

    def setup_ui(self) -> None:
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Canvas for grid
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.simulation.grid.size * self.cell_size,
            height=self.simulation.grid.size * self.cell_size
        )
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=1, column=0, columnspan=4, pady=5)

        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_simulation)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.step_button = ttk.Button(self.control_frame, text="Step", command=self.step_simulation)
        self.step_button.grid(row=0, column=2, padx=5)

        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=2, column=0, columnspan=4, pady=5)

        self.step_label = ttk.Label(self.status_frame, text="Step: 0")
        self.step_label.grid(row=0, column=0, padx=5)

        self.treasure_label = ttk.Label(self.status_frame, text="Treasure Collected: 0")
        self.treasure_label.grid(row=0, column=1, padx=5)

        # Legend frame
        self.legend_frame = ttk.LabelFrame(self.main_frame, text="Legend", padding="5")
        self.legend_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))

        # Column 1: Treasures
        treasure_frame = ttk.Frame(self.legend_frame)
        treasure_frame.grid(row=0, column=0, padx=10, sticky=tk.W)
        ttk.Label(treasure_frame, text="Treasures", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(treasure_frame, text="• Bronze (Low Value)").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(treasure_frame, text="• Silver (Medium Value)").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(treasure_frame, text="• Gold (High Value)").grid(row=3, column=0, sticky=tk.W)

        # Column 2: Hunters
        hunter_frame = ttk.Frame(self.legend_frame)
        hunter_frame.grid(row=0, column=1, padx=10, sticky=tk.W)
        ttk.Label(hunter_frame, text="Hunters", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(hunter_frame, text="• Navigation (Blue)").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(hunter_frame, text="• Endurance (Green)").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(hunter_frame, text="• Stealth (Indigo)").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(hunter_frame, text="Green bar = Stamina").grid(row=4, column=0, sticky=tk.W)

        # Column 3: Knights
        knight_frame = ttk.Frame(self.legend_frame)
        knight_frame.grid(row=0, column=2, padx=10, sticky=tk.W)
        ttk.Label(knight_frame, text="Knights", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(knight_frame, text="• Red - Patrol").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(knight_frame, text="• Capture hunters").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(knight_frame, text="Red bar = Energy").grid(row=3, column=0, sticky=tk.W)

        # Column 4: Hideouts
        hideout_frame = ttk.Frame(self.legend_frame)
        hideout_frame.grid(row=0, column=3, padx=10, sticky=tk.W)
        ttk.Label(hideout_frame, text="Hideouts", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(hideout_frame, text="• Brown").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(hideout_frame, text="• Safe haven").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(hideout_frame, text="Number = Hunters").grid(row=3, column=0, sticky=tk.W)

        # Draw initial grid
        self.draw_grid()

    def draw_grid(self) -> None:
        self.canvas.delete("all")
        state = self.simulation.get_state()

        # Draw grid lines
        for i in range(self.simulation.grid.size + 1):
            # Vertical lines
            self.canvas.create_line(
                i * self.cell_size, 0,
                i * self.cell_size, self.simulation.grid.size * self.cell_size
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * self.cell_size,
                self.simulation.grid.size * self.cell_size, i * self.cell_size
            )

        # Draw treasures
        for x, y, treasure_type, _ in state['treasures']:
            self.draw_cell(x, y, 'TREASURE', treasure_type)

        # Draw hunters
        for x, y, skill, stamina, _ in state['hunters']:
            self.draw_cell(x, y, 'HUNTER', skill)
            # Draw stamina indicator
            self.draw_stamina_indicator(x, y, stamina)

        # Draw knights
        for x, y, energy, _ in state['knights']:
            self.draw_cell(x, y, 'KNIGHT')
            # Draw energy indicator
            self.draw_energy_indicator(x, y, energy)

        # Draw hideouts
        for x, y, hunter_count, _ in state['hideouts']:
            self.draw_cell(x, y, 'HIDEOUT')
            # Draw hunter count
            self.draw_hunter_count(x, y, hunter_count)

        # Update status labels
        self.step_label.config(text=f"Step: {state['step_count']}")
        self.treasure_label.config(text=f"Treasure Collected: {state['total_treasure_collected']}")

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