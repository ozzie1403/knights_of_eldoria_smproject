# src/backend/services/ai_service.py

from typing import List, Optional
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight

class AIService:
    @staticmethod
    def find_nearest_treasure(hunter: TreasureHunter, grid: Grid) -> Optional[tuple[int, int]]:
        min_distance = float('inf')
        nearest = None
        for x in range(grid.size):
            for y in range(grid.size):
                treasures = grid.get_treasure_at(x, y)
                if treasures:
                    dist = abs(hunter.position[0] - x) + abs(hunter.position[1] - y)
                    if dist < min_distance:
                        min_distance = dist
                        nearest = (x, y)
        return nearest

    @staticmethod
    def move_hunter_towards_treasure(hunter: TreasureHunter, grid: Grid):
        if hunter.carrying_treasure is None:
            target = AIService.find_nearest_treasure(hunter, grid)
            if target:
                AIService.move_towards(hunter, target, grid)

    @staticmethod
    def move_knight_towards_hunter(knight: Knight, hunters: List[TreasureHunter], grid: Grid):
        min_distance = float('inf')
        nearest = None
        for h in hunters:
            dist = abs(knight.position[0] - h.position[0]) + abs(knight.position[1] - h.position[1])
            if dist <= 3 and dist < min_distance:
                min_distance = dist
                nearest = h
        if nearest:
            AIService.move_towards(knight, nearest.position, grid)

    @staticmethod
    def move_towards(entity, target: tuple[int, int], grid: Grid):
        x, y = entity.position
        tx, ty = target
        if x < tx: x += 1
        elif x > tx: x -= 1
        if y < ty: y += 1
        elif y > ty: y -= 1
        entity.position = grid.wrap_position(x, y)
