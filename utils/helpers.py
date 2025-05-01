def calculate_wrapped_distance(x1, y1, x2, y2, width, height):
    """Calculate the wrapped distance between two points on a grid with wrap-around edges."""
    dx = min(abs(x2 - x1), width - abs(x2 - x1))
    dy = min(abs(y2 - y1), height - abs(y2 - y1))
    return dx + dy  # Manhattan distance


def calculate_wrapped_direction(x1, y1, x2, y2, width, height):
    """Calculate the direction to move from (x1,y1) to (x2,y2) accounting for wrap-around."""
    # Calculate x direction with wrap-around consideration
    dx = (x2 - x1 + width // 2) % width - width // 2

    # Calculate y direction with wrap-around consideration
    dy = (y2 - y1 + height // 2) % height - height // 2

    return dx, dy