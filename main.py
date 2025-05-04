import argparse
import time
import sys
import tkinter as tk
from tkinter import ttk
from models.simulation import Simulation, SimulationState
from models.enums import CellType, TreasureType, HunterState

def validate_size(size: int) -> int:
    """Validate and return the grid size."""
    if size < 20:
        print(f"Warning: Minimum grid size is 20. Adjusting size from {size} to 20.")
        return 20
    return size

def validate_delay(delay: float) -> float:
    """Validate and return the delay value."""
    if delay < 0:
        print(f"Warning: Delay cannot be negative. Setting delay to 0.")
        return 0
    return delay

def print_grid(simulation):
    """Print the current state of the grid with plain symbols."""
    try:
        state = simulation.get_simulation_state()
        grid_contents = state['grid_contents']
        
        # Print grid without numbers or colors
        for row in grid_contents:
            for cell in row:
                symbol = cell['symbol']
                print(symbol, end=" ")
            print()
        print()
    except Exception as e:
        print(f"Error displaying grid: {str(e)}")
        return False
    return True

def print_status(simulation):
    """Print current simulation statistics."""
    try:
        state = simulation.get_simulation_state()
        metrics = simulation.get_success_metrics()
        
        print(f"\nStep: {int(state['step'])}")
        print(f"Active Hunters: {state['active_hunters']}")
        print(f"Treasure Collected: {metrics['collected_treasure']:.2f}")
        print(f"Collection Efficiency: {metrics['collection_efficiency']:.2f}%")
        print(f"Hunter Survival Rate: {metrics['hunter_survival_rate']:.2f}%")
        print("-" * 40)
    except Exception as e:
        print(f"Error displaying status: {str(e)}")
        return False
    return True

def print_final_report(simulation):
    """Print the final simulation report."""
    try:
        report = simulation.get_final_report()
        print("\nFinal Report:")
        print(f"Simulation completed after {report['total_steps']} steps")
        print(f"Reason: {report['completion_reason']}")
        print("\nSuccess Metrics:")
        metrics = report['success_metrics']
        print(f"Total Treasure: {metrics['total_treasure']:.2f}")
        print(f"Collected Treasure: {metrics['collected_treasure']:.2f}")
        print(f"Collection Efficiency: {metrics['collection_efficiency']:.2f}%")
        print(f"Hunter Survival Rate: {metrics['hunter_survival_rate']:.2f}%")
        print(f"Average Treasure per Hunter: {metrics['avg_treasure_per_hunter']:.2f}")
    except Exception as e:
        print(f"Error displaying final report: {str(e)}")

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    if sys.platform.startswith('win'):
        import os
        os.system('cls')
    else:
        print("\033[H\033[J", end="")

class SimulationGUI:
    def __init__(self, root, simulation, delay=0.5):
        self.root = root
        self.simulation = simulation
        self.delay = delay
        self.is_running = False
        
        # Configure the main window
        self.root.title("Knights of Eldoria Simulation")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create grid canvas
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.grid(row=0, column=0, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=400, height=400, bg='white')
        self.canvas.grid(row=0, column=0)
        
        # Create status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status labels
        self.step_label = ttk.Label(self.status_frame, text="Step: 0")
        self.step_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.hunters_label = ttk.Label(self.status_frame, text="Active Hunters: 0")
        self.hunters_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.efficiency_label = ttk.Label(self.status_frame, text="Collection Efficiency: 0.00%")
        self.efficiency_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.survival_label = ttk.Label(self.status_frame, text="Hunter Survival Rate: 0.00%")
        self.survival_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Add legend section
        legend_frame = ttk.LabelFrame(self.status_frame, text="Legend", padding="5")
        legend_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Treasure types and their wealth increase
        ttk.Label(legend_frame, text="Treasure Types:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(legend_frame, text="Bronze (+3% wealth)", foreground='#CD7F32').grid(row=1, column=0, sticky=tk.W)
        ttk.Label(legend_frame, text="Silver (+7% wealth)", foreground='#C0C0C0').grid(row=2, column=0, sticky=tk.W)
        ttk.Label(legend_frame, text="Gold (+13% wealth)", foreground='#FFD700').grid(row=3, column=0, sticky=tk.W)
        
        # Treasure degradation
        ttk.Label(legend_frame, text="\nTreasure Degradation:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(legend_frame, text="• All treasures lose 0.1% value per step").grid(row=5, column=0, sticky=tk.W)
        ttk.Label(legend_frame, text="• Treasures are removed when value reaches 0").grid(row=6, column=0, sticky=tk.W)
        
        # Treasure deposited
        ttk.Label(legend_frame, text="\nTreasure Deposited:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=2)
        self.deposited_bronze_label = ttk.Label(legend_frame, text="Bronze: 0", foreground='#CD7F32')
        self.deposited_bronze_label.grid(row=8, column=0, sticky=tk.W)
        self.deposited_silver_label = ttk.Label(legend_frame, text="Silver: 0", foreground='#C0C0C0')
        self.deposited_silver_label.grid(row=9, column=0, sticky=tk.W)
        self.deposited_gold_label = ttk.Label(legend_frame, text="Gold: 0", foreground='#FFD700')
        self.deposited_gold_label.grid(row=10, column=0, sticky=tk.W)
        
        # Control buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(self.button_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.step_button = ttk.Button(self.button_frame, text="Step", command=self.single_step)
        self.step_button.grid(row=0, column=2, padx=5)
        
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=3, padx=5)
        
        # Cell colors
        self.colors = {
            'H': '#00FF00',  # Green for hunters
            'T_bronze': '#CD7F32',  # Bronze treasure
            'T_silver': '#C0C0C0',  # Silver treasure
            'T_gold': '#FFD700',    # Gold treasure
            'O': '#0000FF',  # Blue for hideouts
            '.': '#FFFFFF'   # White for empty
        }
        
        # Initialize the display
        self.update_display()
    
    def draw_grid(self):
        """Draw the current state of the grid in a clean, uniform way."""
        self.canvas.delete("all")
        cell_width = self.canvas.winfo_width() / self.simulation.size
        cell_height = self.canvas.winfo_height() / self.simulation.size
        font_main = ("Arial", int(min(cell_width, cell_height) * 0.5), "bold")

        for y in range(self.simulation.size):
            for x in range(self.simulation.size):
                x1 = x * cell_width
                y1 = y * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                cell_info = self.simulation.grid.get_grid_contents(x, y)
                cell_type = cell_info['type']

                # Set background color by cell type
                if cell_type == CellType.EMPTY.value:
                    fill_color = "white"
                    text = ""
                elif cell_type == CellType.TREASURE_HUNTER.value:
                    fill_color = "#00FF00"  # Green for hunters
                    text = "H"
                elif cell_type == CellType.TREASURE.value:
                    treasure_type = cell_info.get('treasure_type', TreasureType.BRONZE.value)
                    if treasure_type == TreasureType.BRONZE.value:
                        fill_color = "#CD7F32"
                    elif treasure_type == TreasureType.SILVER.value:
                        fill_color = "#C0C0C0"
                    else:
                        fill_color = "#FFD700"
                    # Display the current value as a whole number (no decimal)
                    text = f"{int(cell_info.get('value', 0))}"
                elif cell_type == CellType.HIDEOUT.value:
                    fill_color = "#3399FF"  # Blue for hideout
                    text = "O"
                else:
                    fill_color = "gray"
                    text = ""

                # Draw cell background
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

                # Draw centered text if needed
                if text:
                    self.canvas.create_text(
                        x1 + cell_width/2, y1 + cell_height/2,
                        text=text, font=font_main
                    )

    def update_status(self):
        """Update the status labels with current simulation state."""
        try:
            # Get current simulation state
            state = self.simulation.get_simulation_state()
            metrics = self.simulation.get_success_metrics()
            
            # Update basic status labels
            self.step_label.config(text=f"Step: {int(state['step'])}")
            self.hunters_label.config(text=f"Active Hunters: {state['active_hunters']}")
            self.efficiency_label.config(text=f"Collection Efficiency: {metrics['collection_efficiency']:.2f}%")
            self.survival_label.config(text=f"Hunter Survival Rate: {metrics['hunter_survival_rate']:.2f}%")
            
            # Update deposited treasure counts in the legend dynamically
            deposited = metrics.get('deposited_treasure', {'bronze': 0, 'silver': 0, 'gold': 0})
            self.deposited_bronze_label.config(text=f"Bronze: {deposited.get('bronze', 0)}")
            self.deposited_silver_label.config(text=f"Silver: {deposited.get('silver', 0)}")
            self.deposited_gold_label.config(text=f"Gold: {deposited.get('gold', 0)}")
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
    
    def update_display(self):
        """Update both grid and status display."""
        self.draw_grid()
        self.update_status()
    
    def start_simulation(self):
        """Start the simulation."""
        self.is_running = True
        self.simulation.state = SimulationState.RUNNING
        self.run_simulation()
    
    def pause_simulation(self):
        """Pause the simulation."""
        self.is_running = False
        self.simulation.state = SimulationState.PAUSED
    
    def single_step(self):
        """Perform a single simulation step."""
        if self.simulation.state != SimulationState.RUNNING:
            self.simulation.step()
            self.update_display()
    
    def run_simulation(self):
        """Run the simulation step by step"""
        if self.is_running and self.simulation.state == SimulationState.RUNNING:
            print(f"[DEBUG][GUI] Running simulation step {self.simulation.current_step}")
            self.simulation.step()
            self.update_display()
            self.root.after(1000, self.run_simulation)  # Schedule next step
        elif self.simulation.state in [SimulationState.TREASURE_DEPLETED,
                                     SimulationState.HUNTERS_ELIMINATED,
                                     SimulationState.COMPLETED]:
            self.is_running = False
            self.show_final_report()
    
    def show_final_report(self):
        """Show the final simulation report."""
        try:
            report = self.simulation.get_final_report()
            metrics = report['success_metrics']
            
            # Create a new window for the final report
            report_window = tk.Toplevel(self.root)
            report_window.title("Simulation Final Report")
            report_window.geometry("400x300")
            
            # Add report content
            ttk.Label(report_window, text="Final Report", font=('Arial', 14, 'bold')).pack(pady=10)
            ttk.Label(report_window, text=f"Simulation completed after {report['total_steps']} steps").pack()
            ttk.Label(report_window, text=f"Reason: {report['completion_reason']}").pack(pady=5)
            
            ttk.Label(report_window, text="Success Metrics:", font=('Arial', 12, 'bold')).pack(pady=5)
            ttk.Label(report_window, text=f"Total Treasure: {metrics['total_treasure']:.2f}").pack()
            ttk.Label(report_window, text=f"Collected Treasure: {metrics['collected_treasure']:.2f}").pack()
            ttk.Label(report_window, text=f"Collection Efficiency: {metrics['collection_efficiency']:.2f}%").pack()
            ttk.Label(report_window, text=f"Hunter Survival Rate: {metrics['hunter_survival_rate']:.2f}%").pack()
            ttk.Label(report_window, text=f"Average Treasure per Hunter: {metrics['avg_treasure_per_hunter']:.2f}").pack()
            
        except Exception as e:
            print(f"Error showing final report: {str(e)}")

    def reset_simulation(self):
        """Reset the simulation to its initial state."""
        self.is_running = False
        # Recreate the simulation object with the same size
        self.simulation = Simulation(self.simulation.size)
        self.update_display()

def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Knights of Eldoria Simulation')
        parser.add_argument('--size', type=int, default=20,
                           help='Size of the grid (minimum 20, default: 20)')
        parser.add_argument('--delay', type=float, default=0.5,
                           help='Delay between steps in seconds (default: 0.5)')
        args = parser.parse_args()
        
        # Validate input parameters
        size = max(20, args.size)
        delay = max(0, args.delay)
        
        # Create and initialize simulation
        print("Initializing Knights of Eldoria simulation...")
        simulation = Simulation(size=size)
        
        # Create and run the GUI
        root = tk.Tk()
        app = SimulationGUI(root, simulation, delay)
        root.mainloop()
        
    except Exception as e:
        print(f"\nError: An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 