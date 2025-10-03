"""
Relevance scoring for adaptive RAG
"""

from typing import List, Dict, Any

class RelevanceScorer:
    """Scorer for relevance assessment"""
    
    def __init__(self):
        pass
    
    def mean_relevance(self, results: List[Dict[str, Any]]) -> float:
        """Calculate mean relevance score"""
        if not results:
            return 0.0
        
        scores = [result.get('similarity', 0.0) for result in results]
        return sum(scores) / len(scores)
    
    def novelty_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate novelty score (diversity of results)"""
        if len(results) < 2:
            return 1.0
        
        # Simple diversity based on unique sources
        unique_sources = set(result.get('id', '') for result in results)
        return len(unique_sources) / len(results)
    
    def relevance_delta(self, results: List[Dict[str, Any]]) -> float:
        """Calculate relevance delta (difference between top and bottom scores)"""
        if len(results) < 2:
            return 0.0
        
        scores = [result.get('similarity', 0.0) for result in results]
        scores.sort(reverse=True)
        
        return scores[0] - scores[-1]
