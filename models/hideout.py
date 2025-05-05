import random
from typing import List, Dict, Optional
from models.entity import Entity, EntityType, Position
from models.types import HunterSkill, KnowledgePacket, MemoryItem
from .ai_controllers import HideoutAI


class Hideout(Entity):
    """
    Represents a hideout for treasure hunters. Hunters can rest here,
    share knowledge, and new hunters can be recruited.
    """

    def __init__(self, name: str, position: Position, grid_width: int, grid_height: int):
        super().__init__(name, EntityType.HIDEOUT, position)
        self.occupants = []  # Hunters currently in the hideout
        self.max_occupants = 5  # Maximum hunters per hideout
        self.knowledge_base = KnowledgePacket()  # Shared knowledge
        self.treasure_collected = 0.0  # Total treasure value collected
        self.recruitment_chance = 0.2  # 20% chance of recruiting when conditions met
        self.wealth = 0.0
        self.treasures_collected = 0
        self.attraction_radius = 5  # Initial attraction radius
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Set visual properties
        self.icon = "H"  # Hideout icon
        self.color = "#00FF00"  # Green color

        # Initialize AI controller
        self.ai = HideoutAI(self, grid_width, grid_height)

    def act(self, grid, entities: List[Entity]) -> None:
        """Perform the hideout's action for this simulation step."""
        # Update occupants list with hunters at this position
        self._update_occupants(grid)
        self.ai.update(grid, entities)

    def _update_occupants(self, grid) -> None:
        """Update the list of hunters currently in this hideout."""
        # Get the entity at this position
        entity_at_position = grid.get_entity_at(self.position)

        # Check if it's a hunter
        if entity_at_position and entity_at_position.type == EntityType.HUNTER:
            # Add to occupants if not already there
            if entity_at_position not in self.occupants:
                if len(self.occupants) < self.max_occupants:
                    self.occupants.append(entity_at_position)

        # Remove occupants that are no longer at this position
        self.occupants = [o for o in self.occupants if
                          o.position.x == self.position.x and
                          o.position.y == self.position.y]

    def receive_knowledge(self, hunter, packet: KnowledgePacket) -> None:
        """Receive knowledge from a hunter and add it to the knowledge base."""
        if not packet:
            return

        # Add treasure locations to knowledge base
        for memory in packet.treasure_locations:
            self._update_knowledge_base(memory, 'treasure')

        # Add hideout locations to knowledge base
        for memory in packet.hideout_locations:
            self._update_knowledge_base(memory, 'hideout')

    def _update_knowledge_base(self, memory: MemoryItem, memory_type: str) -> None:
        """Update knowledge base with new information, avoiding duplicates."""
        # Determine which list to update
        memory_list = (self.knowledge_base.treasure_locations if memory_type == 'treasure'
                       else self.knowledge_base.hideout_locations)

        # Check if we already have memory of this position
        for i, item in enumerate(memory_list):
            if (item.entity_type == memory.entity_type and
                    item.position.x == memory.position.x and
                    item.position.y == memory.position.y):
                # Update existing memory with newer information if it's more recent
                if memory.timestamp_seen > item.timestamp_seen:
                    memory_list[i] = memory
                return

        # Add new memory item
        if memory_type == 'treasure':
            self.knowledge_base.add_treasure_memory(memory)
        else:
            self.knowledge_base.add_hideout_memory(memory)

    def share_knowledge(self) -> KnowledgePacket:
        """Share the hideout's knowledge base with hunters."""
        return self.knowledge_base

    def deposit_treasure(self, treasure_value: float) -> None:
        """Deposit treasure and update hideout stats."""
        self.wealth += treasure_value
        self.treasures_collected += 1
        # Increase attraction radius based on wealth
        self.attraction_radius = min(10, 5 + int(self.wealth / 10))

    def get_report(self) -> str:
        """Generate a report of the hideout's performance."""
        return (
            f"\nHideout {self.id} Report:\n"
            f"Total Wealth: {self.wealth:.1f}\n"
            f"Treasures Collected: {self.treasures_collected}\n"
            f"Attraction Radius: {self.attraction_radius}"
        )