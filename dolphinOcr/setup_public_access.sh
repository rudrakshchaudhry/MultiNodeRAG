#!/bin/bash
# ngrok Setup Script for MultiNodeRAG Public Access

echo "🌐 Setting up ngrok for public RAG API access"
echo "============================================="

# Check if ngrok is already installed
if [ -f "./ngrok" ]; then
    echo "✅ ngrok already installed"
else
    echo "📥 Downloading ngrok..."
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    rm ngrok-v3-stable-linux-amd64.tgz
    echo "✅ ngrok downloaded and installed"
fi

# Check if RAG API is running
echo "🔍 Checking RAG API status..."
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ RAG API is running on port 8081"
else
    echo "❌ RAG API is not running. Please start it first:"
    echo "   ./manage_rag_hosting.sh start"
    exit 1
fi

# Start ngrok tunnel
echo "🚀 Starting ngrok tunnel..."
echo "Public URL will be available shortly..."
echo "Press Ctrl+C to stop the tunnel"
echo ""

./ngrok http 8081 --log=stdout
