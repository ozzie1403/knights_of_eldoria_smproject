import enum

# Grid settings
DEFAULT_GRID_SIZE = 20
MIN_GRID_SIZE = 10
MAX_GRID_SIZE = 50

# Entity types
class EntityType(enum.Enum):
    EMPTY = 0
    TREASURE = 1
    HUNTER = 2
    HIDEOUT = 3
    KNIGHT = 4
    GARRISON = 5  # Added garrison entity type

# Treasure types and values
class TreasureType(enum.Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2

TREASURE_VALUES = {
    TreasureType.BRONZE: 3.0,  # 3% wealth increase
    TreasureType.SILVER: 7.0,  # 7% wealth increase
    TreasureType.GOLD: 13.0,   # 13% wealth increase
}

# Hunter skills
class HunterSkill(enum.Enum):
    NAVIGATION = 0  # Better at finding paths
    ENDURANCE = 1   # Loses less stamina
    STEALTH = 2     # Less likely to be detected by knights

# Hunter parameters
HUNTER_STAMINA_LOSS_MOVEMENT = 2.0  # 2% stamina loss per movement
HUNTER_STAMINA_GAIN_REST = 1.0      # 1% stamina gain per rest
HUNTER_CRITICAL_STAMINA = 6.0       # Critical stamina level
HUNTER_COLLAPSE_COUNTDOWN = 3       # Steps before hunter collapses at 0 stamina

# Knight parameters
KNIGHT_DETECTION_RADIUS = 3         # Cells a knight can detect hunters
KNIGHT_ENERGY_LOSS_CHASE = 20.0     # Energy loss during chase
KNIGHT_ENERGY_LOSS_MOVEMENT = 1.0   # Energy loss during normal movement
KNIGHT_ENERGY_GAIN_REST = 10.0      # Energy gain during rest
KNIGHT_CRITICAL_ENERGY = 20.0       # Critical energy level

# Knight interaction outcomes
KNIGHT_DETAIN_STAMINA_LOSS = 5.0    # Stamina loss when detained
KNIGHT_CHALLENGE_STAMINA_LOSS = 20.0 # Stamina loss when challenged
KNIGHT_DETAIN_PROBABILITY = 0.7     # 70% chance to detain vs challenge

# Hideout parameters
HIDEOUT_MAX_CAPACITY = 5            # Maximum hunters per hideout
HIDEOUT_RECRUIT_PROBABILITY = 0.2   # 20% chance to recruit new hunter

# Garrison parameters
GARRISON_MAX_CAPACITY = 3           # Maximum knights per garrison

# Treasure parameters
TREASURE_VALUE_DECAY = 0.001        # 0.1% value loss per step