"""
Slow enemy bonus - makes enemies slower.
Port of server/model/Bonus/BonusEnemySlow.js
"""
from typing import Any, List

from .bonus_enemy import BonusEnemy
from ..base_avatar import BaseAvatar


class BonusEnemySlow(BonusEnemy):
    """Makes all enemy avatars slower."""
    
    duration = 6000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['velocity', -0.75 * BaseAvatar.DEFAULT_VELOCITY]]

