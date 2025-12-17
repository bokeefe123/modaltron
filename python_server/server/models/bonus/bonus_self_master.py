"""
Master self bonus - makes the avatar invincible.
Port of server/model/Bonus/BonusSelfMaster.js
"""
from typing import Any, List

from .bonus_self import BonusSelf


class BonusSelfMaster(BonusSelf):
    """Makes the picking avatar invincible."""
    
    duration = 2000
    probability = 0.1
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['invincible', 1]]

