"""
Straight angle enemy bonus - makes enemies turn at right angles.
Port of server/model/Bonus/BonusEnemyStraightAngle.js
"""
import math
from typing import Any, List

from .bonus_enemy import BonusEnemy
from ..base_avatar import BaseAvatar


class BonusEnemyStraightAngle(BonusEnemy):
    """Makes all enemy avatars turn at right angles only."""
    
    duration = 5000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [
            ['directionInLoop', False],
            ['angularVelocityBase', math.pi / 2]
        ]

