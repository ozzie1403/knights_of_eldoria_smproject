from models.location import Location
from utils.helpers import calculate_wrapped_distance
import heapq


class AStarPathfinder:
    """A* pathfinding algorithm implementation for grid-based movement with wrap-around edges."""

    def __init__(self, grid):
        self.grid = grid

    def find_path(self, start: Location, goal: Location, avoid_entity_types=None):
        """
        Find a path from start to goal using A* algorithm.

        Args:
            start: Starting location
            goal: Goal location
            avoid_entity_types: List of entity types to avoid in the path

        Returns:
            List of Locations representing the path (including start and goal)
            or empty list if no path is found
        """
        if not avoid_entity_types:
            avoid_entity_types = []

        # If start and goal are the same, return immediately
        if start.x == goal.x and start.y == goal.y:
            return [start]

        # Initialize the open and closed sets
        open_set = []
        closed_set = set()

        # Dictionary to store the parent of each node
        came_from = {}

        # Dictionary to store g scores (cost from start to current node)
        g_score = {self._hash_location(start): 0}

        # Dictionary to store f scores (g score + heuristic)
        f_score = {self._hash_location(start): self._heuristic(start, goal)}

        # Add start node to open set
        heapq.heappush(open_set, (f_score[self._hash_location(start)], self._hash_location(start)))

        while open_set:
            # Get the node with the lowest f score
            current_hash = heapq.heappop(open_set)[1]
            current = self._unhash_location(current_hash)

            # If we've reached the goal, reconstruct the path
            if current.x == goal.x and current.y == goal.y:
                return self._reconstruct_path(came_from, current)

            # Add current to closed set
            closed_set.add(current_hash)

            # Check all neighbors
            for neighbor in self._get_neighbors(current):
                neighbor_hash = self._hash_location(neighbor)

                # Skip if neighbor is in closed set
                if neighbor_hash in closed_set:
                    continue

                # Skip if neighbor contains an entity to avoid
                entity = self.grid.get_entity_at(neighbor)
                if entity and entity.type in avoid_entity_types:
                    continue

                # Calculate tentative g score
                tentative_g_score = g_score[self._hash_location(current)] + 1

                # If neighbor is not in open set or has a better g score
                if (neighbor_hash not in g_score) or (tentative_g_score < g_score[neighbor_hash]):
                    # Update the path
                    came_from[neighbor_hash] = current
                    g_score[neighbor_hash] = tentative_g_score
                    f_score[neighbor_hash] = tentative_g_score + self._heuristic(neighbor, goal)

                    # Add to open set if not already there
                    if neighbor_hash not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor_hash], neighbor_hash))

        # No path found
        return []

    def _get_neighbors(self, location: Location):
        """Get all valid neighbors of a location, accounting for wrap-around."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, right, down, left

        for dx, dy in directions:
            new_x = (location.x + dx) % self.grid.width
            new_y = (location.y + dy) % self.grid.height
            neighbors.append(Location(new_x, new_y))

        return neighbors

    def _heuristic(self, a: Location, b: Location):
        """Calculate the heuristic (Manhattan distance with wrap-around)."""
        return calculate_wrapped_distance(
            a.x, a.y, b.x, b.y, self.grid.width, self.grid.height
        )

    def _hash_location(self, location: Location):
        """Convert a location to a hashable value."""
        return (location.x, location.y)

    def _unhash_location(self, hash_value):
        """Convert a hash back to a location."""
        return Location(hash_value[0], hash_value[1])

    def _reconstruct_path(self, came_from, current):
        """Reconstruct the path from the start to the goal."""
        path = [current]
        current_hash = self._hash_location(current)

        while current_hash in came_from:
            current = came_from[current_hash]
            current_hash = self._hash_location(current)
            path.append(current)

        return path[::-1]  # Reverse to get path from start to goal