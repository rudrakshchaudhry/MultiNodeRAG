#!/usr/bin/env python3
"""
Simple RAG API for testing - minimal version without heavy model loading
"""

import os
import sys
import time
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Add the adaptive_rag directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'adaptive_rag')))

from adaptive_rag.core.query_analyzer import QueryAnalyzer
from adaptive_rag.config.adaptive_config import get_adaptive_config

# --- FastAPI Models ---
class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_new_tokens: Optional[int] = None
    profile: Optional[str] = None
    query_metadata: Optional[Dict[str, Any]] = None

class RAGResponse(BaseModel):
    answer: str
    used_rag: bool
    context_blocks: List[Dict[str, Any]]
    router_decision: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    model_used: str

class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str = "Simple RAG API is running"
    uptime_seconds: float = 0.0
    config_status: Dict[str, Any] = {}

# --- Global State ---
class AppState:
    def __init__(self):
        self.config = None
        self.query_analyzer = None
        self.start_time = time.time()

app_state = AppState()

# --- FastAPI App ---
app = FastAPI(
    title="Simple RAG API",
    description="A minimal RAG API for testing and development",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    print("🚀 Starting Simple RAG API...")
    
    try:
        # Load configuration
        app_state.config = get_adaptive_config()
        print("✅ Configuration loaded")
        
        # Initialize query analyzer
        app_state.query_analyzer = QueryAnalyzer(app_state.config)
        print("✅ Query analyzer initialized")
        
        print("🎉 Simple RAG API ready!")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app_state.start_time
    return HealthResponse(
        status="healthy",
        message="Simple RAG API is running",
        uptime_seconds=uptime,
        config_status={
            "retrieval_k": app_state.config.start_k if app_state.config else "unknown",
            "model_max_tokens": app_state.config.model_max_tokens if app_state.config else "unknown",
            "telemetry_enabled": app_state.config.enable_telemetry if app_state.config else "unknown"
        }
    )

@app.post("/query", response_model=RAGResponse)
async def process_query(request: QueryRequest):
    """Process a user query using the adaptive RAG system"""
    if not app_state.query_analyzer:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    start_time = time.time()
    query = request.query
    
    # Analyze query complexity
    complexity_analysis = app_state.query_analyzer.analyze_query(query, request.query_metadata)
    use_rag = complexity_analysis.recommendation == "rag"
    
    # For this simple version, we'll just return mock responses
    if use_rag:
        answer = f"[RAG Response] Based on the complexity analysis, this query would benefit from RAG retrieval. Query: {query}"
        context_blocks = [
            {"text": "This is a mock context block for demonstration", "relevance": 0.8, "label": "Context 1"}
        ]
    else:
        answer = f"[Direct Response] This is a simple query that can be answered directly. Query: {query}"
        context_blocks = []
    
    end_time = time.time()
    
    router_decision = {
        'use_rag': use_rag,
        'reason': complexity_analysis.reasoning,
        'confidence': complexity_analysis.confidence,
        'complexity_score': complexity_analysis.complexity_score,
        'routing_method': 'complexity_analysis'
    }
    
    performance_metrics = {
        'total_time': end_time - start_time,
        'model_generation_tokens': 0,  # Mock value
        'model_generation_time': end_time - start_time
    }
    
    return RAGResponse(
        answer=answer,
        used_rag=use_rag,
        context_blocks=context_blocks,
        router_decision=router_decision,
        performance_metrics=performance_metrics,
        model_used="mock-model"
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("RAG_API_PORT", 8080))
    print(f"Starting Simple RAG API server on port {port}")
    uvicorn.run(
        "simple_rag_api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
