"""
Island class for spatial partitioning.
Port of server/core/Island.js
"""
import math
from typing import Optional, TYPE_CHECKING

from ..collection import Collection

if TYPE_CHECKING:
    from .body import Body


class Island:
    """
    Represents a region of the game world for spatial partitioning.
    Used to optimize collision detection by only checking bodies in nearby regions.
    """
    
    def __init__(self, id: str, size: float, x: float, y: float):
        self.id = id
        self.size = size
        self.from_x = x
        self.from_y = y
        self.to_x = x + size
        self.to_y = y + size
        self.bodies: Collection['Body'] = Collection([], 'id')
    
    def add_body(self, body: 'Body') -> None:
        """Add a body to this island."""
        if self.bodies.add(body):
            body.islands.add(self)
    
    def remove_body(self, body: 'Body') -> None:
        """Remove a body from this island."""
        self.bodies.remove(body)
        body.islands.remove(self)
    
    def test_body(self, body: 'Body') -> bool:
        """Test if the given body position is free (no collisions)."""
        return self.get_body(body) is None
    
    def get_body(self, body: 'Body') -> Optional['Body']:
        """Get the first body that collides with the given body."""
        if self.body_in_bound(body, self.from_x, self.from_y, self.to_x, self.to_y):
            for other in self.bodies.items:
                if self.bodies_touch(other, body):
                    return other
        return None
    
    def bodies_touch(self, body_a: 'Body', body_b: 'Body') -> bool:
        """Check if two bodies are touching."""
        distance = self.get_distance(body_a.x, body_a.y, body_b.x, body_b.y)
        radius = body_a.radius + body_b.radius
        match = body_a.match(body_b)
        return distance < radius and match
    
    def body_in_bound(self, body: 'Body', from_x: float, from_y: float, to_x: float, to_y: float) -> bool:
        """Check if a body is within bounds."""
        return (body.x + body.radius > from_x and
                body.x - body.radius < to_x and
                body.y + body.radius > from_y and
                body.y - body.radius < to_y)
    
    def get_distance(self, from_x: float, from_y: float, to_x: float, to_y: float) -> float:
        """Calculate distance between two points."""
        return math.sqrt((from_x - to_x) ** 2 + (from_y - to_y) ** 2)
    
    def clear(self) -> None:
        """Clear all bodies from this island."""
        self.bodies.clear()

