"""
Game bonus - affects the game itself.
Port of server/model/Bonus/BonusGame.js
"""
from typing import Any, TYPE_CHECKING

from .bonus import Bonus

if TYPE_CHECKING:
    from ..avatar import Avatar
    from ..game import Game


class BonusGame(Bonus):
    """
    Bonus that affects the game itself.
    """
    
    affect = 'game'
    
    def get_target(self, avatar: 'Avatar', game: 'Game') -> 'Game':
        """Get target (the game)."""
        return game
    
    def on(self) -> None:
        """Apply bonus effect."""
        if self.target:
            self.target.bonus_stack.add(self)
    
    def off(self) -> None:
        """Remove bonus effect."""
        if self.target:
            self.target.bonus_stack.remove(self)

