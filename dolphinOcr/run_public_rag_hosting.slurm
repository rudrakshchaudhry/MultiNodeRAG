#!/bin/bash
#SBATCH --job-name=public_rag_api
#SBATCH --output=slurm_output/public_rag_api_%j.out
#SBATCH --error=slurm_output/public_rag_api_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16GB
#SBATCH --time=24:00:00
#SBATCH --signal=SIGTERM@120

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/dolphinOcr

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output
mkdir -p logs

# Set environment variables
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Get the node name for hosting
NODE_NAME=$(hostname)
PORT=8083

# Print configuration
echo "🚀 Starting Public RAG API Hosting Service"
echo "=========================================="
echo "Node: $NODE_NAME"
echo "Port: $PORT"
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "🌐 This API is designed for external access"
echo "🔗 API will be available at: http://$NODE_NAME:$PORT"
echo "📚 CORS enabled for cross-origin requests"
echo ""

# Create a PID file for process management
PID_FILE="logs/public_rag_api.pid"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down Public RAG API server..."
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
    echo "✅ Public RAG API server stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start the public RAG API server in background
cd RAG_system
export RAG_API_PORT=$PORT
export RAG_API_HOST=0.0.0.0
nohup python public_rag_api.py > ../logs/public_rag_api.log 2>&1 &
API_PID=$!

# Save PID
echo $API_PID > ../$PID_FILE

echo "✅ Public RAG API server started with PID: $API_PID"
echo "📋 Logs: logs/public_rag_api.log"
echo "🔗 API URL: http://$NODE_NAME:$PORT"
echo ""

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 10

# Test if server is running
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ Public RAG API server is running and healthy!"
    echo "🌐 API available at: http://$NODE_NAME:$PORT"
    echo "📊 Health check: http://$NODE_NAME:$PORT/health"
    echo "📋 API docs: http://$NODE_NAME:$PORT/docs"
    echo "🔗 Root endpoint: http://$NODE_NAME:$PORT/"
    echo ""
    echo "🌍 EXTERNAL ACCESS INFORMATION:"
    echo "==============================="
    echo "• API Base URL: http://$NODE_NAME:$PORT"
    echo "• Health Check: http://$NODE_NAME:$PORT/health"
    echo "• Query Endpoint: http://$NODE_NAME:$PORT/query"
    echo "• API Documentation: http://$NODE_NAME:$PORT/docs"
    echo "• Models Endpoint: http://$NODE_NAME:$PORT/models"
    echo ""
    echo "🔧 INTEGRATION EXAMPLES:"
    echo "========================"
    echo "• JavaScript: fetch('http://$NODE_NAME:$PORT/query', {...})"
    echo "• Python: requests.post('http://$NODE_NAME:$PORT/query', ...)"
    echo "• curl: curl -X POST http://$NODE_NAME:$PORT/query -d '{...}'"
else
    echo "❌ Public RAG API server failed to start"
    exit 1
fi

# Keep the job running and monitor the API
echo "🔄 Monitoring Public RAG API server..."
while kill -0 $API_PID 2>/dev/null; do
    sleep 30
    
    # Check if API is still responding
    if ! curl -s http://localhost:$PORT/health > /dev/null; then
        echo "❌ Public RAG API server is not responding, restarting..."
        kill -TERM $API_PID
        sleep 5
        nohup python public_rag_api.py > ../logs/public_rag_api.log 2>&1 &
        API_PID=$!
        echo $API_PID > ../$PID_FILE
        echo "✅ Public RAG API server restarted with PID: $API_PID"
    fi
done

echo "🛑 Public RAG API server process ended"
cleanup
