import os
import glob
import json
import torch
import faiss
import pickle
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# Import configuration
from config import CHUNK_SIZE, CHUNK_OVERLAP, ENABLE_MATH_ENHANCEMENT

# Paths
MARKDOWN_DIR = '/home/rchaudhry_umass_edu/rag/data/output/markdown'
JSON_DIR = '/home/rchaudhry_umass_edu/rag/data/output/recognition_json'
INDEX_DIR = '/home/rchaudhry_umass_edu/rag/data/index_data'

# embedding model for mathematical and technical content
EMBED_MODEL = 'BAAI/bge-small-en-v1.5'  

# Mathematical content patterns for enhancement
MATH_PATTERNS = [
    r'\$.*?\$',  # LaTeX inline math
    r'\\\(.*?\\\)',  # LaTeX display math
    r'\\\[.*?\\\]',  # LaTeX display math
    r'[0-9]+\.?[0-9]*',  # Numbers
    r'[a-zA-Z]+\([^)]*\)',  # Functions
    r'[+\-*/=<>≤≥≠≈]',  # Mathematical operators
    r'[∫∑∏√∞θαβγδμσ²³]',  # Mathematical symbols
]

class EnhancedContentProcessor:
    """Process and enhance content for better retrieval"""
    
    @staticmethod
    def extract_math_content(text: str) -> str:
        """Extract mathematical expressions and enhance them"""
        if not ENABLE_MATH_ENHANCEMENT:
            return text
            
        math_content = []
        for pattern in MATH_PATTERNS:
            matches = re.findall(pattern, text)
            math_content.extend(matches)
        
        # Add mathematical keywords if found
        math_keywords = ['probability', 'distribution', 'random', 'expectation', 'variance', 
                        'theorem', 'proof', 'formula', 'equation', 'solve', 'calculate',
                        'random variable', 'probability mass function', 'probability density function',
                        'cumulative distribution function', 'moment generating function',
                        'central limit theorem', 'law of large numbers', 'bayes theorem',
                        'conditional probability', 'independence', 'joint probability']
        
        enhanced_text = text
        for keyword in math_keywords:
            if keyword.lower() in text.lower():
                enhanced_text += f" {keyword}"
        
        return enhanced_text
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Create overlapping chunks for better context retrieval"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                # Enhance each chunk with mathematical content if enabled
                if ENABLE_MATH_ENHANCEMENT:
                    enhanced_chunk = EnhancedContentProcessor.extract_math_content(chunk)
                    chunks.append(enhanced_chunk)
                else:
                    chunks.append(chunk)
        
        return chunks

def build_enhanced_index():
    """Build an enhanced index for better content retrieval"""
    
    print("Building enhanced index for improved content retrieval...")
    
    # Load markdown files
    md_files = sorted(glob.glob(os.path.join(MARKDOWN_DIR, '*.md')))
    md_texts = []
    md_filenames = []
    md_chunks = []
    
    processor = EnhancedContentProcessor()
    
    print(f"Processing {len(md_files)} markdown files...")
    
    for f in md_files:
        with open(f, 'r', encoding='utf-8') as file:
            text = file.read()
            md_texts.append(text)
            md_filenames.append(os.path.basename(f))
            
            # Create chunks with mathematical enhancement
            chunks = processor.chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            md_chunks.extend(chunks)
    
    print(f"Created {len(md_chunks)} chunks from {len(md_texts)} documents")
    
    # Load JSON files for enrichment
    json_files = sorted(glob.glob(os.path.join(JSON_DIR, '*.json')))
    json_data = {}
    for f in json_files:
        with open(f, 'r', encoding='utf-8') as file:
            json_data[os.path.basename(f)] = json.load(file)
    
    # Build embeddings for chunks
    print(f"Loading embedding model: {EMBED_MODEL}")
    embedder = SentenceTransformer(EMBED_MODEL)
    
    print("Creating embeddings for chunks...")
    chunk_embeddings = embedder.encode(md_chunks, convert_to_numpy=True, show_progress_bar=True)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(chunk_embeddings)
    
    # Build enhanced FAISS index
    print("Building enhanced FAISS index...")
    
    # Use IndexFlatIP (Inner Product) for cosine similarity with normalized vectors
    # This is more efficient than IndexFlatL2 for normalized vectors
    dimension = chunk_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    
    # Add vectors to index
    index.add(chunk_embeddings)
    
    print(f"Index built with {index.ntotal} vectors of dimension {dimension}")
    
    # Save enhanced index and data
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    print("Saving enhanced index and data...")
    
    # Save FAISS index
    faiss.write_index(index, os.path.join(INDEX_DIR, 'faiss.index'))
    
    # Save chunk data
    with open(os.path.join(INDEX_DIR, 'md_chunks.pkl'), 'wb') as f:
        pickle.dump(md_chunks, f)
    
    # Save filenames (for reference)
    with open(os.path.join(INDEX_DIR, 'md_filenames.pkl'), 'wb') as f:
        pickle.dump(md_filenames, f)
    
    # Save chunk embeddings
    np.save(os.path.join(INDEX_DIR, 'chunk_embeddings.npy'), chunk_embeddings)
    
    # Save JSON data
    with open(os.path.join(INDEX_DIR, 'json_data.pkl'), 'wb') as f:
        pickle.dump(json_data, f)
    
    # Save metadata
    metadata = {
        'num_documents': len(md_texts),
        'num_chunks': len(md_chunks),
        'chunk_size': CHUNK_SIZE,
        'overlap': CHUNK_OVERLAP,
        'embedding_model': EMBED_MODEL,
        'embedding_dimension': dimension,
        'index_type': 'IndexFlatIP',
        'similarity_metric': 'cosine',
        'math_enhancement_enabled': ENABLE_MATH_ENHANCEMENT
    }
    
    with open(os.path.join(INDEX_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Enhanced indexing complete!")
    print(f"Index saved to: {INDEX_DIR}")
    print(f"Number of chunks: {len(md_chunks)}")
    print(f"Embedding dimension: {dimension}")
    print(f"Index type: IndexFlatIP (optimized for cosine similarity)")
    print(f"Math enhancement: {'Enabled' if ENABLE_MATH_ENHANCEMENT else 'Disabled'}")
    
    # Test the index
    print("\nTesting index with sample query...")
    test_query = "probability distribution"
    test_emb = embedder.encode([test_query], convert_to_numpy=True)
    faiss.normalize_L2(test_emb)
    
    D, I = index.search(test_emb, 3)
    print(f"Sample query: '{test_query}'")
    print(f"Top 3 similarities: {1 - D[0]}")
    print(f"Top 3 chunk indices: {I[0]}")
    
    return index, md_chunks, chunk_embeddings

if __name__ == "__main__":
    build_enhanced_index() 