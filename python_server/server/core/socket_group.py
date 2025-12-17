"""
Socket group for broadcasting events to multiple clients.
Port of server/core/SocketGroup.js
"""
from typing import Any, Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..socket_client import SocketClient
    from ..collection import Collection


class SocketGroup:
    """
    Manages a group of socket clients for broadcasting events.
    """
    
    def __init__(self, clients: Optional['Collection[SocketClient]'] = None):
        from ..collection import Collection
        self.clients: 'Collection[SocketClient]' = clients if clients is not None else Collection()
    
    def on(self, name: str, callback: Callable) -> None:
        """Add a listener to all clients."""
        for client in self.clients.items:
            client.on(name, callback)
    
    def remove_listener(self, name: str, callback: Callable) -> None:
        """Remove a listener from all clients."""
        for client in self.clients.items:
            client.remove_listener(name, callback)
    
    def add_events(self, events: List[List[Any]], force: bool = False) -> None:
        """Add multiple events to all clients."""
        for client in self.clients.items:
            client.add_events(events, force)
    
    def add_event(self, name: str, data: Any = None, callback: Callable = None, force: bool = False) -> None:
        """Add an event to all clients."""
        for client in self.clients.items:
            client.add_event(name, data, callback, force)

