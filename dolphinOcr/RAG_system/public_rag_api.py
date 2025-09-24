#!/usr/bin/env python3
"""
Public RAG API - Designed for external access
"""

import os
import sys
import time
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
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
    api_version: str = "1.0.0"

class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str = "Public RAG API is running"
    uptime_seconds: float = 0.0
    api_version: str = "1.0.0"
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
    title="Public RAG API",
    description="A public RAG API for external applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    print("🚀 Starting Public RAG API...")
    
    try:
        # Load configuration
        app_state.config = get_adaptive_config()
        print("✅ Configuration loaded")
        
        # Initialize query analyzer
        app_state.query_analyzer = QueryAnalyzer(app_state.config)
        print("✅ Query analyzer initialized")
        
        print("🎉 Public RAG API ready!")
        print("🌐 Accessible from external applications")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic info"""
    uptime = time.time() - app_state.start_time
    return HealthResponse(
        status="healthy",
        message="Public RAG API is running",
        uptime_seconds=uptime,
        api_version="1.0.0",
        config_status={
            "retrieval_k": app_state.config.start_k if app_state.config else "unknown",
            "model_max_tokens": app_state.config.model_max_tokens if app_state.config else "unknown",
            "telemetry_enabled": app_state.config.enable_telemetry if app_state.config else "unknown"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app_state.start_time
    return HealthResponse(
        status="healthy",
        message="Public RAG API is running",
        uptime_seconds=uptime,
        api_version="1.0.0",
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
    
    # Enhanced responses based on complexity
    if use_rag:
        answer = f"""Based on the complexity analysis, this query would benefit from RAG retrieval.

**Query Analysis:**
- Complexity Score: {complexity_analysis.complexity_score:.2f}
- Confidence: {complexity_analysis.confidence:.2f}
- Reasoning: {complexity_analysis.reasoning}

**Response:** This is a complex query that would be enhanced with additional context from the knowledge base. The RAG system would retrieve relevant documents and provide a more comprehensive answer.

**Original Query:** {query}"""
        
        context_blocks = [
            {
                "text": "This is a mock context block demonstrating how RAG would enhance the response with relevant information from the knowledge base.",
                "relevance": 0.8,
                "label": "Knowledge Base Context",
                "source": "mock-document.pdf",
                "page": 1
            },
            {
                "text": "Additional context would be retrieved based on the query complexity and relevance scoring.",
                "relevance": 0.7,
                "label": "Supporting Information",
                "source": "reference-material.pdf",
                "page": 3
            }
        ]
    else:
        answer = f"""This is a simple query that can be answered directly.

**Query Analysis:**
- Complexity Score: {complexity_analysis.complexity_score:.2f}
- Confidence: {complexity_analysis.confidence:.2f}
- Reasoning: {complexity_analysis.reasoning}

**Response:** {query}

This query was determined to be simple enough for direct generation without additional context retrieval."""
        
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
        'model_generation_time': end_time - start_time,
        'api_version': '1.0.0'
    }
    
    return RAGResponse(
        answer=answer,
        used_rag=use_rag,
        context_blocks=context_blocks,
        router_decision=router_decision,
        performance_metrics=performance_metrics,
        model_used="public-rag-api",
        api_version="1.0.0"
    )

@app.get("/models")
async def get_models():
    """Get available models and capabilities"""
    return {
        "api_version": "1.0.0",
        "models": [
            {
                "name": "public-rag-api",
                "type": "rag",
                "capabilities": ["query_analysis", "context_retrieval", "adaptive_routing"],
                "status": "available"
            }
        ],
        "features": [
            "Adaptive query routing",
            "Complexity analysis",
            "Context retrieval",
            "CORS enabled",
            "External access"
        ]
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("RAG_API_PORT", 8080))
    host = os.environ.get("RAG_API_HOST", "0.0.0.0")
    print(f"Starting Public RAG API server on {host}:{port}")
    uvicorn.run(
        "public_rag_api:app",
        host=host,
        port=port,
        reload=False
    )
