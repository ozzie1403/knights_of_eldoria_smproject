import math
import random
from typing import Tuple, List, Dict, Optional

def calculate_wrapped_distance(x1: int, y1: int, x2: int, y2: int, width: int, height: int) -> float:
    """Calculate the shortest distance between two points in a wrapping grid."""
    dx = min(abs(x1 - x2), width - abs(x1 - x2))
    dy = min(abs(y1 - y2), height - abs(y1 - y2))
    return math.sqrt(dx * dx + dy * dy)

def get_move_direction(x1: int, y1: int, x2: int, y2: int, width: int, height: int) -> Tuple[int, int]:
    """Calculate the best direction to move from (x1,y1) to (x2,y2) in a wrapping grid."""
    dx = (x2 - x1 + width // 2) % width - width // 2
    dy = (y2 - y1 + height // 2) % height - height // 2
    
    # Decide which direction to move based on the larger absolute difference
    move_x, move_y = 0, 0
    if abs(dx) > abs(dy):
        move_x = 1 if dx > 0 else -1
    elif dy != 0:
        move_y = 1 if dy > 0 else -1
        
    return move_x, move_y

def get_nearest_entity(x: int, y: int, entities: List[Tuple[int, int]], width: int, height: int) -> Optional[Tuple[int, int]]:
    """Find the nearest entity to the position (x,y)."""
    if not entities:
        return None
        
    nearest = None
    min_distance = float('inf')
    
    for ex, ey in entities:
        distance = calculate_wrapped_distance(x, y, ex, ey, width, height)
        if distance < min_distance:
            min_distance = distance
            nearest = (ex, ey)
            
    return nearest

def choose_random_empty_cell(grid, width: int, height: int, max_attempts: int = 100) -> Optional[Tuple[int, int]]:
    """Find a random empty cell in the grid."""
    for _ in range(max_attempts):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if grid[y][x] is None:
            return x, y
    return None