from models.location import Location
from utils.helpers import calculate_wrapped_distance
from typing import List, Tuple, Dict, Set
import random
import math


class KMeansCluster:
    """K-means clustering for strategic decision making in the simulation."""

    def __init__(self, grid):
        self.grid = grid

    def cluster_locations(self, locations: List[Location], k: int, max_iterations: int = 10):
        """
        Cluster locations into k groups using K-means algorithm.

        Args:
            locations: List of locations to cluster
            k: Number of clusters
            max_iterations: Maximum number of iterations

        Returns:
            Dictionary mapping cluster index to list of locations in that cluster
        """
        if not locations:
            return {}

        if len(locations) <= k:
            # Not enough locations to make k clusters, just return each location as its own cluster
            return {i: [loc] for i, loc in enumerate(locations[:k])}

        # Initialize centroids randomly from the locations
        centroids = random.sample(locations, k)

        # Initialize clusters
        clusters = {}

        for _ in range(max_iterations):
            # Reset clusters
            clusters = {i: [] for i in range(k)}

            # Assign each location to the nearest centroid
            for location in locations:
                nearest_centroid_idx = self._find_nearest_centroid(location, centroids)
                clusters[nearest_centroid_idx].append(location)

            # Update centroids
            new_centroids = []
            for i in range(k):
                if clusters[i]:
                    new_centroid = self._calculate_centroid(clusters[i])
                    new_centroids.append(new_centroid)
                else:
                    # If a cluster is empty, keep the old centroid
                    new_centroids.append(centroids[i])

            # Check if centroids have changed
            if all(self._are_locations_equal(c1, c2) for c1, c2 in zip(centroids, new_centroids)):
                break

            centroids = new_centroids

        return clusters

    def _find_nearest_centroid(self, location: Location, centroids: List[Location]):
        """Find the index of the nearest centroid to a location."""
        min_distance = float('inf')
        nearest_idx = 0

        for i, centroid in enumerate(centroids):
            distance = calculate_wrapped_distance(
                location.x, location.y,
                centroid.x, centroid.y,
                self.grid.width, self.grid.height
            )

            if distance < min_distance:
                min_distance = distance
                nearest_idx = i

        return nearest_idx

    def _calculate_centroid(self, locations: List[Location]):
        """Calculate the centroid of a group of locations, accounting for wrap-around."""
        if not locations:
            return None

        # For a grid with wrap-around, we need to be careful about the center calculation
        # We'll use a circular mean approach

        # Convert to radians
        x_radians = [2 * math.pi * loc.x / self.grid.width for loc in locations]
        y_radians = [2 * math.pi * loc.y / self.grid.height for loc in locations]

        # Calculate averages of sin and cos
        x_sin_avg = sum(math.sin(rad) for rad in x_radians) / len(locations)
        x_cos_avg = sum(math.cos(rad) for rad in x_radians) / len(locations)
        y_sin_avg = sum(math.sin(rad) for rad in y_radians) / len(locations)
        y_cos_avg = sum(math.cos(rad) for rad in y_radians) / len(locations)

        # Convert back to grid coordinates
        x_angle = math.atan2(x_sin_avg, x_cos_avg)
        y_angle = math.atan2(y_sin_avg, y_cos_avg)

        x = int((x_angle / (2 * math.pi) * self.grid.width) % self.grid.width)
        y = int((y_angle / (2 * math.pi) * self.grid.height) % self.grid.height)

        return Location(x, y)

    def _are_locations_equal(self, loc1: Location, loc2: Location):
        """Check if two locations are equal."""
        return loc1.x == loc2.x and loc1.y == loc2.y

    def find_optimal_regions(self, treasure_locations: List[Location], knight_locations: List[Location],
                             num_regions: int):
        """
        Find optimal regions for hunters to explore based on treasure density and knight avoidance.

        Args:
            treasure_locations: Locations of known treasures
            knight_locations: Locations of known knights
            num_regions: Number of regions to identify

        Returns:
            List of Location objects representing the centers of optimal regions
        """
        if not treasure_locations:
            return []

        # Create a safety score map based on distance from knights
        safety_scores = {}
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                loc = Location(x, y)

                # Calculate minimum distance to knights
                min_knight_distance = float('inf')
                for knight_loc in knight_locations:
                    distance = calculate_wrapped_distance(
                        x, y, knight_loc.x, knight_loc.y,
                        self.grid.width, self.grid.height
                    )
                    min_knight_distance = min(min_knight_distance, distance)

                # Higher score for locations further from knights
                if knight_locations:
                    safety_scores[(x, y)] = min_knight_distance
                else:
                    safety_scores[(x, y)] = self.grid.width  # Maximum possible safety if no knights

        # Calculate treasure density scores
        treasure_clusters = self.cluster_locations(treasure_locations, min(num_regions, len(treasure_locations)))

        # Calculate the value of each cluster based on number of treasures
        cluster_values = {i: len(cluster) for i, cluster in treasure_clusters.items()}

        # Get the centroids of the clusters
        centroids = []
        for i in range(len(treasure_clusters)):
            if treasure_clusters[i]:
                centroid = self._calculate_centroid(treasure_clusters[i])
                centroids.append((centroid, cluster_values[i]))

        # Sort centroids by value (highest first)
        centroids.sort(key=lambda x: x[1], reverse=True)

        # Return the top regions, prioritizing safety and treasure density
        optimal_regions = []
        for centroid, _ in centroids[:num_regions]:
            # Find the safest cell near the centroid
            max_safety = -1
            best_location = centroid

            # Check cells in a small radius around the centroid
            radius = 3
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = (centroid.x + dx) % self.grid.width
                    y = (centroid.y + dy) % self.grid.height

                    safety = safety_scores.get((x, y), 0)
                    if safety > max_safety:
                        max_safety = safety
                        best_location = Location(x, y)

            optimal_regions.append(best_location)

        return optimal_regions