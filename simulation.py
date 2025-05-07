import enum
import math
import os
import random
import sklearn
import tkinter as tk
import typing
from textblob import TextBlob
import unittest
import pytest
from typing import List, Tuple
from grid import EldoriaGrid
from entities.hunter import Hunter, HunterSkill
from entities.hideout import Hideout
from entities.knight import Knight
from entities.treasure import Treasure
from entities.garrison import Garrison
from entities.base_entity import EntityType


class Simulation:
    def __init__(self, width: int = 20, height: int = 20):
        """Initialize the simulation with a grid of specified size"""
        self.grid = EldoriaGrid(width, height)
        self.hunters: List[Hunter] = []
        self.hideouts: List[Hideout] = []
        self.knights: List[Knight] = []
        self.garrisons: List[Garrison] = []
        self.fixed_hideout_positions = [
            (width // 4, height // 4),
            (3 * width // 4, 3 * height // 4),
            (width // 4, 3 * height // 4),
            (3 * width // 4, height // 4)
        ]
        self.fixed_garrison_positions = [
            (width // 2, height // 4),
            (width // 2, 3 * height // 4),
            (width // 4, height // 2),
            (3 * width // 4, height // 2)
        ]

    def setup(self, num_hunters: int = 3, num_hideouts: int = 2, num_knights: int = 2, num_treasures: int = 10,
              num_garrisons: int = 2):
        """Setup the simulation with initial entities"""
        # Create hideouts at fixed positions
        for pos in self.fixed_hideout_positions[:num_hideouts]:
            hideout = Hideout(pos, grid=self.grid)
            self.hideouts.append(hideout)
            self.grid.add_entity(hideout)

        # Create garrisons at fixed positions
        for pos in self.fixed_garrison_positions[:num_garrisons]:
            garrison = Garrison(pos)
            self.garrisons.append(garrison)
            self.grid.add_entity(garrison)

        # Create hunters
        for _ in range(num_hunters):
            # Start hunters at random hideout
            start_hideout = random.choice(self.hideouts)
            hunter = Hunter(start_hideout.position)
            self.hunters.append(hunter)
            self.grid.add_entity(hunter)
            # Share initial knowledge
            start_hideout.share_knowledge(hunter)

        # Create knights
        for _ in range(num_knights):
            # Start knights at random garrison
            start_garrison = random.choice(self.garrisons)
            knight = Knight(start_garrison.position)
            self.knights.append(knight)
            self.grid.add_entity(knight)
            # Set up patrol route
            patrol_route = [
                (knight.position[0], knight.position[1]),
                ((knight.position[0] + 5) % self.grid.width, knight.position[1]),
                ((knight.position[0] + 5) % self.grid.width, (knight.position[1] + 5) % self.grid.height),
                (knight.position[0], (knight.position[1] + 5) % self.grid.height)
            ]
            knight.set_patrol_route(patrol_route)

        # Generate treasures
        self.grid.generate_random_treasure(num_treasures)

    def _update_treasures(self) -> None:
        """Update all treasures, decaying their value and removing depleted ones"""
        treasures = self.grid.entities[EntityType.TREASURE].copy()
        for treasure in treasures:
            if treasure.decay_value():
                # Remove depleted treasure
                self.grid.remove_entity(treasure)

    def _find_nearest(self, pos: Tuple[int, int], targets: List[Tuple[int, int]], grid_size: Tuple[int, int]) -> Tuple[
        int, int]:
        if not targets:
            return pos

        def dist(a, b):
            x1, y1 = a
            x2, y2 = b
            dx = min(abs(x1 - x2), grid_size[0] - abs(x1 - x2))
            dy = min(abs(y1 - y2), grid_size[1] - abs(y1 - y2))
            return dx + dy

        return min(targets, key=lambda t: dist(pos, t))

    def _recruit_hunter(self, hideout: Hideout):
        if not hideout.can_accommodate():
            return
        hunters_here = hideout.get_current_hunters()
        if len(hunters_here) < 5:
            skills = set(h.skill for h in hunters_here)
            if len(skills) > 1 and random.random() < 0.2:
                skill = random.choice(list(skills))
                new_hunter = Hunter(hideout.position, skill=skill)
                self.hunters.append(new_hunter)
                self.grid.add_entity(new_hunter)
                hideout.share_knowledge(new_hunter)  # Share knowledge with new recruit
                print(f"Recruitment: New hunter with skill {skill.value} at {hideout.position}")

    def _should_end_simulation(self) -> bool:
        """Check if the simulation should end"""
        # Check if there are no treasures left in the grid AND no hunters carrying treasures
        no_grid_treasures = not self.grid.entities[EntityType.TREASURE]
        no_carried_treasures = not any(hunter.carrying_treasure for hunter in self.hunters)

        if no_grid_treasures and no_carried_treasures:
            print("Simulation ended: All treasures have been collected and deposited")
            return True

        # Check if there are no hunters and no hideouts that can recruit new ones
        if not self.hunters:
            can_recruit = False
            for hideout in self.hideouts:
                if hideout.can_accommodate():
                    can_recruit = True
                    break
            if not can_recruit:
                print("Simulation ended: No hunters left and no hideouts can recruit new ones")
                return True

        return False

    def run(self, steps: int = 100):
        """Run the simulation for a specified number of steps"""
        grid_size = (self.grid.width, self.grid.height)

        for step in range(steps):
            # Check if simulation should end
            if self._should_end_simulation():
                return

            print(f"\nStep {step + 1}:")
            print(self.grid)

            # Update treasures
            self._update_treasures()

            # Update hunters
            for hunter in self.hunters[:]:  # Use a copy to allow removal
                if hunter.is_collapsed():
                    self.grid.remove_entity(hunter)
                    self.hunters.remove(hunter)
                    continue

                # Handle hunter movement and actions
                current_hideout = None
                for hideout in self.hideouts:
                    if hideout.position == hunter.position:
                        current_hideout = hideout
                        break

                # Try to retrieve lost treasure first
                if hunter.attempt_retrieval(self.grid, grid_size, step + 1):
                    hunter.update_stamina(moving=True, resting=False)
                    continue

                if current_hideout:
                    # Share knowledge with hideout
                    current_hideout.share_knowledge(hunter)
                    # If carrying treasure, deposit it
                    if hunter.carrying_treasure is not None:
                        current_hideout.deposit_treasure(hunter.drop_treasure())
                        print(f"Hunter at {hunter.position} dropped off treasure at hideout {hunter.position}")
                    # If stamina is low, start resting
                    if hunter.should_rest():
                        hunter.start_resting()
                        hunter.update_stamina(moving=False, resting=True)
                        if hunter.stamina >= 100.0:
                            hunter.stop_resting()
                        continue
                    # Check for recruitment opportunities
                    for other_hunter in self.hunters:
                        if (other_hunter.position == hunter.position and
                                other_hunter != hunter and
                                not other_hunter.carrying_treasure and
                                not other_hunter.resting and
                                not other_hunter.memory):
                            hunter.share_memory(other_hunter)
                # If stamina is low, go to nearest hideout
                if hunter.should_rest():
                    hideouts = list(hunter.memory_hideouts) or [h.position for h in self.hideouts]
                    nearest_hideout = self._find_nearest(hunter.position, hideouts, grid_size)
                    if hunter.position == nearest_hideout:
                        hunter.start_resting()
                        hunter.update_stamina(moving=False, resting=True)
                    else:
                        new_pos = hunter.move_towards(nearest_hideout, grid_size, self.grid)
                        self.grid.move_entity(hunter, new_pos)
                        hunter.update_stamina(moving=True, resting=False)
                    continue
                # If carrying treasure, return to nearest hideout
                if hunter.carrying_treasure:
                    hideouts = list(hunter.memory_hideouts) or [h.position for h in self.hideouts]
                    nearest_hideout = self._find_nearest(hunter.position, hideouts, grid_size)
                    if hunter.position == nearest_hideout:
                        # Deposit treasure
                        for hideout in self.hideouts:
                            if hideout.position == hunter.position:
                                hideout.deposit_treasure(hunter.drop_treasure())
                                print(f"Hunter at {hunter.position} dropped off treasure at hideout {hunter.position}")
                                break
                        hunter.update_stamina(moving=False, resting=False)
                    else:
                        new_pos = hunter.move_towards(nearest_hideout, grid_size, self.grid)
                        self.grid.move_entity(hunter, new_pos)
                        hunter.update_stamina(moving=True, resting=False)
                    continue
                # Scan for treasure
                treasures = hunter.scan_for_treasure(self.grid, grid_size, step + 1)
                if treasures:
                    # Pick up the most valuable one
                    most_valuable = max(treasures, key=lambda t: t.current_value)
                    # Move to that cell if not already there
                    if most_valuable.position != hunter.position:
                        new_pos = hunter.move_towards(most_valuable.position, grid_size, self.grid)
                        self.grid.move_entity(hunter, new_pos)
                        hunter.update_stamina(moving=True, resting=False)
                    else:
                        # Pick up treasure if not already carrying one
                        if hunter.carrying_treasure is None:  # Only try to collect if not already carrying treasure
                            if hunter.collect_treasure(most_valuable):
                                self.grid.remove_entity(most_valuable)
                                print(f"Hunter at {hunter.position} collected treasure at {most_valuable.position}")
                                # After collecting treasure, immediately head to nearest hideout
                                hideouts = list(hunter.memory_hideouts) or [h.position for h in self.hideouts]
                                nearest_hideout = self._find_nearest(hunter.position, hideouts, grid_size)
                                if hunter.position != nearest_hideout:
                                    new_pos = hunter.move_towards(nearest_hideout, grid_size, self.grid)
                                    self.grid.move_entity(hunter, new_pos)
                                    hunter.update_stamina(moving=True, resting=False)
                        hunter.update_stamina(moving=False, resting=False)
                    continue
                # Scan for hideouts
                hunter.scan_for_hideouts(self.grid, grid_size)
                # Update memory
                hunter.update_memory(step + 1)
                # Move randomly if nothing else to do
                dx, dy = random.choice(
                    [d for d in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]])
                new_pos = ((hunter.position[0] + dx) % self.grid.width, (hunter.position[1] + dy) % self.grid.height)
                self.grid.move_entity(hunter, new_pos)
                hunter.update_stamina(moving=True, resting=False)

            # Teamwork: recruitment at hideouts
            for hideout in self.hideouts:
                self._recruit_hunter(hideout)

            # Update knights
            for knight in self.knights:
                # Check if knight needs to retreat
                if knight.should_retreat():
                    if knight.retreat_to_garrison(self.grid, grid_size):
                        continue

                # Scan for hunters
                target_hunter = knight.scan_for_hunters(self.grid, grid_size)

                if target_hunter:
                    # Move towards the hunter
                    new_pos = knight.move_towards(target_hunter.position, grid_size, self.grid)
                    self.grid.move_entity(knight, new_pos)

                    # If knight catches the hunter
                    if knight.position == target_hunter.position:
                        print(f"Knight at {knight.position} caught hunter at {target_hunter.position}")
                        # Handle the caught hunter
                        hunter_removed, dropped_treasures = knight.handle_caught_hunter(target_hunter)

                        # Add any dropped treasures back to the grid and remember them
                        for treasure in dropped_treasures:
                            self.grid.add_entity(treasure)
                            target_hunter.remember_lost_treasure(treasure, step + 1)

                        # Remove hunter if they collapsed
                        if hunter_removed:
                            self.grid.remove_entity(target_hunter)
                            self.hunters.remove(target_hunter)
                else:
                    # Continue patrolling if no hunter detected
                    new_pos = knight.move_along_route(grid_size, self.grid)
                    self.grid.move_entity(knight, new_pos)

            # Update garrisons
            for garrison in self.garrisons:
                garrison.recover_knights()

            # If running a single step, return after completing it
            if steps == 1:
                return

    def cleanup(self):
        """Clean up the simulation"""
        self.hunters.clear()
        self.hideouts.clear()
        self.knights.clear()
        self.garrisons.clear()
        self.grid = None

    def _distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate the shortest distance between two positions considering grid wrapping"""
        x1, y1 = pos1
        x2, y2 = pos2
        dx = min(abs(x1 - x2), self.grid.width - abs(x1 - x2))
        dy = min(abs(y1 - y2), self.grid.height - abs(y1 - y2))
        return dx + dy

    def step(self) -> None:
        """Advance the simulation by one step"""
        # Update hunters first
        for hunter in self.hunters:
            if not hunter.is_detained:
                # Try to retrieve lost treasure first
                if hunter.attempt_retrieval(self.grid, self.grid_size):
                    continue

                # If at hideout, share knowledge and deposit treasure
                if self._is_at_hideout(hunter.position):
                    hunter.share_knowledge(self.hideouts)
                    if hunter.carried_treasure:
                        self.hideouts[0].deposit_treasure(hunter.carried_treasure)
                        hunter.carried_treasure = None
                        print(f"Hunter at {hunter.position} deposited treasure at hideout")
                    continue

                # Regular hunter behavior
                hunter.scan_for_treasure(self.grid, self.grid_size)
                hunter.move(self.grid_size)

        # Update knights
        for knight in self.knights:
            # Handle garrison retreat
            if knight.should_retreat():
                if knight.retreat_to_garrison(self.grid, self.grid_size):
                    continue

            # Regular knight behavior
            hunter = knight.scan_for_hunters(self.grid, self.grid_size)
            if hunter:
                knight.target_hunter = hunter
                new_pos = knight.move_towards(hunter.position, self.grid_size)
                if new_pos == hunter.position:
                    # Knight caught hunter
                    if hunter.carried_treasure:
                        # Remember lost treasure
                        hunter.remember_lost_treasure(hunter.carried_treasure)
                        # Add treasure back to grid
                        self.grid.add_entity(hunter.carried_treasure)
                        hunter.carried_treasure = None
                    # Detain or challenge hunter
                    if random.random() < knight.aggression:
                        hunter.is_detained = True
                        print(f"Hunter at {hunter.position} has been detained by knight")
                    else:
                        print(f"Hunter at {hunter.position} was challenged by knight but escaped")
                else:
                    knight.position = new_pos
            else:
                # Patrol behavior
                new_pos = knight.move_along_route(self.grid_size, self.grid)
                knight.position = new_pos

        # Update garrisons
        for garrison in self.garrisons:
            garrison.recover_knights()


if __name__ == "__main__":
    # Create and run the simulation
    sim = Simulation(width=20, height=20)
    sim.setup(num_hunters=3, num_hideouts=2, num_knights=2, num_treasures=10, num_garrisons=2)
    sim.run(steps=50)
    sim.cleanup()