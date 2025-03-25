import pytest
from src.backend.models.treasure import Treasure, TreasureType

def test_treasure_initialization():
    treasure = Treasure(TreasureType.GOLD, (5, 5))
    assert treasure.treasure_type == TreasureType.GOLD
    assert treasure.value == 13  # Gold starts with 13% value
    assert treasure.position == (5, 5)

def test_treasure_decay():
    treasure = Treasure(TreasureType.SILVER, (3, 3))
    initial_value = treasure.value

    treasure.decay()
    assert treasure.value == initial_value - 0.1

def test_treasure_depletion():
    treasure = Treasure(TreasureType.BRONZE, (1, 1))
    treasure.value = 0.05  # Almost depleted

    treasure.decay()
    assert treasure.is_depleted()
