"""
Base avatar class.
Port of shared/model/BaseAvatar.js
"""
import math
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter

if TYPE_CHECKING:
    from .base_player import BasePlayer
    from .base_trail import BaseTrail
    from .base_bonus_stack import BaseBonusStack


class BaseAvatar(EventEmitter):
    """
    Base class for game avatars (snake-like characters).
    """
    
    # Default values (class constants)
    DEFAULT_VELOCITY = 16.0
    DEFAULT_ANGULAR_VELOCITY_BASE = 2.8 / 1000
    DEFAULT_RADIUS = 0.6
    DEFAULT_TRAIL_LATENCY = 3
    DEFAULT_INVERSE = False
    DEFAULT_INVINCIBLE = False
    DEFAULT_DIRECTION_IN_LOOP = True
    
    def __init__(self, player: 'BasePlayer'):
        super().__init__()
        
        self.id = player.id
        self.name = player.name
        self.color = player.color
        self.player = player
        
        self.x: float = 0
        self.y: float = 0
        self.angle: float = 0
        self.velocity_x: float = 0
        self.velocity_y: float = 0
        self.angular_velocity: float = 0
        self.alive: bool = True
        self.printing: bool = False
        self.score: int = 0
        self.round_score: int = 0
        self.ready: bool = False
        self.present: bool = True
        
        # Instance-specific overridable properties
        self._velocity = BaseAvatar.DEFAULT_VELOCITY
        self._radius = BaseAvatar.DEFAULT_RADIUS
        self._angular_velocity_base = BaseAvatar.DEFAULT_ANGULAR_VELOCITY_BASE
        self._inverse = BaseAvatar.DEFAULT_INVERSE
        self._invincible = BaseAvatar.DEFAULT_INVINCIBLE
        self._direction_in_loop = BaseAvatar.DEFAULT_DIRECTION_IN_LOOP
        self.trail_latency = BaseAvatar.DEFAULT_TRAIL_LATENCY
        
        # These are set by subclasses
        self.trail: Optional['BaseTrail'] = None
        self.bonus_stack: Optional['BaseBonusStack'] = None
    
    @property
    def velocity(self) -> float:
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: float):
        self._velocity = value
    
    @property
    def radius(self) -> float:
        return self._radius
    
    @radius.setter
    def radius(self, value: float):
        self._radius = value
    
    @property
    def angular_velocity_base(self) -> float:
        return self._angular_velocity_base
    
    @angular_velocity_base.setter
    def angular_velocity_base(self, value: float):
        self._angular_velocity_base = value
    
    @property
    def inverse(self) -> bool:
        return self._inverse
    
    @inverse.setter
    def inverse(self, value: bool):
        self._inverse = value
    
    @property
    def invincible(self) -> bool:
        return self._invincible
    
    @invincible.setter
    def invincible(self, value: bool):
        self._invincible = value
    
    @property
    def direction_in_loop(self) -> bool:
        return self._direction_in_loop
    
    @direction_in_loop.setter
    def direction_in_loop(self, value: bool):
        self._direction_in_loop = value
    
    def equal(self, avatar: 'BaseAvatar') -> bool:
        """Check if this avatar equals another."""
        return self.id == avatar.id
    
    def set_position(self, x: float, y: float) -> None:
        """Set the avatar's position."""
        self.x = x
        self.y = y
    
    def add_point(self, x: float, y: float) -> None:
        """Add a point to the trail."""
        if self.trail:
            self.trail.add_point(x, y)
    
    def update_angular_velocity(self, factor: Optional[float] = None) -> None:
        """Update angular velocity based on a factor."""
        if factor is None:
            if self.angular_velocity == 0:
                return
            factor = (1 if self.angular_velocity > 0 else -1) * (-1 if self.inverse else 1)
        
        self.set_angular_velocity(factor * self.angular_velocity_base * (-1 if self.inverse else 1))
    
    def set_angular_velocity(self, angular_velocity: float) -> None:
        """Set the angular velocity."""
        self.angular_velocity = angular_velocity
    
    def set_angle(self, angle: float) -> None:
        """Set the avatar's angle."""
        if self.angle != angle:
            self.angle = angle
            self.update_velocities()
    
    def update(self, step: float) -> None:
        """Update the avatar (override in subclasses)."""
        pass
    
    def update_angle(self, step: float) -> None:
        """Update the angle based on angular velocity."""
        if self.angular_velocity:
            if self.direction_in_loop:
                self.set_angle(self.angle + self.angular_velocity * step)
            else:
                self.set_angle(self.angle + self.angular_velocity)
                self.update_angular_velocity(0)
    
    def update_position(self, step: float) -> None:
        """Update position based on velocity."""
        self.set_position(
            self.x + self.velocity_x * step,
            self.y + self.velocity_y * step
        )
    
    def set_velocity(self, velocity: float) -> None:
        """Set the movement velocity."""
        velocity = max(velocity, BaseAvatar.DEFAULT_VELOCITY / 2)
        if self.velocity != velocity:
            self._velocity = velocity
            self.update_velocities()
    
    def update_velocities(self) -> None:
        """Update x/y velocity components based on angle."""
        velocity = self.velocity / 1000
        self.velocity_x = math.cos(self.angle) * velocity
        self.velocity_y = math.sin(self.angle) * velocity
        self.update_base_angular_velocity()
    
    def update_base_angular_velocity(self) -> None:
        """Update base angular velocity based on movement speed."""
        if self.direction_in_loop:
            ratio = self.velocity / BaseAvatar.DEFAULT_VELOCITY
            self._angular_velocity_base = ratio * BaseAvatar.DEFAULT_ANGULAR_VELOCITY_BASE + math.log(1 / ratio) / 1000
            self.update_angular_velocity()
    
    def set_radius(self, radius: float) -> None:
        """Set the collision radius."""
        self._radius = max(radius, BaseAvatar.DEFAULT_RADIUS / 8)
    
    def set_inverse(self, inverse: bool) -> None:
        """Set inverted controls."""
        if self.inverse != inverse:
            self._inverse = bool(inverse)
            self.update_angular_velocity()
    
    def set_invincible(self, invincible: bool) -> None:
        """Set invincibility."""
        self._invincible = bool(invincible)
    
    def get_distance(self, from_x: float, from_y: float, to_x: float, to_y: float) -> float:
        """Calculate distance between two points."""
        return math.sqrt((from_x - to_x) ** 2 + (from_y - to_y) ** 2)
    
    def die(self) -> None:
        """Handle avatar death."""
        if self.bonus_stack:
            self.bonus_stack.clear()
        self.alive = False
        self.add_point(self.x, self.y)
    
    def set_printing(self, printing: bool) -> None:
        """Set whether the avatar is printing trail."""
        printing = bool(printing)
        if self.printing != printing:
            self.printing = printing
            self.add_point(self.x, self.y)
            if not self.printing and self.trail:
                self.trail.clear()
    
    def add_score(self, score: int) -> None:
        """Add to round score."""
        self.set_round_score(self.round_score + score)
    
    def resolve_score(self) -> None:
        """Resolve round score into total score."""
        self.set_score(self.score + self.round_score)
        self.round_score = 0
    
    def set_round_score(self, score: int) -> None:
        """Set round score."""
        self.round_score = score
    
    def set_score(self, score: int) -> None:
        """Set total score."""
        self.score = score
    
    def set_color(self, color: str) -> None:
        """Set avatar color."""
        self.color = color
    
    def clear(self) -> None:
        """Clear/reset the avatar for a new round."""
        if self.bonus_stack:
            self.bonus_stack.clear()
        
        self.x = self.radius
        self.y = self.radius
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.round_score = 0
        self._velocity = BaseAvatar.DEFAULT_VELOCITY
        self.alive = True
        self.printing = False
        self.color = self.player.color
        self._radius = BaseAvatar.DEFAULT_RADIUS
        self._inverse = BaseAvatar.DEFAULT_INVERSE
        self._invincible = BaseAvatar.DEFAULT_INVINCIBLE
        self._direction_in_loop = BaseAvatar.DEFAULT_DIRECTION_IN_LOOP
        self._angular_velocity_base = BaseAvatar.DEFAULT_ANGULAR_VELOCITY_BASE
    
    def destroy(self) -> None:
        """Destroy the avatar."""
        self.clear()
        self.present = False
        self.alive = False
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize avatar info."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'score': self.score
        }

