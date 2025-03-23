from src.backend.models.grid import Grid
from src.backend.models.hunter import TreasureHunter
from src.backend.models.knight import Knight

class MovementService:
    @staticmethod
    def move_entity_towards(entity, target: tuple[int, int], grid: Grid):
        """Moves an entity (hunter/knight) one step towards a target."""
        x, y = entity.position
        tx, ty = target

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1

        entity.position = grid.wrap_position(x, y)

    @staticmethod
    def move_hunter(hunter: TreasureHunter, direction: str, grid: Grid):
        """Moves a hunter in a specified direction."""
        hunter.move(direction, grid)

    @staticmethod
    def move_knight(knight: Knight, hunters: list[TreasureHunter], grid: Grid):
        """Moves a knight towards the closest hunter if within a 3-cell radius."""
        min_distance = float('inf')
        nearest_hunter = None

        for hunter in hunters:
            distance = abs(knight.position[0] - hunter.position[0]) + abs(knight.position[1] - hunter.position[1])
            if distance <= 3 and distance < min_distance:
                min_distance = distance
                nearest_hunter = hunter

        if nearest_hunter:
            MovementService.move_entity_towards(knight, nearest_hunter.position, grid)
