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
    BRONZE = 0
    SILVER = 1
    GOLD = 2

class HunterSkill(Enum):
    """Enum for different hunter skills"""
    NAVIGATION = 0  # Better at finding paths and remembering locations
    ENDURANCE = 1   # Better stamina management and recovery
    STEALTH = 2     # Better at avoiding detection and moving quietly 

class HunterState(Enum):
    """Enum for different states a treasure hunter can be in"""
    EXPLORING = 0    # Looking for treasure
    CARRYING = 1     # Carrying treasure to hideout
    RETURNING = 2    # Returning to hideout
    RESTING = 3      # Resting at hideout
    COLLAPSED = 4    # Hunter has collapsed from exhaustion
    SHARING = 5      # Sharing treasure with other hunters
    COORDINATING = 6 # Coordinating with team members 