"""
Room class.
Port of server/model/Room.js
"""
from typing import TYPE_CHECKING

from .base_room import BaseRoom
from .room_config import RoomConfig

if TYPE_CHECKING:
    from .player import Player
    from ..controllers.room_controller import RoomController


class Room(BaseRoom):
    """
    Server-side room implementation.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.config = RoomConfig(self)
        
        # Controller is set after initialization
        self.controller: 'RoomController' = None
    
    def close(self) -> None:
        """Close the room."""
        self.emit('close', {'room': self})
    
    def add_player(self, player: 'Player') -> bool:
        """Add a player to the room."""
        result = super().add_player(player)
        if result:
            self.emit('player:join', {'room': self, 'player': player})
        return result
    
    def remove_player(self, player: 'Player') -> bool:
        """Remove a player from the room."""
        result = super().remove_player(player)
        if result:
            self.emit('player:leave', {'room': self, 'player': player})
        return result

