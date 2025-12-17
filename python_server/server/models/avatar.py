"""
Avatar class.
Port of server/model/Avatar.js
"""
from typing import Any, Dict, Optional, TYPE_CHECKING

from .base_avatar import BaseAvatar
from .trail import Trail
from .bonus_stack import BonusStack
from ..core.avatar_body import AvatarBody

if TYPE_CHECKING:
    from .player import Player
    from ..managers.print_manager import PrintManager


class Avatar(BaseAvatar):
    """
    Server-side avatar implementation with body tracking and events.
    """
    
    def __init__(self, player: 'Player'):
        super().__init__(player)
        
        self.body_count = 0
        self.body = AvatarBody(self.x, self.y, self)
        self.trail = Trail(self)
        self.bonus_stack = BonusStack(self)
        
        # Print manager handles trail printing logic
        from ..managers.print_manager import PrintManager
        self.print_manager = PrintManager(self)
    
    def update(self, step: float) -> None:
        """Update avatar for a frame."""
        if self.alive:
            self.update_angle(step)
            self.update_position(step)
            
            if self.printing and self.is_time_to_draw():
                self.add_point(self.x, self.y)
    
    def is_time_to_draw(self) -> bool:
        """Check if it's time to add a trail point."""
        if self.trail.last_x is None:
            return True
        return self.get_distance(self.trail.last_x, self.trail.last_y, self.x, self.y) > self.radius
    
    def set_position(self, x: float, y: float) -> None:
        """Set position and update body."""
        super().set_position(x, y)
        
        self.body.x = self.x
        self.body.y = self.y
        self.body.num = self.body_count
        
        self.emit('position', self)
    
    def set_velocity(self, velocity: float) -> None:
        """Set velocity and emit event."""
        if self.velocity != velocity:
            super().set_velocity(velocity)
            self.emit('property', {'avatar': self, 'property': 'velocity', 'value': self.velocity})
    
    def set_angle(self, angle: float) -> None:
        """Set angle and emit event."""
        if self.angle != angle:
            super().set_angle(angle)
            self.emit('angle', self)
    
    def set_angular_velocity(self, angular_velocity: float) -> None:
        """Set angular velocity."""
        if self.angular_velocity != angular_velocity:
            super().set_angular_velocity(angular_velocity)
    
    def set_radius(self, radius: float) -> None:
        """Set radius and emit event."""
        if self.radius != radius:
            super().set_radius(radius)
            self.body.radius = self.radius
            self.emit('property', {'avatar': self, 'property': 'radius', 'value': self.radius})
    
    def set_invincible(self, invincible: bool) -> None:
        """Set invincibility and emit event."""
        super().set_invincible(invincible)
        self.emit('property', {'avatar': self, 'property': 'invincible', 'value': self.invincible})
    
    def set_inverse(self, inverse: bool) -> None:
        """Set inverse controls and emit event."""
        super().set_inverse(inverse)
        self.emit('property', {'avatar': self, 'property': 'inverse', 'value': self.inverse})
    
    def set_color(self, color: str) -> None:
        """Set color and emit event."""
        self.color = color
        self.emit('property', {'avatar': self, 'property': 'color', 'value': self.color})
    
    def add_point(self, x: float, y: float, important: bool = False) -> None:
        """Add a trail point and emit event."""
        super().add_point(x, y)
        self.emit('point', {'avatar': self, 'x': x, 'y': y, 'important': important})
    
    def set_printing(self, printing: bool) -> None:
        """Set printing state and emit event."""
        super().set_printing(printing)
        self.emit('property', {'avatar': self, 'property': 'printing', 'value': self.printing})
    
    def die(self, body: Optional['AvatarBody'] = None) -> None:
        """Handle avatar death."""
        super().die()
        self.print_manager.stop()
        self.emit('die', {
            'avatar': self,
            'killer': body.data if body else None,
            'old': body.is_old() if body else None
        })
    
    def set_score(self, score: int) -> None:
        """Set score and emit event."""
        super().set_score(score)
        self.emit('score', self)
    
    def set_round_score(self, score: int) -> None:
        """Set round score and emit event."""
        super().set_round_score(score)
        self.emit('score:round', self)
    
    def clear(self) -> None:
        """Clear avatar for new round."""
        super().clear()
        self.print_manager.stop()
        self.body_count = 0

