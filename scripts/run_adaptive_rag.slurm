#!/bin/bash
#SBATCH --job-name=adaptive_rag
#SBATCH --output=slurm_output/adaptive_rag_%j.out
#SBATCH --error=slurm_output/adaptive_rag_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH --time=12:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output
mkdir -p results

# Set environment variables for adaptive RAG
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Print configuration
echo "🚀 Starting Simplified Adaptive RAG Server"
echo "=========================================="
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "Uses query complexity analysis for routing decisions"
echo ""

# Start the simplified adaptive RAG server
cd src/rag_system
python adaptive_rag_server.py