"""
Bonus manager for spawning and managing bonuses.
Port of server/manager/BonusManager.js
"""
import asyncio
import random
from typing import List, Optional, Type, TYPE_CHECKING

from .base_bonus_manager import BaseBonusManager
from ..core.world import World
from ..core.body import Body
from ..models.base_bonus import BaseBonus

if TYPE_CHECKING:
    from ..models.game import Game
    from ..models.bonus.bonus import Bonus
    from ..models.avatar import Avatar


class BonusManager(BaseBonusManager):
    """
    Server-side bonus manager that handles spawning bonuses.
    """
    
    def __init__(self, game: 'Game', bonus_types: List[Type['Bonus']], rate: float):
        super().__init__(game)
        
        self.world = World(game.size, 1)
        self.poping_timeout: Optional[asyncio.TimerHandle] = None
        self.bonus_types = bonus_types
        self.bonus_poping_time = self.bonus_poping_time - ((self.bonus_poping_time / 2) * rate)
    
    def start(self) -> None:
        """Start spawning bonuses."""
        super().start()
        self.world.activate()
        
        if self.bonus_types:
            self._schedule_pop()
    
    def _schedule_pop(self) -> None:
        """Schedule the next bonus spawn."""
        loop = asyncio.get_event_loop()
        delay = self.get_random_poping_time() / 1000
        self.poping_timeout = loop.call_later(delay, self.pop_bonus)
    
    def stop(self) -> None:
        """Stop spawning bonuses."""
        if self.poping_timeout:
            self.poping_timeout.cancel()
            self.poping_timeout = None
        super().stop()
    
    def clear(self) -> None:
        """Clear all bonuses."""
        self.world.clear()
        super().clear()
    
    def pop_bonus(self) -> None:
        """Spawn a new bonus."""
        if self.bonus_types:
            self._schedule_pop()
            
            if self.bonuses.count() < self.bonus_cap:
                bonus_type = self.get_random_bonus_type()
                
                if bonus_type:
                    position = self.get_random_position(BaseBonus.radius, self.bonus_poping_margin)
                    bonus = bonus_type(position[0], position[1])
                    self.add(bonus)
    
    def get_random_position(self, radius: float, border: float) -> tuple:
        """Get a random position for a bonus."""
        margin = radius + border * self.game.world.size
        body = Body(
            self.game.world._get_random_point(margin),
            self.game.world._get_random_point(margin),
            margin
        )
        
        max_attempts = 100
        attempts = 0
        while (not self.game.world.test_body(body) or not self.world.test_body(body)) and attempts < max_attempts:
            body.x = self.game.world._get_random_point(margin)
            body.y = self.game.world._get_random_point(margin)
            attempts += 1
        
        return (body.x, body.y)
    
    def test_catch(self, avatar: 'Avatar') -> None:
        """Test if an avatar catches a bonus."""
        if avatar.body:
            body = self.world.get_body(avatar.body)
            bonus = body.data if body else None
            
            if bonus and self.remove(bonus):
                bonus.apply_to(avatar, self.game)
    
    def add(self, bonus: 'Bonus') -> bool:
        """Add a bonus to the game."""
        if super().add(bonus):
            self.world.add_body(bonus.body)
            self.emit('bonus:pop', bonus)
            return True
        return False
    
    def remove(self, bonus: 'Bonus') -> bool:
        """Remove a bonus from the game."""
        if super().remove(bonus):
            self.world.remove_body(bonus.body)
            self.emit('bonus:clear', bonus)
            return True
        return False
    
    def get_random_poping_time(self) -> float:
        """Get random time until next bonus spawn."""
        return self.bonus_poping_time * (1 + random.random())
    
    def get_random_bonus_type(self) -> Optional[Type['Bonus']]:
        """Get a random bonus type based on probability."""
        if not self.bonus_types:
            return None
        
        pot = []
        bonuses = []
        
        for bonus_type in self.bonus_types:
            probability = bonus_type.probability
            # Use instance method for probability if it exists
            temp_bonus = bonus_type(0, 0)
            probability = temp_bonus.get_probability(self.game)
            
            if probability > 0:
                bonuses.append(bonus_type)
                pot.append(probability + (pot[-1] if pot else 0))
        
        if not pot:
            return None
        
        value = random.random() * pot[-1]
        
        for i, cumulative in enumerate(pot):
            if value < cumulative:
                return bonuses[i]
        
        return None
    
    def set_size(self) -> None:
        """Update bonus world size."""
        self.world.clear()
        self.world = World(self.game.size, 1)

