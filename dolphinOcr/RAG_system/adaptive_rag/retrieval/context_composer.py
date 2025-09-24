"""
Context composition for adaptive RAG
"""

from typing import List, Dict, Any

class ContextComposer:
    """Composes context from retrieved chunks"""
    
    def __init__(self, max_tokens: int = 1100):
        self.max_tokens = max_tokens
    
    def compose(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compose context from chunks with deduplication and labeling"""
        if not chunks:
            return []
        
        # Sort by score (highest first)
        sorted_chunks = sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)
        
        # Deduplicate
        deduplicated = self._deduplicate_chunks(sorted_chunks)
        
        # Trim to token budget
        trimmed = self._trim_to_budget(deduplicated)
        
        # Label chunks
        labeled = self._label_chunks(trimmed)
        
        return labeled
    
    def _deduplicate_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove near-duplicate chunks"""
        if len(chunks) <= 1:
            return chunks
        
        # Simple deduplication based on content similarity
        unique_chunks = []
        for chunk in chunks:
            is_duplicate = False
            for existing in unique_chunks:
                similarity = self._calculate_similarity(chunk['text'], existing['text'])
                if similarity > 0.92:  # High similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simplified)"""
        # Simple Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _trim_to_budget(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trim chunks to fit within token budget"""
        current_tokens = 0
        selected_chunks = []
        
        for chunk in chunks:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            chunk_tokens = len(chunk['text']) // 4
            
            if current_tokens + chunk_tokens <= self.max_tokens:
                selected_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Try to truncate the chunk
                remaining_tokens = self.max_tokens - current_tokens
                if remaining_tokens > 50:  # Only if we have significant space left
                    truncated_text = chunk['text'][:remaining_tokens * 4]
                    chunk_copy = chunk.copy()
                    chunk_copy['text'] = truncated_text
                    selected_chunks.append(chunk_copy)
                break
        
        return selected_chunks
    
    def _label_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Label chunks with C1, C2, etc."""
        labeled_chunks = []
        for i, chunk in enumerate(chunks):
            labeled_chunk = chunk.copy()
            labeled_chunk['label'] = f'C{i+1}'
            labeled_chunks.append(labeled_chunk)
        
        return labeled_chunks
