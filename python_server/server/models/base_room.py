"""
Base room class.
Port of shared/model/BaseRoom.js
"""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection

if TYPE_CHECKING:
    from .base_player import BasePlayer
    from .base_room_config import BaseRoomConfig
    from .game import Game


class BaseRoom(EventEmitter):
    """
    Base class for game rooms.
    """
    
    # Minimum players to start
    min_player = 1
    
    # Maximum name length
    max_length = 25
    
    # Launch countdown time (ms)
    launch_time = 5000
    
    def __init__(self, name: str):
        super().__init__()
        
        self.name = name
        self.players: Collection['BasePlayer'] = Collection([], 'id', True)
        self.config: Optional['BaseRoomConfig'] = None  # Set by subclass
        self.game: Optional['Game'] = None
        
        self._close_game = self.close_game
    
    def add_player(self, player: 'BasePlayer') -> bool:
        """Add a player to the room."""
        return self.players.add(player)
    
    def equal(self, room: Optional['BaseRoom']) -> bool:
        """Check if this room equals another."""
        return room is not None and self.name == room.name
    
    def is_name_available(self, name: str) -> bool:
        """Check if a player name is available."""
        return self.players.match(lambda p: p.name == name) is None
    
    def remove_player(self, player: 'BasePlayer') -> bool:
        """Remove a player from the room."""
        return self.players.remove(player)
    
    def is_ready(self) -> bool:
        """Check if room is ready to start."""
        if self.game:
            return False
        if self.players.count() < self.min_player:
            return False
        return self.players.filter(lambda p: not p.ready).is_empty()
    
    def new_game(self) -> Optional['Game']:
        """Create a new game."""
        if not self.game:
            from .game import Game
            self.game = Game(self)
            self.game.on('end', self._close_game)
            self.emit('game:new', {'room': self, 'game': self.game})
            return self.game
        return None
    
    def close_game(self, data: Any = None) -> None:
        """Close the current game."""
        if self.game:
            self.game = None
            self.emit('game:end', {'room': self})
            
            # Filter out disconnected players
            self.players = self.players.filter(lambda p: p.client is not None)
            
            # Reset remaining players
            for player in self.players.items:
                player.reset()
    
    def serialize(self, full: bool = True) -> Dict[str, Any]:
        """Serialize room info."""
        data = {
            'name': self.name,
            'players': [p.serialize() for p in self.players.items] if full else self.players.count(),
            'game': self.game is not None,
            'open': self.config.open if self.config else True
        }
        
        if full and self.config:
            data['config'] = self.config.serialize()
        
        return data

