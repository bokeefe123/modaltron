"""
Base bonus class.
Port of shared/model/BaseBonus.js
"""
from typing import Any, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter

if TYPE_CHECKING:
    from .base_avatar import BaseAvatar
    from .base_game import BaseGame


class BaseBonus(EventEmitter):
    """
    Base class for all bonus types.
    """
    
    # Target affected: 'self', 'enemy', 'all', 'game'
    affect = 'self'
    
    # Collision radius
    radius = 3.0
    
    # Effect duration in milliseconds
    duration = 5000
    
    # Probability to appear (0-1)
    probability = 1.0
    
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self.id: Optional[int] = None
    
    def clear(self) -> None:
        """Clear the bonus."""
        pass
    
    def apply_to(self, avatar: 'BaseAvatar', game: 'BaseGame') -> None:
        """Apply the bonus to a target."""
        pass
    
    def get_probability(self, game: 'BaseGame') -> float:
        """Get the probability of this bonus appearing."""
        return self.probability
    
    def get_effects(self, target: Any) -> List[List[Any]]:
        """Get the effects of this bonus. Override in subclasses."""
        return []

