import pytest
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight
from src.backend.models.treasure import Treasure, TreasureType
from src.backend.services.ai_service import AIService

def test_find_nearest_treasure():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))

    # Place a treasure at (7,7) and (2,2)
    grid.cells[7][7] = Treasure(TreasureType.GOLD, (7, 7))
    grid.cells[2][2] = Treasure(TreasureType.BRONZE, (2, 2))

    nearest_treasure = AIService.find_nearest_treasure(hunter, grid)
    assert nearest_treasure == (7, 7)

def test_move_hunter_towards_treasure():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))
    grid.cells[7][7] = Treasure(TreasureType.GOLD, (7, 7))

    AIService.move_hunter_towards_treasure(hunter, grid)
    assert hunter.position in [(6, 5), (5, 6)]  # Moving towards (7,7)

def test_move_knight_towards_hunter():
    grid = Grid(10)
    knight = Knight((2, 2))
    hunter = TreasureHunter("Hunter1", (4, 4))

    AIService.move_knight_towards_hunter(knight, [hunter], grid)
    assert knight.position in [(3, 2), (2, 3)]  # Moving towards (4,4)
