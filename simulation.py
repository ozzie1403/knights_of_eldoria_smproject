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
from entities.base_entity import EntityType


class Simulation:
    def __init__(self, width: int = 20, height: int = 20):
        """Initialize the simulation with a grid of specified size"""
        self.grid = EldoriaGrid(width, height)
        self.hunters: List[Hunter] = []
        self.hideouts: List[Hideout] = []
        self.knights: List[Knight] = []
        self.fixed_hideout_positions = [
            (width // 4, height // 4),
            (3 * width // 4, 3 * height // 4),
            (width // 4, 3 * height // 4),
            (3 * width // 4, height // 4)
        ]

    def setup(self, num_hunters: int = 3, num_hideouts: int = 2, num_knights: int = 0, num_treasures: int = 10):
        """Setup the simulation with initial entities"""
        # Create hideouts at fixed positions
        for pos in self.fixed_hideout_positions[:num_hideouts]:
            hideout = Hideout(pos, grid=self.grid)
            self.hideouts.append(hideout)
            self.grid.add_entity(hideout)

        # Create hunters
        for _ in range(num_hunters):
            # Start hunters at random hideout
            start_hideout = random.choice(self.hideouts)
            hunter = Hunter(start_hideout.position)
            self.hunters.append(hunter)
            self.grid.add_entity(hunter)
            # Share initial knowledge
            start_hideout.share_knowledge(hunter)

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

    def run(self, steps: int = 100):
        """Run the simulation for a specified number of steps"""
        for step in range(steps):
            print(f"\nStep {step + 1}:")
            print(self.grid)

            # Update treasure values and remove depleted ones
            self._update_treasures()

            # Move hunters
            for hunter in self.hunters[:]:
                if hunter.is_collapsed():
                    print(f"Hunter at {hunter.position} has collapsed and is removed.")
                    self.grid.remove_entity(hunter)
                    self.hunters.remove(hunter)
                    continue
                grid_size = (self.grid.width, self.grid.height)
                # If stamina is 0, handle collapse countdown
                if hunter.stamina <= 0.0:
                    hunter.step_collapse()
                    continue
                # Check if hunter is at a hideout
                current_hideout = next((h for h in self.hideouts if h.position == hunter.position), None)
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
                        new_pos = hunter.move_towards(nearest_hideout, grid_size)
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
                        new_pos = hunter.move_towards(nearest_hideout, grid_size)
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
                        new_pos = hunter.move_towards(most_valuable.position, grid_size)
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
                                    new_pos = hunter.move_towards(nearest_hideout, grid_size)
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

            # If running a single step, return after completing it
            if steps == 1:
                return

    def cleanup(self):
        """Clean up the simulation"""
        self.hunters.clear()
        self.hideouts.clear()
        self.knights.clear()
        self.grid = None

    def _distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate the shortest distance between two positions considering grid wrapping"""
        x1, y1 = pos1
        x2, y2 = pos2
        dx = min(abs(x1 - x2), self.grid.width - abs(x1 - x2))
        dy = min(abs(y1 - y2), self.grid.height - abs(y1 - y2))
        return dx + dy


if __name__ == "__main__":
    # Create and run the simulation
    sim = Simulation(width=20, height=20)
    sim.setup(num_hunters=3, num_hideouts=2, num_knights=0, num_treasures=10)
    sim.run(steps=50)
    sim.cleanup()