"""
Base room configuration.
Port of shared/model/BaseRoomConfig.js
"""
import random
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter

if TYPE_CHECKING:
    from .base_room import BaseRoom


class BaseRoomConfig(EventEmitter):
    """
    Base class for room configuration.
    """
    
    # Password length for private rooms
    password_length = 4
    
    def __init__(self, room: 'BaseRoom'):
        super().__init__()
        
        self.room = room
        self.max_score: Optional[int] = None
        self.open = True
        self.password: Optional[str] = None
        
        self.variables: Dict[str, float] = {
            'bonusRate': 0
        }
        
        self.bonuses: Dict[str, bool] = {
            'BonusSelfSmall': True,
            'BonusSelfSlow': True,
            'BonusSelfFast': True,
            'BonusSelfMaster': True,
            'BonusEnemySlow': True,
            'BonusEnemyFast': True,
            'BonusEnemyBig': True,
            'BonusEnemyInverse': True,
            'BonusEnemyStraightAngle': True,
            'BonusGameBorderless': True,
            'BonusAllColor': True,
            'BonusGameClear': True
        }
    
    def set_max_score(self, max_score: Any) -> bool:
        """Set maximum score."""
        try:
            max_score = int(max_score)
        except (ValueError, TypeError):
            max_score = None
        
        self.max_score = max_score if max_score else None
        return True
    
    def variable_exists(self, variable: str) -> bool:
        """Check if a variable exists."""
        return variable in self.variables
    
    def set_variable(self, variable: str, value: Any) -> bool:
        """Set a variable value."""
        if not self.variable_exists(variable):
            return False
        
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False
        
        if value < -1 or value > 1:
            return False
        
        self.variables[variable] = value
        return True
    
    def get_variable(self, variable: str) -> Optional[float]:
        """Get a variable value."""
        if not self.variable_exists(variable):
            return None
        return self.variables[variable]
    
    def bonus_exists(self, bonus: str) -> bool:
        """Check if a bonus exists."""
        return bonus in self.bonuses
    
    def toggle_bonus(self, bonus: str) -> bool:
        """Toggle a bonus on/off."""
        if not self.bonus_exists(bonus):
            return False
        self.bonuses[bonus] = not self.bonuses[bonus]
        return True
    
    def get_bonus(self, bonus: str) -> Optional[bool]:
        """Get bonus enabled state."""
        if not self.bonus_exists(bonus):
            return None
        return self.bonuses[bonus]
    
    def set_bonus(self, bonus: str, value: bool) -> None:
        """Set bonus enabled state."""
        if self.bonus_exists(bonus):
            self.bonuses[bonus] = bool(value)
    
    def get_max_score(self) -> int:
        """Get the max score (custom or default)."""
        return self.max_score if self.max_score else self.get_default_max_score()
    
    def get_default_max_score(self) -> int:
        """Get default max score based on player count."""
        return max(1, (self.room.players.count() - 1) * 10)
    
    def allow(self, password: Optional[str]) -> bool:
        """Check if joining is allowed."""
        return self.open or self.password == password
    
    def generate_password(self) -> str:
        """Generate a random password."""
        return ''.join(str(random.randint(1, 9)) for _ in range(self.password_length))
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize configuration."""
        return {
            'maxScore': self.max_score,
            'variables': self.variables,
            'bonuses': self.bonuses,
            'open': self.open,
            'password': self.password
        }

