from models.entity import Entity, EntityType, Position


class Garrison(Entity):
    """
    Represents a garrison for knights. Knights can rest here to
    recover energy.
    """

    def __init__(self, entity_id: str, position: Position):
        super().__init__(entity_id, EntityType.GARRISON, position)
        self.energy_recovery_bonus = 5.0  # Additional 5% recovery at garrison

        # Set visual properties
        self.icon = "G"
        self.color = "#708090"  # Slate gray

    def act(self, grid, entities) -> None:
        """Perform the garrison's action for this simulation step."""
        # Apply energy recovery bonus to knights at this position
        entity_at_position = grid.get_entity_at(self.position)
        if entity_at_position and entity_at_position.type == EntityType.KNIGHT:
            # Knights recover faster at garrisons
            if hasattr(entity_at_position, 'energy_recovery_rate'):
                entity_at_position.energy_recovery_rate += self.energy_recovery_bonus