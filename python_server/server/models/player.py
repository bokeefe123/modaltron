"""
Player class.
Port of server/model/Player.js
"""
from typing import Any, Dict, TYPE_CHECKING

from .base_player import BasePlayer

if TYPE_CHECKING:
    from ..socket_client import SocketClient


class Player(BasePlayer):
    """
    Server-side player implementation.
    """
    
    def __init__(self, client: 'SocketClient', name: str, color: str = None):
        super().__init__(client, name, color)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize player info including activity status."""
        data = super().serialize()
        data['active'] = self.client.active
        return data

