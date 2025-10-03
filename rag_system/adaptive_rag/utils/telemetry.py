"""
Telemetry logging for adaptive RAG system
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from ..config.adaptive_config import get_adaptive_config

def log_router_decision(query: str, decision: Any, performance_metrics: Dict[str, Any]) -> None:
    """Log router decision for analysis and optimization"""
    config = get_adaptive_config()
    
    if not config.enable_telemetry:
        return
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query[:200],  # Truncate long queries
        'decision': {
            'use_rag': decision.use_rag,
            'reason': decision.reason,
            'confidence': decision.confidence,
            'profile': decision.profile
        },
        'performance': performance_metrics,
        'config': {
            'token_cutoff': config.token_cutoff,
            'start_k': config.start_k,
            'relevance_threshold': config.relevance_threshold
        }
    }
    
    try:
        with open(config.telemetry_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        # Silently fail if logging fails
        pass

def setup_telemetry(log_file: Optional[str] = None) -> None:
    """Setup telemetry logging"""
    config = get_adaptive_config()
    
    if log_file:
        config.telemetry_log_file = log_file
    
    if config.enable_telemetry:
        # Ensure log file exists
        try:
            with open(config.telemetry_log_file, 'a') as f:
                pass
        except Exception:
            # Disable telemetry if we can't write to log file
            config.enable_telemetry = False

def get_telemetry_stats(log_file: Optional[str] = None) -> Dict[str, Any]:
    """Get statistics from telemetry logs"""
    config = get_adaptive_config()
    log_file = log_file or config.telemetry_log_file
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        total_queries = len(lines)
        rag_queries = 0
        direct_queries = 0
        reasons = {}
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                if entry['decision']['use_rag']:
                    rag_queries += 1
                else:
                    direct_queries += 1
                
                reason = entry['decision']['reason']
                reasons[reason] = reasons.get(reason, 0) + 1
            except:
                continue
        
        return {
            'total_queries': total_queries,
            'rag_queries': rag_queries,
            'direct_queries': direct_queries,
            'rag_percentage': (rag_queries / total_queries * 100) if total_queries > 0 else 0,
            'decision_reasons': reasons,
            'avg_response_time': 0.0  # Could calculate from performance metrics
        }
    except Exception:
        return {
            'total_queries': 0,
            'rag_queries': 0,
            'direct_queries': 0,
            'rag_percentage': 0.0,
            'decision_reasons': {},
            'avg_response_time': 0.0
        }
