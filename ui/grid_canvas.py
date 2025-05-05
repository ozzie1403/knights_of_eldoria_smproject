import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, Tuple

from simulation.simulation_manager import SimulationManager
from models.entity import EntityType


class GridCanvas(tk.Canvas):
    """
    Canvas for visualizing the simulation grid.
    Displays entities with their icons and colors.
    """

    def __init__(self, master, simulation: SimulationManager):
        super().__init__(master, bg="#f3e8c8", highlightthickness=1, highlightbackground="#8B4513")
        self.master = master
        self.simulation = simulation
        self.cell_size = 30  # Default cell size in pixels
        self.grid_width = simulation.grid_width
        self.grid_height = simulation.grid_height

        # Entity colors
        self.entity_colors = {
            EntityType.KNIGHT: "#8B0000",  # Dark red
            EntityType.HUNTER: "#4169E1",  # Royal blue
            EntityType.TREASURE: "#FFD700",  # Gold
            EntityType.HIDEOUT: "#8B4513",  # Saddle brown
            EntityType.GARRISON: "#708090"  # Slate gray
        }

        # Set up the canvas
        self._setup_canvas()

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

    def _setup_canvas(self) -> None:
        """Set up the initial canvas."""
        self.update_grid()

        # Add tooltip
        self.tooltip = tk.Label(self, text="", bg="#FFFACD", relief="solid", borderwidth=1)
        self.tooltip.place_forget()

        # Bind mouse events for tooltips
        self.bind("<Motion>", self._on_mouse_move)
        self.bind("<Leave>", self._on_mouse_leave)

    def _on_resize(self, event) -> None:
        """Handle canvas resize event."""
        # Calculate new cell size based on canvas dimensions
        self.cell_size = min(
            event.width // self.grid_width,
            event.height // self.grid_height
        )
        self.update_grid()

    def update_grid(self) -> None:
        """Update the grid visualization with current simulation state."""
        self.delete("all")  # Clear canvas

        # Calculate cell size to fit the canvas
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            self.cell_size = min(
                canvas_width // self.grid_width,
                canvas_height // self.grid_height
            )

        # Calculate grid dimensions
        grid_pixel_width = self.cell_size * self.grid_width
        grid_pixel_height = self.cell_size * self.grid_height

        # Center the grid in the canvas
        self.x_offset = (canvas_width - grid_pixel_width) // 2
        self.y_offset = (canvas_height - grid_pixel_height) // 2

        # Draw grid lines
        for i in range(self.grid_width + 1):
            x = self.x_offset + i * self.cell_size
            self.create_line(x, self.y_offset, x, self.y_offset + grid_pixel_height,
                             fill="#8B4513", width=1)

        for i in range(self.grid_height + 1):
            y = self.y_offset + i * self.cell_size
            self.create_line(self.x_offset, y, self.x_offset + grid_pixel_width, y,
                             fill="#8B4513", width=1)

        # Draw entities
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                entity = self.simulation.get_entity_at(x, y)
                if entity:
                    self._draw_entity(x, y, entity)

    def _draw_entity(self, x: int, y: int, entity) -> None:
        """Draw an entity at the specified grid position."""
        # Calculate pixel coordinates
        pixel_x = self.x_offset + x * self.cell_size
        pixel_y = self.y_offset + y * self.cell_size

        # Draw cell background based on entity type
        color = entity.color if hasattr(entity, 'color') else self.entity_colors.get(
            entity.type, "#000000")

        # Create cell background with slightly smaller size for spacing
        margin = 1
        self.create_rectangle(
            pixel_x + margin, pixel_y + margin,
            pixel_x + self.cell_size - margin, pixel_y + self.cell_size - margin,
            fill=color, outline="", tags=f"entity_{x}_{y}"
        )

        # Draw entity icon/text
        icon = entity.icon if hasattr(entity, 'icon') else "?"
        self.create_text(
            pixel_x + self.cell_size // 2,
            pixel_y + self.cell_size // 2,
            text=icon, fill="white", font=("Helvetica", int(self.cell_size * 0.5)),
            tags=f"entity_{x}_{y}"
        )

        # Store entity info for tooltip
        self.tag_bind(f"entity_{x}_{y}", "<Enter>",
                      lambda e, entity=entity: self._show_tooltip(e, entity))

    def _show_tooltip(self, event, entity) -> None:
        """Show tooltip with entity information."""
        # Create tooltip text
        if entity.type == EntityType.KNIGHT:
            text = f"Knight\nState: {entity.state.name}\nEnergy: {entity.energy:.1f}%"
        elif entity.type == EntityType.HUNTER:
            text = (f"Hunter\nSkill: {entity.skill.name}\n"
                    f"State: {entity.state.name}\nStamina: {entity.stamina:.1f}%\n"
                    f"Wealth: {entity.wealth:.1f}")
            if entity.carrying_treasure:
                text += f"\nCarrying: {entity.carrying_treasure['type'].name}"
        elif entity.type == EntityType.TREASURE:
            text = f"{entity.treasure_type.name} Treasure\nValue: {entity.current_value:.1f}"
        elif entity.type == EntityType.HIDEOUT:
            text = f"Hideout\nOccupants: {len(entity.occupants)}/{entity.max_occupants}"
        elif entity.type == EntityType.GARRISON:
            text = f"Garrison\nKnights can rest here"
        else:
            text = str(entity)

        # Update and show tooltip
        self.tooltip.config(text=text)
        self.tooltip.place(x=event.x + 10, y=event.y + 10)

    def _on_mouse_move(self, event) -> None:
        """Handle mouse movement to update tooltip position."""
        # If tooltip is visible, update its position
        if self.tooltip.winfo_viewable():
            self.tooltip.place(x=event.x + 10, y=event.y + 10)

    def _on_mouse_leave(self, event) -> None:
        """Hide tooltip when mouse leaves canvas."""
        self.tooltip.place_forget()