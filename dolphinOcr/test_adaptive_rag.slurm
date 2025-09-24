#!/bin/bash
#SBATCH --job-name=test_adaptive_rag
#SBATCH --output=slurm_output/test_adaptive_rag_%j.out
#SBATCH --error=slurm_output/test_adaptive_rag_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32GB
#SBATCH --time=02:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/dolphinOcr

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output

# Set environment variables for adaptive RAG
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Print configuration
echo "🧪 Starting Simplified Adaptive RAG Test Suite"
echo "============================================="
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "Tests query complexity analysis approach"
echo ""

# Run the simplified test suite
cd RAG_system
python test_adaptive_rag.py