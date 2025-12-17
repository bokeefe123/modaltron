"""
Base bonus class for server.
Port of server/model/Bonus/Bonus.js
"""
import asyncio
from typing import Any, Optional, TYPE_CHECKING

from ..base_bonus import BaseBonus
from ...core.body import Body

if TYPE_CHECKING:
    from ..avatar import Avatar
    from ..game import Game


class Bonus(BaseBonus):
    """
    Server-side bonus implementation with body for collision detection.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.body = Body(self.x, self.y, self.radius, self)
        self.target: Any = None
        self.timeout_handle: Optional[asyncio.TimerHandle] = None
    
    def apply_to(self, avatar: 'Avatar', game: 'Game') -> None:
        """Apply bonus to avatar/game."""
        self.target = self.get_target(avatar, game)
        
        if self.duration:
            loop = asyncio.get_event_loop()
            self.timeout_handle = loop.call_later(self.duration / 1000, self.off)
        
        self.on()
    
    def get_target(self, avatar: 'Avatar', game: 'Game') -> Any:
        """Get the target for this bonus. Override in subclasses."""
        return avatar
    
    def on(self) -> None:
        """Apply bonus effect. Override in subclasses."""
        pass
    
    def off(self) -> None:
        """Remove bonus effect. Override in subclasses."""
        pass
    
    def clear(self) -> None:
        """Clear the bonus."""
        if self.timeout_handle:
            self.timeout_handle.cancel()
            self.timeout_handle = None

