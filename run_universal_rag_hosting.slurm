#!/bin/bash
#SBATCH --job-name=rag_api_host
#SBATCH --output=slurm_output/rag_api_host_%j.out
#SBATCH --error=slurm_output/rag_api_host_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32GB
#SBATCH --time=23:30:00
#SBATCH --signal=SIGTERM@120
#SBATCH --requeue

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output
mkdir -p logs

# Set environment variables for universal RAG
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Set API keys (you can override these)
export GEMINI_API_KEY=${GEMINI_API_KEY:-""}
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY:-""}

# Get the node name for hosting
NODE_NAME=$(hostname)
PORT=8081

# Print configuration
echo "🚀 Starting Universal RAG API Hosting Service"
echo "============================================="
echo "Node: $NODE_NAME"
echo "Port: $PORT"
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "Supports: Gemini, OpenAI, HuggingFace, Custom APIs"
echo "API will be available at: http://$NODE_NAME:$PORT"
echo ""

# Create a PID file for process management
PID_FILE="logs/rag_api.pid"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down RAG API server..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill -TERM "$PID"
            sleep 5
            if kill -0 "$PID" 2>/dev/null; then
                kill -KILL "$PID"
            fi
        fi
        rm -f "$PID_FILE"
    fi
    echo "✅ RAG API server stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start the universal RAG API server in background
cd rag_system
# Set the port as an environment variable since the script doesn't accept CLI args
export RAG_API_PORT=$PORT
nohup python universal_rag_api.py > ../logs/rag_api.log 2>&1 &
API_PID=$!

# Save PID
echo $API_PID > ../logs/rag_api.pid

echo "✅ RAG API server started with PID: $API_PID"
echo "📋 Logs: logs/rag_api.log"
echo "🔗 API URL: http://$NODE_NAME:$PORT"
echo ""

# Wait for server to start (model loading can take 2-3 minutes)
echo "⏳ Waiting for server to start (this may take 2-3 minutes for model loading)..."
sleep 30

# Test if server is running
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ RAG API server is running and healthy!"
    echo "🌐 API available at: http://$NODE_NAME:$PORT"
    echo "📊 Health check: http://$NODE_NAME:$PORT/health"
    echo "📋 API docs: http://$NODE_NAME:$PORT/docs"
else
    echo "❌ RAG API server failed to start"
    exit 1
fi

# Keep the job running and monitor the API
echo "🔄 Monitoring RAG API server..."
while kill -0 $API_PID 2>/dev/null; do
    sleep 30
    
    # Check if API is still responding
    if ! curl -s http://localhost:$PORT/health > /dev/null; then
        echo "❌ RAG API server is not responding, restarting..."
        kill -TERM $API_PID
        sleep 5
        nohup python universal_rag_api.py > ../logs/rag_api.log 2>&1 &
        API_PID=$!
        echo $API_PID > ../logs/rag_api.pid
        echo "✅ RAG API server restarted with PID: $API_PID"
    fi
done

echo "🛑 RAG API server process ended"
cleanup
