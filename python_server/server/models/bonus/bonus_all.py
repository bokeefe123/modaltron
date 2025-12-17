"""
All bonus - affects all avatars.
Port of server/model/Bonus/BonusAll.js
"""
from typing import Any, List, TYPE_CHECKING

from .bonus import Bonus

if TYPE_CHECKING:
    from ..avatar import Avatar
    from ..game import Game


class BonusAll(Bonus):
    """
    Bonus that affects all alive avatars.
    """
    
    affect = 'all'
    
    def get_target(self, avatar: 'Avatar', game: 'Game') -> List['Avatar']:
        """Get target (all alive avatars)."""
        return [a for a in game.avatars.items if a.alive]
    
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

