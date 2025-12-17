"""
Enemy bonus - affects all other avatars.
Port of server/model/Bonus/BonusEnemy.js
"""
from typing import Any, List, TYPE_CHECKING

from .bonus import Bonus

if TYPE_CHECKING:
    from ..avatar import Avatar
    from ..game import Game


class BonusEnemy(Bonus):
    """
    Bonus that affects all avatars except the one who picks it up.
    """
    
    affect = 'enemy'
    
    def get_target(self, avatar: 'Avatar', game: 'Game') -> List['Avatar']:
        """Get target (all other alive avatars)."""
        return [a for a in game.avatars.items if a.alive and not a.equal(avatar)]
    
    def on(self) -> None:
        """Apply bonus effect to all targets."""
        if self.target:
            for avatar in self.target:
                avatar.bonus_stack.add(self)
    
    def off(self) -> None:
        """Remove bonus effect from all targets."""
        if self.target:
            for avatar in self.target:
                avatar.bonus_stack.remove(self)

