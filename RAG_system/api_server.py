import os
import pickle
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Import configuration
from config import (
    SIMILARITY_THRESHOLD, MIN_RELEVANT_RESULTS, DOMAIN_THRESHOLD,
    DOMAIN_KEYWORDS, NO_RELEVANT_INFO_MESSAGE, DOMAIN_DESCRIPTION,
    DEBUG_SIMILARITY_SCORES, DEBUG_DOMAIN_CHECK
)

# Paths
INDEX_DIR = '/home/rchaudhry_umass_edu/rag/dolphinOcr/RAG_system/index_data'
MODEL_PATH = '/datasets/ai/llama3/hub/models--meta-llama--Meta-Llama-3-8B-Instruct/snapshots/5f0b02c75b57c5855da9ae460ce51323ea669d8a'
EMBED_MODEL = 'all-MiniLM-L6-v2'

# Load index and data once at startup
print('Loading FAISS index and data...')
index = faiss.read_index(os.path.join(INDEX_DIR, 'faiss.index'))
with open(os.path.join(INDEX_DIR, 'md_filenames.pkl'), 'rb') as f:
    md_filenames = pickle.load(f)
with open(os.path.join(INDEX_DIR, 'md_texts.pkl'), 'rb') as f:
    md_texts = pickle.load(f)
with open(os.path.join(INDEX_DIR, 'json_data.pkl'), 'rb') as f:
    json_data = pickle.load(f)
md_embeddings = np.load(os.path.join(INDEX_DIR, 'md_embeddings.npy'))

# Load embedding model
embedder = SentenceTransformer(EMBED_MODEL)

# Load Llama-3 model and tokenizer
print('Loading Llama-3 (Meta-Llama-3-8B-Instruct) model...')
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16, device_map='auto', trust_remote_code=True)

def retrieve_markdown(query, top_k=3, similarity_threshold=SIMILARITY_THRESHOLD):
    """
    Retrieve relevant markdown files based on query similarity.
    Returns empty list if no results meet the similarity threshold.
    """
    query_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, top_k)
    
    # Convert distances to cosine similarities
    # FAISS L2 distance: similarity = 1 - (distance^2 / 2) for normalized vectors
    # For inner product (if using IP index): similarity = distance directly
    similarities = 1 - (D[0] ** 2 / 2)  # Assuming L2 normalized embeddings
    
    results = []
    relevant_count = 0
    
    for idx, similarity in zip(I[0], similarities):
        if similarity >= similarity_threshold:
            fname = md_filenames[idx]
            text = md_texts[idx]
            # Optionally, enrich with JSON if available
            json_name = fname.replace('.md', '.json')
            extra = ''
            if json_name in json_data:
                extra = f"\n\n[Structured Data]\n{str(json_data[json_name])[:1000]}..."  # Truncate for context size
            results.append((fname, text + extra, similarity))
            relevant_count += 1
        else:
            if DEBUG_SIMILARITY_SCORES:
                print(f"Filtered out {md_filenames[idx]} (similarity: {similarity:.3f} < {similarity_threshold})")
    
    # Return empty if not enough relevant results
    if relevant_count < MIN_RELEVANT_RESULTS:
        print(f"Only {relevant_count} relevant results found (minimum required: {MIN_RELEVANT_RESULTS})")
        return []
    
    return results

def is_query_relevant_to_domain(query):
    """
    Check if query is potentially relevant to the knowledge base domain.
    This is a simple heuristic - you can make it more sophisticated.
    """
    query_lower = query.lower()
    
    # Check if query contains domain-specific terms
    for keyword in DOMAIN_KEYWORDS:
        if keyword in query_lower:
            if DEBUG_DOMAIN_CHECK:
                print(f"Query contains domain keyword: {keyword}")
            return True
    
    # Additional check: embed query and compare with a few representative documents
    query_emb = embedder.encode([query], convert_to_numpy=True)
    
    # Sample a few embeddings to check general domain relevance
    sample_size = min(50, len(md_embeddings))
    sample_indices = np.random.choice(len(md_embeddings), sample_size, replace=False)
    sample_embeddings = md_embeddings[sample_indices]
    
    # Calculate similarities with sample
    similarities = np.dot(query_emb, sample_embeddings.T)[0]
    max_similarity = np.max(similarities)
    
    if DEBUG_DOMAIN_CHECK:
        print(f"Max similarity with sample documents: {max_similarity:.3f} (threshold: {DOMAIN_THRESHOLD})")
    
    return max_similarity >= DOMAIN_THRESHOLD

def build_prompt(query, context_blocks):
    prompt = "You are a helpful assistant. Use the following context to answer the user's question.\n\n"
    for fname, ctx, similarity in context_blocks:
        prompt += f"[File: {fname}] (Similarity: {similarity:.3f})\n{ctx}\n\n"
    prompt += f"[User Question]\n{query}\n\n[Answer]"
    return prompt

def answer_query(query, top_k=3, max_new_tokens=512, similarity_threshold=SIMILARITY_THRESHOLD):
    """
    Answer query with relevance filtering.
    Returns None for answer if query is not relevant to knowledge base.
    """
    
    # First check if query is potentially relevant to the domain
    if not is_query_relevant_to_domain(query):
        return None, []
    
    # Retrieve relevant context
    context_blocks = retrieve_markdown(query, top_k=top_k, similarity_threshold=similarity_threshold)
    
    # If no relevant context found, return None
    if not context_blocks:
        return None, []
    
    # Generate answer using retrieved context
    prompt = build_prompt(query, context_blocks)
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7)
    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    return answer, context_blocks

# FastAPI app
app = FastAPI(title="RAG API", description="Retrieval-Augmented Generation API using Llama-3")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    max_new_tokens: int = 512
    similarity_threshold: float = SIMILARITY_THRESHOLD  # Allow custom threshold

class QueryResponse(BaseModel):
    answer: str
    context_files: list
    is_relevant: bool = True
    message: str = ""

@app.get("/")
def root():
    return {
        "message": "RAG API is running", 
        "model": "Llama-3-8B-Instruct",
        "default_similarity_threshold": SIMILARITY_THRESHOLD,
        "domain": DOMAIN_DESCRIPTION,
        "python_version": "3.8.18",
        "min_relevant_results": MIN_RELEVANT_RESULTS
    }

@app.post("/rag", response_model=QueryResponse)
def rag_endpoint(req: QueryRequest):
    try:
        answer, context_blocks = answer_query(
            req.query, 
            top_k=req.top_k, 
            max_new_tokens=req.max_new_tokens,
            similarity_threshold=req.similarity_threshold
        )
        
        if answer is None:
            return {
                "answer": NO_RELEVANT_INFO_MESSAGE,
                "context_files": [],
                "is_relevant": False,
                "message": "Query not relevant to knowledge base domain or no sufficiently similar content found."
            }
        
        return {
            "answer": answer,
            "context_files": [
                {
                    "filename": fname, 
                    "context": ctx[:1000],
                    "similarity_score": float(similarity)
                } for fname, ctx, similarity in context_blocks
            ],
            "is_relevant": True,
            "message": f"Found {len(context_blocks)} relevant documents with similarity >= {req.similarity_threshold}"
        }
        
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}", 
            "context_files": [],
            "is_relevant": False,
            "message": f"Server error: {str(e)}"
        }

if __name__ == "__main__":
    print("Starting RAG API server...")
    print(f"Default similarity threshold: {SIMILARITY_THRESHOLD}")
    print(f"Python version: 3.8.18")
    print(f"Domain: {DOMAIN_DESCRIPTION}")
    uvicorn.run(app, host="0.0.0.0", port=8000)