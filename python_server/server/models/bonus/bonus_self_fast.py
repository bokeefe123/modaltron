"""
Fast self bonus - makes the avatar faster.
Port of server/model/Bonus/BonusSelfFast.js
"""
from typing import Any, List

from .bonus_self import BonusSelf
from ..base_avatar import BaseAvatar


class BonusSelfFast(BonusSelf):
    """Makes the picking avatar faster."""
    
    duration = 4000
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['velocity', 0.5 * BaseAvatar.DEFAULT_VELOCITY]]

