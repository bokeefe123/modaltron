"""
Big enemy bonus - makes enemies bigger.
Port of server/model/Bonus/BonusEnemyBig.js
"""
from typing import Any, List

from .bonus_enemy import BonusEnemy


class BonusEnemyBig(BonusEnemy):
    """Makes all enemy avatars bigger."""
    
    duration = 7500
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['radius', 1]]

