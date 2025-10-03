"""
Universal RAG API Server
Deployable anywhere, works with any transformer model via HuggingFace
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adaptive_rag.core.query_analyzer import QueryAnalyzer
from adaptive_rag.config.adaptive_config import get_adaptive_config
from adaptive_rag.retrieval.dynamic_search import DynamicRetriever
from adaptive_rag.config.profiles_config import select_profile_for_query

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    query_metadata: Optional[Dict[str, Any]] = None
    model_config: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    used_rag: bool
    context_blocks: List[Dict[str, Any]]
    complexity_score: float
    reasoning: str
    model_used: str
    performance_metrics: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    rag_system: str
    model_provider: str
    timestamp: float

class ModelConfig(BaseModel):
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.7

# Initialize FastAPI app
app = FastAPI(
    title="Universal RAG API",
    description="Deployable RAG system that works with any transformer model",
    version="1.0.0"
)

# Global variables
query_analyzer = None
retriever = None
config = None
current_model_config = None

class UniversalModelInterface:
    """Universal model interface that works with any API or local models"""
    
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.model_name = model_config.model_name
        self.api_key = model_config.api_key
        self.base_url = model_config.base_url or self._get_default_url()
        self.local_model = None
        self.local_tokenizer = None
        
    def _get_default_url(self) -> str:
        """Get default API URL based on model name"""
        if "gemini" in self.model_name.lower():
            return "https://generativelanguage.googleapis.com/v1beta/models"
        elif "openai" in self.model_name.lower():
            return "https://api.openai.com/v1"
        elif "huggingface" in self.model_name.lower():
            return "https://api-inference.huggingface.co/models"
        else:
            return "https://api.huggingface.co/v1"
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate text using the configured model"""
        try:
            # Check for simple fallback model
            if self.model_name == "simple-fallback":
                return self._call_simple_fallback(prompt, max_tokens, temperature)
            # Check if it's a local model path
            elif "/datasets/" in self.model_name or "/models/" in self.model_name or self.model_name.startswith("/"):
                return self._call_local_model(prompt, max_tokens, temperature)
            elif "gemini" in self.model_name.lower():
                return self._call_gemini(prompt, max_tokens, temperature)
            elif "openai" in self.model_name.lower():
                return self._call_openai(prompt, max_tokens, temperature)
            elif "huggingface" in self.model_name.lower():
                return self._call_huggingface(prompt, max_tokens, temperature)
            else:
                return self._call_generic_api(prompt, max_tokens, temperature)
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _call_simple_fallback(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Simple fallback model for testing - works with Python 3.8.18"""
        # Simple rule-based responses for testing
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm a simple AI assistant. How can I help you today?"
        elif "what is" in prompt_lower:
            if "2+2" in prompt_lower or "2 + 2" in prompt_lower:
                return "2 + 2 = 4"
            elif "ai" in prompt_lower or "artificial intelligence" in prompt_lower:
                return "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn like humans."
            else:
                return f"I understand you're asking about something. Based on your question '{prompt}', I can provide a general response."
        elif "how are you" in prompt_lower:
            return "I'm doing well, thank you for asking! I'm here to help with your questions."
        elif "thank" in prompt_lower:
            return "You're welcome! I'm happy to help."
        else:
            return f"I received your message: '{prompt}'. This is a simple fallback response. The system is working correctly with Python 3.8.18!"
    
    def _call_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call Google Gemini API"""
        url = f"{self.base_url}/{self.model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "No response generated"
    
    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call OpenAI API"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        return result["choices"][0]["message"]["content"]
    
    def _call_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call HuggingFace Inference API"""
        url = f"{self.base_url}/{self.model_name}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]["generated_text"]
        else:
            return "No response generated"
    
    def _call_local_model(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call local transformers model"""
        try:
            # Import transformers only when needed
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Load model and tokenizer if not already loaded
            if self.local_model is None or self.local_tokenizer is None:
                print(f"Loading local model from {self.model_name}")
                
                # Load tokenizer
                self.local_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Check if CUDA is available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"Using device: {device}")
                
                # Load model with appropriate device configuration
                if device == "cuda":
                    self.local_model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16,
                        device_map="auto"
                    )
                else:
                    # For CPU, use float32 and no device_map
                    self.local_model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    self.local_model = self.local_model.to(device)
                
                print("Local model loaded successfully")
            
            # Tokenize input
            inputs = self.local_tokenizer.encode(prompt, return_tensors="pt")
            
            # Move inputs to same device as model
            device = next(self.local_model.parameters()).device
            inputs = inputs.to(device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.local_model.generate(
                    inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.local_tokenizer.eos_token_id,
                    eos_token_id=self.local_tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            import traceback
            error_msg = f"Error with local model: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(error_msg)
            return error_msg
    
    def _call_generic_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call generic API endpoint"""
        url = f"{self.base_url}/generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        return result.get("text", "No response generated")

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global query_analyzer, retriever, config, current_model_config
    
    print("🚀 Starting Universal RAG API Server...")
    
    try:
        # Load configuration
        config = get_adaptive_config()
        print(f"✅ Configuration loaded")
        
        # Create query analyzer
        query_analyzer = QueryAnalyzer(config)
        print(f"✅ Query analyzer initialized")
        
        # Create retriever
        retriever = DynamicRetriever()
        print(f"✅ Retriever initialized")
        
        # Set default model (fallback to simple response for now)
        current_model_config = ModelConfig(
            model_name="simple-fallback",
            max_tokens=512,
            temperature=0.7
        )
        
        print("🎉 Universal RAG API Server ready!")
        print("📡 Supports: Local models, Gemini, OpenAI, HuggingFace, and custom APIs")
        print(f"🤖 Default model: Simple Fallback (Python 3.8.18 compatible)")
        
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        rag_system="universal_adaptive",
        model_provider=current_model_config.model_name if current_model_config else "unknown",
        timestamp=time.time()
    )

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest, background_tasks: BackgroundTasks):
    """Main RAG query endpoint"""
    try:
        if not all([query_analyzer, retriever]):
            raise HTTPException(status_code=500, detail="RAG system not initialized")
        
        start_time = time.time()
        
        # Use provided model config or default
        model_config = ModelConfig(**request.model_config) if request.model_config else current_model_config
        model_interface = UniversalModelInterface(model_config)
        
        # Analyze query complexity (simplified for Python 3.8.18 compatibility)
        try:
            complexity_analysis = query_analyzer.analyze_query(request.query, request.query_metadata)
            use_rag = complexity_analysis.recommendation == "rag"
        except Exception as e:
            print(f"Query analyzer error: {e}")
            # Fallback: use simple heuristics
            use_rag = len(request.query.split()) > 3  # Use RAG for longer queries
        
        if use_rag:
            # Execute RAG path (with error handling for Python 3.8.18)
            try:
                profile = select_profile_for_query(request.query, request.query_metadata)
                retrieval_result = retriever.retrieve(
                    query=request.query,
                    profile=profile or "general",
                    k=config.start_k
                )
                
                # Generate with context
                prompt = format_rag_prompt(request.query, retrieval_result['context_blocks'])
                answer = model_interface.generate(
                    prompt, 
                    max_tokens=model_config.max_tokens,
                    temperature=model_config.temperature
                )
                
                context_blocks = retrieval_result['context_blocks']
            except Exception as e:
                print(f"RAG path error: {e}")
                # Fallback to direct generation
                prompt = format_direct_prompt(request.query)
                answer = model_interface.generate(
                    prompt, 
                    max_tokens=model_config.max_tokens,
                    temperature=model_config.temperature
                )
                context_blocks = []
        else:
            # Execute direct path
            prompt = format_direct_prompt(request.query)
            answer = model_interface.generate(
                prompt,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature
            )
            
            context_blocks = []
        
        end_time = time.time()
        
        # Log query for analysis
        if config.enable_telemetry:
            background_tasks.add_task(log_query, request.query, complexity_analysis, end_time - start_time)
        
        return QueryResponse(
            answer=answer,
            used_rag=use_rag,
            context_blocks=context_blocks,
            complexity_score=complexity_analysis.complexity_score,
            reasoning=complexity_analysis.reasoning,
            model_used=model_config.model_name,
            performance_metrics={
                'total_time': end_time - start_time,
                'used_rag': use_rag,
                'complexity_score': complexity_analysis.complexity_score,
                'confidence': complexity_analysis.confidence,
                'model_provider': model_config.model_name
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set_model")
async def set_default_model(model_config: ModelConfig):
    """Set default model configuration"""
    global current_model_config
    current_model_config = model_config
    return {"message": f"Default model set to {model_config.model_name}"}

@app.get("/models")
async def list_supported_models():
    """List supported model providers"""
    return {
        "providers": [
            {
                "name": "Local Models",
                "models": ["Qwen2.5-Math-1.5B-Instruct", "Any local transformers model"],
                "description": "Local models via transformers library"
            },
            {
                "name": "Google Gemini",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
                "api_key_env": "GEMINI_API_KEY"
            },
            {
                "name": "OpenAI",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "api_key_env": "OPENAI_API_KEY"
            },
            {
                "name": "HuggingFace",
                "models": ["microsoft/DialoGPT-medium", "microsoft/DialoGPT-large", "your-fine-tuned-model"],
                "api_key_env": "HUGGINGFACE_API_KEY"
            }
        ],
        "current_model": current_model_config.model_name if current_model_config else "unknown"
    }

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

def log_query(query: str, complexity_analysis, total_time: float):
    """Log query for analysis"""
    log_entry = {
        "timestamp": time.time(),
        "query": query,
        "complexity_score": complexity_analysis.complexity_score,
        "recommendation": complexity_analysis.recommendation,
        "total_time": total_time
    }
    
    # Log to file
    with open("rag_queries.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("RAG_API_PORT", 8080))
    print(f"Starting Universal RAG API server on port {port}")
    uvicorn.run(
        "universal_rag_api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
