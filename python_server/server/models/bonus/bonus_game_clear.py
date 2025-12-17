"""
Clear game bonus - clears all trails.
Port of server/model/Bonus/BonusGameClear.js
"""
from typing import Any, List, TYPE_CHECKING

from .bonus_game import BonusGame
from ..base_bonus import BaseBonus

if TYPE_CHECKING:
    from ..game import Game


class BonusGameClear(BonusGame):
    """Clears all trails from the game."""
    
    duration = 0  # Instant effect
    
    def get_probability(self, game: 'Game') -> float:
        """Adjust probability based on game state."""
        alive_count = game.get_alive_avatars().count()
        present_count = game.get_present_avatars().count()
        
        if present_count == 0:
            return 0
        
        ratio = 1 - alive_count / present_count
        
        if ratio < 0.5:
            return self.probability
        
        return round((BaseBonus.probability - ratio) * 10) / 10
    
    def on(self) -> None:
        """Clear all trails."""
        if self.target:
            self.target.clear_trails()
    
    def get_effects(self, game: Any) -> List[List[Any]]:
        return []

