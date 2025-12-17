"""
Body class for collision detection.
Port of server/core/Body.js
"""
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..collection import Collection


class Body:
    """
    Represents a physical body in the game world for collision detection.
    """
    
    def __init__(self, x: float, y: float, radius: float, data: Any = None):
        from ..collection import Collection
        
        self.x = x
        self.y = y
        self.radius = radius
        self.data = data
        self.islands: 'Collection' = Collection()
        self.id: Optional[int] = None
    
    def match(self, body: 'Body') -> bool:
        """
        Check if this body should collide with another body.
        Override in subclasses for custom collision logic.
        """
        return True

