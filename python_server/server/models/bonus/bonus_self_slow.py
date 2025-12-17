"""
Slow self bonus - makes the avatar slower.
Port of server/model/Bonus/BonusSelfSlow.js
"""
from typing import Any, List

from .bonus_self import BonusSelf
from ..base_avatar import BaseAvatar


class BonusSelfSlow(BonusSelf):
    """Makes the picking avatar slower."""
    
    duration = 4000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['velocity', -0.5 * BaseAvatar.DEFAULT_VELOCITY]]

