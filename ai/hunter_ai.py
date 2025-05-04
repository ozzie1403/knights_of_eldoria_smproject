class HunterAI:
    """
    Class for advanced hunter AI logic (decision-making, pathfinding, etc.).
    Extend this class to implement custom hunter behaviors.
    """
    def __init__(self, hunter):
        self.hunter = hunter

    def decide_next_action(self):
        """
        Decide the next action for the hunter.
        """
        # If carrying treasure, force return to hideout
        if self.hunter.carried_treasure is not None:
            return "return_to_hideout"
        # Otherwise, explore or look for treasure
        return "explore" 