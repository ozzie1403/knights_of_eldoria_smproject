from enum import Enum, auto

class EntityType(Enum):
    HUNTER = auto()
    KNIGHT = auto()
    TREASURE = auto()
    HIDEOUT = auto()

class HunterSkill(Enum):
    NAVIGATION = auto()  # Better at finding treasures
    ENDURANCE = auto()   # Better stamina management
    STEALTH = auto()     # Harder to detect by knights

class TreasureType(Enum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()

class KnightAction(Enum):
    PATROL = auto()     # Random movement
    PURSUE = auto()     # Chase a hunter
    DETAIN = auto()     # Try to capture a hunter
    REST = auto()       # Recover energy

class KnightSkill(Enum):
    NOVICE = auto()
    INTERMEDIATE = auto()
    EXPERT = auto()
    MASTER = auto()

class DragonSkill(Enum):
    WEAK = auto()
    AVERAGE = auto()
    STRONG = auto()
    LEGENDARY = auto() 