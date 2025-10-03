"""
Adaptive RAG System - Intelligent query routing and dynamic retrieval
"""

__version__ = "1.0.0"
__author__ = "Adaptive RAG Team"

from .core.query_analyzer import QueryAnalyzer
from .config.adaptive_config import ADAPTIVE_CONFIG

__all__ = [
    "QueryAnalyzer",
    "ADAPTIVE_CONFIG"
]
