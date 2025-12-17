"""
Color all bonus - gives everyone the same random color.
Port of server/model/Bonus/BonusAllColor.js
"""
import random
from typing import Any, List

from .bonus_all import BonusAll


class BonusAllColor(BonusAll):
    """Changes all avatars to the same random color."""
    
    duration = 8000
    probability = 0.3
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.color = self._get_random_color()
    
    def _get_random_color(self) -> str:
        """Generate a random bright color."""
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def get_effects(self, avatar: Any) -> List[List[Any]]:
        return [['color', self.color]]

