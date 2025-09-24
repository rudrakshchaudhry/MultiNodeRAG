# External RAG API Integration Guide

## 🌐 **API Access Information**

### **Current API Endpoints**
- **Base URL**: `http://gpu013:8082` (Internal Unity access)
- **Public URL**: `http://gpu013:8083` (External access - when deployed)

### **Available Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check and status |
| `/query` | POST | Main query processing |
| `/models` | GET | Available models and capabilities |
| `/docs` | GET | Interactive API documentation |

## 🚀 **Quick Start Integration**

### **1. Test API Connectivity**
```bash
# Test health check
curl http://gpu013:8082/health

# Test query endpoint
curl -X POST http://gpu013:8082/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is probability?"}'
```

### **2. JavaScript Integration**
```javascript
// Basic RAG API client
class RAGClient {
    constructor(baseUrl = 'http://gpu013:8082') {
        this.baseUrl = baseUrl;
    }
    
    async query(question, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: question,
                    ...options
                })
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('RAG API Error:', error);
            throw error;
        }
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// Usage
const ragClient = new RAGClient('http://gpu013:8082');

// Query the API
ragClient.query("What is the Central Limit Theorem?")
    .then(response => {
        console.log('Answer:', response.answer);
        console.log('Used RAG:', response.used_rag);
        console.log('Complexity Score:', response.router_decision.complexity_score);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

### **3. Python Integration**
```python
import requests
import json

class RAGClient:
    def __init__(self, base_url='http://gpu013:8082'):
        self.base_url = base_url
    
    def query(self, question, **kwargs):
        """Send a query to the RAG API"""
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={
                    "query": question,
                    **kwargs
                },
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"RAG API Error: {e}")
            return None
    
    def health_check(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None

# Usage
rag_client = RAGClient('http://gpu013:8082')

# Query the API
result = rag_client.query("What is probability?")
if result:
    print(f"Answer: {result['answer']}")
    print(f"Used RAG: {result['used_rag']}")
    print(f"Complexity Score: {result['router_decision']['complexity_score']}")
```

## 🔧 **Integration with Your AI-Tutor Application**

### **1. Update Your `api/gemini.js`**
```javascript
// Add RAG integration to your existing Gemini API
const RAG_API_URL = process.env.RAG_API_URL || 'http://gpu013:8082';

async function getRAGContext(query) {
    try {
        const response = await fetch(`${RAG_API_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                query_metadata: {
                    source: 'ai-tutor',
                    subject: 'probability-statistics'
                }
            })
        });
        
        if (!response.ok) throw new Error('RAG API error');
        
        const ragData = await response.json();
        return {
            context: ragData.context_blocks || [],
            usedRAG: ragData.used_rag,
            complexityScore: ragData.router_decision?.complexity_score || 0
        };
    } catch (error) {
        console.warn('RAG context unavailable:', error.message);
        return { context: [], usedRAG: false, complexityScore: 0 };
    }
}

// Modify your existing generateResponse function
async function generateResponse(messages, options = {}) {
    const lastMessage = messages[messages.length - 1];
    const userQuery = lastMessage.content;
    
    // Get RAG context
    const ragContext = await getRAGContext(userQuery);
    
    // Enhance system prompt with RAG context
    let enhancedSystemPrompt = systemPrompt;
    
    if (ragContext.usedRAG && ragContext.context.length > 0) {
        const contextText = ragContext.context
            .map(block => `[${block.label || 'Context'}]: ${block.text}`)
            .join('\n\n');
            
        enhancedSystemPrompt += `\n\nRELEVANT CONTEXT FROM KNOWLEDGE BASE:\n${contextText}\n\nUse this context to provide more accurate and detailed responses.`;
    }
    
    // Rest of your existing Gemini API call...
    // Add ragContext to your response
}
```

### **2. Update Your Frontend (`tutor-chat.js`)**
```javascript
// Add RAG status display
function displayRAGStatus(ragMetadata) {
    if (ragMetadata.usedRAG) {
        const statusElement = document.createElement('div');
        statusElement.className = 'rag-status';
        statusElement.innerHTML = `
            <span class="rag-indicator">📚</span>
            <span>Enhanced with knowledge base (Complexity: ${(ragMetadata.complexityScore * 100).toFixed(0)}%)</span>
        `;
        return statusElement;
    }
    return null;
}

// Modify your message processing
async function processMessage(messageText, messageType = 'text') {
    try {
        showLoadingIndicator();
        
        const response = await fetch('/api/gemini', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: messageText,
                type: messageType,
                sessionId: getCurrentSessionId()
            })
        });
        
        const data = await response.json();
        displayMessage(data.response, 'ai');
        
        // Display RAG status
        if (data.ragMetadata) {
            const ragStatus = displayRAGStatus(data.ragMetadata);
            if (ragStatus) {
                const chatContainer = document.getElementById('chat-container');
                chatContainer.appendChild(ragStatus);
            }
        }
        
    } catch (error) {
        console.error('Error processing message:', error);
        displayMessage('Sorry, I encountered an error. Please try again.', 'ai');
    } finally {
        hideLoadingIndicator();
    }
}
```

## 🌍 **External Access Solutions**

### **Option 1: SSH Tunnel (Quick Setup)**
```bash
# Create SSH tunnel from your local machine
ssh -L 8082:gpu013:8082 rchaudhry_umass_edu@login.unity.rc.umass.edu

# Now your local machine can access:
# http://localhost:8082
```

### **Option 2: Reverse Proxy (Recommended)**
Set up a reverse proxy on a public server:

```nginx
# nginx configuration
server {
    listen 80;
    server_name your-rag-api.com;
    
    location / {
        proxy_pass http://gpu013:8082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### **Option 3: Cloud Deployment**
Deploy to a cloud service with public access:

```bash
# Deploy to AWS/GCP/Azure
# Or use Docker on a VPS
```

## 📊 **API Response Format**

### **Query Response Structure**
```json
{
    "answer": "Response text with enhanced context",
    "used_rag": true,
    "context_blocks": [
        {
            "text": "Context from knowledge base",
            "relevance": 0.8,
            "label": "Context 1",
            "source": "document.pdf",
            "page": 1
        }
    ],
    "router_decision": {
        "use_rag": true,
        "reason": "Query has high complexity",
        "confidence": 0.7,
        "complexity_score": 0.8,
        "routing_method": "complexity_analysis"
    },
    "performance_metrics": {
        "total_time": 0.5,
        "model_generation_tokens": 0,
        "model_generation_time": 0.5
    },
    "model_used": "public-rag-api",
    "api_version": "1.0.0"
}
```

## 🔒 **Security Considerations**

### **1. CORS Configuration**
```javascript
// Configure CORS for your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  // Your actual domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### **2. API Key Authentication (Optional)**
```javascript
// Add API key validation
const API_KEY = process.env.RAG_API_KEY;

app.use((req, res, next) => {
    const apiKey = req.headers['x-api-key'];
    if (apiKey !== API_KEY) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
});
```

### **3. Rate Limiting (Optional)**
```javascript
// Add rate limiting
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/query', limiter);
```

## 🧪 **Testing Your Integration**

### **1. Test API Connectivity**
```bash
# Test health check
curl http://gpu013:8082/health

# Test query
curl -X POST http://gpu013:8082/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Central Limit Theorem?"}'
```

### **2. Test from Your Application**
```javascript
// Test from your AI-Tutor app
const ragClient = new RAGClient('http://gpu013:8082');

ragClient.query("What is probability?")
    .then(response => {
        console.log('✅ RAG API working:', response);
    })
    .catch(error => {
        console.error('❌ RAG API error:', error);
    });
```

## 🚀 **Deployment Steps**

### **1. Start RAG API on Unity**
```bash
# Start the public RAG API
cd /home/rchaudhry_umass_edu/rag/dolphinOcr
sbatch run_public_rag_hosting.slurm
```

### **2. Update Your Application**
1. Add RAG integration to your `api/gemini.js`
2. Update frontend to display RAG status
3. Set environment variables
4. Deploy to Vercel

### **3. Test Integration**
1. Test API connectivity
2. Test query processing
3. Verify RAG status display
4. Test with complex queries

## 🎯 **Expected Results**

After integration:
- ✅ **Enhanced Responses**: More accurate, context-aware answers
- ✅ **Visual Indicators**: Shows when responses are enhanced with RAG
- ✅ **Complexity Analysis**: Routes queries intelligently
- ✅ **External Access**: Works from any external application
- ✅ **Minimal Changes**: Integrates with existing codebase

Your RAG API is now **ready for external integration**! 🎉
