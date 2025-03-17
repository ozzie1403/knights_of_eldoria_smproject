import random
from enum import Enum
from typing import List, Optional


class TreasureType(Enum):
    BRONZE = 3  # Increases wealth by 3%
    SILVER = 7  # Increases wealth by 7%
    GOLD = 13  # Increases wealth by 13%


class Treasure:
    def __init__(self, treasure_type: TreasureType, position: tuple[int, int]):
        self.treasure_type = treasure_type
        self.value = treasure_type.value  # Percentage value increase
        self.position = position

    def decay(self):
        """Treasure loses 0.1% of its value per step."""
        self.value = max(0, self.value - 0.1)

    def is_depleted(self) -> bool:
        """Returns True if the treasure has lost all its value."""
        return self.value <= 0


class Grid:
    def __init__(self, size: int = 20):
        self.size = size
        self.cells = [[None for _ in range(size)] for _ in range(size)]

    def wrap_position(self, x: int, y: int) -> tuple[int, int]:
        """Ensures grid wraps around edges."""
        return x % self.size, y % self.size

    def place_treasure(self, count: int = 10):
        """Randomly place treasures in the grid."""
        for _ in range(count):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            treasure_type = random.choice(list(TreasureType))
            self.cells[x][y] = Treasure(treasure_type, (x, y))

    def get_treasure_at(self, x: int, y: int) -> Optional[Treasure]:
        """Returns the treasure at the given position, if any."""
        return self.cells[x][y] if isinstance(self.cells[x][y], Treasure) else None

    def update_treasures(self):
        """Decays all treasures and removes depleted ones."""
        for x in range(self.size):
            for y in range(self.size):
                treasure = self.get_treasure_at(x, y)
                if treasure:
                    treasure.decay()
                    if treasure.is_depleted():
                        self.cells[x][y] = None


class TreasureHunter:
    def __init__(self, name: str, position: tuple[int, int], stamina: float = 100.0):
        self.name = name
        self.position = position
        self.stamina = stamina
        self.carrying_treasure: Optional[Treasure] = None

    def move(self, direction: str, grid: Grid):
        """Moves the hunter in a given direction if stamina allows."""
        if self.stamina <= 0:
            return

        x, y = self.position
        if direction == "up":
            y -= 1
        elif direction == "down":
            y += 1
        elif direction == "left":
            x -= 1
        elif direction == "right":
            x += 1

        self.position = grid.wrap_position(x, y)
        self.stamina = max(0, self.stamina - 2)  # Decrease stamina by 2% per move

    def pick_up_treasure(self, grid: Grid):
        """Picks up a treasure if available and not already carrying one."""
        if self.carrying_treasure is None:
            treasure = grid.get_treasure_at(*self.position)
            if treasure:
                self.carrying_treasure = treasure
                grid.cells[self.position[0]][self.position[1]] = None

    def drop_treasure(self):
        """Drops the carried treasure."""
        self.carrying_treasure = None

    def rest(self):
        """Regains stamina while resting in a hideout."""
        self.stamina = min(100, self.stamina + 1)


class Knight:
    def __init__(self, position: tuple[int, int], energy: float = 100.0):
        self.position = position
        self.energy = energy

    def move_towards(self, target_position: tuple[int, int], grid: Grid):
        """Moves the knight one step towards the target position."""
        if self.energy <= 20:
            return  # Knights retreat when energy is low

        x, y = self.position
        tx, ty = target_position

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1

        self.position = grid.wrap_position(x, y)
        self.energy = max(0, self.energy - 10)  # Knights lose 10% energy per move

    def attack_hunter(self, hunter: TreasureHunter):
        """Knights attack a hunter, reducing stamina."""
        if self.energy > 0:
            hunter.stamina = max(0, hunter.stamina - 20)  # Reduces hunter stamina
            hunter.drop_treasure()  # Forces hunter to drop treasure

    def rest(self):
        """Recovers knight's energy."""
        self.energy = min(100, self.energy + 10)


class Simulation:
    def __init__(self, grid_size=20, num_hunters=3, num_knights=2, num_treasures=10):
        self.grid = Grid(grid_size)
        self.hunters = [
            TreasureHunter(f"Hunter{i + 1}", (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))) for i
            in range(num_hunters)]
        self.knights = [Knight((random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))) for _ in
                        range(num_knights)]
        self.grid.place_treasure(num_treasures)

    def run_step(self):
        """Runs one step of the simulation."""
        for hunter in self.hunters:
            hunter.move(random.choice(["up", "down", "left", "right"]), self.grid)
            hunter.pick_up_treasure(self.grid)
        for knight in self.knights:
            if self.hunters:
                knight.move_towards(self.hunters[0].position, self.grid)
                knight.attack_hunter(self.hunters[0])
        self.grid.update_treasures()

    def run(self, steps=100):
        """Runs the simulation for a given number of steps."""
        for _ in range(steps):
            self.run_step()
