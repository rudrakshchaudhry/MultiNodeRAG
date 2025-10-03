"""
Simplified Adaptive RAG API Server
Uses query complexity analysis for routing decisions
"""

import os
import sys
import time
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adaptive_rag.core.query_analyzer import QueryAnalyzer
from adaptive_rag.core.model_interface import create_model_interface, GenerationConfig
from adaptive_rag.config.adaptive_config import get_adaptive_config
from adaptive_rag.retrieval.dynamic_search import DynamicRetriever
from adaptive_rag.config.profiles_config import select_profile_for_query
from transformers import AutoTokenizer, AutoModelForCausalLM

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    query_metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    used_rag: bool
    context_blocks: List[Dict[str, Any]]
    complexity_score: float
    reasoning: str
    performance_metrics: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    model_type: str
    router_type: str
    timestamp: float

# Initialize FastAPI app
app = FastAPI(
    title="Simplified Adaptive RAG API",
    description="Adaptive RAG system using query complexity analysis",
    version="3.0.0"
)

# Global variables
query_analyzer = None
model_interface = None
retriever = None
config = None

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global query_analyzer, model_interface, retriever, config
    
    print("🚀 Starting Simplified Adaptive RAG Server...")
    
    try:
        # Load configuration
        config = get_adaptive_config()
        print(f"✅ Configuration loaded")
        
        # Load model
        model, tokenizer = load_model()
        
        # Create model interface
        model_interface = create_model_interface(model, tokenizer, model_type="auto")
        print(f"✅ Model interface created: {model_interface.get_model_info()}")
        
        # Create query analyzer
        query_analyzer = QueryAnalyzer(config)
        print(f"✅ Query analyzer initialized")
        
        # Create retriever
        retriever = DynamicRetriever()
        print(f"✅ Retriever initialized")
        
        print("🎉 Simplified Adaptive RAG Server ready!")
        
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        raise

def load_model():
    """Load the model and tokenizer"""
    try:
        # Load Qwen model
        model_path = "/datasets/ai/qwen/hub/models--Qwen--Qwen2.5-Math-7B-Instruct/snapshots/ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
        
        print(f"Loading model from {model_path}...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )
        
        print("✅ Model loaded successfully")
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        # Return a mock model for testing
        return MockModel(), MockTokenizer()

class MockModel:
    """Mock model for testing"""
    def generate(self, **kwargs):
        return MockOutput()

class MockTokenizer:
    """Mock tokenizer for testing"""
    def __call__(self, text, **kwargs):
        return {"input_ids": [[1, 2, 3]], "attention_mask": [[1, 1, 1]]}
    
    def decode(self, tokens, **kwargs):
        return "This is a mock response for testing purposes."

class MockOutput:
    """Mock model output for testing"""
    def __init__(self):
        self.sequences = [[1, 2, 3, 4, 5]]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_type=model_interface.get_model_info()["model_type"] if model_interface else "unknown",
        router_type="simplified_complexity",
        timestamp=time.time()
    )

@app.post("/adaptive_rag", response_model=QueryResponse)
async def adaptive_rag_query(request: QueryRequest):
    """Main adaptive RAG endpoint"""
    try:
        if not all([query_analyzer, model_interface, retriever]):
            raise HTTPException(status_code=500, detail="System not initialized")
        
        start_time = time.time()
        
        # Analyze query complexity
        complexity_analysis = query_analyzer.analyze_query(request.query, request.query_metadata)
        
        # Make routing decision
        use_rag = complexity_analysis.recommendation == "rag"
        
        if use_rag:
            # Execute RAG path
            profile = select_profile_for_query(request.query, request.query_metadata)
            retrieval_result = retriever.retrieve(
                query=request.query,
                profile=profile or "general",
                k=config.retrieval_k,
                query_metadata=request.query_metadata
            )
            
            # Generate with context
            prompt = format_rag_prompt(request.query, retrieval_result['context_blocks'])
            result = model_interface.generate(prompt, GenerationConfig(
                max_new_tokens=config.model_max_tokens,
                temperature=config.model_temperature
            ))
            
            answer = result.text
            context_blocks = retrieval_result['context_blocks']
        else:
            # Execute direct path
            prompt = format_direct_prompt(request.query)
            result = model_interface.generate(prompt, GenerationConfig(
                max_new_tokens=config.model_max_tokens,
                temperature=config.model_temperature
            ))
            
            answer = result.text
            context_blocks = []
        
        end_time = time.time()
        
        return QueryResponse(
            answer=answer,
            used_rag=use_rag,
            context_blocks=context_blocks,
            complexity_score=complexity_analysis.complexity_score,
            reasoning=complexity_analysis.reasoning,
            performance_metrics={
                'total_time': end_time - start_time,
                'used_rag': use_rag,
                'complexity_score': complexity_analysis.complexity_score,
                'confidence': complexity_analysis.confidence
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def format_direct_prompt(query: str) -> str:
    """Format prompt for direct generation"""
    return f"""You are a helpful AI assistant. Please answer the following question directly and concisely.

Question: {query}

Answer:"""

def format_rag_prompt(query: str, context_blocks: List[Dict[str, Any]]) -> str:
    """Format prompt for RAG generation with context"""
    context_text = "\n\n".join([
        f"Context {i+1}:\n{block['content']}" 
        for i, block in enumerate(context_blocks)
    ])
    
    return f"""You are a helpful AI assistant. Use the provided context to answer the question. If the context doesn't contain enough information, use your knowledge to provide a helpful answer.

Context:
{context_text}

Question: {query}

Answer:"""

@app.get("/config")
async def get_config():
    """Get current configuration"""
    if not config:
        raise HTTPException(status_code=500, detail="Configuration not loaded")
    
    return {
        "retrieval_k": config.retrieval_k,
        "model_max_tokens": config.model_max_tokens,
        "model_temperature": config.model_temperature,
        "enable_telemetry": config.enable_telemetry,
        "router_type": "simplified_complexity"
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "router_type": "simplified_complexity",
        "model_type": model_interface.get_model_info()["model_type"] if model_interface else "unknown",
        "config": {
            "retrieval_k": config.retrieval_k if config else None,
            "model_max_tokens": config.model_max_tokens if config else None,
            "model_temperature": config.model_temperature if config else None
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "adaptive_rag_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )