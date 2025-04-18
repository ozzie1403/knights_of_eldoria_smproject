# src/backend/services/movement_service.py

from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter

class MovementService:
    @staticmethod
    def move_hunter(hunter: TreasureHunter, direction: str, grid: Grid):
        """Moves hunter in a specified direction manually (used for player control)."""
        if direction in ["up", "down", "left", "right"]:
            hunter.move(direction, grid)
