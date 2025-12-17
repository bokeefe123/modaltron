"""
Game class.
Port of server/model/Game.js
"""
from typing import Any, Optional, TYPE_CHECKING

from .base_game import BaseGame
from .game_bonus_stack import GameBonusStack
from ..core.world import World
from ..core.avatar_body import AvatarBody
from ..collection import Collection

if TYPE_CHECKING:
    from .room import Room
    from .avatar import Avatar
    from ..controllers.game_controller import GameController


class Game(BaseGame):
    """
    Server-side game implementation with physics and collision detection.
    """
    
    def __init__(self, room: 'Room'):
        super().__init__(room)
        
        self.world = World(self.size)
        self.deaths: Collection['Avatar'] = Collection([], 'id')
        self.bonus_stack = GameBonusStack(self)
        self.round_winner: Optional['Avatar'] = None
        self.game_winner: Optional['Avatar'] = None
        self.death_in_frame = False
        
        # Controller is set after initialization
        self.controller: 'GameController' = None
        
        # Set up bonus manager
        from ..managers.bonus_manager import BonusManager
        self.bonus_manager = BonusManager(
            self,
            room.config.get_bonuses(),
            room.config.get_variable('bonusRate')
        )
        
        # Set up avatars
        for avatar in self.avatars.items:
            avatar.clear()
            avatar.on('point', self._on_point)
    
    def _on_point(self, data: dict) -> None:
        """Handle avatar point event."""
        if self.started and self.world.active:
            avatar = data['avatar']
            self.world.add_body(AvatarBody(data['x'], data['y'], avatar))
    
    def update(self, step: float) -> None:
        """Update game state for a frame."""
        score = self.deaths.count()
        self.death_in_frame = False
        
        for avatar in self.avatars.items:
            if avatar.alive:
                avatar.update(step)
                
                # Check border collision
                border = self.world.get_bound_intersect(
                    avatar.body,
                    0 if self.borderless else avatar.radius
                )
                
                if border:
                    if self.borderless:
                        position = self.world.get_opposite(border[0], border[1])
                        avatar.set_position(position[0], position[1])
                    else:
                        self.kill(avatar, None, score)
                else:
                    # Check collision with other bodies
                    if not avatar.invincible:
                        killer = self.world.get_body(avatar.body)
                        if killer:
                            self.kill(avatar, killer, score)
                
                # Update print manager and check bonuses
                if avatar.alive:
                    avatar.print_manager.test()
                    self.bonus_manager.test_catch(avatar)
        
        if self.death_in_frame:
            self.check_round_end()
    
    def kill(self, avatar: 'Avatar', killer: Optional[AvatarBody], score: int) -> None:
        """Kill an avatar."""
        avatar.die(killer)
        avatar.add_score(score)
        self.deaths.add(avatar)
        self.death_in_frame = True
    
    def remove_avatar(self, avatar: 'Avatar') -> None:
        """Remove an avatar from the game."""
        super().remove_avatar(avatar)
        self.emit('player:leave', {'player': avatar.player})
        self.check_round_end()
    
    def is_won(self) -> Any:
        """Check if the game is won. Returns winner avatar, True, or None."""
        present = self.get_present_avatars().count()
        
        if present <= 0:
            return True
        if self.avatars.count() > 1 and present <= 1:
            return True
        
        max_score = self.max_score
        players = self.avatars.filter(lambda a: a.present and a.score >= max_score)
        
        if players.count() == 0:
            return None
        
        if players.count() == 1:
            return players.get_first()
        
        self.sort_avatars(players)
        
        if players.items[0].score == players.items[1].score:
            return None
        return players.get_first()
    
    def check_round_end(self) -> None:
        """Check if the round should end."""
        if not self.in_round:
            return
        
        alive_count = 0
        for avatar in self.avatars.items:
            if avatar.alive:
                alive_count += 1
                if alive_count > 1:
                    return  # More than one alive, continue
        
        self.end_round()
    
    def resolve_scores(self) -> None:
        """Resolve scores at end of round."""
        winner = None
        
        if self.avatars.count() == 1:
            winner = self.avatars.get_first()
        else:
            winner = self.avatars.match(lambda a: a.alive)
        
        if winner:
            winner.add_score(max(self.avatars.count() - 1, 1))
            self.round_winner = winner
        
        for avatar in self.avatars.items:
            avatar.resolve_score()
    
    def clear_trails(self) -> None:
        """Clear all trails (for BonusGameClear)."""
        self.world.clear()
        self.world.activate()
        self.emit('clear', {'game': self})
    
    def set_size(self, size: Optional[int] = None) -> None:
        """Update game size."""
        super().set_size(size)
        self.world.clear()
        self.world = World(self.size)
        self.bonus_manager.set_size()
    
    def on_round_end(self) -> None:
        """Handle round end."""
        self.resolve_scores()
        self.emit('round:end', {'winner': self.round_winner})
    
    def on_round_new(self) -> None:
        """Handle new round."""
        self.emit('round:new', {'game': self})
        super().on_round_new()
        
        self.round_winner = None
        self.world.clear()
        self.deaths.clear()
        self.bonus_stack.clear()
        
        for avatar in self.avatars.items:
            if avatar.present:
                position = self.world.get_random_position(avatar.radius, self.spawn_margin)
                avatar.set_position(position[0], position[1])
                avatar.set_angle(self.world.get_random_direction(avatar.x, avatar.y, self.spawn_angle_margin))
            else:
                self.deaths.add(avatar)
    
    def on_start(self) -> None:
        """Handle game start."""
        self.emit('game:start', {'game': self})
        
        # Start print managers after warmup
        import asyncio
        for avatar in self.avatars.items:
            asyncio.get_event_loop().call_later(3.0, avatar.print_manager.start)
        
        self.world.activate()
        super().on_start()
    
    def on_stop(self) -> None:
        """Handle game stop."""
        self.emit('game:stop', {'game': self})
        super().on_stop()
        
        won = self.is_won()
        
        if won:
            from .avatar import Avatar
            if isinstance(won, Avatar):
                self.game_winner = won
            self.end()
        else:
            self.new_round()
    
    def set_borderless(self, borderless: bool) -> None:
        """Set borderless mode and emit event."""
        if self.borderless != borderless:
            super().set_borderless(borderless)
            self.emit('borderless', self.borderless)
    
    def end(self) -> bool:
        """End the game."""
        if super().end():
            self.avatars.clear()
            self.world.clear()
            return True
        return False

