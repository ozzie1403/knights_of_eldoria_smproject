class Location:
    """Represents a location in the grid with x, y coordinates."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Location({self.x}, {self.y})"

    def get_wrapped_coords(self, width: int, height: int) -> tuple:
        """Get coordinates wrapped around grid boundaries."""
        # Ensure we don't divide by zero
        if width <= 0 or height <= 0:
            return self.x, self.y

        return self.x % width, self.y % height

