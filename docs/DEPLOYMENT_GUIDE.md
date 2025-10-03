# Universal RAG API Deployment Guide

Deploy your RAG system anywhere and integrate with any transformer model!

## 🚀 **Quick Deployment Options**

### Option 1: SLURM Cluster (Current Setup)
```bash
# Deploy on your current cluster
sbatch run_universal_rag.slurm

# Check status
squeue -u $USER

# View logs
tail -f slurm_output/universal_rag_*.out
```

### Option 2: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.8.18-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY RAG_system/ ./RAG_system/
COPY run_universal_rag.slurm .

EXPOSE 8080
CMD ["python", "RAG_system/universal_rag_api.py"]
```

### Option 3: Cloud Deployment (AWS/GCP/Azure)
```bash
# Deploy to cloud with your preferred method
# The API is stateless and can run anywhere
```

## 🔧 **Integration with Your Next.js App**

### 1. Install the Client Library
```bash
# Copy the client library to your Next.js project
cp client-libraries/nextjs-rag-client.js ./lib/
cp client-libraries/RAGChatComponent.jsx ./components/
```

### 2. Environment Variables
```bash
# .env.local
NEXT_PUBLIC_RAG_API_URL=http://your-rag-server:8080
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_key
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_key
NEXT_PUBLIC_HUGGINGFACE_API_KEY=your_hf_key
```

### 3. Use in Your Components
```jsx
// pages/chat.js
import RAGChatComponent from '../components/RAGChatComponent';

export default function ChatPage() {
  return (
    <div>
      <h1>AI Chat with RAG</h1>
      <RAGChatComponent 
        ragApiUrl={process.env.NEXT_PUBLIC_RAG_API_URL}
        defaultModel="gemini-1.5-flash"
      />
    </div>
  );
}
```

### 4. API Integration
```javascript
// lib/rag-client.js
import RAGClient from './nextjs-rag-client';

const ragClient = new RAGClient(
  process.env.NEXT_PUBLIC_RAG_API_URL,
  process.env.NEXT_PUBLIC_API_KEY
);

// Use in your API routes
export async function POST(request) {
  const { question } = await request.json();
  
  const response = await ragClient.queryWithGemini(question, {
    queryMetadata: { source: 'api' }
  });
  
  return Response.json(response);
}
```

## 🔄 **Model Switching**

### Switch to Your Fine-tuned Model
```javascript
// Switch to your HuggingFace model
await ragClient.setDefaultModel({
  model_name: "your-username/your-fine-tuned-model",
  api_key: process.env.NEXT_PUBLIC_HUGGINGFACE_API_KEY,
  max_tokens: 512,
  temperature: 0.7
});

// Or use per-query
const response = await ragClient.queryWithHuggingFace(
  "What is machine learning?",
  "your-username/your-fine-tuned-model"
);
```

### Dynamic Model Selection
```javascript
// Select model based on query type
const getModelForQuery = (query) => {
  if (query.includes('math') || query.includes('theorem')) {
    return 'your-math-model';
  } else if (query.includes('code') || query.includes('programming')) {
    return 'your-code-model';
  } else {
    return 'gemini-1.5-flash';
  }
};

const response = await ragClient.query(question, {
  modelConfig: {
    model_name: getModelForQuery(question),
    // ... other config
  }
});
```

## 🌐 **Production Deployment**

### 1. Server Configuration
```bash
# Set production environment variables
export RAG_API_URL=https://your-domain.com
export GEMINI_API_KEY=your_production_key
export OPENAI_API_KEY=your_production_key
export HUGGINGFACE_API_KEY=your_production_key
```

### 2. Load Balancing
```nginx
# nginx.conf
upstream rag_api {
    server rag-server-1:8080;
    server rag-server-2:8080;
    server rag-server-3:8080;
}

server {
    listen 80;
    location /api/rag/ {
        proxy_pass http://rag_api/;
    }
}
```

### 3. Monitoring
```javascript
// Add monitoring to your Next.js app
const monitorRAGUsage = async (query, response) => {
  // Send to your analytics service
  await fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify({
      query,
      model_used: response.model_used,
      used_rag: response.used_rag,
      complexity_score: response.complexity_score,
      response_time: response.performance_metrics.total_time
    })
  });
};
```

## 🔒 **Security & Authentication**

### API Key Management
```javascript
// Secure API key handling
const getApiKey = (modelName) => {
  // Use server-side environment variables
  return process.env[`${modelName.toUpperCase()}_API_KEY`];
};
```

### Rate Limiting
```javascript
// Add rate limiting to your Next.js API routes
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
```

## 📊 **Performance Optimization**

### 1. Caching
```javascript
// Add caching to your Next.js app
import { cache } from 'react';

const getCachedResponse = cache(async (query) => {
  return await ragClient.query(query);
});
```

### 2. Streaming Responses
```javascript
// For long responses, implement streaming
const streamResponse = async (query) => {
  const response = await fetch('/api/rag/stream', {
    method: 'POST',
    body: JSON.stringify({ query })
  });
  
  const reader = response.body.getReader();
  // Handle streaming...
};
```

## 🧪 **Testing**

### Unit Tests
```javascript
// __tests__/rag-client.test.js
import RAGClient from '../lib/nextjs-rag-client';

describe('RAGClient', () => {
  test('should query successfully', async () => {
    const client = new RAGClient('http://localhost:8080');
    const response = await client.query('What is AI?');
    
    expect(response.answer).toBeDefined();
    expect(response.used_rag).toBeDefined();
  });
});
```

### Integration Tests
```javascript
// Test with your actual RAG server
const testRAGIntegration = async () => {
  const client = new RAGClient(process.env.RAG_API_URL);
  
  const testQueries = [
    'What is machine learning?',
    'Explain quantum computing',
    'How does neural networks work?'
  ];
  
  for (const query of testQueries) {
    const response = await client.query(query);
    console.log(`Query: ${query}`);
    console.log(`Used RAG: ${response.used_rag}`);
    console.log(`Complexity: ${response.complexity_score}`);
  }
};
```

## 🎯 **Key Benefits**

1. **Universal Compatibility** - Works with any transformer model
2. **Easy Integration** - Drop-in components for Next.js
3. **Flexible Deployment** - Deploy anywhere (SLURM, Docker, Cloud)
4. **Model Agnostic** - Switch between models easily
5. **Production Ready** - Built-in monitoring and error handling
6. **Scalable** - Horizontal scaling support

## 🚀 **Next Steps**

1. **Deploy the Universal RAG API** using SLURM or Docker
2. **Integrate with your Next.js app** using the provided components
3. **Configure your fine-tuned model** when ready
4. **Add monitoring and analytics** for production use
5. **Scale horizontally** as your usage grows

Your RAG system is now **universally deployable** and **model-agnostic**! 🎉
