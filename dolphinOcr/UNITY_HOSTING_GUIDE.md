# Unity Server RAG API Hosting Guide

Host your Universal RAG API on Unity server using SLURM for persistent, production-ready service.

## 🚀 **Quick Start**

### 1. Start RAG API Hosting
```bash
# Start the hosting service
./run_system.sh host

# Or use the management script directly
./manage_rag_hosting.sh start
```

### 2. Check Status
```bash
# Check if it's running
./manage_rag_hosting.sh status

# Test the API
./manage_rag_hosting.sh test

# Get API URLs for your Next.js app
./manage_rag_hosting.sh url
```

### 3. Send Test Queries
```bash
# Test with a simple query
./manage_rag_hosting.sh query "What is artificial intelligence?"

# Test with a complex query
./manage_rag_hosting.sh query "Explain the Central Limit Theorem and its applications"
```

## 🔧 **Hosting Management**

### Available Commands
```bash
./manage_rag_hosting.sh start     # Start hosting service
./manage_rag_hosting.sh stop      # Stop hosting service
./manage_rag_hosting.sh restart   # Restart hosting service
./manage_rag_hosting.sh status    # Check status and get URLs
./manage_rag_hosting.sh logs      # View server logs
./manage_rag_hosting.sh test      # Test API connection
./manage_rag_hosting.sh query     # Send test queries
./manage_rag_hosting.sh url       # Get API URLs for integration
```

### Status Monitoring
```bash
# Check job status
squeue -u $USER

# View detailed logs
./manage_rag_hosting.sh logs

# Test API health
./manage_rag_hosting.sh test
```

## 🌐 **API Endpoints**

Once running, your RAG API will be available at:
- **Base URL**: `http://[node-name]:8080`
- **Health Check**: `http://[node-name]:8080/health`
- **API Documentation**: `http://[node-name]:8080/docs`
- **Query Endpoint**: `http://[node-name]:8080/query`
- **Models Endpoint**: `http://[node-name]:8080/models`

## 🔗 **Next.js Integration**

### 1. Get Your API URL
```bash
./manage_rag_hosting.sh url
```

### 2. Update Environment Variables
```bash
# .env.local
NEXT_PUBLIC_RAG_API_URL=http://[node-name]:8080
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_key
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_key
NEXT_PUBLIC_HUGGINGFACE_API_KEY=your_hf_key
```

### 3. Use in Your Next.js App
```javascript
// lib/rag-client.js
import RAGClient from './nextjs-rag-client';

const ragClient = new RAGClient(process.env.NEXT_PUBLIC_RAG_API_URL);

// Query with Gemini
const response = await ragClient.queryWithGemini("What is AI?");

// Query with your fine-tuned model
const response = await ragClient.queryWithHuggingFace(
  "What is machine learning?", 
  "your-username/your-fine-tuned-model"
);
```

## 🔄 **Model Switching**

### Switch Default Model
```bash
# Via API call
curl -X POST http://[node-name]:8080/set_model \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "your-fine-tuned-model",
    "api_key": "your-hf-key",
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

### Per-Query Model Selection
```javascript
// In your Next.js app
const response = await ragClient.query("What is AI?", {
  modelConfig: {
    model_name: "your-fine-tuned-model",
    api_key: process.env.NEXT_PUBLIC_HUGGINGFACE_API_KEY,
    max_tokens: 512,
    temperature: 0.7
  }
});
```

## 📊 **Monitoring & Logs**

### View Logs
```bash
# Server logs
./manage_rag_hosting.sh logs

# SLURM job logs
tail -f slurm_output/rag_api_host_*.out

# Real-time monitoring
watch -n 5 './manage_rag_hosting.sh status'
```

### Health Monitoring
```bash
# Test API health
./manage_rag_hosting.sh test

# Check if API is responding
curl -s http://[node-name]:8080/health | python -m json.tool
```

## 🔒 **Security & Configuration**

### API Keys
```bash
# Set your API keys
export GEMINI_API_KEY="your_gemini_key"
export OPENAI_API_KEY="your_openai_key"
export HUGGINGFACE_API_KEY="your_hf_key"

# Then start hosting
./manage_rag_hosting.sh start
```

### Network Access
- The API binds to `0.0.0.0:8080` for external access
- Make sure your Unity server allows connections on port 8080
- Consider firewall rules for production use

## 🚀 **Production Deployment**

### 1. Persistent Hosting
```bash
# Start hosting with 24-hour runtime
./manage_rag_hosting.sh start

# The service will automatically restart if it fails
# Monitor with: ./manage_rag_hosting.sh status
```

### 2. Load Balancing (Optional)
If you need multiple instances:
```bash
# Start multiple hosting jobs
./manage_rag_hosting.sh start
# Wait for first to start, then start another
sbatch run_universal_rag_hosting.slurm
```

### 3. Monitoring Setup
```bash
# Create a monitoring script
cat > monitor_rag.sh << 'EOF'
#!/bin/bash
while true; do
    if ! ./manage_rag_hosting.sh test > /dev/null 2>&1; then
        echo "RAG API down, restarting..."
        ./manage_rag_hosting.sh restart
    fi
    sleep 60
done
EOF

chmod +x monitor_rag.sh
nohup ./monitor_rag.sh &
```

## 🧪 **Testing**

### Automated Testing
```bash
# Run comprehensive tests
python test_hosting.py

# Test specific URL
python test_hosting.py http://[node-name]:8080
```

### Manual Testing
```bash
# Test health
curl http://[node-name]:8080/health

# Test query
curl -X POST http://[node-name]:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

## 🔧 **Troubleshooting**

### Common Issues

#### 1. API Not Responding
```bash
# Check if job is running
squeue -u $USER

# Check logs
./manage_rag_hosting.sh logs

# Restart if needed
./manage_rag_hosting.sh restart
```

#### 2. Port Already in Use
```bash
# Check what's using port 8080
netstat -tulpn | grep 8080

# Kill the process or use a different port
```

#### 3. Model API Errors
```bash
# Check API keys
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
echo $HUGGINGFACE_API_KEY

# Test model endpoints individually
```

### Debug Mode
```bash
# Start with debug logging
export RAG_DEBUG=true
./manage_rag_hosting.sh start
```

## 📈 **Performance Optimization**

### Resource Allocation
- **CPU**: 8 cores (adjustable in SLURM file)
- **Memory**: 32GB (adjustable in SLURM file)
- **GPU**: A100 (for model loading, not required for API calls)
- **Runtime**: 24 hours (extendable)

### Scaling
- **Horizontal**: Start multiple hosting jobs
- **Vertical**: Increase CPU/memory in SLURM file
- **Caching**: Enable query caching in configuration

## 🎯 **Integration Checklist**

- [ ] Start RAG API hosting: `./run_system.sh host`
- [ ] Verify API is running: `./manage_rag_hosting.sh test`
- [ ] Get API URL: `./manage_rag_hosting.sh url`
- [ ] Update Next.js environment variables
- [ ] Copy client libraries to your Next.js project
- [ ] Test integration with your app
- [ ] Set up monitoring and alerts
- [ ] Configure your fine-tuned model when ready

## 🚀 **Next Steps**

1. **Start hosting**: `./run_system.sh host`
2. **Get API URL**: `./manage_rag_hosting.sh url`
3. **Integrate with Next.js**: Use provided client libraries
4. **Test thoroughly**: Use provided test scripts
5. **Monitor in production**: Set up monitoring and alerts

Your RAG API is now **hosted on Unity server** and ready for production use! 🎉
