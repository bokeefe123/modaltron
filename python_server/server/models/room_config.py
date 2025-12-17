"""
Room configuration.
Port of server/model/RoomConfig.js
"""
from typing import Any, Dict, List, Type, TYPE_CHECKING

from .base_room_config import BaseRoomConfig

if TYPE_CHECKING:
    from .room import Room
    from .bonus.bonus import Bonus


class RoomConfig(BaseRoomConfig):
    """
    Server-side room configuration with bonus type mappings.
    """
    
    def __init__(self, room: 'Room'):
        super().__init__(room)
        
        # Import bonus types lazily to avoid circular imports
        self._bonus_types: Dict[str, Type['Bonus']] = {}
    
    def _get_bonus_types(self) -> Dict[str, Type['Bonus']]:
        """Lazy load bonus types."""
        if not self._bonus_types:
            from .bonus import (
                BonusSelfSmall, BonusSelfSlow, BonusSelfFast, BonusSelfMaster,
                BonusEnemySlow, BonusEnemyFast, BonusEnemyBig, BonusEnemyInverse,
                BonusEnemyStraightAngle, BonusGameBorderless, BonusAllColor,
                BonusGameClear
            )
            self._bonus_types = {
                'BonusSelfSmall': BonusSelfSmall,
                'BonusSelfSlow': BonusSelfSlow,
                'BonusSelfFast': BonusSelfFast,
                'BonusSelfMaster': BonusSelfMaster,
                'BonusEnemySlow': BonusEnemySlow,
                'BonusEnemyFast': BonusEnemyFast,
                'BonusEnemyBig': BonusEnemyBig,
                'BonusEnemyInverse': BonusEnemyInverse,
                'BonusEnemyStraightAngle': BonusEnemyStraightAngle,
                'BonusGameBorderless': BonusGameBorderless,
                'BonusAllColor': BonusAllColor,
                'BonusGameClear': BonusGameClear
            }
        return self._bonus_types
    
    def set_open(self, open_state: bool) -> bool:
        """Set room open state."""
        if self.open != open_state:
            self.open = open_state
            self.password = None if self.open else self.generate_password()
            self.emit('room:config:open', {'room': self.room, 'open': self.open})
            return True
        return False
    
    def get_bonuses(self) -> List[Type['Bonus']]:
        """Get list of enabled bonus types."""
        bonus_types = self._get_bonus_types()
        return [bonus_types[name] for name, enabled in self.bonuses.items() if enabled and name in bonus_types]

