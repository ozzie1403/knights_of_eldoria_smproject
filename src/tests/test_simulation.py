import unittest
from src.core.grid import Grid, Position
from src.core.treasure import Treasure, TreasureType
from src.core.hunter import Hunter
from src.core.hideout import Hideout
from src.core.simulation import Simulation

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.simulation = Simulation(grid_size=20, num_hunters=3, num_treasures=10, num_hideouts=2)

    def test_treasure_decay(self):
        """Test that treasure values decay correctly."""
        treasure = Treasure(Position(0, 0), TreasureType.GOLD)
        initial_value = treasure.value
        treasure.decay()
        self.assertEqual(treasure.value, initial_value - 0.1)

    def test_treasure_depletion(self):
        """Test that treasures are removed when depleted."""
        treasure = Treasure(Position(0, 0), TreasureType.GOLD)
        treasure.value = 0.1
        treasure.decay()
        self.assertTrue(treasure.is_depleted())

    def test_hunter_movement(self):
        """Test hunter movement and stamina depletion."""
        hunter = Hunter(Position(0, 0))
        initial_stamina = hunter.stamina
        hunter.move(Position(1, 0))
        self.assertEqual(hunter.stamina, initial_stamina - 2.0)
        self.assertEqual(hunter.position, Position(1, 0))

    def test_hunter_resting(self):
        """Test hunter resting in hideout."""
        hunter = Hunter(Position(0, 0))
        hunter.stamina = 5.0  # Below rest threshold
        initial_stamina = hunter.stamina
        hunter.rest()
        self.assertEqual(hunter.stamina, initial_stamina + 1.0)

    def test_hunter_collapse(self):
        """Test hunter collapse after stamina depletion."""
        hunter = Hunter(Position(0, 0))
        hunter.stamina = 1.0
        hunter.move(Position(1, 0))
        self.assertTrue(hunter.is_collapsed)

    def test_treasure_collection(self):
        """Test treasure collection and deposit."""
        hunter = Hunter(Position(0, 0))
        treasure = Treasure(Position(0, 0), TreasureType.GOLD)
        self.assertTrue(hunter.pick_up_treasure(treasure))
        self.assertEqual(hunter.carrying_treasure, treasure)
        
        deposited = hunter.deposit_treasure()
        self.assertEqual(deposited, treasure)
        self.assertIsNone(hunter.carrying_treasure)

    def test_hideout_capacity(self):
        """Test hideout hunter capacity."""
        hideout = Hideout(Position(0, 0))
        for _ in range(hideout.max_hunters):
            self.assertTrue(hideout.can_accommodate())
            hunter = Hunter(Position(0, 0))
            self.assertTrue(hideout.add_hunter(hunter))
        
        self.assertFalse(hideout.can_accommodate())
        hunter = Hunter(Position(0, 0))
        self.assertFalse(hideout.add_hunter(hunter))

if __name__ == '__main__':
    unittest.main() 