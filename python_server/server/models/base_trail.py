"""
Base trail class for avatar trails.
Port of shared/model/BaseTrail.js
"""
from typing import List, Tuple, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter

if TYPE_CHECKING:
    from .base_avatar import BaseAvatar


class BaseTrail(EventEmitter):
    """
    Base class for avatar trails.
    Tracks points where the avatar has been.
    """
    
    def __init__(self, avatar: 'BaseAvatar'):
        super().__init__()
        self.avatar = avatar
        self.color = avatar.color
        self.radius = avatar.radius
        self.points: List[Tuple[float, float]] = []
        self.last_x: Optional[float] = None
        self.last_y: Optional[float] = None
    
    def add_point(self, x: float, y: float) -> None:
        """Add a point to the trail."""
        self.points.append((x, y))
        self.last_x = x
        self.last_y = y
    
    def clear(self) -> None:
        """Clear the trail."""
        self.points.clear()
        self.last_x = None
        self.last_y = None

