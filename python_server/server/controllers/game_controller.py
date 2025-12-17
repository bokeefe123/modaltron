"""
Game controller for managing active games.
Port of server/controller/GameController.js
"""
import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection
from ..core.socket_group import SocketGroup
from ..services.compressor import Compressor

if TYPE_CHECKING:
    from ..models.game import Game
    from ..socket_client import SocketClient
    from ..models.avatar import Avatar


class GameController(EventEmitter):
    """
    Controller for managing an active game session.
    """
    
    # Time to wait for players to load
    waiting_time = 30000  # ms
    
    def __init__(self, game: 'Game'):
        super().__init__()
        
        self.game = game
        self.clients: Collection['SocketClient'] = Collection()
        self.socket_group = SocketGroup(self.clients)
        self.compressor = Compressor()
        self.waiting: Optional[asyncio.TimerHandle] = None
        
        game.controller = self
        self._load_game()
    
    def _load_game(self) -> None:
        """Load game and attach event handlers."""
        self.game.on('game:start', self._on_game_start)
        self.game.on('game:stop', self._on_game_stop)
        self.game.on('end', self._on_end)
        self.game.on('clear', self._on_clear)
        self.game.on('player:leave', self._on_player_leave)
        self.game.on('round:new', self._on_round_new)
        self.game.on('round:end', self._on_round_end)
        self.game.on('borderless', self._on_borderless)
        self.game.bonus_manager.on('bonus:pop', self._on_bonus_pop)
        self.game.bonus_manager.on('bonus:clear', self._on_bonus_clear)
        
        # Attach all room clients
        for client in self.game.room.controller.clients.items:
            self.attach(client)
        
        # Start waiting timer
        loop = asyncio.get_event_loop()
        self.waiting = loop.call_later(self.waiting_time / 1000, self._stop_waiting)
    
    def _unload_game(self) -> None:
        """Unload game and detach event handlers."""
        self.game.remove_listener('game:start', self._on_game_start)
        self.game.remove_listener('game:stop', self._on_game_stop)
        self.game.remove_listener('end', self._on_end)
        self.game.remove_listener('clear', self._on_clear)
        self.game.remove_listener('player:leave', self._on_player_leave)
        self.game.remove_listener('round:new', self._on_round_new)
        self.game.remove_listener('round:end', self._on_round_end)
        self.game.remove_listener('borderless', self._on_borderless)
        self.game.bonus_manager.remove_listener('bonus:pop', self._on_bonus_pop)
        self.game.bonus_manager.remove_listener('bonus:clear', self._on_bonus_clear)
        
        for client in list(self.clients.items):
            self.detach(client)
    
    def attach(self, client: 'SocketClient') -> None:
        """Attach a client to the game."""
        if self.clients.add(client):
            self._attach_events(client)
            self.socket_group.add_event('game:spectators', self._count_spectators())
            asyncio.create_task(client.start_ping())
    
    def detach(self, client: 'SocketClient') -> None:
        """Detach a client from the game."""
        self._detach_events(client)
        
        if self.clients.remove(client):
            for player in list(client.players.items):
                if player.avatar:
                    self.game.remove_avatar(player.avatar)
            self.socket_group.add_event('game:spectators', self._count_spectators())
            asyncio.create_task(client.stop_ping())
    
    def _attach_events(self, client: 'SocketClient') -> None:
        """Attach event handlers for a client."""
        client.on('ready', lambda data: self._on_ready(client))
        
        if not client.players.is_empty():
            client.on('player:move', lambda data: self._on_move(client, data))
        
        for player in client.players.items:
            avatar = player.get_avatar()
            avatar.on('die', self._on_die)
            avatar.on('position', self._on_position)
            avatar.on('angle', self._on_angle)
            avatar.on('point', self._on_point)
            avatar.on('score', self._on_score)
            avatar.on('score:round', self._on_round_score)
            avatar.on('property', self._on_property)
            avatar.bonus_stack.on('change', self._on_bonus_stack)
    
    def _detach_events(self, client: 'SocketClient') -> None:
        """Detach event handlers for a client."""
        # Note: In production, we'd need to store references to remove specific listeners
        pass
    
    def _attach_spectator(self, client: 'SocketClient') -> None:
        """Send current game state to a spectator."""
        properties = {
            'angle': 'angle',
            'radius': 'radius',
            'color': 'color',
            'printing': 'printing',
            'score': 'score'
        }
        
        events = [[
            'spectate', {
                'inRound': self.game.in_round,
                'rendered': self.game.rendered is not None,
                'maxScore': self.game.max_score
            }
        ]]
        
        for avatar in self.game.avatars.items:
            events.append(['position', [
                avatar.id,
                self.compressor.compress(avatar.x),
                self.compressor.compress(avatar.y)
            ]])
            
            for prop_name, prop_key in properties.items():
                events.append(['property', {
                    'avatar': avatar.id,
                    'property': prop_name,
                    'value': getattr(avatar, prop_key)
                }])
            
            if not avatar.alive:
                events.append(['die', {'avatar': avatar.id}])
        
        if self.game.in_round:
            for bonus in self.game.bonus_manager.bonuses.items:
                events.append(['bonus:pop', [
                    bonus.id,
                    self.compressor.compress(bonus.x),
                    self.compressor.compress(bonus.y),
                    type(bonus).__name__
                ]])
        else:
            self.socket_group.add_event(
                'round:end',
                self.game.round_winner.id if self.game.round_winner else None
            )
        
        events.append(['game:spectators', self._count_spectators()])
        client.add_events(events)
    
    def _count_spectators(self) -> int:
        """Count spectators (clients not playing)."""
        return self.clients.filter(lambda c: not c.is_playing()).count()
    
    def _on_ready(self, client: 'SocketClient') -> None:
        """Handle client ready event."""
        if self.game.started:
            self._attach_spectator(client)
        else:
            for player in client.players.items:
                avatar = player.get_avatar()
                avatar.ready = True
                self.socket_group.add_event('ready', avatar.id)
            self._check_ready()
    
    def _check_ready(self) -> None:
        """Check if all players are ready."""
        if self.game.is_ready():
            if self.waiting:
                self.waiting.cancel()
                self.waiting = None
            self.game.new_round()
    
    def _stop_waiting(self) -> None:
        """Stop waiting for loading players."""
        if self.waiting and not self.game.is_ready():
            self.waiting = None
            
            avatars = self.game.get_loading_avatars()
            for avatar in avatars.items:
                self.detach(avatar.player.client)
            
            self._check_ready()
    
    def _on_move(self, client: 'SocketClient', data: Dict[str, Any]) -> None:
        """Handle player move input."""
        player = client.players.get_by_id(data['avatar'])
        if player and player.avatar:
            player.avatar.update_angular_velocity(data['move'])
    
    def _on_point(self, data: Dict[str, Any]) -> None:
        """Handle avatar point event."""
        if data.get('important'):
            self.socket_group.add_event('point', data['avatar'].id)
    
    def _on_position(self, avatar: 'Avatar') -> None:
        """Handle avatar position update."""
        self.socket_group.add_event('position', [
            avatar.id,
            self.compressor.compress(avatar.x),
            self.compressor.compress(avatar.y)
        ])
    
    def _on_angle(self, avatar: 'Avatar') -> None:
        """Handle avatar angle update."""
        self.socket_group.add_event('angle', [
            avatar.id,
            self.compressor.compress(avatar.angle)
        ])
    
    def _on_die(self, data: Dict[str, Any]) -> None:
        """Handle avatar death."""
        self.socket_group.add_event('die', [
            data['avatar'].id,
            data['killer'].id if data['killer'] else None,
            data['old']
        ])
    
    def _on_bonus_pop(self, bonus: Any) -> None:
        """Handle bonus spawn."""
        self.socket_group.add_event('bonus:pop', [
            bonus.id,
            self.compressor.compress(bonus.x),
            self.compressor.compress(bonus.y),
            type(bonus).__name__
        ])
    
    def _on_bonus_clear(self, bonus: Any) -> None:
        """Handle bonus pickup."""
        self.socket_group.add_event('bonus:clear', bonus.id)
    
    def _on_score(self, avatar: 'Avatar') -> None:
        """Handle score update."""
        self.socket_group.add_event('score', [avatar.id, avatar.score])
    
    def _on_round_score(self, avatar: 'Avatar') -> None:
        """Handle round score update."""
        self.socket_group.add_event('score:round', [avatar.id, avatar.round_score])
    
    def _on_property(self, data: Dict[str, Any]) -> None:
        """Handle property change."""
        self.socket_group.add_event('property', [
            data['avatar'].id,
            data['property'],
            data['value']
        ])
    
    def _on_bonus_stack(self, data: Dict[str, Any]) -> None:
        """Handle bonus stack change."""
        bonus = data['bonus']
        self.socket_group.add_event('bonus:stack', [
            data['avatar'].id,
            data['method'],
            bonus.id,
            type(bonus).__name__,
            bonus.duration
        ])
    
    def _on_game_start(self, data: Any) -> None:
        """Handle game start."""
        self.socket_group.add_event('game:start')
    
    def _on_game_stop(self, data: Any) -> None:
        """Handle game stop."""
        self.socket_group.add_event('game:stop')
    
    def _on_round_new(self, data: Any) -> None:
        """Handle new round."""
        self.socket_group.add_event('round:new')
    
    def _on_round_end(self, data: Any) -> None:
        """Handle round end."""
        winner = data.get('winner')
        self.socket_group.add_event('round:end', winner.id if winner else None)
    
    def _on_player_leave(self, data: Any) -> None:
        """Handle player leave."""
        self.socket_group.add_event('game:leave', data['player'].id)
    
    def _on_clear(self, data: Any) -> None:
        """Handle trail clear."""
        self.socket_group.add_event('clear')
    
    def _on_borderless(self, borderless: bool) -> None:
        """Handle borderless mode change."""
        self.socket_group.add_event('borderless', borderless)
    
    def _on_end(self, data: Any) -> None:
        """Handle game end."""
        self.socket_group.add_event('end')
        self._unload_game()

