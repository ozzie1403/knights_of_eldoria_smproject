from enum import Enum

class CellType(Enum):
    """Enum for different types of cells in the grid"""
    EMPTY = 0
    TREASURE = 1
    TREASURE_HUNTER = 2
    HIDEOUT = 3
    KNIGHT = 4
    GARRISON = 5

class TreasureType(Enum):
    """Enum for different types of treasures and their values"""
    BRONZE = 1
    SILVER = 2
    GOLD = 3

class HunterSkill(Enum):
    """Enum for different hunter skills"""
    NAVIGATION = 0  # Better at finding paths and remembering locations
    ENDURANCE = 1   # Better stamina management and recovery
    STEALTH = 2     # Better at avoiding detection and moving quietly 