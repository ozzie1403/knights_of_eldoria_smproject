# src/front_end/ui.py

import tkinter as tk
import requests

API_URL = "http://127.0.0.1:5000"

class GameUI:
    def __init__(self, master, simulation):
        self.master = master
        self.simulation = simulation
        self.running = False
        self.step_count = 0

        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack()

        self.control_frame = tk.Frame(master)
        self.control_frame.pack()

        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(master, text="Step: 0 | Hunters: 0 | Knights: 0 | Treasures: 0")
        self.status_label.pack()

        self.master.bind("<Up>", lambda e: self.manual_move("up"))
        self.master.bind("<Down>", lambda e: self.manual_move("down"))
        self.master.bind("<Left>", lambda e: self.manual_move("left"))
        self.master.bind("<Right>", lambda e: self.manual_move("right"))

        self.update_ui()

    def update_ui(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_entities()
        self.update_status()
        self.master.after(1000, self.update_ui)

    def draw_grid(self):
        size = 25
        for i in range(0, 500, size):
            self.canvas.create_line(i, 0, i, 500, fill="gray")
            self.canvas.create_line(0, i, 500, i, fill="gray")

    def draw_entities(self):
        try:
            response = requests.get(f"{API_URL}/state")
            response.raise_for_status()
            game_state = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game state: {e}")
            return

        size = 25
        for h in game_state.get("hunters", []):
            x, y = h["position"]
            self.canvas.create_oval(x*size, y*size, (x+1)*size, (y+1)*size, fill="blue")

        for k in game_state.get("knights", []):
            x, y = k["position"]
            self.canvas.create_rectangle(x*size, y*size, (x+1)*size, (y+1)*size, fill="red")

        for t in game_state.get("treasures", []):
            x, y = t["position"]
            self.canvas.create_oval(x*size, y*size, (x+1)*size, (y+1)*size, fill="gold")

    def update_status(self):
        try:
            response = requests.get(f"{API_URL}/state")
            game_state = response.json()
            self.status_label.config(
                text=f"Step: {game_state['step']} | Hunters: {len(game_state['hunters'])} | Knights: {len(game_state['knights'])} | Treasures: {len(game_state['treasures'])}"
            )
        except:
            self.status_label.config(text="Error fetching game state.")

    def start_simulation(self):
        requests.post(f"{API_URL}/start", json={"steps": 1})

    def pause_simulation(self):
        self.running = False

    def reset_simulation(self):
        requests.post(f"{API_URL}/reset")
        self.step_count = 0

    def manual_move(self, direction):
        requests.post(f"{API_URL}/move", json={"direction": direction})
