from enum import Enum, auto

class EntityType(Enum):
    EMPTY = auto()
    TREASURE = auto()
    HUNTER = auto()
    KNIGHT = auto()
    HIDEOUT = auto()
    GARRISON = auto()

class CellType(Enum):
    EMPTY = "."
    TREASURE = "T"
    HUNTER = "H"
    KNIGHT = "K"
    HIDEOUT = "O"
    GARRISON = "G"

class HunterState(Enum):
    SEARCHING = auto()
    CARRYING = auto()
    RESTING = auto()
    RETURNING = auto()
    COLLAPSED = auto()

class HunterSkill(Enum):
    NAVIGATION = auto()  # Better pathfinding
    ENDURANCE = auto()   # Less stamina loss
    STEALTH = auto()     # Harder to detect

class KnightState(Enum):
    PATROLLING = auto()  # Random movement, looking for hunters
    CHASING = auto()     # Following a specific hunter
    RESTING = auto()     # Recovering energy in garrison

class KnightAction(Enum):
    PATROL = auto()      # Random movement
    CHASE = auto()       # Pursue a hunter
    REST = auto()        # Recover energy
    DETAIN = auto()      # Light punishment
    CHALLENGE = auto()   # Heavy punishment

class KnightSkill(Enum):
    NOVICE = auto()      # Basic detection
    INTERMEDIATE = auto() # Better detection
    EXPERT = auto()      # Best detection
    MASTER = auto()      # Perfect detection

class TreasureType(Enum):
    BRONZE = 0.03  # 3% wealth increase
    SILVER = 0.07  # 7% wealth increase
    GOLD = 0.13    # 13% wealth increase

class DragonSkill(Enum):
    WEAK = auto()
    AVERAGE = auto()
    STRONG = auto()
    LEGENDARY = auto() 