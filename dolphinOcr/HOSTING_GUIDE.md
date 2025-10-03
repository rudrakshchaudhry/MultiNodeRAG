# MultiNodeRAG Hosting Guide

## Quick Start

### 1. Start Persistent RAG API Hosting
```bash
cd /home/rchaudhry_umass_edu/rag/dolphinOcr
./manage_rag_hosting.sh persistent
```

### 2. Set Up Public Access (Optional)
```bash
# In another terminal
./setup_public_access.sh
```

### 3. Monitor Status
```bash
./manage_rag_hosting.sh status
./manage_rag_hosting.sh test
```

## Commands

- `./manage_rag_hosting.sh start` - Start single RAG API job
- `./manage_rag_hosting.sh persistent` - Start 24/7 persistent hosting
- `./manage_rag_hosting.sh stop` - Stop all RAG API jobs
- `./manage_rag_hosting.sh status` - Check hosting status
- `./manage_rag_hosting.sh test` - Test API connection
- `./manage_rag_hosting.sh query "your question"` - Send test query
- `./manage_rag_hosting.sh url` - Get API URLs for integration

## Features

- ✅ **24/7 Hosting** - Auto-restart every 23.5 hours
- ✅ **GPU Acceleration** - A100 GPU support
- ✅ **Public Access** - ngrok tunnel for external access
- ✅ **Health Monitoring** - Automatic health checks
- ✅ **Easy Management** - Simple command-line interface

## API Endpoints

- **Health Check**: `/health`
- **Query**: `/query`
- **Documentation**: `/docs`
- **Models**: `/models`

## Integration

Use the URLs from `./manage_rag_hosting.sh url` in your applications:

```javascript
// Next.js
const RAG_API_URL = "http://node-name:8081";

// Query example
const response = await fetch(`${RAG_API_URL}/query`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "Your question here" })
});
```
