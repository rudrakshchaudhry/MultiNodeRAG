"""
Query caching for adaptive RAG
"""

import time
from typing import Dict, Any, Optional
from collections import OrderedDict

class QueryCache:
    """LRU cache for query results"""
    
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.total_queries = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self.total_queries += 1
        
        if key in self.cache:
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            return value
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if key in self.cache:
            # Update existing
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        if self.total_queries == 0:
            return 0.0
        return self.hits / self.total_queries
    
    def get_size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def get_total_queries(self) -> int:
        """Get total number of queries"""
        return self.total_queries
    
    def clear(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        self.hits = 0
        self.total_queries = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'total_queries': self.total_queries,
            'hit_rate': self.get_hit_rate()
        }
