#!/bin/bash
#SBATCH --job-name=simple_rag_api
#SBATCH --output=slurm_output/simple_rag_api_%j.out
#SBATCH --error=slurm_output/simple_rag_api_%j.err
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
PORT=8082

# Print configuration
echo "🚀 Starting Simple RAG API Hosting Service"
echo "=========================================="
echo "Node: $NODE_NAME"
echo "Port: $PORT"
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "This is a minimal version for testing and development"
echo "API will be available at: http://$NODE_NAME:$PORT"
echo ""

# Create a PID file for process management
PID_FILE="logs/simple_rag_api.pid"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down Simple RAG API server..."
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
    echo "✅ Simple RAG API server stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start the simple RAG API server in background
cd RAG_system
export RAG_API_PORT=$PORT
nohup python simple_rag_api.py > ../logs/simple_rag_api.log 2>&1 &
API_PID=$!

# Save PID
echo $API_PID > ../$PID_FILE

echo "✅ Simple RAG API server started with PID: $API_PID"
echo "📋 Logs: logs/simple_rag_api.log"
echo "🔗 API URL: http://$NODE_NAME:$PORT"
echo ""

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 10

# Test if server is running
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ Simple RAG API server is running and healthy!"
    echo "🌐 API available at: http://$NODE_NAME:$PORT"
    echo "📊 Health check: http://$NODE_NAME:$PORT/health"
    echo "📋 API docs: http://$NODE_NAME:$PORT/docs"
else
    echo "❌ Simple RAG API server failed to start"
    exit 1
fi

# Keep the job running and monitor the API
echo "🔄 Monitoring Simple RAG API server..."
while kill -0 $API_PID 2>/dev/null; do
    sleep 30
    
    # Check if API is still responding
    if ! curl -s http://localhost:$PORT/health > /dev/null; then
        echo "❌ Simple RAG API server is not responding, restarting..."
        kill -TERM $API_PID
        sleep 5
        nohup python simple_rag_api.py > ../logs/simple_rag_api.log 2>&1 &
        API_PID=$!
        echo $API_PID > ../$PID_FILE
        echo "✅ Simple RAG API server restarted with PID: $API_PID"
    fi
done

echo "🛑 Simple RAG API server process ended"
cleanup
