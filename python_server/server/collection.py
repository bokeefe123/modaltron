"""
Collection class - A typed list with id-based indexing and utility methods.
Port of shared/Collection.js
"""
from typing import TypeVar, Generic, List, Optional, Callable, Any
import random

T = TypeVar('T')


class Collection(Generic[T]):
    """
    A collection that maintains items with unique IDs.
    Supports auto-indexing, filtering, mapping, and various utility operations.
    """
    
    def __init__(self, items: Optional[List[T]] = None, key: str = 'id', index: bool = False):
        self.ids: List[Any] = []
        self.items: List[T] = []
        self.key = key
        self.index = index
        self._id_counter = 0
        
        if items:
            for item in reversed(items):
                self.add(item)
    
    def clear(self) -> None:
        """Clear all items from the collection."""
        self.ids.clear()
        self.items.clear()
        self._id_counter = 0
    
    def count(self) -> int:
        """Return the number of items in the collection."""
        return len(self.ids)
    
    def is_empty(self) -> bool:
        """Check if the collection is empty."""
        return len(self.ids) == 0
    
    def _get_id(self, element: T) -> Any:
        """Get the ID of an element."""
        return getattr(element, self.key, None)
    
    def _set_id(self, element: T) -> None:
        """Set ID on element if auto-indexing is enabled."""
        if self.index:
            current_id = self._get_id(element)
            if current_id is not None and current_id:
                if current_id > self._id_counter:
                    self._id_counter = current_id
            else:
                self._id_counter += 1
                setattr(element, self.key, self._id_counter)
    
    def add(self, element: T, ttl: Optional[int] = None) -> bool:
        """
        Add an element to the collection.
        Returns True if added successfully, False if element already exists.
        """
        self._set_id(element)
        
        if self.exists(element):
            return False
        
        element_id = self._get_id(element)
        self.ids.append(element_id)
        self.items.append(element)
        
        # TTL support would require asyncio scheduling - skip for now
        return True
    
    def remove(self, element: T) -> bool:
        """Remove an element from the collection."""
        element_id = self._get_id(element)
        try:
            index = self.ids.index(element_id)
            self._delete_index(index)
            return True
        except ValueError:
            return False
    
    def remove_by_id(self, id_value: Any) -> bool:
        """Remove an element by its ID."""
        try:
            index = self.ids.index(id_value)
            self._delete_index(index)
            return True
        except ValueError:
            return False
    
    def _delete_index(self, index: int) -> None:
        """Delete element at the given index."""
        del self.items[index]
        del self.ids[index]
    
    def get_by_id(self, id_value: Any) -> Optional[T]:
        """Get an element by its ID."""
        try:
            index = self.ids.index(id_value)
            return self.items[index]
        except ValueError:
            return None
    
    def get_by_index(self, index: int) -> Optional[T]:
        """Get an element by its index."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def exists(self, element: T) -> bool:
        """Check if an element exists in the collection."""
        element_id = self._get_id(element)
        return element_id in self.ids
    
    def index_exists(self, id_value: Any) -> bool:
        """Check if an ID exists in the collection."""
        return id_value in self.ids
    
    def get_element_index(self, element: T) -> int:
        """Get the index of an element."""
        element_id = self._get_id(element)
        try:
            return self.ids.index(element_id)
        except ValueError:
            return -1
    
    def map(self, callable: Callable[[T], Any]) -> 'Collection':
        """Map a function over all items, returning a new collection."""
        elements = [callable(item) for item in reversed(self.items)]
        return Collection(elements, self.key, self.index)
    
    def filter(self, callable: Callable[[T], bool]) -> 'Collection':
        """Filter items by a predicate, returning a new collection."""
        elements = [item for item in reversed(self.items) if callable(item)]
        return Collection(elements, self.key, self.index)
    
    def match(self, callable: Callable[[T], bool]) -> Optional[T]:
        """Find the first item matching a predicate."""
        for item in self.items:
            if callable(item):
                return item
        return None
    
    def walk(self, callable: Callable[[T], None]) -> None:
        """Apply a function to each item."""
        for item in reversed(self.items):
            callable(item)
    
    def get_random_item(self) -> Optional[T]:
        """Get a random item from the collection."""
        if not self.items:
            return None
        return random.choice(self.items)
    
    def get_first(self) -> Optional[T]:
        """Get the first item in the collection."""
        return self.items[0] if self.items else None
    
    def get_last(self) -> Optional[T]:
        """Get the last item in the collection."""
        return self.items[-1] if self.items else None
    
    def sort(self, key: Callable[[T], Any], reverse: bool = False) -> None:
        """Sort the collection in place."""
        self.items.sort(key=key, reverse=reverse)
        self._rebuild_ids()
    
    def _rebuild_ids(self) -> None:
        """Rebuild the ID list after sorting."""
        self.ids = [self._get_id(item) for item in self.items]

