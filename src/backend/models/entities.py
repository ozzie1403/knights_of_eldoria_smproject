from dataclasses import dataclass
from typing import Optional, List, Dict, Set, Tuple, Any
from enum import Enum, auto
import random
import math

class TreasureType(Enum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()

class HunterSkill(Enum):
    NAVIGATION = auto()
    ENDURANCE = auto()
    STEALTH = auto()

class KnightAction(Enum):
    DETAIN = auto()
    CHALLENGE = auto()
    REST = auto()
    PATROL = auto()

class CellType(Enum):
    EMPTY = auto()
    TREASURE = auto()
    HUNTER = auto()
    HIDEOUT = auto()
    KNIGHT = auto()

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

    def distance_to(self, other: 'Position') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

@dataclass
class Treasure:
    position: Position
    treasure_type: TreasureType
    value: float = 100.0  # Initial value is 100%

    def decay(self) -> None:
        self.value = max(0.0, self.value - 0.1)

    def get_value_increase(self) -> float:
        if self.treasure_type == TreasureType.BRONZE:
            return 3.0
        elif self.treasure_type == TreasureType.SILVER:
            return 7.0
        else:  # GOLD
            return 13.0

@dataclass
class Hunter:
    position: Position
    skill: HunterSkill
    stamina: float = 100.0
    carried_treasure: Optional[Treasure] = None
    known_treasures: List[Position] = None
    known_hideouts: List[Position] = None
    known_knights: List[Position] = None
    steps_since_collapse: int = 0
    is_collapsed: bool = False

    def __post_init__(self):
        if self.known_treasures is None:
            self.known_treasures = []
        if self.known_hideouts is None:
            self.known_hideouts = []
        if self.known_knights is None:
            self.known_knights = []

    def move(self, new_position: Position) -> None:
        if not self.can_move():
            return
            
        self.position = new_position
        # Skill-based stamina depletion
        if self.skill == HunterSkill.ENDURANCE:
            self.stamina = max(0.0, self.stamina - 1.5)  # 25% less stamina depletion
        else:
            self.stamina = max(0.0, self.stamina - 2.0)

    def rest(self) -> None:
        if self.skill == HunterSkill.ENDURANCE:
            self.stamina = min(100.0, self.stamina + 1.2)  # 20% faster recovery
        else:
            self.stamina = min(100.0, self.stamina + 1.0)

    def can_move(self) -> bool:
        if self.is_collapsed:
            self.steps_since_collapse += 1
            if self.steps_since_collapse >= 3:
                return False
            return True
        return self.stamina > 0.0

    def needs_rest(self) -> bool:
        return self.stamina <= 6.0

    def collapse(self) -> None:
        if self.stamina <= 0.0 and not self.is_collapsed:
            self.is_collapsed = True
            self.steps_since_collapse = 0

    def get_skill_efficiency(self) -> float:
        if self.skill == HunterSkill.NAVIGATION:
            return 1.2  # 20% faster movement
        elif self.skill == HunterSkill.ENDURANCE:
            return 1.0  # Normal speed
        else:  # STEALTH
            return 0.8  # 20% slower but harder to detect

    def prioritize_treasure(self, treasures: List[Treasure]) -> Optional[Treasure]:
        if not treasures:
            return None
            
        # Sort treasures by value and type
        sorted_treasures = sorted(treasures, 
                                key=lambda t: (t.value, t.treasure_type.value), 
                                reverse=True)
        return sorted_treasures[0]

@dataclass
class Knight:
    position: Position
    energy: float = 100.0
    current_action: KnightAction = KnightAction.PATROL
    last_known_hunter_positions: List[Position] = None
    is_resting: bool = False

    def __post_init__(self):
        if self.last_known_hunter_positions is None:
            self.last_known_hunter_positions = []

    def move(self, new_position: Position) -> None:
        if not self.can_pursue():
            return
            
        self.position = new_position
        self.energy = max(0.0, self.energy - 20.0)
        self.current_action = KnightAction.PATROL

    def rest(self) -> None:
        self.is_resting = True
        self.energy = min(100.0, self.energy + 10.0)
        if self.energy >= 100.0:
            self.is_resting = False
            self.current_action = KnightAction.PATROL

    def can_pursue(self) -> bool:
        return self.energy > 20.0 and not self.is_resting

    def needs_rest(self) -> bool:
        return self.energy <= 20.0

    def detect_hunter(self, hunter_position: Position) -> None:
        if hunter_position not in self.last_known_hunter_positions:
            self.last_known_hunter_positions.append(hunter_position)

    def clear_known_positions(self) -> None:
        self.last_known_hunter_positions.clear()

    def choose_action(self, hunter: Hunter) -> KnightAction:
        if self.energy <= 20.0:
            return KnightAction.REST
        return random.choice([KnightAction.DETAIN, KnightAction.CHALLENGE])

@dataclass
class Hideout:
    position: Position
    hunters: List[Hunter] = None
    stored_treasures: List[Treasure] = None
    max_capacity: int = 5
    known_treasures: List[Position] = None
    known_knights: List[Position] = None

    def __post_init__(self):
        if self.hunters is None:
            self.hunters = []
        if self.stored_treasures is None:
            self.stored_treasures = []
        if self.known_treasures is None:
            self.known_treasures = []
        if self.known_knights is None:
            self.known_knights = []

    def can_accommodate(self) -> bool:
        return len(self.hunters) < self.max_capacity

    def add_hunter(self, hunter: Hunter) -> bool:
        if self.can_accommodate():
            self.hunters.append(hunter)
            self.share_information(hunter)
            return True
        return False

    def remove_hunter(self, hunter: Hunter) -> bool:
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False

    def share_information(self, hunter: Hunter) -> None:
        # Share known treasures
        for treasure_pos in self.known_treasures:
            if treasure_pos not in hunter.known_treasures:
                hunter.known_treasures.append(treasure_pos)
        
        # Share known knights
        for knight_pos in self.known_knights:
            if knight_pos not in hunter.known_knights:
                hunter.known_knights.append(knight_pos)

        # Share known hideouts
        for other_hunter in self.hunters:
            if other_hunter != hunter:
                for hideout_pos in other_hunter.known_hideouts:
                    if hideout_pos not in hunter.known_hideouts:
                        hunter.known_hideouts.append(hideout_pos)

    def try_recruit_hunter(self, grid_size: int) -> Optional[Hunter]:
        if not self.can_accommodate():
            return None

        # Check if we have a diverse set of skills
        skills_present = {h.skill for h in self.hunters}
        if len(skills_present) < 2:  # Need at least 2 different skills
            return None

        # 20% chance of recruitment
        if random.random() > 0.2:
            return None

        # Choose a random skill from existing hunters
        new_skill = random.choice(list(skills_present))
        return Hunter(Position(random.randint(0, grid_size-1), 
                             random.randint(0, grid_size-1)), 
                     new_skill)

    def update_known_positions(self, treasure_pos: Position = None, knight_pos: Position = None) -> None:
        if treasure_pos and treasure_pos not in self.known_treasures:
            self.known_treasures.append(treasure_pos)
        if knight_pos and knight_pos not in self.known_knights:
            self.known_knights.append(knight_pos)