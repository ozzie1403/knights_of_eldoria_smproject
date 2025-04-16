# src/backend/models/simulation.py

import random
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight
from src.backend.models.treasure import TreasureType
from src.backend.models.hideout import Hideout
from src.backend.services.ai_service import AIService


class Simulation:
    def __init__(self, grid_size=20, num_hunters=3, num_knights=2, num_treasures=10, num_hideouts=2):
        self.grid = Grid(grid_size)
        self.hunters = [TreasureHunter(f"Hunter{i+1}", self._random_position()) for i in range(num_hunters)]
        self.knights = [Knight(self._random_position()) for _ in range(num_knights)]
        self.hideouts = [Hideout(*self._random_position()) for _ in range(num_hideouts)]
        self.grid.place_treasure(count=num_treasures)
        self.step_counter = 0

    def _random_position(self) -> tuple[int, int]:
        return (random.randint(0, self.grid.size - 1), random.randint(0, self.grid.size - 1))

    def run_step(self):
        self.step_counter += 1

        # AI for hunters
        for hunter in self.hunters:
            if hunter.carrying_treasure:
                # Move towards nearest hideout
                target = min(self.hideouts, key=lambda h: self._manhattan_distance(hunter.position, h.position)).position
                AIService.move_towards(hunter, target, self.grid)
                if hunter.position == target:
                    for hideout in self.hideouts:
                        if hideout.position == hunter.position:
                            hunter.deposit_treasure(hideout)
            else:
                AIService.move_hunter_towards_treasure(hunter, self.grid)
                hunter.pick_up_treasure(self.grid)

        # Knights patrol and chase
        for knight in self.knights:
            AIService.move_knight_towards_hunter(knight, self.hunters, self.grid)
            for hunter in self.hunters:
                knight.attack(hunter)

        # Regenerate stamina/energy
        for hunter in self.hunters:
            for hideout in self.hideouts:
                if hunter.position == hideout.position:
                    hunter.rest()

        for knight in self.knights:
            knight.rest()

        # Decay and remove depleted treasures
        self.grid.update_treasures()

    def _manhattan_distance(self, pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_state(self) -> dict:
        return {
            "step": self.step_counter,
            "hunters": [{"name": h.name, "position": h.position, "stamina": h.stamina} for h in self.hunters],
            "knights": [{"position": k.position, "energy": k.energy} for k in self.knights],
            "treasures": [
                {"position": (x, y), "type": t.treasure_type.name, "value": t.value}
                for x in range(self.grid.size)
                for y in range(self.grid.size)
                for t in self.grid.get_treasure_at(x, y)
            ]
        }
