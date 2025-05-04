import argparse
import time
import sys
import tkinter as tk
from tkinter import ttk
from colorama import init, Fore, Style
from models.simulation import Simulation, SimulationState

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
    """Print the current state of the grid with colored entities."""
    try:
        state = simulation.get_simulation_state()
        grid_contents = state['grid_contents']
        
        # Print grid without numbers
        for row in grid_contents:
            for cell in row:
                symbol = cell['symbol']
                if symbol == 'H':  # Hunter
                    print(Fore.GREEN + "H" + Style.RESET_ALL, end=" ")
                elif symbol == 'T':  # Treasure
                    print(Fore.YELLOW + "T" + Style.RESET_ALL, end=" ")
                elif symbol == 'O':  # Hideout
                    print(Fore.BLUE + "O" + Style.RESET_ALL, end=" ")
                else:  # Empty
                    print(".", end=" ")
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
        
        self.treasure_label = ttk.Label(self.status_frame, text="Treasure Collected: 0.00")
        self.treasure_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.efficiency_label = ttk.Label(self.status_frame, text="Collection Efficiency: 0.00%")
        self.efficiency_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.survival_label = ttk.Label(self.status_frame, text="Hunter Survival Rate: 0.00%")
        self.survival_label.grid(row=4, column=0, sticky=tk.W, pady=2)
        
        # Control buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(self.button_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.step_button = ttk.Button(self.button_frame, text="Step", command=self.single_step)
        self.step_button.grid(row=0, column=2, padx=5)
        
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
        """Draw the current state of the grid on the canvas."""
        self.canvas.delete("all")
        
        try:
            state = self.simulation.get_simulation_state()
            grid_contents = state['grid_contents']
            
            # Calculate cell size based on canvas size and grid dimensions
            cell_size = min(400 // len(grid_contents[0]), 400 // len(grid_contents))
            
            # Draw grid
            for y, row in enumerate(grid_contents):
                for x, cell in enumerate(row):
                    # Calculate cell position
                    x1 = x * cell_size
                    y1 = y * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Get cell color
                    symbol = cell['symbol']
                    color = self.colors.get(symbol, '#FFFFFF')
                    # Special handling for treasures by type
                    if symbol == 'T':
                        treasure_type = cell.get('treasure_type')
                        if treasure_type == 0:  # Bronze
                            color = self.colors['T_bronze']
                        elif treasure_type == 1:  # Silver
                            color = self.colors['T_silver']
                        elif treasure_type == 2:  # Gold
                            color = self.colors['T_gold']
                    
                    # Draw cell
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')
        except Exception as e:
            print(f"Error drawing grid: {str(e)}")
    
    def update_status(self):
        """Update the status labels with current simulation state."""
        try:
            state = self.simulation.get_simulation_state()
            metrics = self.simulation.get_success_metrics()
            
            self.step_label.config(text=f"Step: {int(state['step'])}")
            self.hunters_label.config(text=f"Active Hunters: {state['active_hunters']}")
            self.treasure_label.config(text=f"Treasure Collected: {metrics['collected_treasure']:.2f}")
            self.efficiency_label.config(text=f"Collection Efficiency: {metrics['collection_efficiency']:.2f}%")
            self.survival_label.config(text=f"Hunter Survival Rate: {metrics['hunter_survival_rate']:.2f}%")
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
        """Run the simulation with the specified delay."""
        if self.is_running and self.simulation.state == SimulationState.RUNNING:
            self.simulation.step()
            self.update_display()
            # Schedule next step with delay
            self.root.after(int(self.delay * 1000), self.run_simulation)
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