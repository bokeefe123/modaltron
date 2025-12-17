"""
Bonus stack for managing active bonuses on avatars.
Port of server/model/BonusStack.js
"""
from typing import Any, Dict, TYPE_CHECKING

from .base_bonus_stack import BaseBonusStack
from .base_avatar import BaseAvatar

if TYPE_CHECKING:
    from .base_bonus import BaseBonus
    from .avatar import Avatar


class BonusStack(BaseBonusStack):
    """
    Server-side bonus stack that emits events on changes.
    """
    
    def __init__(self, avatar: 'Avatar'):
        super().__init__(avatar)
    
    def add(self, bonus: 'BaseBonus') -> None:
        """Add a bonus to the stack."""
        super().add(bonus)
        self.emit('change', {'avatar': self.target, 'method': 'add', 'bonus': bonus})
    
    def remove(self, bonus: 'BaseBonus') -> None:
        """Remove a bonus from the stack."""
        super().remove(bonus)
        self.emit('change', {'avatar': self.target, 'method': 'remove', 'bonus': bonus})
    
    def apply(self, property: str, value: Any) -> None:
        """Apply a value to the target's property with special handling."""
        avatar = self.target
        
        if property == 'radius':
            avatar.set_radius(BaseAvatar.DEFAULT_RADIUS * (2 ** value))
        elif property == 'velocity':
            avatar.set_velocity(value)
        elif property == 'inverse':
            avatar.set_inverse(value % 2 != 0)
        elif property == 'invincible':
            avatar.set_invincible(bool(value))
        elif property == 'printing':
            if value > 0:
                avatar.print_manager.start()
            else:
                avatar.print_manager.stop()
        elif property == 'color':
            avatar.set_color(value)
        else:
            super().apply(property, value)
    
    def get_default_property(self, property: str) -> Any:
        """Get default property value."""
        if property == 'printing':
            return 1
        elif property == 'radius':
            return 0
        elif property == 'color':
            return self.target.player.color
        elif property == 'velocity':
            return BaseAvatar.DEFAULT_VELOCITY
        elif property == 'inverse':
            return 0  # Number of inverse bonuses active
        elif property == 'invincible':
            return 0  # Number of invincible bonuses active
        else:
            return 0
    
    def append(self, properties: Dict[str, Any], property: str, value: Any) -> None:
        """Append a value to a property."""
        if property in ('directionInLoop', 'angularVelocityBase', 'color'):
            # These properties are replaced, not added
            properties[property] = value
        else:
            super().append(properties, property, value)

