import tkinter as tk
from tkinter import ttk, messagebox
import random
from simulation import Simulation
from entities.base_entity import EntityType
from entities.treasure import TreasureType


class EldoriaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eldoria Simulation")

        # Default simulation parameters
        self.grid_size = 20
        self.num_hideouts = 2
        self.hunters_per_hideout = 2
        self.num_treasures = 10
        self.simulation = None
        self.is_running = False
        self.step_delay = 500  # milliseconds
        self.current_step = 0

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create legend frame
        self.legend_frame = ttk.LabelFrame(self.main_frame, text="Legend", padding="5")
        self.legend_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Add legend items
        legend_items = [
            ("H", "Hunter"),
            ("H*", "Hunter carrying treasure"),
            ("K", "Knight"),
            ("T", "Treasure"),
            ("T*", "Depleted treasure"),
            ("D", "Hideout"),
            ("D*", "Hideout with treasure"),
            ("X", "Collapsed hunter")
        ]

        for i, (symbol, description) in enumerate(legend_items):
            ttk.Label(self.legend_frame, text=f"{symbol}: {description}").grid(row=i // 2, column=i % 2, sticky=tk.W,
                                                                               padx=5, pady=2)

        # Create control frame
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Create control variables
        self.grid_size_var = tk.StringVar(value=str(self.grid_size))
        self.hideouts_var = tk.StringVar(value=str(self.num_hideouts))
        self.hunters_var = tk.StringVar(value=str(self.hunters_per_hideout))
        self.treasures_var = tk.StringVar(value=str(self.num_treasures))

        # Add control inputs
        ttk.Label(self.control_frame, text="Grid Size:").grid(row=0, column=0, padx=5)
        ttk.Entry(self.control_frame, textvariable=self.grid_size_var, width=5).grid(row=0, column=1, padx=5)

        ttk.Label(self.control_frame, text="Hideouts:").grid(row=0, column=2, padx=5)
        ttk.Entry(self.control_frame, textvariable=self.hideouts_var, width=5).grid(row=0, column=3, padx=5)

        ttk.Label(self.control_frame, text="Hunters per Hideout:").grid(row=0, column=4, padx=5)
        ttk.Entry(self.control_frame, textvariable=self.hunters_var, width=5).grid(row=0, column=5, padx=5)

        ttk.Label(self.control_frame, text="Treasures:").grid(row=0, column=6, padx=5)
        ttk.Entry(self.control_frame, textvariable=self.treasures_var, width=5).grid(row=0, column=7, padx=5)

        # Add control buttons
        ttk.Button(self.control_frame, text="Initialize", command=self.initialize_simulation).grid(row=0, column=8,
                                                                                                   padx=5)
        ttk.Button(self.control_frame, text="Start", command=self.start_simulation).grid(row=0, column=9, padx=5)
        ttk.Button(self.control_frame, text="Stop", command=self.stop_simulation).grid(row=0, column=10, padx=5)
        ttk.Button(self.control_frame, text="Step", command=self.run_step).grid(row=0, column=11, padx=5)

        # Create grid frame
        self.grid_frame = ttk.Frame(self.main_frame)
        self.grid_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Create canvas for grid
        self.canvas = tk.Canvas(self.grid_frame, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.rowconfigure(0, weight=1)

        # Add status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Initialize simulation
        self.initialize_simulation()

    def initialize_simulation(self):
        try:
            self.grid_size = int(self.grid_size_var.get())
            self.num_hideouts = int(self.hideouts_var.get())
            self.hunters_per_hideout = int(self.hunters_var.get())
            self.num_treasures = int(self.treasures_var.get())

            if self.grid_size < 20:
                messagebox.showwarning("Invalid Grid Size", "Grid size must be at least 20x20")
                return

            self.simulation = Simulation(width=self.grid_size, height=self.grid_size)
            self.simulation.setup(
                num_hunters=self.num_hideouts * self.hunters_per_hideout,
                num_hideouts=self.num_hideouts,
                num_knights=2,
                num_treasures=self.num_treasures
            )

            self.current_step = 0
            self.draw_grid()
            self.update_display()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all parameters")

    def draw_grid(self):
        self.canvas.delete("all")
        cell_size = min(600 // self.grid_size, 600 // self.grid_size)

        # Draw grid lines
        for i in range(self.grid_size + 1):
            # Vertical lines
            self.canvas.create_line(i * cell_size, 0, i * cell_size, self.grid_size * cell_size)
            # Horizontal lines
            self.canvas.create_line(0, i * cell_size, self.grid_size * cell_size, i * cell_size)

    def update_display(self):
        if not self.simulation:
            return

        self.canvas.delete("entities")
        cell_size = min(600 // self.grid_size, 600 // self.grid_size)

        # Draw entities
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                entities = self.simulation.grid.get_entities_at((x, y))
                if entities:
                    # Get the center of the cell
                    center_x = x * cell_size + cell_size // 2
                    center_y = y * cell_size + cell_size // 2

                    # Draw each entity
                    for entity in entities:
                        if entity.entity_type == EntityType.TREASURE:
                            color = {
                                TreasureType.BRONZE: "brown",
                                TreasureType.SILVER: "gray",
                                TreasureType.GOLD: "gold"
                            }[entity.treasure_type]
                            self.canvas.create_oval(
                                center_x - cell_size // 3, center_y - cell_size // 3,
                                center_x + cell_size // 3, center_y + cell_size // 3,
                                fill=color, tags="entities"
                            )
                        elif entity.entity_type == EntityType.HUNTER:
                            # Draw hunter with different color if carrying treasure
                            fill_color = "purple" if entity.carrying_treasure else "blue"
                            self.canvas.create_rectangle(
                                center_x - cell_size // 3, center_y - cell_size // 3,
                                center_x + cell_size // 3, center_y + cell_size // 3,
                                fill=fill_color, tags="entities"
                            )
                            # Add a small indicator for treasure
                            if entity.carrying_treasure:
                                self.canvas.create_oval(
                                    center_x - cell_size // 6, center_y - cell_size // 6,
                                    center_x + cell_size // 6, center_y + cell_size // 6,
                                    fill="gold", tags="entities"
                                )
                        elif entity.entity_type == EntityType.HIDEOUT:
                            self.canvas.create_polygon(
                                center_x, center_y - cell_size // 2,
                                          center_x + cell_size // 2, center_y + cell_size // 2,
                                          center_x - cell_size // 2, center_y + cell_size // 2,
                                fill="green", tags="entities"
                            )
                        elif entity.entity_type == EntityType.KNIGHT:
                            self.canvas.create_rectangle(
                                center_x - cell_size // 3, center_y - cell_size // 3,
                                center_x + cell_size // 3, center_y + cell_size // 3,
                                fill="red", tags="entities"
                            )
                        elif entity.entity_type == EntityType.GARRISON:
                            self.canvas.create_polygon(
                                center_x, center_y - cell_size // 2,
                                          center_x + cell_size // 2, center_y + cell_size // 2,
                                          center_x - cell_size // 2, center_y + cell_size // 2,
                                fill="purple", tags="entities"
                            )

    def start_simulation(self):
        if not self.simulation:
            return
        self.is_running = True
        self.run_simulation()

    def stop_simulation(self):
        self.is_running = False

    def step_simulation(self):
        if not self.simulation:
            return
        self.run_step()
        self.update_display()

    def run_simulation(self):
        if not self.is_running:
            return

        self.current_step += 1
        self.run_step()
        self.update_display()

        # Update window title with current step
        treasures_left = len(self.simulation.grid.entities[EntityType.TREASURE])
        hunters_alive = len(self.simulation.hunters)
        self.root.title(
            f"Eldoria Simulation - Step {self.current_step} - Treasures: {treasures_left}, Hunters: {hunters_alive}")

        # Check if simulation should end
        no_grid_treasures = not self.simulation.grid.entities[EntityType.TREASURE]
        no_carried_treasures = not any(hunter.carrying_treasure for hunter in self.simulation.hunters)

        if no_grid_treasures and no_carried_treasures:
            self.is_running = False
            messagebox.showinfo("Simulation Ended", "All treasures have been collected and deposited!")
            return

        if not self.simulation.hunters:
            can_recruit = False
            for hideout in self.simulation.hideouts:
                if hideout.can_accommodate():
                    can_recruit = True
                    break
            if not can_recruit:
                self.is_running = False
                messagebox.showinfo("Simulation Ended", "No hunters left and no hideouts can recruit new ones!")
                return

        # Schedule next step
        self.root.after(self.step_delay, self.run_simulation)

    def run_step(self):
        if not self.simulation:
            return
        self.simulation.run(steps=1)
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = EldoriaGUI(root)
    root.mainloop()