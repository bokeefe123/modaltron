"""
Avatar body for collision detection.
Port of server/core/AvatarBody.js
"""
import time
from typing import TYPE_CHECKING

from .body import Body

if TYPE_CHECKING:
    from ..models.avatar import Avatar


class AvatarBody(Body):
    """
    Represents an avatar's trail point for collision detection.
    """
    
    # Age considered "old" for collision feedback (milliseconds)
    old_age = 2000
    
    def __init__(self, x: float, y: float, avatar: 'Avatar'):
        super().__init__(x, y, avatar.radius, avatar)
        self.num = avatar.body_count
        avatar.body_count += 1
        self.birth = time.time() * 1000  # Store in milliseconds
    
    def match(self, body: 'Body') -> bool:
        """
        Check if this body should collide with another body.
        Avatars don't collide with their own recent trail points.
        """
        if isinstance(body, AvatarBody) and self.data.equal(body.data):
            # Don't collide with own recent trail
            return body.num - self.num > self.data.trail_latency
        return True
    
    def is_old(self) -> bool:
        """Check if this trail point is old (for UI feedback)."""
        return (time.time() * 1000) - self.birth >= self.old_age

