from typing import List, Tuple, Dict, Optional
from models.location import Location
from utils.helpers import calculate_wrapped_distance
from utils.constants import EntityType, HunterSkill
import random
from sklearn.cluster import KMeans
import numpy as np

def find_nearest_entity(current_location: Location, locations: List[Location], 
                        width: int, height: int) -> Optional[Location]:
    """Find the nearest entity location from a list of locations."""
    if not locations:
        return None
    
    nearest = None
    min_distance = float('inf')
    
    for location in locations:
        distance = calculate_wrapped_distance(
            current_location.x, current_location.y,
            location.x, location.y,
            width, height
        )
        if distance < min_distance:
            min_distance = distance
            nearest = location
    
    return nearest

def cluster_treasure_locations(hunter_location: Location, treasure_locations: List[Location], 
                               width: int, height: int) -> Optional[Location]:
    """Use K-means clustering to find the best treasure to target."""
    if not treasure_locations:
        return None
    
    if len(treasure_locations) == 1:
        return treasure_locations[0]
    
    # Convert locations to numpy array
    locations_array = np.array([[loc.x, loc.y] for loc in treasure_locations])
    
    # Determine number of clusters (at most 3, but depends on data)
    n_clusters = min(3, len(locations_array))
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(locations_array)
    
    # Find the closest cluster center to the hunter
    hunter_pos = np.array([[hunter_location.x, hunter_location.y]])
    distances = np.linalg.norm(kmeans.cluster_centers_ - hunter_pos, axis=1)
    closest_cluster = np.argmin(distances)
    
    # Get the treasures in the closest cluster
    mask = kmeans.labels_ == closest_cluster
    cluster_treasures = [treasure_locations[i] for i in range(len(treasure_locations)) if mask[i]]
    
    # Return the closest treasure in that cluster
    return find_nearest_entity(hunter_location, cluster_treasures, width, height)

def decide_hunter_action(hunter, grid):
    """Decide the next action for a treasure hunter using AI techniques."""
    # If carrying treasure, bring it to a hideout
    if hunter.carrying_treasure_value > 0:
        if hunter.known_hideout_locations:
            return "deposit", find_nearest_entity(
                hunter.location, 
                list(hunter.known_hideout_locations),
                grid.width, grid.height
            )
        return "explore", None
    
    # If stamina is critically low, find a hideout to rest
    if hunter.stamina <= hunter.critical_stamina:
        if hunter.known_hideout_locations:
            return "rest", find_nearest_entity(
                hunter.location,
                list(hunter.known_hideout_locations),
                grid.width, grid.height
            )
        return "explore", None
    
    # If there are known treasures, use clustering to decide which to pursue
    if hunter.known_treasure_locations:
        target = cluster_treasure_locations(
            hunter.location,
            list(hunter.known_treasure_locations),
            grid.width, grid.height
        )
        if target:
            # Verify it's still there
            entity = grid.get_entity_at(target)
            if entity and entity.type == EntityType.TREASURE:
                return "collect", target
            else:
                # Remove from known locations if treasure is gone
                hunter.knowledge.remove_treasure_location(target)
    
    # If no known treasure or target is invalid, explore
    return "explore", None

def decide_knight_action(knight, grid):
    """Decide the next action for a knight."""
    # If resting, continue resting
    if knight.resting:
        return "rest", None
    
    # If energy is critically low, rest
    if knight.energy <= knight.critical_energy:
        return "rest", None
    
    # Check for hunters in detection radius
    nearby_hunters = grid.get_nearby_entities(
        knight.location, 
        knight.detection_radius,
        EntityType.HUNTER
    )
    
    # If we have a target, continue pursuit
    if knight.target and knight.target in grid.entities:
        distance = calculate_wrapped_distance(
            knight.location.x, knight.location.y,
            knight.target.location.x, knight.target.location.y,
            grid.width, grid.height
        )
        # If we caught the target
        if distance < 1.5:
            return "catch", knight.target
        # Continue pursuit
        return "pursue", knight.target.location
    
    # If no current target but hunters detected, choose one
    if nearby_hunters:
        # If hunter has stealth skill, they're less likely to be detected
        detectable_hunters = []
        for hunter in nearby_hunters:
            if hunter.skill == HunterSkill.STEALTH:
                if random.random() < 0.5:  # 50% chance to remain undetected
                    detectable_hunters.append(hunter)
            else:
                detectable_hunters.append(hunter)
        
        if detectable_hunters:
            target = random.choice(detectable_hunters)
            return "target", target
    
    # No hunters detected, patrol randomly
    return "patrol", None