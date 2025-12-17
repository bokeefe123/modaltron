"""
Base bonus manager.
Port of shared/manager/BaseBonusManager.js
"""
from typing import TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection

if TYPE_CHECKING:
    from ..models.game import Game
    from ..models.bonus.bonus import Bonus


class BaseBonusManager(EventEmitter):
    """
    Base class for managing bonuses in the game.
    """
    
    # Maximum number of bonuses on the map
    bonus_cap = 20
    
    # Interval between bonus spawns (ms, varies x1 to x3)
    bonus_poping_time = 3000
    
    # Margin from bonus to trails
    bonus_poping_margin = 0.01
    
    def __init__(self, game: 'Game'):
        super().__init__()
        self.game = game
        self.bonuses: Collection['Bonus'] = Collection([], 'id', True)
    
    def start(self) -> None:
        """Start the bonus manager."""
        self.clear()
    
    def stop(self) -> None:
        """Stop the bonus manager."""
        self.clear()
    
    def add(self, bonus: 'Bonus') -> bool:
        """Add a bonus to the game."""
        return self.bonuses.add(bonus)
    
    def remove(self, bonus: 'Bonus') -> bool:
        """Remove a bonus from the game."""
        bonus.clear()
        return self.bonuses.remove(bonus)
    
    def clear(self) -> None:
        """Clear all bonuses."""
        for bonus in self.bonuses.items:
            bonus.clear()
        self.bonuses.clear()

