import pytest
from models.grid import Grid
from models.enums import CellType

@pytest.fixture
def grid():
    """Create a 5x5 grid for testing"""
    return Grid(5, 5)

def test_wrap_coordinates(grid):
    """Test coordinate wrapping"""
    # Test wrapping around right edge
    assert grid.wrap_coordinates(5, 0) == (0, 0)
    assert grid.wrap_coordinates(6, 0) == (1, 0)
    
    # Test wrapping around left edge
    assert grid.wrap_coordinates(-1, 0) == (4, 0)
    assert grid.wrap_coordinates(-2, 0) == (3, 0)
    
    # Test wrapping around bottom edge
    assert grid.wrap_coordinates(0, 5) == (0, 0)
    assert grid.wrap_coordinates(0, 6) == (0, 1)
    
    # Test wrapping around top edge
    assert grid.wrap_coordinates(0, -1) == (0, 4)
    assert grid.wrap_coordinates(0, -2) == (0, 3)
    
    # Test wrapping both coordinates
    assert grid.wrap_coordinates(6, 6) == (1, 1)
    assert grid.wrap_coordinates(-1, -1) == (4, 4)

def test_set_and_get_cell(grid):
    """Test setting and getting cell values with wrapping"""
    # Set a value at wrapped coordinates
    grid.set_cell(6, 6, CellType.WALL.value)
    
    # Verify the value is set at the wrapped position
    assert grid.get_cell(1, 1) == CellType.WALL.value
    
    # Set a value at negative coordinates
    grid.set_cell(-1, -1, CellType.PATH.value)
    
    # Verify the value is set at the wrapped position
    assert grid.get_cell(4, 4) == CellType.PATH.value

def test_neighbors_with_wrapping(grid):
    """Test getting neighbors with wrapping"""
    # Test neighbors of corner cell (0, 0)
    neighbors = grid.get_neighbors(0, 0)
    expected = [(0, 1), (1, 0), (0, 4), (4, 0)]  # up, right, down, left (wrapped)
    assert sorted(neighbors) == sorted(expected)
    
    # Test diagonal neighbors of corner cell (0, 0)
    diag_neighbors = grid.get_diagonal_neighbors(0, 0)
    expected_diag = [(1, 1), (1, 4), (4, 1), (4, 4)]  # diagonal (wrapped)
    assert sorted(diag_neighbors) == sorted(expected_diag)

def test_clear_cell(grid):
    """Test clearing cells with wrapping"""
    # Set a value and clear it using wrapped coordinates
    grid.set_cell(6, 6, CellType.WALL.value)
    grid.clear_cell(1, 1)
    assert grid.get_cell(1, 1) == CellType.EMPTY.value

def test_random_fill(grid):
    """Test random filling of the grid"""
    grid.random_fill()
    
    # Check that all cells have valid values
    for y in range(grid.height):
        for x in range(grid.width):
            value = grid.get_cell(x, y)
            assert value in [cell.value for cell in CellType]

def test_clear_grid(grid):
    """Test clearing the entire grid"""
    # Fill grid with random values
    grid.random_fill()
    
    # Clear the grid
    grid.clear_grid()
    
    # Verify all cells are empty
    for y in range(grid.height):
        for x in range(grid.width):
            assert grid.get_cell(x, y) == CellType.EMPTY.value

def test_all_neighbors(grid):
    """Test getting all neighbors (including diagonals) with wrapping"""
    # Test all neighbors of corner cell (0, 0)
    all_neighbors = grid.get_all_neighbors(0, 0)
    expected = [
        (0, 1), (1, 0), (0, 4), (4, 0),  # orthogonal
        (1, 1), (1, 4), (4, 1), (4, 4)   # diagonal
    ]
    assert sorted(all_neighbors) == sorted(expected) 