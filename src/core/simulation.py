from typing import List, Optional, Dict, Set, Any, Union
from dataclasses import dataclass
import random
import math
from src.core.grid import Grid
from src.core.position import Position
from src.core.treasure import Treasure, TreasureType
from src.core.hunter import Hunter
from src.core.hideout import Hideout
from src.core.enums import EntityType, TreasureType, HunterSkill, KnightAction
from src.core.knight import Knight

class Simulation:
    def __init__(self, grid_size: int = 20, num_hunters: int = 3, num_treasures: int = 10, num_hideouts: int = 2, num_knights: int = 2):
        self.grid = Grid(grid_size)
        self.step_count = 0
        self.total_treasure_collected = 0
        self._nearest_cache: Dict[Position, Dict[str, Any]] = {}
        self.initialize_simulation(num_hunters, num_treasures, num_hideouts, num_knights)

    def initialize_simulation(self, num_hunters: int, num_treasures: int, num_hideouts: int, num_knights: int) -> None:
        """Initialize the simulation with hunters, treasures, hideouts, and knights."""
        # Place hideouts first
        for _ in range(num_hideouts):
            pos = self.grid.get_random_empty_position()
            if pos:
                hideout = Hideout(pos)
                self.grid.add_entity(hideout)

        # Place hunters in hideouts
        for _ in range(num_hunters):
            if self.grid.hideouts:
                hideout = random.choice(self.grid.hideouts)
                if hideout.can_accommodate():
                    hunter = Hunter(hideout.position)
                    if self.grid.add_entity(hunter):
                        hideout.add_hunter(hunter)

        # Place treasures with proper type distribution
        treasure_types = [TreasureType.BRONZE] * 4 + [TreasureType.SILVER] * 3 + [TreasureType.GOLD] * 3
        for _ in range(num_treasures):
            pos = self.grid.get_random_empty_position()
            if pos:
                treasure_type = random.choice(treasure_types)
                treasure = Treasure(pos, treasure_type)
                self.grid.add_entity(treasure)

        # Place knights
        for _ in range(num_knights):
            pos = self.grid.get_random_empty_position()
            if pos:
                knight = Knight(pos)
                self.grid.add_entity(knight)

    def validate_state(self) -> bool:
        # All entities in the grid must be in exactly one list
        all_entities = set(self.grid.entities.values())
        all_listed = set(self.grid.hunters + self.grid.knights + self.grid.treasures + self.grid.hideouts)
        # Check for missing or extra entities
        if all_entities != all_listed:
            print("Entity mismatch:", all_entities.symmetric_difference(all_listed))
            return False
        # Check for duplicates in lists
        for lst in [self.grid.hunters, self.grid.knights, self.grid.treasures, self.grid.hideouts]:
            if len(lst) != len(set(lst)):
                print("Duplicate entity in list detected")
                return False
        return True

    def update_treasures(self) -> None:
        """Update all treasures in the simulation."""
        treasures_to_remove: List[Position] = []
        for treasure in self.grid.treasures[:]:  # Create a copy of the list
            try:
                treasure.decay()
                if treasure.is_depleted():
                    treasures_to_remove.append(treasure.position)
            except Exception as e:
                print(f"Error updating treasure at {treasure.position}: {e}")
                treasures_to_remove.append(treasure.position)
        
        for pos in treasures_to_remove:
            try:
                self.grid.remove_entity(pos)
            except Exception as e:
                print(f"Error removing treasure at {pos}: {e}")

    def update_hunters(self) -> None:
        """Update all hunters in the simulation."""
        hunters_to_remove: List[Position] = []
        
        for hunter in self.grid.hunters[:]:  # Create a copy of the list
            try:
                if not hunter.can_move():
                    if hunter.is_collapsed and hunter.steps_since_collapse >= 3:
                        hunters_to_remove.append(hunter.position)
                    continue

                # Check if hunter needs to rest
                if hunter.needs_rest():
                    nearest_hideout = self.find_nearest_hideout(hunter.position)
                    if nearest_hideout:
                        self.move_towards(hunter, nearest_hideout.position)
                        if hunter.position == nearest_hideout.position:
                            hunter.rest()
                            continue

                # If carrying treasure, move to nearest hideout
                if hunter.carrying_treasure:
                    nearest_hideout = self.find_nearest_hideout(hunter.position)
                    if nearest_hideout:
                        self.move_towards(hunter, nearest_hideout.position)
                        if hunter.position == nearest_hideout.position:
                            hideout = self.grid.get_entity_at(nearest_hideout.position)
                            if isinstance(hideout, Hideout):
                                hideout.store_treasure(hunter.deposit_treasure())
                                self.total_treasure_collected += 1
                else:
                    # Look for nearest treasure
                    nearest_treasure = self.find_nearest_treasure(hunter.position)
                    if nearest_treasure:
                        self.move_towards(hunter, nearest_treasure.position)
                        if hunter.position == nearest_treasure.position:
                            treasure = self.grid.get_entity_at(nearest_treasure.position)
                            if isinstance(treasure, Treasure):
                                hunter.pick_up_treasure(treasure)
                                self.grid.remove_entity(treasure.position)
            except Exception as e:
                print(f"Error updating hunter at {hunter.position}: {e}")
                hunters_to_remove.append(hunter.position)

        # Remove collapsed hunters
        for pos in hunters_to_remove:
            try:
                self.grid.remove_entity(pos)
            except Exception as e:
                print(f"Error removing hunter at {pos}: {e}")

    def update_knights(self) -> None:
        """Update all knights in the simulation."""
        for knight in self.grid.knights[:]:  # Create a copy of the list
            try:
                if not knight.can_move():
                    if knight.is_resting:
                        knight.rest()
                    continue

                # Find nearest hunter
                nearest_hunter = self.find_nearest_hunter(knight.position)
                if nearest_hunter:
                    self.move_towards(knight, nearest_hunter.position)
                    if knight.position == nearest_hunter.position:
                        # Knight catches hunter
                        self.grid.remove_entity(nearest_hunter.position)
            except Exception as e:
                print(f"Error updating knight at {knight.position}: {e}")

    def move_towards(self, entity: Union[Hunter, Knight], target: Position) -> None:
        """Move an entity towards a target position."""
        try:
            current_pos = entity.position
            best_move = None
            min_dist = float('inf')

            for new_pos in self.grid.get_adjacent_positions(current_pos):
                if self.grid.get_entity_at(new_pos):
                    continue
                dist = new_pos.distance_to(target)
                if dist < min_dist:
                    min_dist = dist
                    best_move = new_pos

            if best_move:
                # Remove entity from current position
                if current_pos in self.grid.entities:
                    self.grid.entities.pop(current_pos)
                
                # Move entity to new position
                entity.move(best_move)
                self.grid.entities[best_move] = entity
        except Exception as e:
            print(f"Error moving entity from {current_pos} to {target}: {e}")

    def find_nearest_hideout(self, position: Position) -> Optional[Hideout]:
        """Find the nearest hideout to a position."""
        if not self.grid.hideouts:
            return None
        try:
            return min(self.grid.hideouts, key=lambda h: position.distance_to(h.position))
        except Exception as e:
            print(f"Error finding nearest hideout to {position}: {e}")
            return None

    def find_nearest_treasure(self, position: Position) -> Optional[Treasure]:
        """Find the nearest treasure to a position."""
        if not self.grid.treasures:
            return None
        try:
            return min(self.grid.treasures, key=lambda t: position.distance_to(t.position))
        except Exception as e:
            print(f"Error finding nearest treasure to {position}: {e}")
            return None

    def find_nearest_hunter(self, position: Position) -> Optional[Hunter]:
        """Find the nearest hunter to a position."""
        if not self.grid.hunters:
            return None
        try:
            return min(self.grid.hunters, key=lambda h: position.distance_to(h.position))
        except Exception as e:
            print(f"Error finding nearest hunter to {position}: {e}")
            return None

    def step(self) -> bool:
        """Perform one simulation step. Returns False if simulation should end."""
        try:
            self.step_count += 1

            # Prepare environment state for agent perception
            environment = self.get_state()
            # Add all hunter objects for swarm behavior
            environment['all_hunters'] = self.grid.hunters[:]

            # Hunters perceive and act
            for hunter in self.grid.hunters[:]:
                hunter.perceive(environment)
            # Multi-agent communication: broadcast warnings and hints
            for hunter in self.grid.hunters[:]:
                hunter.communicate(self.grid.hunters[:])
            # Bayesian update: update belief map
            for hunter in self.grid.hunters[:]:
                hunter.update_belief_map(self.grid.size)
            for hunter in self.grid.hunters[:]:
                action = hunter.act(environment)
                if action == 'rest':
                    hunter.rest()
                elif action == 'go_hideout':
                    nearest_hideout = self.find_nearest_hideout(hunter.position)
                    if nearest_hideout:
                        path = hunter.plan_path(nearest_hideout.position, self.grid)
                        if path and len(path) > 1:
                            self.move_towards(hunter, path[1])
                        else:
                            self.move_towards(hunter, nearest_hideout.position)
                        if hunter.position == nearest_hideout.position:
                            hunter.rest()
                elif action == 'avoid_knight':
                    visible_knights = hunter.knowledge.get('visible_knights', [])
                    if not visible_knights:
                        visible_knights = list(hunter.knowledge.get('warnings', []))
                    if visible_knights:
                        knight_pos = Position(visible_knights[0][0], visible_knights[0][1])
                        dx = hunter.position.x - knight_pos.x
                        dy = hunter.position.y - knight_pos.y
                        new_pos = self.grid.wrap_position(Position(hunter.position.x + (1 if dx <= 0 else -1), hunter.position.y + (1 if dy <= 0 else -1)))
                        if not self.grid.get_entity_at(new_pos):
                            self.grid.entities.pop(hunter.position, None)
                            hunter.move(new_pos)
                            self.grid.entities[new_pos] = hunter
                elif action == 'go_treasure':
                    visible_treasures = hunter.knowledge.get('visible_treasures', [])
                    if not visible_treasures:
                        visible_treasures = list(hunter.knowledge.get('treasure_hints', []))
                    if visible_treasures:
                        treasure_pos = Position(visible_treasures[0][0], visible_treasures[0][1])
                        path = hunter.plan_path(treasure_pos, self.grid)
                        if path and len(path) > 1:
                            self.move_towards(hunter, path[1])
                        else:
                            self.move_towards(hunter, treasure_pos)
                        if hunter.position == treasure_pos:
                            treasure = self.grid.get_entity_at(treasure_pos)
                            if treasure:
                                hunter.pick_up_treasure(treasure)
                                self.grid.remove_entity(treasure_pos)
                elif action == 'swarm':
                    swarm_pos = hunter.knowledge.get('swarm_target')
                    if swarm_pos:
                        self.move_towards(hunter, swarm_pos)
                else:  # explore
                    # Use Bayesian belief map to pick the most likely cell
                    belief_map = hunter.knowledge.get('belief_map')
                    if belief_map:
                        max_prob = 0.0
                        target = None
                        for x in range(self.grid.size):
                            for y in range(self.grid.size):
                                if belief_map[x][y] > max_prob:
                                    max_prob = belief_map[x][y]
                                    target = Position(x, y)
                        if target and max_prob > 0.2:
                            self.move_towards(hunter, target)
                            continue
                    adj = self.grid.get_adjacent_positions(hunter.position)
                    random.shuffle(adj)
                    for pos in adj:
                        if not self.grid.get_entity_at(pos):
                            self.grid.entities.pop(hunter.position, None)
                            hunter.move(pos)
                            self.grid.entities[pos] = hunter
                            break

            # Knights perceive and act
            for knight in self.grid.knights[:]:
                knight.perceive(environment)
                action = knight.act(environment)
                if action == 'rest':
                    knight.rest()
                elif action == 'pursue_hunter':
                    visible_hunters = knight.knowledge.get('visible_hunters', [])
                    if visible_hunters:
                        # Use adversarial search to predict hunter move
                        hunter_objs = [h for h in self.grid.hunters if (h.position.x, h.position.y) == (visible_hunters[0][0], visible_hunters[0][1])]
                        if hunter_objs:
                            predicted = knight.predict_hunter_move(hunter_objs, self.grid)
                            self.move_towards(knight, predicted)
                            if knight.position == predicted:
                                self.grid.remove_entity(predicted)
                        else:
                            hunter_pos = Position(visible_hunters[0][0], visible_hunters[0][1])
                            self.move_towards(knight, hunter_pos)
                            if knight.position == hunter_pos:
                                self.grid.remove_entity(hunter_pos)
                else:  # patrol
                    adj = self.grid.get_adjacent_positions(knight.position)
                    random.shuffle(adj)
                    for pos in adj:
                        if not self.grid.get_entity_at(pos):
                            self.grid.entities.pop(knight.position, None)
                            knight.move(pos)
                            self.grid.entities[pos] = knight
                            break

            # Update treasures (decay)
            self.update_treasures()

            # Validate state after updates
            if not self.validate_state():
                print("Invalid simulation state detected!")
                return False

            # Check end conditions
            if not self.grid.treasures:
                print("Simulation ended: No more treasures to collect")
                if self.grid.hunters:
                    self.evolve_hunters()
                return False

            if not self.grid.hunters:
                print("Simulation ended: All hunters eliminated")
                return False

            return True
        except Exception as e:
            print(f"Error in simulation step {self.step_count}: {e}")
            return False

    def get_state(self) -> Dict[str, Any]:
        """Return current simulation state for visualization."""
        try:
            return {
                'grid_size': self.grid.size,
                'step_count': self.step_count,
                'total_treasure_collected': self.total_treasure_collected,
                'treasures': [(t.position.x, t.position.y, t.treasure_type.name, t.value) for t in self.grid.treasures if isinstance(t, Treasure)],
                'hunters': [(h.position.x, h.position.y, h.stamina, h.is_collapsed) for h in self.grid.hunters if isinstance(h, Hunter)],
                'knights': [(k.position.x, k.position.y, k.stamina, k.is_resting) for k in self.grid.knights if isinstance(k, Knight)],
                'hideouts': [(h.position.x, h.position.y, len(h.hunters), len(h.stored_treasures)) for h in self.grid.hideouts if isinstance(h, Hideout)]
            }
        except Exception as e:
            print(f"Error getting simulation state: {e}")
            return {
                'grid_size': self.grid.size,
                'step_count': self.step_count,
                'total_treasure_collected': self.total_treasure_collected,
                'treasures': [],
                'hunters': [],
                'knights': [],
                'hideouts': []
            }

    def __repr__(self) -> str:
        return f"Simulation(grid={self.grid}, hunters={len(self.grid.hunters)}, treasures={len(self.grid.treasures)}, hideouts={len(self.grid.hideouts)})"

    def evolve_hunters(self):
        """Evolve hunter strategies using a simple genetic algorithm (placeholder)."""
        # Select top-performing hunters (e.g., those who collected treasure)
        top_hunters = sorted(self.grid.hunters, key=lambda h: h.stamina, reverse=True)[:max(1, len(self.grid.hunters)//2)]
        # Crossover and mutate to create new strategies
        new_strategies = []
        for _ in range(len(self.grid.hunters)):
            parent1 = random.choice(top_hunters).strategy
            parent2 = random.choice(top_hunters).strategy
            # Single-point crossover
            point = random.randint(1, len(parent1)-1)
            child = parent1[:point] + parent2[point:]
            # Mutation
            if random.random() < 0.2:
                idx = random.randint(0, len(child)-1)
                child[idx] += random.choice([-1, 1])
                child[idx] = max(1, child[idx])
            new_strategies.append(child)
        # Assign new strategies
        for h, strat in zip(self.grid.hunters, new_strategies):
            h.strategy = strat 