"""
Configuration package for Adaptive RAG System
"""

from .adaptive_config import ADAPTIVE_CONFIG, get_adaptive_config
from .profiles_config import PROFILE_CONFIGS, get_profile_config

__all__ = [
    "ADAPTIVE_CONFIG",
    "get_adaptive_config", 
    "PROFILE_CONFIGS",
    "get_profile_config"
]
