"""
Event emitter implementation for Python.
Provides the same interface as Node.js EventEmitter.
"""
from typing import Callable, Dict, List, Any
from collections import defaultdict


class EventEmitter:
    """
    A simple event emitter that mimics Node.js EventEmitter interface.
    Supports on, emit, remove_listener, and once.
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._once_listeners: Dict[str, List[Callable]] = defaultdict(list)
    
    def on(self, event: str, callback: Callable) -> 'EventEmitter':
        """Register a listener for an event."""
        self._listeners[event].append(callback)
        return self
    
    def once(self, event: str, callback: Callable) -> 'EventEmitter':
        """Register a one-time listener for an event."""
        self._once_listeners[event].append(callback)
        return self
    
    def emit(self, event: str, *args, **kwargs) -> bool:
        """
        Emit an event with optional data.
        Returns True if there were listeners for the event.
        """
        had_listeners = False
        
        # Call regular listeners
        if event in self._listeners:
            for callback in self._listeners[event][:]:  # Copy list to allow modification
                callback(*args, **kwargs)
                had_listeners = True
        
        # Call one-time listeners and remove them
        if event in self._once_listeners:
            listeners = self._once_listeners[event]
            self._once_listeners[event] = []
            for callback in listeners:
                callback(*args, **kwargs)
                had_listeners = True
        
        return had_listeners
    
    def remove_listener(self, event: str, callback: Callable) -> 'EventEmitter':
        """Remove a specific listener for an event."""
        if event in self._listeners:
            try:
                self._listeners[event].remove(callback)
            except ValueError:
                pass
        
        if event in self._once_listeners:
            try:
                self._once_listeners[event].remove(callback)
            except ValueError:
                pass
        
        return self
    
    def remove_all_listeners(self, event: str = None) -> 'EventEmitter':
        """Remove all listeners for an event, or all events if not specified."""
        if event is None:
            self._listeners.clear()
            self._once_listeners.clear()
        else:
            self._listeners.pop(event, None)
            self._once_listeners.pop(event, None)
        return self
    
    def listeners(self, event: str) -> List[Callable]:
        """Get all listeners for an event."""
        return self._listeners.get(event, []) + self._once_listeners.get(event, [])
    
    def listener_count(self, event: str) -> int:
        """Count listeners for an event."""
        return len(self._listeners.get(event, [])) + len(self._once_listeners.get(event, []))

