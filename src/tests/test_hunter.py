import pytest
from backend.models.grid import Grid
from backend.models.hunter import TreasureHunter
from backend.models.treasure import Treasure, TreasureType
from backend.models.hideout import Hideout


def test_hunter_movement():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))

    hunter.move("up", grid)
    assert hunter.position == (5, 4)

    hunter.move("left", grid)
    assert hunter.position == (4, 4)


def test_hunter_pick_up_treasure():
    grid = Grid(10)
    hunter = TreasureHunter("Hunter1", (5, 5))
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    grid.cells[5][5] = treasure

    hunter.pick_up_treasure(grid)
    assert hunter.carrying_treasure == treasure
    assert grid.get_treasure_at(5, 5) is None


def test_hunter_drop_treasure():
    hunter = TreasureHunter("Hunter1", (5, 5))
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    hunter.carrying_treasure = treasure

    hunter.drop_treasure()
    assert hunter.carrying_treasure is None


def test_hunter_rest():
    hunter = TreasureHunter("Hunter1", (5, 5), stamina=50)

    hunter.rest()
    assert hunter.stamina == 51


def test_hunter_deposit_treasure():
    hunter = TreasureHunter("Hunter1", (5, 5))
    hideout = Hideout(5, 5)
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    hunter.carrying_treasure = treasure

    hunter.deposit_treasure(hideout)
    assert treasure in hideout.stored_treasures
    assert hunter.carrying_treasure is None
