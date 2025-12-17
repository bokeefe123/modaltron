"""
World class for game physics and collision detection.
Port of server/core/World.js
"""
import math
import random
from typing import List, Optional, Tuple, TYPE_CHECKING

from ..collection import Collection
from .island import Island
from .body import Body

if TYPE_CHECKING:
    pass


class World:
    """
    Represents the game world with spatial partitioning for efficient collision detection.
    """
    
    # Default island grid size
    island_grid_size = 40
    
    def __init__(self, size: float, islands: Optional[int] = None):
        if islands is None:
            islands = round(size / self.island_grid_size)
        
        self.size = size
        self.islands: Collection[Island] = Collection()
        self.island_size = self.size / islands
        self.active = False
        self.body_count = 0
        
        # Create islands for spatial partitioning
        for y in range(islands - 1, -1, -1):
            for x in range(islands - 1, -1, -1):
                island_id = f"{x}:{y}"
                island = Island(
                    island_id,
                    self.island_size,
                    x * self.island_size,
                    y * self.island_size
                )
                self.islands.add(island)
    
    def get_island_by_point(self, px: float, py: float) -> Optional[Island]:
        """Get the island responsible for the given point."""
        x = int(px / self.island_size)
        y = int(py / self.island_size)
        island_id = f"{x}:{y}"
        return self.islands.get_by_id(island_id)
    
    def add_body(self, body: Body) -> None:
        """Add a body to all concerned islands."""
        if not self.active:
            return
        
        body.id = self.body_count
        self.body_count += 1
        
        # Add to all islands that the body touches
        self._add_body_by_point(body, body.x - body.radius, body.y - body.radius)
        self._add_body_by_point(body, body.x + body.radius, body.y - body.radius)
        self._add_body_by_point(body, body.x - body.radius, body.y + body.radius)
        self._add_body_by_point(body, body.x + body.radius, body.y + body.radius)
    
    def _add_body_by_point(self, body: Body, x: float, y: float) -> None:
        """Add a body to an island if it covers the given point."""
        island = self.get_island_by_point(x, y)
        if island:
            island.add_body(body)
    
    def remove_body(self, body: Body) -> None:
        """Remove a body from all islands."""
        if not self.active:
            return
        
        for island in body.islands.items[:]:
            island.remove_body(body)
    
    def get_body(self, body: Body) -> Optional[Body]:
        """Get any body colliding with the given body."""
        return (
            self._get_body_by_point(body, body.x - body.radius, body.y - body.radius) or
            self._get_body_by_point(body, body.x + body.radius, body.y - body.radius) or
            self._get_body_by_point(body, body.x - body.radius, body.y + body.radius) or
            self._get_body_by_point(body, body.x + body.radius, body.y + body.radius)
        )
    
    def _get_body_by_point(self, body: Body, x: float, y: float) -> Optional[Body]:
        """Get a body colliding with the given body at a specific point."""
        island = self.get_island_by_point(x, y)
        return island.get_body(body) if island else None
    
    def test_body(self, body: Body) -> bool:
        """Test if the body position is free (no collisions)."""
        return (
            self._test_body_by_point(body, body.x - body.radius, body.y - body.radius) and
            self._test_body_by_point(body, body.x + body.radius, body.y - body.radius) and
            self._test_body_by_point(body, body.x - body.radius, body.y + body.radius) and
            self._test_body_by_point(body, body.x + body.radius, body.y + body.radius)
        )
    
    def _test_body_by_point(self, body: Body, x: float, y: float) -> bool:
        """Test if a body position is free at a specific point."""
        island = self.get_island_by_point(x, y)
        return island.test_body(body) if island else False
    
    def get_random_position(self, radius: float, border: float) -> Tuple[float, float]:
        """Get a random position that is free of bodies."""
        margin = radius + border * self.size
        body = Body(self._get_random_point(margin), self._get_random_point(margin), margin)
        
        # Keep trying until we find a free position
        max_attempts = 1000
        attempts = 0
        while not self.test_body(body) and attempts < max_attempts:
            body.x = self._get_random_point(margin)
            body.y = self._get_random_point(margin)
            attempts += 1
        
        return (body.x, body.y)
    
    def get_random_direction(self, x: float, y: float, tolerance: float) -> float:
        """Get a random direction that won't immediately hit a wall."""
        direction = self._get_random_angle()
        margin = tolerance * self.size
        
        max_attempts = 100
        attempts = 0
        while not self._is_direction_valid(direction, x, y, margin) and attempts < max_attempts:
            direction = self._get_random_angle()
            attempts += 1
        
        return direction
    
    def _is_direction_valid(self, angle: float, x: float, y: float, margin: float) -> bool:
        """Check if a direction is valid (won't hit wall too soon)."""
        quarter = math.pi / 2
        
        for i in range(4):
            from_angle = quarter * i
            to_angle = quarter * (i + 1)
            
            if from_angle <= angle < to_angle:
                if self._get_hypotenuse(angle - from_angle, self._get_distance_to_border(i, x, y)) < margin:
                    return False
                next_border = (i + 1) % 4
                if self._get_hypotenuse(to_angle - angle, self._get_distance_to_border(next_border, x, y)) < margin:
                    return False
                return True
        
        return True
    
    def _get_hypotenuse(self, angle: float, adjacent: float) -> float:
        """Calculate hypotenuse from adjacent side."""
        cos_val = math.cos(angle)
        if abs(cos_val) < 0.001:
            return float('inf')
        return adjacent / cos_val
    
    def _get_random_angle(self) -> float:
        """Get a random angle in radians."""
        return random.random() * math.pi * 2
    
    def _get_random_point(self, margin: float) -> float:
        """Get a random point within the world bounds."""
        return margin + random.random() * (self.size - margin * 2)
    
    def get_bound_intersect(self, body: Body, margin: float) -> Optional[Tuple[float, float]]:
        """Check if body intersects with world bounds."""
        if body.x - margin < 0:
            return (0, body.y)
        if body.x + margin > self.size:
            return (self.size, body.y)
        if body.y - margin < 0:
            return (body.x, 0)
        if body.y + margin > self.size:
            return (body.x, self.size)
        return None
    
    def get_opposite(self, x: float, y: float) -> Tuple[float, float]:
        """Get the opposite point (for borderless mode)."""
        if x == 0:
            return (self.size, y)
        if x == self.size:
            return (0, y)
        if y == 0:
            return (x, self.size)
        if y == self.size:
            return (x, 0)
        return (x, y)
    
    def _get_distance_to_border(self, border: int, x: float, y: float) -> float:
        """Get distance from a point to a border."""
        if border == 0:
            return self.size - x
        if border == 1:
            return self.size - y
        if border == 2:
            return x
        if border == 3:
            return y
        return 0
    
    def clear(self) -> None:
        """Clear the world."""
        self.active = False
        self.body_count = 0
        for island in self.islands.items:
            island.clear()
    
    def activate(self) -> None:
        """Activate the world for collision detection."""
        self.active = True

