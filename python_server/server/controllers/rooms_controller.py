"""
Rooms controller for managing room listing and creation.
Port of server/controller/RoomsController.js
"""
from typing import Any, Callable, Dict, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..core.socket_group import SocketGroup
from ..models.room import Room

if TYPE_CHECKING:
    from ..socket_client import SocketClient
    from ..repositories.room_repository import RoomRepository


class RoomsController(EventEmitter):
    """
    Controller for managing the room list.
    """
    
    def __init__(self, repository: 'RoomRepository'):
        super().__init__()
        
        self.socket_group = SocketGroup()
        self.repository = repository
        
        self.repository.on('room:open', self._on_room_open)
        self.repository.on('room:close', self._on_room_close)
    
    def attach(self, client: 'SocketClient') -> None:
        """Attach a client to receive room updates."""
        if self.socket_group.clients.add(client):
            self._attach_events(client)
    
    def detach(self, client: 'SocketClient') -> None:
        """Detach a client from room updates."""
        if self.socket_group.clients.remove(client):
            self._detach_events(client)
    
    def _attach_events(self, client: 'SocketClient') -> None:
        """Attach event handlers for a client."""
        client.on('close', lambda data: self.detach(client))
        client.on('room:fetch', lambda data: self._emit_all_rooms(client))
        client.on('room:create', lambda data: self._on_create_room(client, data[0], data[1]))
        client.on('room:join', lambda data: self._on_join_room(client, data[0], data[1]))
    
    def _detach_events(self, client: 'SocketClient') -> None:
        """Detach event handlers for a client."""
        # Would need to store references to properly remove listeners
        pass
    
    def _emit_all_rooms(self, client: 'SocketClient') -> None:
        """Send all rooms to a client."""
        events = []
        for room in self.repository.rooms.items:
            events.append(['room:open', room.serialize(full=False)])
        client.add_events(events)
    
    def _on_create_room(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        """Handle room creation request."""
        name = data['name'][:Room.max_length].strip() if data.get('name') else None
        room = self.repository.create(name)
        
        if room:
            callback({'success': True, 'room': room.serialize(full=False)})
            self.emit('room:new', {'room': room})
        else:
            callback({'success': False})
    
    def _on_join_room(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        """Handle room join request."""
        room = self.repository.get(data['name'])
        
        if not room:
            return callback({'success': False, 'error': f'Unknown room "{data["name"]}".'})
        
        password = data.get('password')
        
        if not room.config.allow(password):
            return callback({'success': False, 'error': 'Wrong password.'})
        
        room.controller.attach(client, callback)
    
    def _on_room_open(self, data: Dict) -> None:
        """Handle room open event."""
        room = data['room']
        
        room.on('game:new', self._on_room_game)
        room.on('game:end', self._on_room_game)
        room.on('player:join', self._on_room_player)
        room.on('player:leave', self._on_room_player)
        room.config.on('room:config:open', self._on_room_config_open)
        
        self.socket_group.add_event('room:open', room.serialize(full=False))
    
    def _on_room_close(self, data: Dict) -> None:
        """Handle room close event."""
        room = data['room']
        
        room.remove_listener('game:new', self._on_room_game)
        room.remove_listener('game:end', self._on_room_game)
        room.remove_listener('player:join', self._on_room_player)
        room.remove_listener('player:leave', self._on_room_player)
        room.config.remove_listener('room:config:open', self._on_room_config_open)
        
        self.socket_group.add_event('room:close', {'name': room.name})
    
    def _on_room_config_open(self, data: Dict) -> None:
        """Handle room config open change."""
        self.socket_group.add_event('room:config:open', {
            'name': data['room'].name,
            'open': data['open']
        })
    
    def _on_room_player(self, data: Dict) -> None:
        """Handle player join/leave."""
        room_data = data['room'].serialize(full=False)
        self.socket_group.add_event('room:players', {
            'name': room_data['name'],
            'players': room_data['players']
        })
    
    def _on_room_game(self, data: Dict) -> None:
        """Handle room game start/end."""
        room_data = data['room'].serialize(full=False)
        self.socket_group.add_event('room:game', {
            'name': room_data['name'],
            'game': room_data['game']
        })

