# MultiNodeRAG Production Configuration

## Environment Configuration

### Required Environment Variables
```bash
# RAG System Configuration
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# API Configuration
export RAG_API_HOST=0.0.0.0
export RAG_API_PORT=8081

# Model Configuration (Optional)
export GEMINI_API_KEY=""
export OPENAI_API_KEY=""
export HUGGINGFACE_API_KEY=""
```

### Python Dependencies
```bash
# Core dependencies
fastapi>=0.118.0
uvicorn>=0.30.0
transformers>=4.46.3
torch>=2.1.0
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
requests>=2.31.0
pydantic>=2.0.0

# Optional dependencies
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
```

## SLURM Configuration

### Job Parameters
```bash
#SBATCH --job-name=rag_api_hosting
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32GB
#SBATCH --time=23:30:00
#SBATCH --requeue
#SBATCH --signal=SIGUSR1@90
```

### Resource Requirements
- **GPU**: A100 (recommended) or equivalent
- **CPU**: 8 cores minimum
- **Memory**: 32GB minimum
- **Storage**: 100GB for models and indices

## Security Configuration

### Production Security Checklist
- [ ] Enable API key authentication
- [ ] Implement rate limiting
- [ ] Use HTTPS certificates
- [ ] Monitor usage patterns
- [ ] Set up logging and alerting
- [ ] Configure firewall rules
- [ ] Enable audit logging

### API Authentication (Optional)
```python
# Add to universal_rag_api.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials
```

## Monitoring Configuration

### Health Check Endpoints
- `/health` - Basic health check
- `/metrics` - Performance metrics
- `/status` - Detailed system status

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rag_api.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Optimization

### Model Loading Optimization
```python
# Lazy loading for efficiency
def load_model_on_demand():
    if not hasattr(load_model_on_demand, 'model'):
        load_model_on_demand.model = load_model()
    return load_model_on_demand.model
```

### Caching Configuration
```python
# Query result caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query_analysis(query: str):
    return analyze_query(query)
```

## Deployment Checklist

### Pre-deployment
- [ ] Test all endpoints
- [ ] Verify model loading
- [ ] Check resource requirements
- [ ] Validate SLURM configuration
- [ ] Test external access
- [ ] Review security settings

### Post-deployment
- [ ] Monitor system performance
- [ ] Check error rates
- [ ] Verify external access
- [ ] Test auto-restart functionality
- [ ] Monitor resource usage
- [ ] Review logs

## Troubleshooting

### Common Issues
1. **Model Loading Errors**: Check Python 3.8.18 compatibility
2. **Memory Issues**: Increase SLURM memory allocation
3. **Tunnel Connection**: Restart external access manager
4. **Job Timeouts**: Use persistent hosting mode

### Debug Commands
```bash
# Check service status
./manage_rag_hosting.sh status

# Check external access
./manage_external_access.sh status

# View logs
tail -f logs/rag_api.log

# Test API
./manage_rag_hosting.sh test
```
