from enum import Enum, auto
from typing import Dict, List, Tuple, Optional
from models.entity import Position


class TreasureType(Enum):
    """Types of treasure with different values."""
    BRONZE = 0
    SILVER = 1
    GOLD = 2


class HunterSkill(Enum):
    """Skills that hunters can possess."""
    NAVIGATION = 0  # Better at finding paths
    ENDURANCE = 1  # Loses less stamina
    STEALTH = 2  # Less likely to be detected by knights


class HunterState(Enum):
    """Possible states for treasure hunters."""
    EXPLORING = 0  # Looking for treasure
    COLLECTING = 1  # Going to collect treasure
    RETURNING = 2  # Returning to hideout with treasure
    RESTING = 3  # Recovering stamina at hideout
    COLLAPSED = 4  # Out of stamina and unable to move


class KnightState(Enum):
    """Possible states for knights."""
    PATROLLING = 0  # Regular patrol
    PURSUING = 1  # Chasing a hunter
    RESTING = 2  # Recovering energy at garrison
    CHALLENGING = 3  # Confronting a hunter


class Direction(Enum):
    """Cardinal directions for movement."""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class MemoryItem:
    """Represents a memory of an entity's position."""

    def __init__(self, entity_type, position: Position, timestamp: int,
                 value: float = 0.0, treasure_type: TreasureType = None):
        self.entity_type = entity_type
        self.position = position
        self.timestamp_seen = timestamp
        self.value = value
        self.treasure_type = treasure_type

    def __str__(self):
        return f"Memory: {self.entity_type} at {self.position} (t={self.timestamp_seen})"


class KnowledgePacket:
    """Information packet shared between hunters."""

    def __init__(self):
        self.treasure_locations: List[MemoryItem] = []
        self.hideout_locations: List[MemoryItem] = []

    def add_treasure_memory(self, memory: MemoryItem):
        self.treasure_locations.append(memory)

    def add_hideout_memory(self, memory: MemoryItem):
        self.hideout_locations.append(memory)