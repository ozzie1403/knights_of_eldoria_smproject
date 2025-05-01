from sklearn.cluster import KMeans
import numpy as np
from typing import List, Tuple, Optional
from models.location import Location
from utils.helpers import calculate_wrapped_distance


def cluster_locations(hunter_location: Location, target_locations: List[Location],
                      width: int, height: int, n_clusters: int = 3) -> List[List[Location]]:
    """
    Use K-means clustering to group locations based on proximity.

    Args:
        hunter_location: The hunter's current location
        target_locations: List of target locations to cluster
        width: Width of the grid
        height: Height of the grid
        n_clusters: Number of clusters to form

    Returns:
        List of location clusters, ordered by distance from hunter
    """
    if not target_locations:
        return []

    if len(target_locations) <= n_clusters:
        # No need to cluster if we have fewer points than clusters
        return [[loc] for loc in target_locations]

    # Convert locations to numpy array
    locations_array = np.array([[loc.x, loc.y] for loc in target_locations])

    # Determine actual number of clusters
    n_clusters = min(n_clusters, len(locations_array))

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(locations_array)

    # Calculate distance from hunter to each cluster center
    hunter_pos = np.array([[hunter_location.x, hunter_location.y]])
    cluster_centers = kmeans.cluster_centers_

    # Calculate wrapped distances (to handle grid wrapping)
    center_distances = []
    for center in cluster_centers:
        distance = calculate_wrapped_distance(
            hunter_location.x, hunter_location.y,
            int(center[0]), int(center[1]),
            width, height
        )
        center_distances.append(distance)

    # Sort clusters by distance from hunter
    sorted_clusters = []
    for i in np.argsort(center_distances):
        # Get all locations in this cluster
        cluster_locs = [target_locations[j] for j in range(len(target_locations))
                        if kmeans.labels_[j] == i]
        sorted_clusters.append(cluster_locs)

    return sorted_clusters


def predict_knight_movement(knight_location: Location, hunter_location: Location,
                            width: int, height: int) -> List[Location]:
    """
    Predict possible next moves for a knight based on hunter location.

    Args:
        knight_location: The knight's current location
        hunter_location: The hunter's current location
        width: Width of the grid
        height: Height of the grid

    Returns:
        List of possible next locations for the knight, sorted by probability
    """
    # Directions a knight can move
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    # Calculate direction from knight to hunter
    dx = (hunter_location.x - knight_location.x + width // 2) % width - width // 2
    dy = (hunter_location.y - knight_location.y + height // 2) % height - height // 2

    # Prioritize movements that bring knight closer to hunter
    if abs(dx) > abs(dy):
        # X-axis movement more important
        if dx > 0:
            # Hunter is to the right
            directions.sort(key=lambda d: d[0], reverse=True)
        else:
            # Hunter is to the left
            directions.sort(key=lambda d: d[0])
    else:
        # Y-axis movement more important
        if dy > 0:
            # Hunter is below
            directions.sort(key=lambda d: d[1], reverse=True)
        else:
            # Hunter is above
            directions.sort(key=lambda d: d[1])

    # Convert to locations
    possible_moves = []
    for dx, dy in directions:
        new_x = (knight_location.x + dx) % width
        new_y = (knight_location.y + dy) % height
        possible_moves.append(Location(new_x, new_y))

    return possible_moves