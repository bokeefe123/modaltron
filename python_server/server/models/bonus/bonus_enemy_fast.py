"""
Fast enemy bonus - makes enemies faster.
Port of server/model/Bonus/BonusEnemyFast.js
"""
from typing import Any, List

from .bonus_enemy import BonusEnemy
from ..base_avatar import BaseAvatar


class BonusEnemyFast(BonusEnemy):
    """Makes all enemy avatars faster."""
    
    duration = 6000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['velocity', 0.75 * BaseAvatar.DEFAULT_VELOCITY]]

