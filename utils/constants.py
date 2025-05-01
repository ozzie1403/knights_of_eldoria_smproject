from enum import Enum, auto

# Grid constants
DEFAULT_GRID_SIZE = 20


# Entity types
class EntityType(Enum):
    EMPTY = auto()
    TREASURE_HUNTER = auto()
    KNIGHT = auto()
    TREASURE = auto()
    HIDEOUT = auto()
    GARRISON = auto()

    # For easier display
    HUNTER = TREASURE_HUNTER


# Hunter skill types
class HunterSkill(Enum):
    NAVIGATION = auto()  # Better at finding treasures
    STEALTH = auto()  # Better at avoiding knights
    SPEED = auto()  # Moves faster
    PERCEPTION = auto()  # Better at spotting entities


# Treasure types
class TreasureType(Enum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()


# Initial values for different treasure types
TREASURE_VALUES = {
    TreasureType.BRONZE: 3.0,  # Bronze increases wealth by 3%
    TreasureType.SILVER: 7.0,  # Silver increases wealth by 7%
    TreasureType.GOLD: 13.0,  # Gold increases wealth by 13%
}

# Treasure decay rate per step (0.1%)
TREASURE_VALUE_DECAY = 0.001

# Hunter constants
HUNTER_STAMINA_LOSS_MOVE = 2.0  # 2% stamina loss per move
HUNTER_STAMINA_GAIN_REST = 5.0  # 5% stamina gain per rest
HUNTER_CRITICAL_STAMINA = 30.0  # Seek hideout when stamina below 30%
HUNTER_COLLAPSE_COUNTDOWN = 5  # Steps until a collapsed hunter is removed

# Hideout constants
HIDEOUT_MAX_CAPACITY = 5  # Maximum 5 hunters per hideout
HIDEOUT_RECRUIT_PROBABILITY = 0.2  # 20% chance to recruit new hunter

# Knight constants
KNIGHT_DETECTION_RADIUS = 3  # Knights can detect hunters within 3 cells
KNIGHT_ENERGY_LOSS_MOVE = 1.0  # 1% energy loss per move
KNIGHT_ENERGY_GAIN_REST = 10.0  # 10% energy gain when resting in garrison
KNIGHT_LOW_ENERGY = 30.0  # Return to garrison when energy below 30%

# UI constants
COLORS = {
    EntityType.EMPTY: "#E0E0E0",  # Light gray
    EntityType.HUNTER: "#4CAF50",  # Green
    EntityType.KNIGHT: "#F44336",  # Red
    EntityType.TREASURE: "#FFD700",  # Gold
    EntityType.HIDEOUT: "#2196F3",  # Blue
    EntityType.GARRISON: "#9C27B0",  # Purple
}