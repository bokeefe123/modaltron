"""
Inverse enemy bonus - inverts enemy controls.
Port of server/model/Bonus/BonusEnemyInverse.js
"""
from typing import Any, List

from .bonus_enemy import BonusEnemy


class BonusEnemyInverse(BonusEnemy):
    """Inverts controls for all enemy avatars."""
    
    duration = 5000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['inverse', 1]]

