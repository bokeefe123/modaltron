"""
Base game class.
Port of shared/model/BaseGame.js
"""
import asyncio
import time
import math
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection

if TYPE_CHECKING:
    from .base_room import BaseRoom
    from .avatar import Avatar


class BaseGame(EventEmitter):
    """
    Base class for the game logic.
    """
    
    # Loop frame rate (ms between frames)
    framerate = 1000 / 60  # ~16.67ms for 60fps
    
    # Map size factor per player
    per_player_size = 80
    
    # Time before round start (ms)
    warmup_time = 3000
    
    # Time after round end (ms)
    warmdown_time = 5000
    
    # Margin from borders (as fraction of map size)
    spawn_margin = 0.05
    
    # Angle margin from borders
    spawn_angle_margin = 0.3
    
    # Whether the game is borderless (default)
    DEFAULT_BORDERLESS = False
    
    def __init__(self, room: 'BaseRoom'):
        super().__init__()
        
        self.room = room
        self.name = room.name
        self._frame_task: Optional[asyncio.Task] = None
        self.avatars: Collection['Avatar'] = Collection([], 'id')
        
        # Create avatars for all players
        for player in room.players.items:
            avatar = player.get_avatar()
            self.avatars.add(avatar)
        
        self.size = self.get_size(self.avatars.count())
        self.rendered: Optional[float] = None
        self.max_score = room.config.get_max_score()
        self.started = False
        self.in_round = False
        self._borderless = BaseGame.DEFAULT_BORDERLESS
        
        # Bonus manager is set by subclass
        self.bonus_manager = None
    
    @property
    def borderless(self) -> bool:
        return self._borderless
    
    @borderless.setter
    def borderless(self, value: bool):
        self._borderless = bool(value)
    
    def update(self, step: float) -> None:
        """Update game state (override in subclass)."""
        pass
    
    def remove_avatar(self, avatar: 'Avatar') -> None:
        """Remove an avatar from the game."""
        if self.avatars.exists(avatar):
            avatar.die()
            avatar.destroy()
    
    def start(self) -> None:
        """Start the game loop."""
        if not self._frame_task:
            self.on_start()
            self._frame_task = asyncio.create_task(self._run_loop())
    
    def stop(self) -> None:
        """Stop the game loop."""
        if self._frame_task:
            self._frame_task.cancel()
            self._frame_task = None
            self.on_stop()
    
    async def _run_loop(self) -> None:
        """Main game loop."""
        self.rendered = time.time() * 1000
        
        while True:
            await asyncio.sleep(self.framerate / 1000)
            
            now = time.time() * 1000
            step = now - self.rendered
            self.rendered = now
            
            self.on_frame(step)
    
    def on_start(self) -> None:
        """Called when game starts."""
        self.rendered = time.time() * 1000
        if self.bonus_manager:
            self.bonus_manager.start()
    
    def on_stop(self) -> None:
        """Called when game stops."""
        self.rendered = None
        if self.bonus_manager:
            self.bonus_manager.stop()
        
        # Update size based on present players
        size = self.get_size(self.get_present_avatars().count())
        if self.size != size:
            self.set_size(size)
    
    def on_round_new(self) -> None:
        """Called when a new round starts."""
        self._borderless = BaseGame.DEFAULT_BORDERLESS
        
        if self.bonus_manager:
            self.bonus_manager.clear()
        
        for avatar in self.avatars.items:
            if avatar.present:
                avatar.clear()
    
    def on_round_end(self) -> None:
        """Called when round ends."""
        pass
    
    def on_frame(self, step: float) -> None:
        """Called each frame."""
        self.update(step)
    
    def set_size(self, size: Optional[int] = None) -> None:
        """Update game size."""
        if size is None:
            size = self.get_size(self.get_present_avatars().count())
        self.size = size
    
    def get_size(self, players: int) -> int:
        """Calculate map size based on player count."""
        square = self.per_player_size * self.per_player_size
        size = math.sqrt(square + ((players - 1) * square / 5))
        return round(size)
    
    def is_ready(self) -> bool:
        """Check if all avatars are ready."""
        return self.get_loading_avatars().is_empty()
    
    def get_loading_avatars(self) -> Collection['Avatar']:
        """Get avatars still loading."""
        return self.avatars.filter(lambda a: a.present and not a.ready)
    
    def get_alive_avatars(self) -> Collection['Avatar']:
        """Get alive avatars."""
        return self.avatars.filter(lambda a: a.alive)
    
    def get_present_avatars(self) -> Collection['Avatar']:
        """Get present avatars."""
        return self.avatars.filter(lambda a: a.present)
    
    def sort_avatars(self, avatars: Optional[Collection['Avatar']] = None) -> Collection['Avatar']:
        """Sort avatars by score (descending)."""
        if avatars is None:
            avatars = self.avatars
        avatars.sort(key=lambda a: -a.score)
        return avatars
    
    def set_borderless(self, borderless: bool) -> None:
        """Set borderless mode."""
        self._borderless = bool(borderless)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize game info."""
        return {
            'name': self.name,
            'players': [a.serialize() for a in self.avatars.items],
            'maxScore': self.max_score
        }
    
    def new_round(self, time_delay: Optional[int] = None) -> None:
        """Start a new round."""
        self.started = True
        
        if not self.in_round:
            self.in_round = True
            self.on_round_new()
            
            delay = time_delay if time_delay is not None else self.warmup_time
            asyncio.get_event_loop().call_later(delay / 1000, self.start)
    
    def end_round(self) -> None:
        """End the current round."""
        if self.in_round:
            self.in_round = False
            self.on_round_end()
            asyncio.get_event_loop().call_later(self.warmdown_time / 1000, self.stop)
    
    def end(self) -> bool:
        """End the game."""
        if self.started:
            self.started = False
            self.stop()
            self.emit('end', {'game': self})
            return True
        return False

