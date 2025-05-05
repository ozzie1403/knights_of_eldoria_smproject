import tkinter as tk
from tkinter import ttk
from typing import Dict

from simulation.simulation_manager import SimulationManager
from models.types import TreasureType


class StatsPanel(tk.Frame):
    """
    Panel for displaying simulation statistics.
    Shows treasure collected, hunters lost/recruited, etc.
    """

    def __init__(self, master, simulation: SimulationManager):
        super().__init__(master, bg="#e8c496", relief=tk.RAISED, borderwidth=2)
        self.master = master
        self.simulation = simulation

        # Set up the stats panel
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the stats panel UI."""
        # Title
        title = tk.Label(self, text="Simulation Statistics",
                         font=("Helvetica", 14, "bold"), bg="#e8c496", fg="#4b2e0d")
        title.pack(pady=10)

        # Main container with padding
        main_container = tk.Frame(self, bg="#e8c496", padx=15, pady=5)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Step counter
        step_frame = tk.Frame(main_container, bg="#e8c496")
        step_frame.pack(fill=tk.X, pady=5)

        step_label = tk.Label(step_frame, text="Simulation Step:",
                              font=("Helvetica", 12, "bold"), bg="#e8c496", fg="#4b2e0d")
        step_label.pack(side=tk.LEFT)

        self.step_counter = tk.Label(step_frame, text="0",
                                     font=("Helvetica", 12), bg="#e8c496", fg="#4b2e0d")
        self.step_counter.pack(side=tk.RIGHT)

        # Divider
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Treasure section
        treasure_frame = tk.LabelFrame(main_container, text="Treasure",
                                       font=("Helvetica", 12, "bold"), bg="#e8c496", fg="#4b2e0d")
        treasure_frame.pack(fill=tk.X, pady=5)

        # Bronze treasure
        bronze_frame = tk.Frame(treasure_frame, bg="#e8c496")
        bronze_frame.pack(fill=tk.X, pady=2)

        bronze_label = tk.Label(bronze_frame, text="Bronze:",
                                font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        bronze_label.pack(side=tk.LEFT)

        self.bronze_value = tk.Label(bronze_frame, text="0.0",
                                     font=("Helvetica", 10), bg="#e8c496", fg="#CD7F32")
        self.bronze_value.pack(side=tk.RIGHT)

        # Silver treasure
        silver_frame = tk.Frame(treasure_frame, bg="#e8c496")
        silver_frame.pack(fill=tk.X, pady=2)

        silver_label = tk.Label(silver_frame, text="Silver:",
                                font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        silver_label.pack(side=tk.LEFT)

        self.silver_value = tk.Label(silver_frame, text="0.0",
                                     font=("Helvetica", 10), bg="#e8c496", fg="#C0C0C0")
        self.silver_value.pack(side=tk.RIGHT)

        # Gold treasure
        gold_frame = tk.Frame(treasure_frame, bg="#e8c496")
        gold_frame.pack(fill=tk.X, pady=2)

        gold_label = tk.Label(gold_frame, text="Gold:",
                              font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        gold_label.pack(side=tk.LEFT)

        self.gold_value = tk.Label(gold_frame, text="0.0",
                                   font=("Helvetica", 10), bg="#e8c496", fg="#FFD700")
        self.gold_value.pack(side=tk.RIGHT)

        # Total treasure
        total_frame = tk.Frame(treasure_frame, bg="#e8c496")
        total_frame.pack(fill=tk.X, pady=2)

        total_label = tk.Label(total_frame, text="Total:",
                               font=("Helvetica", 10, "bold"), bg="#e8c496", fg="#4b2e0d")
        total_label.pack(side=tk.LEFT)

        self.total_value = tk.Label(total_frame, text="0.0",
                                    font=("Helvetica", 10, "bold"), bg="#e8c496", fg="#4b2e0d")
        self.total_value.pack(side=tk.RIGHT)

        # Divider
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Hunter section
        hunter_frame = tk.LabelFrame(main_container, text="Hunters",
                                     font=("Helvetica", 12, "bold"), bg="#e8c496", fg="#4b2e0d")
        hunter_frame.pack(fill=tk.X, pady=5)

        # Remaining hunters
        remain_hunter_frame = tk.Frame(hunter_frame, bg="#e8c496")
        remain_hunter_frame.pack(fill=tk.X, pady=2)

        remain_hunter_label = tk.Label(remain_hunter_frame, text="Remaining:",
                                       font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        remain_hunter_label.pack(side=tk.LEFT)

        self.remain_hunter_value = tk.Label(remain_hunter_frame, text="0",
                                            font=("Helvetica", 10), bg="#e8c496", fg="#4169E1")
        self.remain_hunter_value.pack(side=tk.RIGHT)

        # Lost hunters
        lost_hunter_frame = tk.Frame(hunter_frame, bg="#e8c496")
        lost_hunter_frame.pack(fill=tk.X, pady=2)

        lost_hunter_label = tk.Label(lost_hunter_frame, text="Lost:",
                                     font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        lost_hunter_label.pack(side=tk.LEFT)

        self.lost_hunter_value = tk.Label(lost_hunter_frame, text="0",
                                          font=("Helvetica", 10), bg="#e8c496", fg="#8B0000")
        self.lost_hunter_value.pack(side=tk.RIGHT)

        # Recruited hunters
        recruit_hunter_frame = tk.Frame(hunter_frame, bg="#e8c496")
        recruit_hunter_frame.pack(fill=tk.X, pady=2)

        recruit_hunter_label = tk.Label(recruit_hunter_frame, text="Recruited:",
                                        font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        recruit_hunter_label.pack(side=tk.LEFT)

        self.recruit_hunter_value = tk.Label(recruit_hunter_frame, text="0",
                                             font=("Helvetica", 10), bg="#e8c496", fg="#228B22")
        self.recruit_hunter_value.pack(side=tk.RIGHT)

        # Average stamina
        stamina_frame = tk.Frame(hunter_frame, bg="#e8c496")
        stamina_frame.pack(fill=tk.X, pady=2)

        stamina_label = tk.Label(stamina_frame, text="Avg. Stamina:",
                                 font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        stamina_label.pack(side=tk.LEFT)

        self.stamina_value = tk.Label(stamina_frame, text="0.0%",
                                      font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        self.stamina_value.pack(side=tk.RIGHT)

        # Divider
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Status section
        status_frame = tk.Frame(main_container, bg="#e8c496")
        status_frame.pack(fill=tk.X, pady=5)

        status_label = tk.Label(status_frame, text="Status:",
                                font=("Helvetica", 12, "bold"), bg="#e8c496", fg="#4b2e0d")
        status_label.pack(side=tk.LEFT)

        self.status_value = tk.Label(status_frame, text="Running",
                                     font=("Helvetica", 12), bg="#e8c496", fg="#228B22")
        self.status_value.pack(side=tk.RIGHT)

        # Completion reason (hidden until simulation completes)
        self.completion_frame = tk.Frame(main_container, bg="#e8c496")

        completion_label = tk.Label(self.completion_frame, text="Reason:",
                                    font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d")
        completion_label.pack(side=tk.LEFT)

        self.completion_value = tk.Label(self.completion_frame, text="",
                                         font=("Helvetica", 10), bg="#e8c496", fg="#4b2e0d",
                                         wraplength=250, justify=tk.LEFT)
        self.completion_value.pack(side=tk.RIGHT)

    def update_stats(self) -> None:
        """Update the stats panel with current simulation statistics."""
        # Get current statistics
        stats = self.simulation.get_statistics()

        # Update step counter
        self.step_counter.config(text=str(self.simulation.step_count))

        # Update treasure values
        self.bronze_value.config(text=f"{stats['treasure_collected'].get(TreasureType.BRONZE, 0.0):.1f}")
        self.silver_value.config(text=f"{stats['treasure_collected'].get(TreasureType.SILVER, 0.0):.1f}")
        self.gold_value.config(text=f"{stats['treasure_collected'].get(TreasureType.GOLD, 0.0):.1f}")
        self.total_value.config(text=f"{stats['treasure_collected']['total']:.1f}")

        # Update hunter stats
        self.remain_hunter_value.config(text=str(stats['remaining_hunters']))
        self.lost_hunter_value.config(text=str(stats['hunters_lost']))
        self.recruit_hunter_value.config(text=str(stats['hunters_recruited']))
        self.stamina_value.config(text=f"{stats['average_hunter_stamina']:.1f}%")

        # Update status
        if self.simulation.is_complete:
            self.status_value.config(text="Complete", fg="#8B0000")
            self.completion_value.config(text=self.simulation.get_completion_reason())
            self.completion_frame.pack(fill=tk.X, pady=5)
        elif self.simulation.is_running:
            self.status_value.config(text="Running", fg="#228B22")
            self.completion_frame.pack_forget()
        else:
            self.status_value.config(text="Paused", fg="#FFA500")
            self.completion_frame.pack_forget()