from typing import List, Optional, Tuple
import random
from sklearn.cluster import KMeans
from textblob import TextBlob
from src.backend.models.entities import Position, Hunter, Knight, Treasure


class AIService:
    @staticmethod
    def analyze_hunter_behavior(hunter: Hunter, known_treasures: List[Position], known_hideouts: List[Position]) -> \
    Tuple[Position, str]:
        """Analyze hunter's behavior and suggest next move."""
        if hunter.stamina <= 6:
            # Find nearest hideout for rest
            nearest_hideout = min(known_hideouts, key=lambda pos: pos.distance_to(hunter.position))
            return nearest_hideout, "rest"

        if hunter.carried_treasure:
            # Find nearest hideout to deposit treasure
            nearest_hideout = min(known_hideouts, key=lambda pos: pos.distance_to(hunter.position))
            return nearest_hideout, "deposit"

        # Find most valuable treasure based on skill
        if known_treasures:
            if hunter.skill == HunterSkill.NAVIGATION:
                # Prefer treasures in clusters
                cluster_centers = AIService.find_treasure_clusters(known_treasures)
                target = min(cluster_centers, key=lambda pos: pos.distance_to(hunter.position))
            elif hunter.skill == HunterSkill.ENDURANCE:
                # Prefer closer treasures
                target = min(known_treasures, key=lambda pos: pos.distance_to(hunter.position))
            else:  # STEALTH
                # Prefer treasures away from known hideouts
                target = max(known_treasures, key=lambda pos: min(h.distance_to(pos) for h in known_hideouts))
            return target, "collect"

        return hunter.position, "explore"

    @staticmethod
    def analyze_knight_behavior(knight: Knight, nearby_hunters: List[Hunter]) -> Tuple[KnightAction, Optional[Hunter]]:
        """Analyze knight's behavior and decide next action."""
        if not knight.can_pursue():
            return KnightAction.REST, None

        if not nearby_hunters:
            return KnightAction.PATROL, None

        # Choose target based on various factors
        target = AIService.select_hunter_target(nearby_hunters)

        # Decide action based on energy level and target's state
        if knight.energy < 50:
            action = KnightAction.DETAIN
        else:
            action = KnightAction.CHALLENGE

        return action, target

    @staticmethod
    def find_treasure_clusters(treasure_positions: List[Position], n_clusters: int = 3) -> List[Position]:
        """Use K-means clustering to find treasure clusters."""
        if len(treasure_positions) <= n_clusters:
            return treasure_positions

        positions = [(pos.x, pos.y) for pos in treasure_positions]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(positions)

        cluster_centers = [Position(int(x), int(y)) for x, y in kmeans.cluster_centers_]
        return cluster_centers

    @staticmethod
    def select_hunter_target(hunters: List[Hunter]) -> Hunter:
        """Select the most appropriate hunter to target."""
        # Prioritize hunters with treasure
        hunters_with_treasure = [h for h in hunters if h.carried_treasure]
        if hunters_with_treasure:
            return random.choice(hunters_with_treasure)

        # Then prioritize hunters with low stamina
        hunters_low_stamina = [h for h in hunters if h.stamina <= 20]
        if hunters_low_stamina:
            return random.choice(hunters_low_stamina)

        return random.choice(hunters)

    @staticmethod
    def generate_hunter_dialogue(hunter: Hunter, action: str) -> str:
        """Generate natural language dialogue for hunter actions."""
        templates = {
            "rest": [
                f"{hunter.skill.name} hunter needs to rest...",
                f"Stamina low, heading to hideout...",
                f"Time for a quick break..."
            ],
            "deposit": [
                f"Delivering {hunter.carried_treasure.treasure_type.name.lower()} treasure...",
                f"Time to cash in this treasure...",
                f"Making a delivery to the hideout..."
            ],
            "collect": [
                f"Tracking down treasure...",
                f"Following treasure map...",
                f"Searching for riches..."
            ],
            "explore": [
                f"Exploring new territory...",
                f"Scouting for treasure...",
                f"Charting the unknown..."
            ]
        }

        dialogue = random.choice(templates[action])
        return dialogue

    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """Analyze sentiment of text using TextBlob."""
        analysis = TextBlob(text)
        return analysis.sentiment.polarity