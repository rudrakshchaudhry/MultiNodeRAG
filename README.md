# MultiNodeRAG - Universal RAG API System

A production-ready Retrieval-Augmented Generation (RAG) API system designed for Unity cluster deployment with persistent hosting and external access.

## 🚀 Quick Start

### Start the RAG API Service
```bash
./scripts/manage_rag_hosting.sh start
```

### Enable External Access
```bash
./scripts/manage_external_access.sh start
```

### Check Status
```bash
./scripts/manage_rag_hosting.sh status
```

## 📁 Project Structure

```
MultiNodeRAG/
├── scripts/                    # Management scripts
│   ├── manage_rag_hosting.sh   # RAG API management
│   ├── manage_external_access.sh # External access management
│   └── run_universal_rag_hosting.slurm # SLURM job script
├── rag_system/                 # Core RAG system
│   ├── universal_rag_api.py    # Main FastAPI application
│   └── adaptive_rag/           # Adaptive RAG components
├── rag_indexing/               # RAG indexing pipeline
├── ocr/                        # OCR processing
├── data/                       # Data storage
│   ├── index_data/             # FAISS indices
│   └── output/                 # Processed documents
├── docs/                       # Documentation
├── logs/                       # Application logs
└── venv/                       # Python virtual environment
```

## 🔧 Configuration

- **Python**: 3.12.3
- **Framework**: FastAPI + Uvicorn
- **Vector Store**: FAISS
- **Embeddings**: BAAI/bge-small-en-v1.5
- **Hosting**: Unity Cluster (SLURM)
- **External Access**: Cloudflare Tunnel

## 📚 Documentation

- [Configuration Guide](docs/CONFIG.md)
- [API Documentation](docs/README.md)

## 🌐 External Access

The system provides persistent external access through Cloudflare Tunnel. The URL updates automatically when jobs restart.

### API Endpoints

- `GET /health` - Health check
- `POST /query` - Query the RAG system
- `GET /models` - List available models
- `POST /models/set` - Set default model

### Example Usage

```bash
# Health check
curl https://your-tunnel-url.trycloudflare.com/health

# Query the system
curl -X POST https://your-tunnel-url.trycloudflare.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

## 🔄 Persistent Hosting

The system is designed for 24/7 operation with:
- Auto-restart on job preemption
- Graceful shutdown handling
- Automatic URL updates
- Health monitoring

## 🛠️ Development

### Virtual Environment
```bash
source venv/bin/activate
```

### Dependencies
All dependencies are installed in the virtual environment:
- FastAPI, Uvicorn
- Transformers, Torch
- FAISS, Sentence-Transformers
- NumPy, Pandas, Scikit-learn

## 📄 License

See [LICENSE](LICENSE) file for details.
