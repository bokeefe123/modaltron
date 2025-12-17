"""
Room repository for managing game rooms.
Port of server/repository/RoomRepository.js
"""
from typing import Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection
from ..services.room_name_generator import RoomNameGenerator
from ..models.room import Room

if TYPE_CHECKING:
    pass


class RoomRepository(EventEmitter):
    """
    Repository for managing game rooms.
    """
    
    def __init__(self):
        super().__init__()
        self.generator = RoomNameGenerator()
        self.rooms: Collection[Room] = Collection([], 'name')
    
    def create(self, name: Optional[str] = None) -> Optional[Room]:
        """Create a new room."""
        if not name:
            name = self.get_random_room_name()
        
        room = Room(name)
        
        if not self.rooms.add(room):
            return None
        
        room.on('close', self._on_room_close)
        self.emit('room:open', {'room': room})
        
        # Initialize room controller
        from ..controllers.room_controller import RoomController
        room.controller = RoomController(room)
        
        return room
    
    def remove(self, room: Room) -> bool:
        """Remove a room."""
        if self.rooms.remove(room):
            self.emit('room:close', {'room': room})
            return True
        return False
    
    def get(self, name: str) -> Optional[Room]:
        """Get a room by name."""
        return self.rooms.get_by_id(name)
    
    def all(self) -> list:
        """Get all rooms."""
        return self.rooms.items
    
    def _on_room_close(self, data: dict) -> None:
        """Handle room close."""
        self.remove(data['room'])
    
    def get_random_room_name(self) -> str:
        """Get a unique random room name."""
        name = self.generator.get_name()
        while name in self.rooms.ids:
            name = self.generator.get_name()
        return name

