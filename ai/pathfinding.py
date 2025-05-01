from typing import List, Tuple, Dict, Set, Optional
from models.location import Location
from utils.helpers import calculate_wrapped_distance, get_move_direction
from utils.constants import EntityType  # Add this import
import heapq


def find_path_astar(start: Location, goal: Location, grid, width: int, height: int) -> List[Location]:
    """A* pathfinding algorithm for finding the shortest path in a wrapping grid."""
    # Create closed set for nodes already evaluated
    closed_set = set()

    # Create open set for nodes to be evaluated, starting with start
    open_set = []
    heapq.heappush(open_set, (0, id(start), start))

    # For each node, which node it can most efficiently be reached from
    came_from = {}

    # For each node, the cost of getting from the start node to that node
    g_score = {start: 0}

    # For each node, the total cost of getting from the start node to the goal
    f_score = {start: calculate_wrapped_distance(start.x, start.y, goal.x, goal.y, width, height)}

    # While there are nodes to evaluate
    while open_set:
        # Get the node with the lowest f_score
        _, _, current = heapq.heappop(open_set)

        # If we've reached the goal, reconstruct the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        # Mark the current node as evaluated
        closed_set.add(current)

        # Check neighbors
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx = (current.x + dx) % width
            ny = (current.y + dy) % height
            neighbor = Location(nx, ny)

            # Skip if neighbor is already evaluated
            if neighbor in closed_set:
                continue

            # Get entity at neighbor
            entity = grid.get_entity_at(neighbor)

            # Skip if neighbor is occupied by something other than treasure, hideout or garrison
            if entity is not None and entity.type not in [EntityType.TREASURE, EntityType.HIDEOUT, EntityType.GARRISON]:
                continue

            # Calculate tentative g_score
            tentative_g_score = g_score.get(current, float('inf')) + 1

            # If neighbor not in open set, add it
            if neighbor not in [loc for _, _, loc in open_set]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + calculate_wrapped_distance(
                    neighbor.x, neighbor.y, goal.x, goal.y, width, height
                )
                heapq.heappush(open_set, (f_score[neighbor], id(neighbor), neighbor))
            elif tentative_g_score < g_score.get(neighbor, float('inf')):
                # This is a better path to neighbor
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + calculate_wrapped_distance(
                    neighbor.x, neighbor.y, goal.x, goal.y, width, height
                )

                # Update neighbor in open_set
                for i, (f, _, loc) in enumerate(open_set):
                    if loc == neighbor:
                        open_set[i] = (f_score[neighbor], id(neighbor), neighbor)
                        heapq.heapify(open_set)
                        break

    # No path found
    return []


def get_next_move(current: Location, target: Location, grid, width: int, height: int) -> Optional[Location]:
    """Get the next move towards a target location."""
    # Use pathfinding if target is far
    if calculate_wrapped_distance(current.x, current.y, target.x, target.y, width, height) > 3:
        path = find_path_astar(current, target, grid, width, height)
        if path:
            return path[0]

    # Otherwise use simple direction
    dx, dy = get_move_direction(current.x, current.y, target.x, target.y, width, height)
    new_x = (current.x + dx) % width
    new_y = (current.y + dy) % height
    return Location(new_x, new_y)