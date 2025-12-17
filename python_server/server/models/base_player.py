"""
Base player class.
Port of shared/model/BasePlayer.js
"""
import re
import random
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter

if TYPE_CHECKING:
    from ..socket_client import SocketClient
    from .avatar import Avatar


class BasePlayer(EventEmitter):
    """
    Base class for players in the game.
    """
    
    # Maximum name length
    max_length = 25
    
    # Maximum color length
    color_max_length = 20
    
    def __init__(self, client: 'SocketClient', name: str, color: Optional[str] = None, ready: bool = False):
        super().__init__()
        
        self.client = client
        self.name = name
        self.color = color if color and self.validate_color(color) else self.get_random_color()
        self.ready = ready
        self.id: Optional[int] = None
        self.avatar: Optional['Avatar'] = None
    
    def set_name(self, name: str) -> None:
        """Set player name."""
        self.name = name
    
    def set_color(self, color: str) -> bool:
        """Set player color. Returns True if valid."""
        if not self.validate_color(color, yiq=True):
            return False
        self.color = color
        return True
    
    def equal(self, player: 'BasePlayer') -> bool:
        """Check if this player equals another."""
        return self.id == player.id
    
    def toggle_ready(self, toggle: Optional[bool] = None) -> None:
        """Toggle or set ready state."""
        if toggle is not None:
            self.ready = bool(toggle)
        else:
            self.ready = not self.ready
    
    def get_avatar(self) -> 'Avatar':
        """Get or create the player's avatar."""
        if not self.avatar:
            from .avatar import Avatar
            self.avatar = Avatar(self)
        return self.avatar
    
    def reset(self) -> None:
        """Reset player after a game."""
        if self.avatar:
            self.avatar.destroy()
            self.avatar = None
        self.ready = False
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize player info."""
        return {
            'client': self.client.id,
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'ready': self.ready
        }
    
    def get_random_color(self) -> str:
        """Generate a random valid color."""
        color = ''
        while not self.validate_color(color, yiq=True):
            r = random.randint(1, 255)
            g = random.randint(1, 255)
            b = random.randint(1, 255)
            color = f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def validate_color(self, color: str, yiq: bool = False) -> bool:
        """Validate a color string."""
        if not isinstance(color, str):
            return False
        
        match = re.match(r'^#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})$', color)
        
        if match and yiq:
            # Check brightness using YIQ formula
            r = int(match.group(1), 16)
            g = int(match.group(2), 16)
            b = int(match.group(3), 16)
            ratio = ((r * 0.4) + (g * 0.5) + (b * 0.3)) / 255
            return ratio > 0.3
        
        return match is not None

