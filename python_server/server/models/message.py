"""
Chat message model.
Port of server/model/Message.js
"""
import time
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..socket_client import SocketClient


class Message:
    """
    Represents a chat message in a room.
    """
    
    max_length = 140
    
    def __init__(self, client: 'SocketClient', content: str):
        self.client = client
        self.content = content
        self.creation = time.time() * 1000
    
    def serialize(self) -> Dict:
        return {
            'client': self.client.id,
            'content': self.content,
            'creation': self.creation
        }

