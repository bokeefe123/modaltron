"""
Self bonus - affects the avatar who picks it up.
Port of server/model/Bonus/BonusSelf.js
"""
from typing import Any, TYPE_CHECKING

from .bonus import Bonus

if TYPE_CHECKING:
    from ..avatar import Avatar
    from ..game import Game


class BonusSelf(Bonus):
    """
    Bonus that affects the avatar who picks it up.
    """
    
    affect = 'self'
    
    def get_target(self, avatar: 'Avatar', game: 'Game') -> Any:
        """Get target (the picking avatar if alive)."""
        return avatar if avatar.alive else None
    
    def on(self) -> None:
        """Apply bonus effect."""
        if self.target:
            self.target.bonus_stack.add(self)
    
    def off(self) -> None:
        """Remove bonus effect."""
        if self.target:
            self.target.bonus_stack.remove(self)

