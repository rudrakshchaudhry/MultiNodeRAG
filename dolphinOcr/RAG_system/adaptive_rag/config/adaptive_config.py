"""
Adaptive RAG Configuration - No hardcoded keywords, learned parameters
"""

import os
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class AdaptiveConfig:
    """Configuration for adaptive RAG behavior"""
    
    # Token monitoring
    token_cutoff: int = 72  # When to give up on direct generation
    
    # Dynamic retrieval
    start_k: int = 3  # Initial retrieval size
    widen_by: int = 3  # How much to widen if relevance low
    max_k: int = 12  # Maximum retrieval size
    
    # Relevance thresholds
    relevance_threshold: float = 0.55  # Threshold for widening
    min_relevance: float = 0.35  # Minimum relevance to include context
    
    # Context management
    max_context_tokens: int = 1100  # Context budget
    max_context_chunks: int = 8  # Maximum number of context chunks
    
    # Caching
    cache_sizes: Dict[str, int] = field(default_factory=lambda: {
        'query': 500,
        'context': 300, 
        'pack': 20
    })
    
    # Model settings
    model_temperature: float = 0.7
    model_top_p: float = 0.95
    model_max_tokens: int = 1024
    model_repetition_penalty: float = 1.05
    
    # Telemetry
    enable_telemetry: bool = True
    telemetry_log_file: str = "adaptive_rag_telemetry.jsonl"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.start_k > self.max_k:
            raise ValueError("start_k cannot be greater than max_k")
        if self.relevance_threshold < self.min_relevance:
            raise ValueError("relevance_threshold cannot be less than min_relevance")

# Global configuration instance
ADAPTIVE_CONFIG = AdaptiveConfig()

def get_adaptive_config() -> AdaptiveConfig:
    """Get the global adaptive configuration"""
    return ADAPTIVE_CONFIG

def update_adaptive_config(**kwargs) -> None:
    """Update adaptive configuration parameters"""
    global ADAPTIVE_CONFIG
    for key, value in kwargs.items():
        if hasattr(ADAPTIVE_CONFIG, key):
            setattr(ADAPTIVE_CONFIG, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")
    
    # Re-validate after update
    ADAPTIVE_CONFIG.__post_init__()

# Environment-based overrides
def load_env_config() -> None:
    """Load configuration from environment variables"""
    env_mapping = {
        'ADAPTIVE_TOKEN_CUTOFF': 'token_cutoff',
        'ADAPTIVE_START_K': 'start_k',
        'ADAPTIVE_WIDEN_BY': 'widen_by',
        'ADAPTIVE_MAX_K': 'max_k',
        'ADAPTIVE_RELEVANCE_THRESHOLD': 'relevance_threshold',
        'ADAPTIVE_MIN_RELEVANCE': 'min_relevance',
        'ADAPTIVE_MAX_CONTEXT_TOKENS': 'max_context_tokens',
        'ADAPTIVE_MAX_CONTEXT_CHUNKS': 'max_context_chunks',
        'ADAPTIVE_MODEL_TEMPERATURE': 'model_temperature',
        'ADAPTIVE_MODEL_TOP_P': 'model_top_p',
        'ADAPTIVE_MODEL_MAX_TOKENS': 'model_max_tokens',
        'ADAPTIVE_MODEL_REPETITION_PENALTY': 'model_repetition_penalty',
    }
    
    updates = {}
    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            # Convert to appropriate type
            if config_key in ['token_cutoff', 'start_k', 'widen_by', 'max_k', 'max_context_tokens', 'max_context_chunks', 'model_max_tokens']:
                updates[config_key] = int(value)
            elif config_key in ['relevance_threshold', 'min_relevance', 'model_temperature', 'model_top_p', 'model_repetition_penalty']:
                updates[config_key] = float(value)
    
    if updates:
        update_adaptive_config(**updates)

# Load environment configuration on import
load_env_config()
