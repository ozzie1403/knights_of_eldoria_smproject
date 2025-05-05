import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Dict, List, Optional

from simulation.simulation_manager import SimulationManager
from models.entity import EntityType
from models.types import TreasureType, HunterSkill, HunterState, KnightState
from ui.grid_canvas import GridCanvas
from ui.control_panel import ControlPanel
from ui.stats_panel import StatsPanel


class SimulationUI(tk.Frame):
    """
    Main UI component for the Knights of Eldoria simulation.
    Contains the grid visualization, control panel, and statistics panel.
    """

    def __init__(self, master, simulation: SimulationManager):
        super().__init__(master)
        self.master = master
        self.simulation = simulation
        self.running = False
        self.update_interval = 500  # milliseconds between simulation steps
        self.update_thread = None
        self.stop_event = threading.Event()

        # Set up the UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main UI components."""
        # Main container with two columns
        main_container = tk.Frame(self, bg="#f3e8c8")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left column for grid and controls (2/3 width)
        left_column = tk.Frame(main_container, bg="#f3e8c8")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Grid canvas (will expand to fill available space)
        self.grid_canvas = GridCanvas(left_column, self.simulation)
        self.grid_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel below grid
        self.control_panel = ControlPanel(left_column, self._on_start, self._on_stop,
                                          self._on_step, self._on_reset,
                                          self._on_speed_change)
        self.control_panel.pack(fill=tk.X, padx=10, pady=10)

        # Right column for statistics (1/3 width)
        right_column = tk.Frame(main_container, bg="#f3e8c8", width=300)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        right_column.pack_propagate(False)  # Prevent shrinking

        # Stats panel
        self.stats_panel = StatsPanel(right_column, self.simulation)
        self.stats_panel.pack(fill=tk.BOTH, expand=True)

        # Start with an initial update
        self._update_ui()

    def _on_start(self) -> None:
        """Start the simulation."""
        if not self.running and not self.simulation.is_complete:
            self.running = True
            self.simulation.start()
            self.stop_event.clear()
            self.update_thread = threading.Thread(target=self._run_simulation)
            self.update_thread.daemon = True
            self.update_thread.start()
            self.control_panel.update_button_states(self.running)

    def _on_stop(self) -> None:
        """Stop the simulation."""
        if self.running:
            self.running = False
            self.simulation.stop()
            self.stop_event.set()
            if self.update_thread:
                self.update_thread.join(timeout=1.0)
            self.control_panel.update_button_states(self.running)

    def _on_step(self) -> None:
        """Step through the simulation."""
        if not self.running and not self.simulation.is_complete:
            self.simulation.step()
            self._update_ui()

            # Check if simulation is complete after step
            if self.simulation.is_complete:
                self._show_completion_message()

    def _on_reset(self) -> None:
        """Reset the simulation."""
        self._on_stop()  # Stop if running
        self.simulation.reset()
        self._update_ui()
        self.control_panel.update_button_states(False)

    def _on_speed_change(self, speed_value: float) -> None:
        """Change the simulation speed."""
        # Convert slider value (1-10) to update interval in ms (1000-50)
        self.update_interval = int(1050 - (speed_value * 100))

    def _run_simulation(self) -> None:
        """Run the simulation in a separate thread."""
        while self.running and not self.stop_event.is_set():
            # Check if simulation is complete
            if self.simulation.is_complete:
                self.running = False
                # Use after to schedule UI update from main thread
                self.after(0, self._show_completion_message)
                break

            # Process one step
            self.simulation.step()

            # Schedule UI update from main thread
            self.after(0, self._update_ui)

            # Wait for next update
            time.sleep(self.update_interval / 1000.0)

    def _update_ui(self) -> None:
        """Update the UI components with current simulation state."""
        self.grid_canvas.update_grid()
        self.stats_panel.update_stats()

        # Update control panel button states
        self.control_panel.update_button_states(self.running, self.simulation.is_complete)

    def _show_completion_message(self) -> None:
        """Show a message when the simulation is complete."""
        messagebox.showinfo(
            "Simulation Complete",
            f"The simulation has ended.\n\n"
            f"Reason: {self.simulation.get_completion_reason()}\n\n"
            f"Final Statistics:\n"
            f"- Treasure Collected: {self.simulation.stats['treasure_collected']['total']:.2f}\n"
            f"- Hunters Lost: {self.simulation.stats['hunters_lost']}\n"
            f"- Hunters Recruited: {self.simulation.stats['hunters_recruited']}"
        )
        self.control_panel.update_button_states(False, True)