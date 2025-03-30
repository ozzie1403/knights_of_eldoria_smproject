import pytest
from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.treasure import Treasure, TreasureType
from src.backend.models.hideout import Hideout


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

    # Place treasure on grid
    grid.place_treasure(treasure)

    # Hunter picks up treasure
    hunter.pick_up_treasure(grid)

    # Assertions
    assert hunter.carrying_treasure is not None, "Hunter should have picked up the treasure."
    assert isinstance(hunter.carrying_treasure, Treasure), "Hunter should be carrying a Treasure object."
    assert hunter.carrying_treasure.position == (5, 5), "Hunter should be carrying the correct treasure."
    assert grid.get_treasure_at(5, 5) is None, "Treasure should be removed from the grid."

def test_hunter_drop_treasure():
    hunter = TreasureHunter("Hunter1", (5, 5))
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    hunter.carrying_treasure = treasure

    hunter.drop_treasure()
    assert hunter.carrying_treasure is None, "Hunter should have dropped the treasure."


def test_hunter_rest():
    hunter = TreasureHunter("Hunter1", (5, 5), stamina=50)

    hunter.rest()
    assert hunter.stamina == 51, "Hunter's stamina should increase by 1."


def test_hunter_deposit_treasure():
    hunter = TreasureHunter("Hunter1", (5, 5))
    hideout = Hideout(5, 5)  # Ensure correct instantiation
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    hunter.carrying_treasure = treasure

    hunter.deposit_treasure(hideout)
    assert treasure in hideout.stored_treasures, "Treasure should be stored in the hideout."
    assert hunter.carrying_treasure is None, "Hunter should have deposited the treasure."
