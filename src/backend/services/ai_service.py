import random
from typing import List, Optional
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight
from src.backend.models.treasure import Treasure


class AIService:
    @staticmethod
    def find_nearest_treasure(hunter: TreasureHunter, grid: Grid) -> Optional[tuple[int, int]]:
        """Finds the nearest treasure for the hunter."""
        min_distance = float('inf')
        nearest_treasure = None

        for x in range(grid.size):
            for y in range(grid.size):
                treasure = grid.get_treasure_at(x, y)
                if treasure:
                    distance = abs(hunter.position[0] - x) + abs(hunter.position[1] - y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_treasure = (x, y)

        return nearest_treasure

    @staticmethod
    def move_hunter_towards_treasure(hunter: TreasureHunter, grid: Grid):
        """Moves the hunter towards the nearest treasure."""
        if hunter.carrying_treasure is None:
            target = AIService.find_nearest_treasure(hunter, grid)
            if target:
                AIService.move_towards(hunter, target, grid)

    @staticmethod
    def move_towards(entity, target: tuple[int, int], grid: Grid):
        """Moves an entity (hunter/knight) one step towards a target."""
        x, y = entity.position
        tx, ty = target

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1

        entity.position = grid.wrap_position(x, y)

    @staticmethod
    def move_knight_towards_hunter(knight: Knight, hunters: List[TreasureHunter], grid: Grid):
        """Moves the knight towards the closest hunter if within a 3-cell radius."""
        min_distance = float('inf')
        nearest_hunter = None

        for hunter in hunters:
            distance = abs(knight.position[0] - hunter.position[0]) + abs(knight.position[1] - hunter.position[1])
            if distance <= 3 and distance < min_distance:
                min_distance = distance
                nearest_hunter = hunter

        if nearest_hunter:
            AIService.move_towards(knight, nearest_hunter.position, grid)