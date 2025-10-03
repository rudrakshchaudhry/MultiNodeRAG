"""
Profile configurations for different content types in Adaptive RAG
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ProfileType(Enum):
    """Available profile types"""
    DEFS = "defs"
    THEOREM = "theorem" 
    WORKED = "worked"
    GENERAL = "general"

@dataclass
class ProfileConfig:
    """Configuration for a specific profile"""
    
    name: str
    source: str  # 'pack', 'index', or 'hybrid'
    index_name: Optional[str] = None
    pack_file: Optional[str] = None
    widenable: bool = True  # Whether this profile supports progressive widening
    priority: int = 1  # Higher priority profiles are tried first
    max_chunks: int = 5  # Maximum chunks for this profile
    
    # Profile-specific settings
    similarity_threshold: float = 0.35
    relevance_boost: float = 0.0  # Additional relevance boost for this profile
    
    def __post_init__(self):
        """Validate profile configuration"""
        if self.source not in ['pack', 'index', 'hybrid']:
            raise ValueError(f"Invalid source type: {self.source}")
        if self.source == 'index' and not self.index_name:
            raise ValueError("index_name required for index source")
        if self.source == 'pack' and not self.pack_file:
            raise ValueError("pack_file required for pack source")

# Profile registry - no hardcoded keywords, content-type based
PROFILE_CONFIGS: Dict[str, ProfileConfig] = {
    ProfileType.DEFS.value: ProfileConfig(
        name="defs",
        source="pack",
        pack_file="packs/definitions.json",
        widenable=False,  # No widening for definition packs
        priority=1,
        max_chunks=3,
        similarity_threshold=0.4
    ),
    
    ProfileType.THEOREM.value: ProfileConfig(
        name="theorem",
        source="index", 
        index_name="theorems",
        widenable=True,
        priority=2,
        max_chunks=5,
        similarity_threshold=0.35,
        relevance_boost=0.1  # Boost for theorem content
    ),
    
    ProfileType.WORKED.value: ProfileConfig(
        name="worked",
        source="index",
        index_name="worked_examples", 
        widenable=True,
        priority=3,
        max_chunks=4,
        similarity_threshold=0.35
    ),
    
    ProfileType.GENERAL.value: ProfileConfig(
        name="general",
        source="index",
        index_name="general",
        widenable=True,
        priority=4,  # Lowest priority fallback
        max_chunks=6,
        similarity_threshold=0.3
    )
}

def get_profile_config(profile_name: str) -> ProfileConfig:
    """Get configuration for a specific profile"""
    if profile_name not in PROFILE_CONFIGS:
        raise ValueError(f"Unknown profile: {profile_name}")
    return PROFILE_CONFIGS[profile_name]

def get_all_profiles() -> Dict[str, ProfileConfig]:
    """Get all available profile configurations"""
    return PROFILE_CONFIGS.copy()

def get_profile_by_priority() -> list:
    """Get profiles sorted by priority (highest first)"""
    return sorted(PROFILE_CONFIGS.values(), key=lambda p: p.priority)

def add_profile(name: str, config: ProfileConfig) -> None:
    """Add a new profile configuration"""
    PROFILE_CONFIGS[name] = config

def remove_profile(name: str) -> None:
    """Remove a profile configuration"""
    if name in PROFILE_CONFIGS:
        del PROFILE_CONFIGS[name]
    else:
        raise ValueError(f"Profile {name} does not exist")

# Profile selection logic (no hardcoded keywords)
def select_profile_for_query(query: str, query_metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Select appropriate profile for a query based on metadata and patterns
    No hardcoded keywords - uses metadata and learned patterns
    """
    # Default to theorem profile
    selected_profile = ProfileType.THEOREM.value
    
    # Use metadata if available
    if query_metadata:
        # Check for explicit profile preference
        if 'preferred_profile' in query_metadata:
            preferred = query_metadata['preferred_profile']
            if preferred in PROFILE_CONFIGS:
                return preferred
        
        # Check for content type hints
        content_type = query_metadata.get('content_type', '')
        if content_type == 'definition':
            selected_profile = ProfileType.DEFS.value
        elif content_type == 'example' or content_type == 'exercise':
            selected_profile = ProfileType.WORKED.value
        elif content_type == 'general':
            selected_profile = ProfileType.GENERAL.value
    
    return selected_profile

def get_profile_metadata() -> Dict[str, Any]:
    """Get metadata about available profiles"""
    return {
        'profiles': list(PROFILE_CONFIGS.keys()),
        'profile_types': [p.value for p in ProfileType],
        'default_profile': ProfileType.THEOREM.value,
        'total_profiles': len(PROFILE_CONFIGS)
    }
