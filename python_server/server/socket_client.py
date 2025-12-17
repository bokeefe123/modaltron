"""
WebSocket client wrapper for handling game communications.
Port of server/core/SocketClient.js and shared/core/BaseSocketClient.js
"""
import json
import asyncio
import time
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from starlette.websockets import WebSocket

from .event_emitter import EventEmitter
from .collection import Collection

if TYPE_CHECKING:
    from .models.player import Player


class BaseSocketClient(EventEmitter):
    """
    Base socket client that handles WebSocket communication.
    Manages event batching and message passing.
    """
    
    def __init__(self, socket: WebSocket, interval: float = 0):
        super().__init__()
        self.socket = socket
        self.interval = interval  # in seconds
        self.events: List[List[Any]] = []
        self.callbacks: Dict[int, Callable] = {}
        self.loop_task: Optional[asyncio.Task] = None
        self.connected = True
        self.call_count = 0
    
    async def start(self) -> None:
        """Start the event flush loop if interval is set."""
        if self.interval and not self.loop_task:
            self.loop_task = asyncio.create_task(self._flush_loop())
            await self.flush()
    
    async def stop(self) -> None:
        """Stop the event flush loop."""
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
            self.loop_task = None
    
    async def _flush_loop(self) -> None:
        """Background loop to flush events at regular intervals."""
        while self.connected:
            await asyncio.sleep(self.interval)
            await self.flush()
    
    def add_event(self, name: str, data: Any = None, callback: Callable = None, force: bool = False) -> None:
        """Add an event to the queue."""
        event = [name]
        
        if data is not None:
            event.append(data)
        
        if callback is not None:
            event.append(self._index_callback(callback))
        
        if not self.interval or force:
            asyncio.create_task(self.send_events([event]))
        else:
            self.events.append(event)
    
    def add_events(self, sources: List[List[Any]], force: bool = False) -> None:
        """Add multiple events to the queue."""
        if not self.interval or force:
            asyncio.create_task(self.send_events(sources))
        else:
            self.events.extend(sources)
    
    def _index_callback(self, callback: Callable) -> int:
        """Index a callback for later execution."""
        index = self.call_count
        self.call_count += 1
        self.callbacks[index] = callback
        return index
    
    def add_callback(self, id: int, data: Any = None) -> None:
        """Send a callback response."""
        event = [id]
        if data is not None:
            event.append(data)
        asyncio.create_task(self.send_events([event]))
    
    async def send_events(self, events: List[List[Any]]) -> None:
        """Send events to the WebSocket client."""
        if self.connected:
            try:
                await self.socket.send_text(json.dumps(events))
            except Exception as e:
                print(f"Error sending events {events}: {e}")
                import traceback
                traceback.print_exc()
                self.connected = False
    
    async def flush(self) -> None:
        """Flush all queued events."""
        if self.events:
            events_to_send = self.events[:]
            self.events.clear()
            await self.send_events(events_to_send)
    
    async def on_message(self, data: str) -> None:
        """Process an incoming message."""
        try:
            messages = json.loads(data)
            for source in messages:
                try:
                    name = source[0]
                    
                    if isinstance(name, str):
                        if len(source) == 3:
                            # Event with callback
                            callback_id = source[2]
                            def create_callback(cid):
                                return lambda result: self.add_callback(cid, result)
                            self.emit(name, [source[1], create_callback(callback_id)])
                        else:
                            # Regular event
                            self.emit(name, source[1] if len(source) > 1 else None)
                    else:
                        # Callback response (name is actually a callback ID)
                        self._play_callback(name, source[1] if len(source) > 1 else None)
                except Exception as e:
                    print(f"Error handling event {source}: {e}")
                    import traceback
                    traceback.print_exc()
        except json.JSONDecodeError as e:
            print(f"Error parsing message: {e}")
    
    def _play_callback(self, id: int, data: Any) -> None:
        """Execute a registered callback."""
        if id in self.callbacks:
            self.callbacks[id](data)
            del self.callbacks[id]
    
    async def on_close(self) -> None:
        """Handle WebSocket close."""
        self.connected = False
        self.emit('close', self)
        await self.stop()
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize client info."""
        return {'id': self.id}


class SocketClient(BaseSocketClient):
    """
    Server-side socket client that extends BaseSocketClient with
    player management and ping tracking.
    """
    
    ping_interval = 1.0  # seconds
    
    def __init__(self, socket: WebSocket, interval: float, ip: str):
        super().__init__(socket, interval)
        self.ip = ip
        self.id: Optional[int] = None
        self.active = True
        self.players: Collection['Player'] = Collection([], 'id')
        self.ping_task: Optional[asyncio.Task] = None
        self.latency: float = 0
        self._last_ping_time: float = 0
        
        # Register handlers
        self.on('whoami', self._identify)
        self.on('activity', self._on_activity)
        self.on('pong', self._on_pong)
    
    def _identify(self, event: List[Any]) -> None:
        """Handle identification request."""
        print(f"Client identify request, self.id = {self.id}")
        callback = event[1]
        callback(self.id)
    
    def _on_activity(self, active: bool) -> None:
        """Handle activity change."""
        self.active = active
    
    def _on_pong(self, data: Any) -> None:
        """Handle pong response for latency calculation."""
        print(f"Received pong with data: {data}")
        # Data contains the original ping timestamp (in milliseconds)
        if data is not None:
            current_time = int(time.time() * 1000)
            self.latency = current_time - int(data)
            print(f"Calculated latency: {self.latency}ms")
        else:
            # Fallback to stored ping time
            self.latency = (time.time() - self._last_ping_time) * 1000
        
        self.add_event('latency', round(self.latency), force=True)
    
    async def start_ping(self) -> None:
        """Start ping loop for latency tracking."""
        if not self.ping_task:
            self.ping_task = asyncio.create_task(self._ping_loop())
    
    async def stop_ping(self) -> None:
        """Stop ping loop."""
        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass
            self.ping_task = None
    
    async def _ping_loop(self) -> None:
        """Background ping loop measuring latency via application-level ping."""
        print(f"Ping loop started for client {self.id}")
        while self.connected:
            await asyncio.sleep(self.ping_interval)
            if self.connected:
                try:
                    # Send application-level ping with timestamp
                    # The client should respond with 'pong' containing the same timestamp
                    self._last_ping_time = time.time()
                    timestamp = int(self._last_ping_time * 1000)
                    print(f"Sending ping with timestamp: {timestamp}")
                    self.add_event('ping', timestamp, force=True)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Ping error: {e}")
    
    def is_playing(self) -> bool:
        """Check if this client has active players."""
        return not self.players.is_empty()
    
    def clear_players(self) -> None:
        """Clear all players for this client."""
        self.emit('players:clear', self)
        self.players.clear()
    
    async def stop(self) -> None:
        """Stop client and cleanup."""
        await super().stop()
        await self.stop_ping()
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize client info."""
        data = super().serialize()
        data['active'] = self.active
        return data

