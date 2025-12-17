"""
Base bonus stack for managing active bonuses.
Port of shared/model/BaseBonusStack.js
"""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..event_emitter import EventEmitter
from ..collection import Collection

if TYPE_CHECKING:
    from .base_bonus import BaseBonus
    from .base_avatar import BaseAvatar


class BaseBonusStack(EventEmitter):
    """
    Base class for managing a stack of active bonuses on a target.
    """
    
    def __init__(self, target: Any):
        super().__init__()
        self.target = target
        self.bonuses: Collection['BaseBonus'] = Collection()
    
    def add(self, bonus: 'BaseBonus') -> None:
        """Add a bonus to the stack."""
        if self.bonuses.add(bonus):
            self.resolve()
    
    def remove(self, bonus: 'BaseBonus') -> None:
        """Remove a bonus from the stack."""
        if self.bonuses.remove(bonus):
            self.resolve(bonus)
    
    def clear(self) -> None:
        """Clear all bonuses."""
        self.bonuses.clear()
    
    def resolve(self, bonus: Optional['BaseBonus'] = None) -> None:
        """Resolve all active bonuses and apply their effects."""
        properties: Dict[str, Any] = {}
        
        # If a bonus is being removed, get its effects to reset those properties
        if bonus is not None:
            effects = bonus.get_effects(self.target)
            for effect in effects:
                prop = effect[0]
                properties[prop] = self.get_default_property(prop)
        
        # Aggregate all active bonus effects
        for active_bonus in self.bonuses.items:
            effects = active_bonus.get_effects(self.target)
            for effect in effects:
                prop = effect[0]
                value = effect[1]
                
                if prop not in properties:
                    properties[prop] = self.get_default_property(prop)
                
                self.append(properties, prop, value)
        
        # Apply all properties
        for prop, value in properties.items():
            self.apply(prop, value)
    
    def apply(self, property: str, value: Any) -> None:
        """Apply a value to the target's property."""
        setattr(self.target, property, value)
    
    def get_default_property(self, property: str) -> Any:
        """Get the default value for a property."""
        return 0
    
    def append(self, properties: Dict[str, Any], property: str, value: Any) -> None:
        """Append a value to a property (default is addition)."""
        properties[property] += value

