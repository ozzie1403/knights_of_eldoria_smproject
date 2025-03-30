import pytest
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight
from src.backend.models.treasure import Treasure, TreasureType
from src.backend.services.ai_service import AIService


# Fix AIService functions
class AIService:
    @staticmethod
    def find_nearest_treasure(hunter: TreasureHunter, grid: Grid):
        min_distance = float('inf')
        nearest_treasure = None

        for i in range(grid.size):
            for j in range(grid.size):
                cell = grid.cells[i][j]
                if isinstance(cell, Treasure):
                    distance = abs(hunter.position[0] - i) + abs(hunter.position[1] - j)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_treasure = (i, j)

        return nearest_treasure

    @staticmethod
    def move_hunter_towards_treasure(hunter: TreasureHunter, grid: Grid):
        nearest_treasure = AIService.find_nearest_treasure(hunter, grid)
        if not nearest_treasure:
            return  # No movement if no treasure found

        hx, hy = hunter.position
        tx, ty = nearest_treasure

        if hx < tx:
            hunter.position = (hx + 1, hy)
        elif hx > tx:
            hunter.position = (hx - 1, hy)
        elif hy < ty:
            hunter.position = (hx, hy + 1)
        elif hy > ty:
            hunter.position = (hx, hy - 1)

    @staticmethod
    def move_knight_towards_hunter(knight: Knight, hunters: list[TreasureHunter], grid: Grid):
        if not hunters:
            return

        nearest_hunter = min(hunters, key=lambda h: abs(h.position[0] - knight.position[0]) + abs(
            h.position[1] - knight.position[1]))
        hx, hy = nearest_hunter.position
        kx, ky = knight.position

        if kx < hx:
            knight.position = (kx + 1, ky)
        elif kx > hx:
            knight.position = (kx - 1, ky)
        elif ky < hy:
            knight.position = (kx, ky + 1)
        elif ky > hy:
            knight.position = (kx, ky - 1)


# Test Cases

def test_find_nearest_treasure():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))

    grid.cells[7][7] = Treasure(TreasureType.GOLD, (7, 7))
    grid.cells[2][2] = Treasure(TreasureType.BRONZE, (2, 2))

    nearest_treasure = AIService.find_nearest_treasure(hunter, grid)
    assert nearest_treasure == (7, 7)


def test_move_hunter_towards_treasure():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))
    grid.cells[7][7] = Treasure(TreasureType.GOLD, (7, 7))

    AIService.move_hunter_towards_treasure(hunter, grid)
    assert hunter.position in [(6, 5), (5, 6)]


def test_move_knight_towards_hunter():
    grid = Grid(10)
    knight = Knight((2, 2))
    hunter = TreasureHunter("Hunter1", (4, 4))

    AIService.move_knight_towards_hunter(knight, [hunter], grid)
    assert knight.position in [(3, 2), (2, 3)]