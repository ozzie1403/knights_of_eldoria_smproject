import unittest
from simulation import Simulation
from grid import EldoriaGrid
from entities.hunter import Hunter, HunterSkill
from entities.hideout import Hideout
from entities.treasure import Treasure, TreasureType
from entities.base_entity import EntityType


class TestEldoriaGrid(unittest.TestCase):
    def setUp(self):
        self.grid = EldoriaGrid(20, 20)
        self.hunter = Hunter((0, 0))
        self.treasure = Treasure((1, 1), TreasureType.GOLD)
        self.hideout = Hideout((2, 2))

    def test_add_entity(self):
        self.grid.add_entity(self.hunter)
        self.assertEqual(len(self.grid.get_entities_at((0, 0))), 1)
        self.assertEqual(len(self.grid.entities[EntityType.HUNTER]), 1)

    def test_remove_entity(self):
        self.grid.add_entity(self.hunter)
        self.grid.remove_entity(self.hunter)
        self.assertEqual(len(self.grid.get_entities_at((0, 0))), 0)
        self.assertEqual(len(self.grid.entities[EntityType.HUNTER]), 0)

    def test_move_entity(self):
        self.grid.add_entity(self.hunter)
        self.grid.move_entity(self.hunter, (1, 1))
        self.assertEqual(len(self.grid.get_entities_at((0, 0))), 0)
        self.assertEqual(len(self.grid.get_entities_at((1, 1))), 1)
        self.assertEqual(self.hunter.position, (1, 1))

    def test_generate_random_treasure(self):
        count = 5
        self.grid.generate_random_treasure(count)
        self.assertEqual(len(self.grid.entities[EntityType.TREASURE]), count)


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.sim = Simulation(20, 20)
        self.sim.setup(num_hunters=2, num_hideouts=1, num_knights=0, num_treasures=3)

    def test_initialization(self):
        self.assertEqual(len(self.sim.hunters), 2)
        self.assertEqual(len(self.sim.hideouts), 1)
        self.assertEqual(len(self.sim.grid.entities[EntityType.TREASURE]), 3)

    def test_treasure_decay(self):
        # Get initial treasure count
        initial_count = len(self.sim.grid.entities[EntityType.TREASURE])

        # Run simulation for enough steps to decay treasures
        self.sim.run(steps=50)

        # Verify some treasures were removed due to decay
        self.assertLess(len(self.sim.grid.entities[EntityType.TREASURE]), initial_count)

    def test_hunter_movement(self):
        initial_pos = self.sim.hunters[0].position
        self.sim.run(steps=1)
        self.assertNotEqual(self.sim.hunters[0].position, initial_pos)

    def test_hunter_treasure_collection(self):
        # Place a treasure near a hunter
        treasure = Treasure(self.sim.hunters[0].position, TreasureType.GOLD)
        self.sim.grid.add_entity(treasure)

        # Run one step
        self.sim.run(steps=1)

        # Verify hunter picked up the treasure
        self.assertTrue(self.sim.hunters[0].carrying_treasure is not None)

    def test_hunter_resting(self):
        # Exhaust hunter's stamina
        hunter = self.sim.hunters[0]
        hunter.stamina = 0

        # Run simulation
        self.sim.run(steps=1)

        # Verify hunter is resting
        self.assertTrue(hunter.resting)

    def test_hideout_treasure_deposit(self):
        # Make a hunter carry treasure
        hunter = self.sim.hunters[0]
        treasure = Treasure(hunter.position, TreasureType.GOLD)
        hunter.carrying_treasure = treasure

        # Move hunter to hideout
        hunter.position = self.sim.hideouts[0].position

        # Run one step
        self.sim.run(steps=1)

        # Verify treasure was deposited
        self.assertIsNone(hunter.carrying_treasure)
        self.assertEqual(len(self.sim.hideouts[0].stored_treasures), 1)

    def test_hunter_collapse(self):
        # Make a hunter collapse
        hunter = self.sim.hunters[0]
        hunter.stamina = 0
        hunter.collapse_countdown = 0

        # Run one step
        self.sim.run(steps=1)

        # Verify hunter was removed
        self.assertNotIn(hunter, self.sim.hunters)
        self.assertEqual(len(self.sim.grid.get_entities_at(hunter.position)), 0)

    def test_cleanup(self):
        self.sim.cleanup()
        self.assertEqual(len(self.sim.hunters), 0)
        self.assertEqual(len(self.sim.hideouts), 0)
        self.assertEqual(len(self.sim.knights), 0)
        self.assertIsNone(self.sim.grid)


if __name__ == '__main__':
    unittest.main()