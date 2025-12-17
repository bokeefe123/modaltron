"""
Room controller for managing room interactions.
Port of server/controller/RoomController.js
"""
import asyncio
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection
from ..core.socket_group import SocketGroup
from ..models.player import Player
from ..models.message import Message

if TYPE_CHECKING:
    from ..models.room import Room
    from ..socket_client import SocketClient


class Chat:
    """Simple chat message storage."""
    
    def __init__(self):
        self.messages: List['Message'] = []
    
    def add_message(self, message: 'Message') -> bool:
        self.messages.append(message)
        return True
    
    def serialize(self, limit: int = 100) -> List[Dict]:
        return [m.serialize() for m in self.messages[-limit:]]


class RoomController(EventEmitter):
    """
    Controller for managing room interactions.
    """
    
    # Time before closing an empty room (ms)
    time_to_close = 10000
    
    def __init__(self, room: 'Room'):
        super().__init__()
        
        self.room = room
        self.clients: Collection['SocketClient'] = Collection()
        self.socket_group = SocketGroup(self.clients)
        self.chat = Chat()
        self.room_master: Optional['SocketClient'] = None
        self.launching: Optional[asyncio.TimerHandle] = None
        
        room.controller = self
        self._load_room()
        self._prompt_check_for_close()
    
    def _load_room(self) -> None:
        """Load room and attach event handlers."""
        self.room.on('close', self._unload_room)
        self.room.on('player:join', self._on_player_join)
        self.room.on('player:leave', self._on_player_leave)
        self.room.on('game:new', self._on_game)
    
    def _unload_room(self, data: Any = None) -> None:
        """Unload room."""
        self.room.remove_listener('close', self._unload_room)
        self.room.remove_listener('player:join', self._on_player_join)
        self.room.remove_listener('player:leave', self._on_player_leave)
        self.room.remove_listener('game:new', self._on_game)
    
    def attach(self, client: 'SocketClient', callback: Callable) -> None:
        """Attach a client to the room."""
        if self.clients.add(client):
            self._attach_events(client)
            self._on_client_add(client)
            callback({
                'success': True,
                'room': self.room.serialize(),
                'master': self.room_master.id if self.room_master else None,
                'clients': [c.serialize() for c in self.clients.items],
                'messages': self.chat.serialize(100),
                'votes': []  # Kick votes simplified
            })
            self.socket_group.add_event('client:add', client.id)
            self.emit('client:add', {'room': self.room, 'client': client})
        else:
            callback({'success': False, 'error': f'Client {client.id} already in the room.'})
    
    def detach(self, client: 'SocketClient') -> None:
        """Detach a client from the room."""
        if self.clients.remove(client):
            if self.room.game:
                self.room.game.controller.detach(client)
            
            client.clear_players()
            self._detach_events(client)
            self._prompt_check_for_close()
            self.socket_group.add_event('client:remove', client.id)
            self.emit('client:remove', {'room': self.room, 'client': client})
    
    def _attach_events(self, client: 'SocketClient') -> None:
        """Attach event handlers for a client."""
        client.on('close', lambda data: self._on_leave(client))
        client.on('room:leave', lambda data: self._on_leave(client))
        client.on('room:talk', lambda data: self._on_talk(client, data[0], data[1]))
        client.on('player:add', lambda data: self._on_player_add(client, data[0], data[1]))
        client.on('player:remove', lambda data: self._on_player_remove(client, data[0], data[1]))
        client.on('room:ready', lambda data: self._on_ready(client, data[0], data[1]))
        client.on('room:color', lambda data: self._on_color(client, data[0], data[1]))
        client.on('room:name', lambda data: self._on_name(client, data[0], data[1]))
        client.on('players:clear', lambda data: self._on_players_clear(client))
    
    def _detach_events(self, client: 'SocketClient') -> None:
        """Detach event handlers for a client."""
        # Would need to store references to properly remove listeners
        pass
    
    def remove_player(self, player: Player) -> None:
        """Remove a player from the room."""
        client = player.client
        if self.room.remove_player(player) and client:
            client.players.remove(player)
            
            if not client.is_playing():
                if self.room_master and self.room_master.id == client.id:
                    self._remove_room_master()
    
    def _nominate_room_master(self) -> None:
        """Nominate a new room master."""
        if self.clients.is_empty() or self.room_master:
            return
        
        room_master = self.clients.match(lambda c: c.active and c.is_playing())
        self._set_room_master(room_master)
    
    def _set_room_master(self, client: Optional['SocketClient']) -> None:
        """Set the room master."""
        if not self.room_master and client:
            self.room_master = client
            # Attach room master specific events
            client.on('room:config:open', lambda data: self._on_config_open(client, data[0], data[1]))
            client.on('room:config:max-score', lambda data: self._on_config_max_score(client, data[0], data[1]))
            client.on('room:launch', lambda data: self._on_launch(client))
            self.socket_group.add_event('room:master', {'client': client.id})
    
    def _remove_room_master(self) -> None:
        """Remove the current room master."""
        if self.room_master:
            self.room_master = None
            self._nominate_room_master()
    
    def _on_client_add(self, client: 'SocketClient') -> None:
        """Handle new client."""
        client.clear_players()
        
        if self.room.game:
            self.room.game.controller.attach(client)
            client.add_event('room:game:start')
        
        self.socket_group.add_event('client:add', {'client': client.serialize()})
        self._nominate_room_master()
    
    def _prompt_check_for_close(self) -> None:
        """Schedule check for closing empty room."""
        if self.clients.is_empty():
            loop = asyncio.get_event_loop()
            loop.call_later(self.time_to_close / 1000, self._check_for_close)
    
    def _check_for_close(self) -> None:
        """Check if room should be closed."""
        if self.clients.is_empty():
            self.room.close()
    
    def _start_launch(self) -> None:
        """Start launch countdown."""
        if not self.launching:
            loop = asyncio.get_event_loop()
            self.launching = loop.call_later(self.room.launch_time / 1000, self._launch)
            self.socket_group.add_event('room:launch:start')
    
    def _cancel_launch(self) -> None:
        """Cancel launch countdown."""
        if self.launching:
            self.launching.cancel()
            self.launching = None
            self.socket_group.add_event('room:launch:cancel')
    
    def _launch(self) -> None:
        """Launch the game."""
        if self.launching:
            self.launching.cancel()
            self.launching = None
        self.room.new_game()
    
    # Event handlers
    def _on_leave(self, client: 'SocketClient') -> None:
        self.detach(client)
    
    def _on_players_clear(self, client: 'SocketClient') -> None:
        for player in list(client.players.items):
            self.remove_player(player)
    
    def _on_player_add(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        name = data['name'][:Player.max_length].strip()
        color = data.get('color')
        
        if not name:
            return callback({'success': False, 'error': 'Invalid name.'})
        
        if self.room.game:
            return callback({'success': False, 'error': 'Game already started.'})
        
        if not self.room.is_name_available(name):
            return callback({'success': False, 'error': 'This username is already used.'})
        
        if not self.clients.exists(client):
            return callback({'success': False, 'error': 'Unknown client'})
        
        player = Player(client, name, color)
        
        if self.room.add_player(player):
            client.players.add(player)
            self.emit('player:add', {'room': self.room, 'player': player})
            callback({'success': True})
            self._nominate_room_master()
        else:
            callback({'success': False, 'error': 'Could not add player.'})
    
    def _on_player_remove(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        player = client.players.get_by_id(data['player'])
        if player:
            self.remove_player(player)
            self.emit('player:remove', {'room': self.room, 'player': player})
        callback({'success': player is not None})
    
    def _on_talk(self, client: 'SocketClient', content: str, callback: Callable) -> None:
        message = Message(client, content[:Message.max_length])
        success = self.chat.add_message(message)
        callback({'success': success})
        if success:
            self.socket_group.add_event('room:talk', message.serialize())
    
    def _on_color(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        player = client.players.get_by_id(data['player'])
        if not player:
            return callback({'success': False})
        
        if player.set_color(data['color']):
            callback({'success': True, 'color': player.color})
            self.socket_group.add_event('player:color', {'player': player.id, 'color': player.color})
        else:
            callback({'success': False, 'color': player.color})
    
    def _on_name(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        player = client.players.get_by_id(data['player'])
        name = data['name'][:Player.max_length].strip()
        
        if not player:
            return callback({'success': False, 'error': f'Unknown player: "{name}"'})
        
        if not name:
            return callback({'success': False, 'error': 'Invalid name.', 'name': player.name})
        
        if not self.room.is_name_available(name):
            return callback({'success': False, 'error': 'This username is already used.', 'name': player.name})
        
        player.set_name(name)
        callback({'success': True, 'name': player.name})
        self.socket_group.add_event('player:name', {'player': player.id, 'name': player.name})
    
    def _on_ready(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        player = client.players.get_by_id(data['player'])
        if player:
            player.toggle_ready()
            callback({'success': True, 'ready': player.ready})
            self.socket_group.add_event('player:ready', {'player': player.id, 'ready': player.ready})
            
            if self.room.is_ready():
                self._launch()
        else:
            callback({'success': False, 'error': f'Player with id "{data["player"]}" not found'})
    
    def _on_config_open(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        if self.room_master and self.room_master.id == client.id:
            success = self.room.config.set_open(data['open'])
        else:
            success = False
        
        callback({
            'success': success,
            'open': self.room.config.open,
            'password': self.room.config.password
        })
        
        if success:
            self.socket_group.add_event('room:config:open', {
                'open': self.room.config.open,
                'password': self.room.config.password
            })
    
    def _on_config_max_score(self, client: 'SocketClient', data: Dict, callback: Callable) -> None:
        if self.room_master and self.room_master.id == client.id:
            success = self.room.config.set_max_score(data['maxScore'])
        else:
            success = False
        
        callback({'success': success, 'maxScore': self.room.config.max_score})
        
        if success:
            self.socket_group.add_event('room:config:max-score', {'maxScore': self.room.config.max_score})
    
    def _on_launch(self, client: 'SocketClient') -> None:
        if self.room_master and self.room_master.id == client.id:
            if self.launching:
                self._cancel_launch()
            else:
                self._start_launch()
    
    def _on_player_join(self, data: Dict) -> None:
        self.socket_group.add_event('room:join', {'player': data['player'].serialize()})
    
    def _on_player_leave(self, data: Dict) -> None:
        self.socket_group.add_event('room:leave', {'player': data['player'].id})
        
        if self.room.is_ready():
            self.room.new_game()
    
    def _on_game(self, data: Any = None) -> None:
        self.socket_group.add_event('room:game:start')
        
        # Create game controller
        from .game_controller import GameController
        GameController(self.room.game)

