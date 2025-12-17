"""
Game bonus stack for managing game-wide bonuses.
Port of server/model/GameBonusStack.js (simplified)
"""
from typing import Any, Dict, TYPE_CHECKING

from .base_bonus_stack import BaseBonusStack

if TYPE_CHECKING:
    from .game import Game
    from .base_bonus import BaseBonus


class GameBonusStack(BaseBonusStack):
    """
    Bonus stack for game-wide effects.
    """
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
    
    def apply(self, property: str, value: Any) -> None:
        """Apply a value to the game's property."""
        game = self.target
        
        if property == 'borderless':
            game.set_borderless(bool(value))
        else:
            super().apply(property, value)
    
    def get_default_property(self, property: str) -> Any:
        """Get default property value."""
        from .base_game import BaseGame
        if property == 'borderless':
            return BaseGame.DEFAULT_BORDERLESS
        return 0

