from typing import Optional, List, Tuple
import random
from src.core.entities.position import Position
from src.core.entities.base import Entity
from src.core.entities.hunter import Hunter
from src.core.entities.treasure import Treasure
from src.core.enums import EntityType, KnightAction

class Knight(Entity):
    def __init__(self, position: Position):
        super().__init__(position, EntityType.KNIGHT)
        self.energy: float = 100.0
        self.current_action: KnightAction = KnightAction.PATROL
        self.detected_hunters: List[Tuple[Hunter, Position]] = []
        self.is_resting: bool = False
        self.detection_radius: int = 3

    def move(self, new_position: Position) -> None:
        """Move the knight to a new position, consuming energy if pursuing."""
        if not self.can_pursue():
            return
            
        self.position = new_position
        if self.current_action == KnightAction.PURSUE:
            self.energy = max(0.0, self.energy - 20.0)  # -20% energy per chase
        self.current_action = KnightAction.PATROL

    def rest(self) -> None:
        """Rest and recover energy."""
        self.is_resting = True
        self.energy = min(100.0, self.energy + 10.0)  # +10% energy per rest step
        if self.energy >= 100.0:
            self.is_resting = False
            self.current_action = KnightAction.PATROL

    def can_pursue(self) -> bool:
        """Check if the knight can pursue hunters."""
        return self.energy > 20.0 and not self.is_resting

    def needs_rest(self) -> bool:
        """Check if the knight needs to rest."""
        return self.energy <= 20.0

    def detect_hunters(self, hunters: List[Hunter]) -> None:
        """Detect hunters within 3 cells and update the detected hunters list."""
        self.detected_hunters.clear()
        for hunter in hunters:
            distance = self.position.distance_to(hunter.position)
            if distance <= self.detection_radius:
                self.detected_hunters.append((hunter, hunter.position))

    def choose_target(self) -> Optional[Hunter]:
        """Choose a hunter to pursue from detected hunters."""
        if not self.detected_hunters:
            return None
        return random.choice(self.detected_hunters)[0]

    def interact_with_hunter(self, hunter: Hunter) -> None:
        """Interact with a caught hunter (detain or challenge)."""
        if random.random() < 0.5:  # 50% chance for each action
            # Detain: -5% stamina
            hunter.stamina = max(0.0, hunter.stamina - 5.0)
        else:
            # Challenge: -20% stamina
            hunter.stamina = max(0.0, hunter.stamina - 20.0)

        # Make hunter drop treasure if carrying any
        if hunter.carrying_treasure:
            dropped_treasure = hunter.carrying_treasure
            hunter.carrying_treasure = None
            # Treasure remains at the drop location
            # Hunter will remember this location for possible retrieval

    def choose_action(self, hunter: Hunter) -> KnightAction:
        """Choose the next action based on current state."""
        if self.energy <= 20.0:
            return KnightAction.REST
        if self.position == hunter.position:
            return KnightAction.DETAIN
        return KnightAction.PURSUE

    def __repr__(self) -> str:
        return f"Knight(Position: {self.position}, Energy: {self.energy:.1f}%, Action: {self.current_action.name})" 