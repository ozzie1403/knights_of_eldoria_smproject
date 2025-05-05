import tkinter as tk
from tkinter import ttk
from typing import Callable


class ControlPanel(tk.Frame):
    """
    Control panel for the simulation with buttons for start, stop, step, and reset,
    and a slider for simulation speed.
    """

    def __init__(self, master, start_callback: Callable, stop_callback: Callable,
                 step_callback: Callable, reset_callback: Callable,
                 speed_callback: Callable):
        super().__init__(master, bg="#d9b381", relief=tk.RAISED, borderwidth=2)
        self.master = master

        # Store callbacks
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.step_callback = step_callback
        self.reset_callback = reset_callback
        self.speed_callback = speed_callback

        # Set up the control panel
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the control panel UI."""
        # Main container
        main_container = tk.Frame(self, bg="#d9b381", padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(main_container, text="Simulation Controls",
                         font=("Helvetica", 14, "bold"), bg="#d9b381", fg="#4b2e0d")
        title.pack(pady=(0, 10))

        # Buttons container
        button_container = tk.Frame(main_container, bg="#d9b381")
        button_container.pack(fill=tk.X, pady=5)

        # Control buttons with custom styling
        button_style = {"font": ("Helvetica", 12),
                        "bg": "#8B4513", "fg": "white",
                        "activebackground": "#a35a1a", "activeforeground": "white",
                        "borderwidth": 2, "relief": tk.RAISED,
                        "width": 10, "padx": 10, "pady": 5}

        # Start button
        self.start_button = tk.Button(button_container, text="Start",
                                      command=self.start_callback, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = tk.Button(button_container, text="Stop",
                                     command=self.stop_callback, **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)

        # Step button
        self.step_button = tk.Button(button_container, text="Step",
                                     command=self.step_callback, **button_style)
        self.step_button.pack(side=tk.LEFT, padx=5)

        # Reset button
        self.reset_button = tk.Button(button_container, text="Reset",
                                      command=self.reset_callback, **button_style)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Speed slider
        speed_container = tk.Frame(main_container, bg="#d9b381")
        speed_container.pack(fill=tk.X, pady=10)

        speed_label = tk.Label(speed_container, text="Simulation Speed:",
                               font=("Helvetica", 12), bg="#d9b381", fg="#4b2e0d")
        speed_label.pack(side=tk.LEFT, padx=(0, 10))

        self.speed_slider = tk.Scale(speed_container, from_=1, to=10, orient=tk.HORIZONTAL,
                                     length=200, bg="#d9b381", troughcolor="#8B4513",
                                     highlightthickness=0, sliderrelief=tk.RAISED,
                                     command=lambda v: self.speed_callback(float(v)))
        self.speed_slider.set(5)  # Default speed
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Simulation settings container (hidden for now, could be expanded later)
        settings_container = tk.Frame(main_container, bg="#d9b381")
        settings_container.pack(fill=tk.X, pady=5)

        self.settings_button = tk.Button(settings_container, text="Settings",
                                         font=("Helvetica", 12),
                                         bg="#4b2e0d", fg="white",
                                         command=self._toggle_settings,
                                         padx=10, pady=5)
        self.settings_button.pack(fill=tk.X)

        # Settings panel (hidden by default)
        self.settings_panel = tk.Frame(main_container, bg="#e8c496", relief=tk.SUNKEN, borderwidth=2)
        # Add settings controls here when needed

    def _toggle_settings(self) -> None:
        """Toggle visibility of settings panel."""
        if self.settings_panel.winfo_ismapped():
            self.settings_panel.pack_forget()
            self.settings_button.config(text="Settings")
        else:
            self.settings_panel.pack(fill=tk.X, pady=5)
            self.settings_button.config(text="Hide Settings")

    def update_button_states(self, is_running: bool, is_complete: bool = False) -> None:
        """Update button states based on simulation state."""
        if is_complete:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.step_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)
        elif is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.step_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.step_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)