"""
Print manager for controlling trail printing.
Port of server/manager/PrintManager.js
"""
import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.avatar import Avatar


class PrintManager:
    """
    Manages when an avatar prints trail (creates gaps/holes).
    """
    
    # Distance for holes (no trail)
    hole_distance = 5.0
    
    # Distance for printing trail
    print_distance = 60.0
    
    def __init__(self, avatar: 'Avatar'):
        self.avatar = avatar
        self.active = False
        self.last_x = 0.0
        self.last_y = 0.0
        self.distance = 0.0
    
    def toggle_printing(self) -> None:
        """Toggle printing state."""
        self.set_printing(not self.avatar.printing)
    
    def set_printing(self, printing: bool) -> None:
        """Set printing state and calculate next distance."""
        self.avatar.set_printing(printing)
        self.distance = self.get_random_distance()
    
    def get_random_distance(self) -> float:
        """Get random distance before next toggle."""
        if self.avatar.printing:
            return self.print_distance * (0.3 + random.random() * 0.7)
        else:
            return self.hole_distance * (0.8 + random.random() * 0.5)
    
    def start(self) -> None:
        """Start the print manager."""
        if not self.active:
            self.active = True
            self.last_x = self.avatar.x
            self.last_y = self.avatar.y
            self.set_printing(True)
    
    def stop(self) -> None:
        """Stop the print manager."""
        if self.active:
            self.active = False
            self.set_printing(False)
            self.clear()
    
    def test(self) -> None:
        """Test if it's time to toggle printing."""
        if self.active:
            self.distance -= self.get_distance(self.last_x, self.last_y, self.avatar.x, self.avatar.y)
            
            self.last_x = self.avatar.x
            self.last_y = self.avatar.y
            
            if self.distance <= 0:
                self.toggle_printing()
    
    def get_distance(self, from_x: float, from_y: float, to_x: float, to_y: float) -> float:
        """Calculate distance between two points."""
        return math.sqrt((from_x - to_x) ** 2 + (from_y - to_y) ** 2)
    
    def clear(self) -> None:
        """Clear the manager state."""
        self.active = False
        self.distance = 0.0
        self.last_x = 0.0
        self.last_y = 0.0

