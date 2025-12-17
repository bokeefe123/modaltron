"""
Small self bonus - makes the avatar smaller.
Port of server/model/Bonus/BonusSelfSmall.js
"""
from typing import Any, List

from .bonus_self import BonusSelf


class BonusSelfSmall(BonusSelf):
    """Makes the picking avatar smaller."""
    
    duration = 7500
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['radius', -1]]

