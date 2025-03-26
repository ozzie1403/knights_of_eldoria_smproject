import pytest
from src.backend.models.grid import Grid
from src.backend.models.knight import Knight
from src.backend.models.hunter import TreasureHunter


def test_knight_movement():
    grid = Grid(10)
    knight = Knight((2, 2))
    target_position = (5, 5)

    knight.move_towards(target_position, grid)
    assert knight.position in [(3, 2), (2, 3)]  # Moving towards (5,5)


def test_knight_attack_hunter():
    knight = Knight((5, 5))
    hunter = TreasureHunter("Hunter1", (5, 5), stamina=50)
    hunter.carrying_treasure = "Gold"

    knight.attack_hunter(hunter)
    assert hunter.stamina == 30  # Stamina reduced by 20
    assert hunter.carrying_treasure is None  # Treasure dropped


def test_knight_rest():
    knight = Knight((5, 5), energy=50)
    knight.rest()
    assert knight.energy == 60  # Energy increased by 10
