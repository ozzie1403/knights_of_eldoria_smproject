import tkinter as tk
from tkinter import ttk
from models.simulation import Simulation
from models.location import Location
from utils.constants import EntityType, TreasureType, COLORS
import time


class SimulationDisplay:
    """UI for displaying and controlling the simulation."""

    def __init__(self, root):
        self.root = root
        self.root.title("Knights of Eldoria Simulation")
        self.simulation = None
        self.running = False
        self.animation_speed = 500  # milliseconds between steps

        # Set up the main window
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        # Create frames
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create control panel at the top
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls")
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        # Add controls
        self._setup_controls(self.control_frame)

        # Create canvas for displaying the grid
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create statistics panel at the bottom
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics")
        self.stats_frame.pack(fill=tk.X)

        self.stats_text = tk.Text(self.stats_frame, height=5, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)

        # Assign colors to entity types
        self.colors = COLORS

        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.root.bind("<Escape>", lambda e: self._stop_simulation())

        # Initialize UI
        self._update_stats()

    def _setup_controls(self, parent):
        """Set up the control panel."""
        # Create a frame for settings
        settings_frame = ttk.LabelFrame(parent, text="Settings")
        settings_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # Grid size
        grid_frame = ttk.Frame(settings_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(grid_frame, text="Grid Size:").pack(side=tk.LEFT)
        self.grid_size_var = tk.IntVar(value=20)
        grid_spin = ttk.Spinbox(grid_frame, from_=10, to=50, textvariable=self.grid_size_var, width=5)
        grid_spin.pack(side=tk.RIGHT)

        # Number of hideouts
        hideout_frame = ttk.Frame(settings_frame)
        hideout_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hideout_frame, text="Hideouts:").pack(side=tk.LEFT)
        self.hideout_var = tk.IntVar(value=3)
        hideout_spin = ttk.Spinbox(hideout_frame, from_=1, to=10, textvariable=self.hideout_var, width=5)
        hideout_spin.pack(side=tk.RIGHT)

        # Number of hunters per hideout
        hunters_frame = ttk.Frame(settings_frame)
        hunters_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hunters_frame, text="Hunters per Hideout:").pack(side=tk.LEFT)
        self.hunters_var = tk.IntVar(value=2)
        hunters_spin = ttk.Spinbox(hunters_frame, from_=1, to=5, textvariable=self.hunters_var, width=5)
        hunters_spin.pack(side=tk.RIGHT)

        # Number of treasures
        treasure_frame = ttk.Frame(settings_frame)
        treasure_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(treasure_frame, text="Treasures:").pack(side=tk.LEFT)
        self.treasure_var = tk.IntVar(value=30)
        treasure_spin = ttk.Spinbox(treasure_frame, from_=5, to=100, textvariable=self.treasure_var, width=5)
        treasure_spin.pack(side=tk.RIGHT)

        # Number of knights
        knight_frame = ttk.Frame(settings_frame)
        knight_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(knight_frame, text="Knights:").pack(side=tk.LEFT)
        self.knight_var = tk.IntVar(value=2)
        knight_spin = ttk.Spinbox(knight_frame, from_=0, to=20, textvariable=self.knight_var, width=5)
        knight_spin.pack(side=tk.RIGHT)

        # Number of garrisons
        garrison_frame = ttk.Frame(settings_frame)
        garrison_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(garrison_frame, text="Garrisons:").pack(side=tk.LEFT)
        self.garrison_var = tk.IntVar(value=2)
        garrison_spin = ttk.Spinbox(garrison_frame, from_=0, to=10, textvariable=self.garrison_var, width=5)
        garrison_spin.pack(side=tk.RIGHT)

        # Animation speed
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(speed_frame, text="Animation Speed (ms):").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=500)  # Default to 500ms
        speed_spin = ttk.Spinbox(speed_frame, from_=100, to=2000, increment=100, textvariable=self.speed_var, width=5)
        speed_spin.pack(side=tk.RIGHT)

        # Create a frame for buttons
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        # Setup button
        self.setup_button = ttk.Button(controls_frame, text="Setup", command=self._setup_simulation)
        self.setup_button.pack(fill=tk.X, padx=5, pady=5)

        # Start/Stop button
        self.start_button = ttk.Button(controls_frame, text="Start", command=self._toggle_simulation, state=tk.DISABLED)
        self.start_button.pack(fill=tk.X, padx=5, pady=5)

        # Step button
        self.step_button = ttk.Button(controls_frame, text="Step", command=self._step_simulation, state=tk.DISABLED)
        self.step_button.pack(fill=tk.X, padx=5, pady=5)

        # Reset button
        self.reset_button = ttk.Button(controls_frame, text="Reset", command=self._reset_simulation, state=tk.DISABLED)
        self.reset_button.pack(fill=tk.X, padx=5, pady=5)

        # Apply speed button
        self.speed_button = ttk.Button(controls_frame, text="Apply Speed", command=self._apply_speed)
        self.speed_button.pack(fill=tk.X, padx=5, pady=5)

    def _on_canvas_resize(self, event):
        """Handle canvas resize event."""
        print(f"Canvas resized: {event.width}x{event.height}")
        if self.simulation:
            self._draw_grid()

    def _setup_simulation(self):
        """Set up a new simulation with current settings."""
        grid_size = self.grid_size_var.get()
        num_hideouts = self.hideout_var.get()
        hunters_per_hideout = self.hunters_var.get()
        num_treasures = self.treasure_var.get()
        num_knights = self.knight_var.get()
        num_garrisons = self.garrison_var.get()

        # Create new simulation
        self.simulation = Simulation(grid_size)

        # Setup simulation
        self.simulation.setup(
            num_hideouts=num_hideouts,
            num_hunters_per_hideout=hunters_per_hideout,
            num_treasures=num_treasures,
            num_knights=num_knights,
            num_garrisons=num_garrisons
        )

        # Draw initial state
        self._draw_grid()
        self._update_stats()

        # Enable controls
        self.start_button.config(state=tk.NORMAL, text="Start")
        self.step_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)

        # Set animation speed
        self.animation_speed = self.speed_var.get()

    def _toggle_simulation(self):
        """Toggle simulation between running and stopped states."""
        if not self.simulation:
            return

        if self.running:
            self._stop_simulation()
        else:
            self._start_simulation()

    def _start_simulation(self):
        """Start the simulation."""
        self.running = True
        self.simulation.running = True
        self.start_button.config(text="Stop")
        self.animation_speed = self.speed_var.get()
        self._run_simulation_step()

    def _stop_simulation(self):
        """Stop the simulation."""
        self.running = False
        self.simulation.running = False
        self.start_button.config(text="Start")

    def _step_simulation(self):
        """Run a single simulation step."""
        if not self.simulation:
            return

        # Perform one step
        self.simulation.step()

        # Update display
        self._draw_grid()
        self._update_stats()

    def _run_simulation_step(self):
        """Run a simulation step and schedule the next one if still running."""
        if not self.running:
            return

        self._step_simulation()

        if self.running:
            # Schedule next step
            self.root.after(self.animation_speed, self._run_simulation_step)

    def _reset_simulation(self):
        """Reset the simulation to initial state."""
        if not self.simulation:
            return

        # Stop the simulation if running
        self._stop_simulation()

        # Setup a new simulation with the same parameters
        self._setup_simulation()

    def _apply_speed(self):
        """Apply the current speed setting."""
        self.animation_speed = self.speed_var.get()

    def _draw_grid(self):
        """Draw the current state of the grid on the canvas."""
        if not self.simulation:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Calculate cell size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        grid_width = self.simulation.grid.width
        grid_height = self.simulation.grid.height

        # Make sure we have valid dimensions
        if canvas_width <= 0 or canvas_height <= 0 or grid_width <= 0 or grid_height <= 0:
            return

        cell_size = min(canvas_width // grid_width, canvas_height // grid_height)
        if cell_size <= 0:
            cell_size = 10  # Minimum cell size

        # Draw grid cells
        for y in range(grid_height):
            for x in range(grid_width):
                # Get entity at this location
                entity = self.simulation.grid.get_entity_at(Location(x, y))

                # Determine cell color
                if entity is None:
                    color = self.colors[EntityType.EMPTY]
                else:
                    color = self.colors[entity.type]

                # Draw cell
                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

                # Add text label for debugging (show entity type)
                if entity:
                    label = entity.type.name[0]  # First letter of entity type
                    self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                            text=label, fill="black", font=("Arial", max(8, cell_size // 3)))

                    # Draw additional details for entities
                    if entity.type == EntityType.HUNTER:
                        # Show stamina as a small bar
                        stamina_width = (cell_size - 4) * entity.stamina / 100
                        self.canvas.create_rectangle(x1 + 2, y1 + 2, x1 + 2 + stamina_width, y1 + 4,
                                                     fill="white", outline="")

                        # Indicate if carrying treasure
                        if entity.carrying_treasure_value > 0:
                            self.canvas.create_oval(x1 + cell_size // 3, y1 + cell_size // 3,
                                                    x2 - cell_size // 3, y2 - cell_size // 3,
                                                    fill=self.colors[EntityType.TREASURE], outline="")

                        # Indicate skill
                        skill_initial = entity.skill.name[0]
                        self.canvas.create_text(x1 + cell_size - 5, y1 + 5,
                                                text=skill_initial, fill="white",
                                                font=("Arial", max(6, cell_size // 4)))

                    elif entity.type == EntityType.KNIGHT:
                        # Show energy as a small bar
                        energy_width = (cell_size - 4) * entity.energy / 100
                        self.canvas.create_rectangle(x1 + 2, y2 - 4, x1 + 2 + energy_width, y2 - 2,
                                                     fill="white", outline="")

                    elif entity.type == EntityType.HIDEOUT:
                        # Show number of hunters and capacity
                        hunter_count = len(entity.hunters)
                        capacity = entity.max_capacity
                        self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2 - 5,
                                                text=f"{hunter_count}/{capacity}", fill="white",
                                                font=("Arial", max(6, cell_size // 4)))

                        # Show stored treasure amount below
                        if entity.stored_treasure_count > 0:
                            self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2 + 5,
                                                    text=f"T:{entity.stored_treasure_count}", fill="gold",
                                                    font=("Arial", max(6, cell_size // 4)))

                    elif entity.type == EntityType.GARRISON:
                        # Show number of knights
                        knight_count = len(entity.knights)
                        self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                                text=str(knight_count), fill="white")

                    elif entity.type == EntityType.TREASURE:
                        # Indicate treasure type with a label
                        if entity.treasure_type == TreasureType.BRONZE:
                            label = "B"
                        elif entity.treasure_type == TreasureType.SILVER:
                            label = "S"
                        else:  # GOLD
                            label = "G"

                        self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                                text=label, fill="black", font=("Arial", max(8, cell_size // 3)))

                        # Show value as tiny bar below
                        value_percentage = entity.value / entity.initial_value
                        value_width = (cell_size - 4) * value_percentage
                        self.canvas.create_rectangle(x1 + 2, y2 - 4, x1 + 2 + value_width, y2 - 2,
                                                     fill="white", outline="")

        # Draw legend
        legend_y = grid_height * cell_size + 10
        legend_x = 10
        legend_spacing = 80

        # Hunter legend
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20,
                                     fill=self.colors[EntityType.HUNTER], outline="black")
        self.canvas.create_text(legend_x + 40, legend_y + 10, text="Hunter", anchor=tk.W)

        # Knight legend
        legend_x += legend_spacing
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20,
                                     fill=self.colors[EntityType.KNIGHT], outline="black")
        self.canvas.create_text(legend_x + 40, legend_y + 10, text="Knight", anchor=tk.W)

        # Treasure legend
        legend_x += legend_spacing
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20,
                                     fill=self.colors[EntityType.TREASURE], outline="black")
        self.canvas.create_text(legend_x + 40, legend_y + 10, text="Treasure", anchor=tk.W)

        # Hideout legend
        legend_x += legend_spacing
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20,
                                     fill=self.colors[EntityType.HIDEOUT], outline="black")
        self.canvas.create_text(legend_x + 40, legend_y + 10, text="Hideout", anchor=tk.W)

        # Garrison legend
        legend_x += legend_spacing
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20,
                                     fill=self.colors[EntityType.GARRISON], outline="black")
        self.canvas.create_text(legend_x + 40, legend_y + 10, text="Garrison", anchor=tk.W)

    def _update_stats(self):
        """Update the statistics display."""
        if not self.simulation:
            return

        # Get current stats
        stats = self.simulation.get_stats()

        # Calculate total wealth of all hunters
        total_hunter_wealth = sum(hunter.wealth for hunter in self.simulation.hunters)

        # Count treasures by type
        bronze_count = 0
        silver_count = 0
        gold_count = 0

        for entity in self.simulation.grid.entities:
            if entity.type == EntityType.TREASURE:
                if entity.treasure_type == TreasureType.BRONZE:
                    bronze_count += 1
                elif entity.treasure_type == TreasureType.SILVER:
                    silver_count += 1
                elif entity.treasure_type == TreasureType.GOLD:
                    gold_count += 1

        # Format stats text
        stats_text = (
            f"Step: {stats['step_count']}\n"
            f"Hunters: {stats['hunters']}  Knights: {stats['knights']}  Hideouts: {stats['hideouts']}  Garrisons: {stats['garrisons']}\n"
            f"Treasures: {stats['treasures']} (Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count})\n"
            f"Total Treasure Collected: {stats['total_treasure_collected']:.2f} ({stats['total_treasure_pieces_collected']} pieces)\n"
            f"Total Hunter Wealth: {total_hunter_wealth:.2f}"
        )

        # Update text widget
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)