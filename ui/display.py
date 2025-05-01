import tkinter as tk
from tkinter import ttk, messagebox
from models.simulation import Simulation
from models.location import Location
from utils.constants import EntityType, DEFAULT_GRID_SIZE
from utils.constants import MIN_GRID_SIZE, MAX_GRID_SIZE


class SimulationDisplay:
    """GUI display for the Knights of Eldoria simulation."""

    def __init__(self, root):
        self.root = root
        self.root.title("Knights of Eldoria")
        self.root.geometry("1000x800")
        self.simulation = None
        self.running = False
        self.animation_speed = 100  # milliseconds between steps

        # Color scheme
        self.colors = {
            EntityType.EMPTY: "#f0f0f0",  # Light gray for empty
            EntityType.TREASURE: "#ffd700",  # Gold for treasure
            EntityType.HUNTER: "#4caf50",  # Green for hunters
            EntityType.HIDEOUT: "#2196f3",  # Blue for hideouts
            EntityType.KNIGHT: "#f44336", # Red for knights
            EntityType.GARRISON: "#9c27b0"  # Purple for garrisons
        }

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for settings and controls
        left_panel = ttk.Frame(main_frame, padding=10, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right panel for grid display
        right_panel = ttk.Frame(main_frame, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Setup control widgets
        self._setup_controls(left_panel)

        # Setup grid canvas
        self.canvas_frame = ttk.Frame(right_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Setup statistics display
        self.stats_frame = ttk.LabelFrame(right_panel, text="Statistics")
        self.stats_frame.pack(fill=tk.X, pady=(10, 0))

        self.stats_text = tk.Text(self.stats_frame, height=5, width=50, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)

        # Bind resize event
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _setup_controls(self, parent):
        """Set up control widgets."""
        # Title
        title_label = ttk.Label(parent, text="Knights of Eldoria", font=("Arial", 16))
        title_label.pack(pady=(0, 20))

        # Settings frame
        settings_frame = ttk.LabelFrame(parent, text="Simulation Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid size
        grid_frame = ttk.Frame(settings_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(grid_frame, text="Grid Size:").pack(side=tk.LEFT)
        self.grid_size_var = tk.IntVar(value=DEFAULT_GRID_SIZE)
        grid_size_spin = ttk.Spinbox(grid_frame, from_=MIN_GRID_SIZE, to=MAX_GRID_SIZE,
                                     textvariable=self.grid_size_var, width=5)
        grid_size_spin.pack(side=tk.RIGHT)

        # Hideouts
        hideout_frame = ttk.Frame(settings_frame)
        hideout_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hideout_frame, text="Hideouts:").pack(side=tk.LEFT)
        self.hideout_var = tk.IntVar(value=3)
        hideout_spin = ttk.Spinbox(hideout_frame, from_=1, to=10,
                                   textvariable=self.hideout_var, width=5)
        hideout_spin.pack(side=tk.RIGHT)

        # Hunters per hideout
        hunters_frame = ttk.Frame(settings_frame)
        hunters_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hunters_frame, text="Hunters per Hideout:").pack(side=tk.LEFT)
        self.hunters_var = tk.IntVar(value=2)
        hunters_spin = ttk.Spinbox(hunters_frame, from_=1, to=5,
                                   textvariable=self.hunters_var, width=5)
        hunters_spin.pack(side=tk.RIGHT)

        # Treasures
        treasure_frame = ttk.Frame(settings_frame)
        treasure_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(treasure_frame, text="Treasures:").pack(side=tk.LEFT)
        self.treasure_var = tk.IntVar(value=30)
        treasure_spin = ttk.Spinbox(treasure_frame, from_=10, to=100,
                                    textvariable=self.treasure_var, width=5)
        treasure_spin.pack(side=tk.RIGHT)

        # Knights
        knight_frame = ttk.Frame(settings_frame)
        knight_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(knight_frame, text="Knights:").pack(side=tk.LEFT)
        self.knight_var = tk.IntVar(value=2)
        knight_spin = ttk.Spinbox(knight_frame, from_=0, to=10,
                                  textvariable=self.knight_var, width=5)
        knight_spin.pack(side=tk.RIGHT)

        #garrison
        garrison_frame = ttk.Frame(settings_frame)
        garrison_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(garrison_frame, text="Garrisons:").pack(side=tk.LEFT)
        self.garrison_var = tk.IntVar(value=2)
        garrison_spin = ttk.Spinbox(garrison_frame, from_=1, to=5,
                                    textvariable=self.garrison_var, width=5)
        garrison_spin.pack(side=tk.RIGHT)

        # Animation speed
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(speed_frame, text="Animation Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=100)
        speed_spin = ttk.Spinbox(speed_frame, from_=10, to=1000, increment=10,
                                 textvariable=self.speed_var, width=5)
        speed_spin.pack(side=tk.RIGHT)

        # Controls frame
        controls_frame = ttk.LabelFrame(parent, text="Controls")
        controls_frame.pack(fill=tk.X)

        # Setup button
        self.setup_button = ttk.Button(controls_frame, text="Setup", command=self._setup_simulation)
        self.setup_button.pack(fill=tk.X, padx=5, pady=5)

        # Start/Stop button
        self.start_button = ttk.Button(controls_frame, text="Start", command=self._toggle_simulation)
        self.start_button.pack(fill=tk.X, padx=5, pady=5)
        self.start_button.config(state=tk.DISABLED)

        # Step button
        self.step_button = ttk.Button(controls_frame, text="Step", command=self._step_simulation)
        self.step_button.pack(fill=tk.X, padx=5, pady=5)
        self.step_button.config(state=tk.DISABLED)

        # Reset button
        self.reset_button = ttk.Button(controls_frame, text="Reset", command=self._reset_simulation)
        self.reset_button.pack(fill=tk.X, padx=5, pady=5)
        self.reset_button.config(state=tk.DISABLED)

    def _on_canvas_resize(self, event):
        """Handle canvas resize event."""
        # Only redraw if simulation exists
        if self.simulation:
            print(f"Canvas resized: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
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

        # No need to call start since we set running=True in setup

        # Draw initial state
        self._draw_grid()
        self._update_stats()

        # Enable controls
        self.start_button.config(state=tk.NORMAL, text="Stop")
        self.step_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)

        # Start simulation after setup
        self.running = True
        self._run_simulation_step()

        # Draw initial state
        self._draw_grid()
        self._update_stats()

        # Enable controls
        self.start_button.config(state=tk.NORMAL, text="Stop")
        self.step_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)

        # Start simulation after setup
        self.running = True
        self._run_simulation_step()

    def _debug_grid(self):
        """Print debug information about the grid."""
        if not self.simulation:
            print("No simulation available")
            return

        print(f"Grid size: {self.simulation.grid.width}x{self.simulation.grid.height}")
        print(f"Total entities: {len(self.simulation.grid.entities)}")

        # Count entity types
        entity_counts = {}
        for entity in self.simulation.grid.entities:
            entity_type = entity.type.name
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        print("Entity counts:")
        for entity_type, count in entity_counts.items():
            print(f"  {entity_type}: {count}")

        # Debug grid content
        print("Grid contents:")
        empty_count = 0
        filled_count = 0

        for y in range(self.simulation.grid.height):
            for x in range(self.simulation.grid.width):
                entity = self.simulation.grid.grid[y][x]
                if entity is None:
                    empty_count += 1
                else:
                    filled_count += 1

        print(f"  Empty cells: {empty_count}")
        print(f"  Filled cells: {filled_count}")

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
        self.simulation.running = True  # Set simulation as running
        self.start_button.config(text="Stop")
        self.animation_speed = self.speed_var.get()
        self._run_simulation_step()

    def _stop_simulation(self):
        """Stop the simulation."""
        self.running = False
        self.simulation.running = False  # Set simulation as stopped
        self.start_button.config(text="Start")

    def _step_simulation(self):
        """Perform a single simulation step."""
        if not self.simulation:
            return

        self.simulation.step()
        self._draw_grid()
        self._update_stats()

        # Check if simulation has ended
        if not self.simulation.running:
            self._stop_simulation()
            messagebox.showinfo("Simulation Complete", "The simulation has ended.")

    def _run_simulation_step(self):
        """Run a simulation step and schedule the next one if still running."""
        if not self.running:
            return

        self._step_simulation()

        if self.running:
            self.root.after(self.animation_speed, self._run_simulation_step)

    def _reset_simulation(self):
        """Reset the simulation."""
        if not self.simulation:
            return

        self._stop_simulation()
        self.simulation.reset()
        self._setup_simulation()

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

                    elif entity.type == EntityType.KNIGHT:
                        # Show energy as a small bar
                        energy_width = (cell_size - 4) * entity.energy / 100
                        self.canvas.create_rectangle(x1 + 2, y2 - 4, x1 + 2 + energy_width, y2 - 2,
                                                     fill="white", outline="")

                    elif entity.type == EntityType.HIDEOUT:
                        # Show number of hunters
                        hunter_count = len(entity.hunters)
                        self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                                text=str(hunter_count), fill="white")

                    elif entity.type == EntityType.GARRISON:
                        # Show number of knights
                        knight_count = len(entity.knights)
                        self.canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                                text=str(knight_count), fill="white")

        # Draw legend
        # (rest of legend code remains the same)

        # Draw legend
        legend_x = 10
        legend_y = canvas_height - 80
        legend_size = 15
        legend_spacing = 25

        # Draw legend title
        self.canvas.create_text(legend_x, legend_y - 20, text="LEGEND:", anchor=tk.W, font=("Arial", 10, "bold"))

        # Draw legend items (in 2 columns)
        entities = [
            (EntityType.HUNTER, "Hunter"),
            (EntityType.TREASURE, "Treasure"),
            (EntityType.HIDEOUT, "Hideout"),
            (EntityType.KNIGHT, "Knight"),
            (EntityType.GARRISON, "Garrison")
        ]

        for i, (entity_type, label) in enumerate(entities):
            row = i % 3
            col = i // 3
            x = legend_x + col * 120
            y = legend_y + row * legend_spacing

            self.canvas.create_rectangle(x, y, x + legend_size, y + legend_size,
                                         fill=self.colors[entity_type], outline="black")
            self.canvas.create_text(x + legend_size + 5, y + legend_size // 2,
                                    text=label, anchor=tk.W)

    def _update_stats(self):
        """Update the statistics display."""
        if not self.simulation:
            return

        # Get current stats
        stats = self.simulation.get_stats()

        # Format stats text
        stats_text = (
            f"Step: {stats['step_count']}\n"
            f"Hunters: {stats['hunters']}  Treasures: {stats['treasures']}  Knights: {stats['knights']}  Garrisons: {stats['garrisons']}\n"
            f"Total Treasure Collected: {stats['total_treasure_collected']:.2f}"
        )

        # Update text widget
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)

