"""
Dynamic retrieval with progressive widening for adaptive RAG
"""

import time
import numpy as np
import faiss
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..config.adaptive_config import get_adaptive_config
from ..config.profiles_config import get_profile_config
from ..caching.query_cache import QueryCache
from .relevance import RelevanceScorer
from .context_composer import ContextComposer

@dataclass
class RetrievalResult:
    """Result from dynamic retrieval"""
    chunks: List[Dict[str, Any]]
    used_widening: bool
    mean_relevance: float
    retrieval_time: float
    profile_used: str

class DynamicRetriever:
    """Dynamic retriever with progressive widening"""
    
    def __init__(self, index_dir: str = None, embed_model: str = None):
        self.config = get_adaptive_config()
        self.index_dir = index_dir or '/home/rchaudhry_umass_edu/rag/dolphinOcr/rag_creation/index_data'
        self.embed_model = embed_model or 'BAAI/bge-small-en-v1.5'
        
        # Initialize components
        self.query_cache = QueryCache(self.config.cache_sizes['query'])
        self.relevance_scorer = RelevanceScorer()
        self.context_composer = ContextComposer(self.config.max_context_tokens)
        
        # Load existing index and data (reuse from current system)
        self._load_index_data()
        
    def _load_index_data(self):
        """Load FAISS index and associated data"""
        import pickle
        import os
        
        # Load index
        self.index = faiss.read_index(os.path.join(self.index_dir, 'faiss.index'))
        
        # Load chunk data
        with open(os.path.join(self.index_dir, 'md_chunks.pkl'), 'rb') as f:
            self.md_chunks = pickle.load(f)
        with open(os.path.join(self.index_dir, 'md_filenames.pkl'), 'rb') as f:
            self.md_filenames = pickle.load(f)
        with open(os.path.join(self.index_dir, 'json_data.pkl'), 'rb') as f:
            self.json_data = pickle.load(f)
        self.chunk_embeddings = np.load(os.path.join(self.index_dir, 'chunk_embeddings.npy'))
        
        # Load embedding model
        from sentence_transformers import SentenceTransformer
        self.embedder = SentenceTransformer(self.embed_model)
        
    def retrieve(self, query: str, profile: str = 'theorem', k: int = None, 
                config: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Perform dynamic retrieval with progressive widening
        """
        start_time = time.time()
        
        # Get profile configuration
        profile_config = get_profile_config(profile)
        
        # Use provided k or profile default
        k = k or profile_config.max_chunks
        
        # Check cache first
        cache_key = f"{profile}::{query}"
        cached_result = self.query_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Perform retrieval based on profile source
        if profile_config.source == 'pack':
            chunks = self._retrieve_from_pack(profile_config)
        else:
            chunks = self._retrieve_from_index(query, profile_config, k, config)
        
        # Compose context
        composed_chunks = self.context_composer.compose(chunks)
        
        # Cache result
        self.query_cache.set(cache_key, composed_chunks)
        
        retrieval_time = time.time() - start_time
        
        return composed_chunks
    
    def _retrieve_from_pack(self, profile_config) -> List[Dict[str, Any]]:
        """Retrieve from pre-defined pack (no search needed)"""
        import json
        import os
        
        pack_file = profile_config.pack_file
        # Make path relative to current directory
        if not os.path.isabs(pack_file):
            pack_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', pack_file)
        
        if not os.path.exists(pack_file):
            # Create default definitions pack if it doesn't exist
            self._create_default_definitions_pack(pack_file)
        
        with open(pack_file, 'r') as f:
            pack_data = json.load(f)
        
        # Convert pack data to chunk format
        chunks = []
        for i, item in enumerate(pack_data):
            chunks.append({
                'id': item.get('id', f'pack_{i}'),
                'text': item.get('text', ''),
                'source': 'pack',
                'score': 1.0,  # Pack items have full relevance
                'label': f'C{i+1}'
            })
        
        return chunks
    
    def _create_default_definitions_pack(self, pack_file: str):
        """Create a default definitions pack"""
        import json
        import os
        
        default_definitions = [
            {
                "id": "defs:probability",
                "text": "Probability is a measure of the likelihood that an event will occur. It is quantified as a number between 0 and 1, where 0 indicates impossibility and 1 indicates certainty."
            },
            {
                "id": "defs:random_variable",
                "text": "A random variable is a variable whose possible values are outcomes of a random phenomenon. It can be discrete (taking countable values) or continuous (taking uncountable values)."
            },
            {
                "id": "defs:expectation",
                "text": "The expected value or expectation of a random variable is the long-run average value of repetitions of the experiment it represents. For discrete random variables, it is the sum of all possible values weighted by their probabilities."
            },
            {
                "id": "defs:variance",
                "text": "Variance measures how far a set of numbers are spread out from their average value. For a random variable, it is the expected value of the squared deviation from the mean."
            },
            {
                "id": "defs:distribution",
                "text": "A probability distribution describes the probabilities of all possible outcomes of a random variable. It can be specified by a probability mass function (discrete) or probability density function (continuous)."
            }
        ]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(pack_file), exist_ok=True)
        
        with open(pack_file, 'w') as f:
            json.dump(default_definitions, f, indent=2)
    
    def _retrieve_from_index(self, query: str, profile_config, k: int, 
                           config: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Retrieve from FAISS index with progressive widening"""
        
        # Use config or default
        config = config or self.config
        
        # Encode query
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        query_embedding = faiss.normalize_L2(query_embedding)
        
        # Initial search with start_k
        start_k = min(k, config.start_k)
        similarities, indices = self.index.search(query_embedding, start_k)
        
        # Filter by similarity threshold
        relevant_results = []
        for i, (sim_score, idx) in enumerate(zip(similarities[0], indices[0])):
            if sim_score >= profile_config.similarity_threshold:
                filename = self.md_filenames[idx]
                content = self.md_chunks[idx]
                
                # Apply profile-specific relevance boost
                boosted_score = sim_score + profile_config.relevance_boost
                
                relevant_results.append({
                    'filename': filename,
                    'content': content,
                    'similarity': float(boosted_score),
                    'index': idx
                })
        
        # Calculate mean relevance
        mean_relevance = self.relevance_scorer.mean_relevance(relevant_results)
        
        # Progressive widening if needed
        used_widening = False
        if (profile_config.widenable and 
            mean_relevance < config.relevance_threshold and 
            len(relevant_results) < k):
            
            # Search with more results
            wider_k = min(start_k + config.widen_by, k, len(self.md_chunks))
            similarities_wider, indices_wider = self.index.search(query_embedding, wider_k)
            
            # Combine and re-rank
            all_results = []
            for i, (sim_score, idx) in enumerate(zip(similarities_wider[0], indices_wider[0])):
                if sim_score >= profile_config.similarity_threshold:
                    filename = self.md_filenames[idx]
                    content = self.md_chunks[idx]
                    boosted_score = sim_score + profile_config.relevance_boost
                    
                    all_results.append({
                        'filename': filename,
                        'content': content,
                        'similarity': float(boosted_score),
                        'index': idx
                    })
            
            # Take top k results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            relevant_results = all_results[:k]
            used_widening = True
        
        # Convert to chunk format
        chunks = []
        for i, result in enumerate(relevant_results):
            chunks.append({
                'id': result['filename'],
                'text': result['content'],
                'source': 'index',
                'score': result['similarity'],
                'label': f'C{i+1}'
            })
        
        return chunks
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about retrieval performance"""
        return {
            'cache_hit_rate': self.query_cache.get_hit_rate(),
            'total_queries': self.query_cache.get_total_queries(),
            'cache_size': self.query_cache.get_size(),
            'index_size': len(self.md_chunks) if hasattr(self, 'md_chunks') else 0
        }
