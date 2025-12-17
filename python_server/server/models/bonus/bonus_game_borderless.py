"""
Borderless game bonus - removes map borders.
Port of server/model/Bonus/BonusGameBorderless.js
"""
from typing import Any, List

from .bonus_game import BonusGame


class BonusGameBorderless(BonusGame):
    """Removes map borders temporarily."""
    
    duration = 8000
    
    def get_effects(self, game: Any) -> List[List[Any]]:
        return [['borderless', 1]]

