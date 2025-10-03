#!/bin/bash
#SBATCH --job-name=universal_rag
#SBATCH --output=slurm_output/universal_rag_%j.out
#SBATCH --error=slurm_output/universal_rag_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32GB
#SBATCH --time=12:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/dolphinOcr

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output

# Set environment variables for universal RAG
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Set API keys (you can override these)
export GEMINI_API_KEY=${GEMINI_API_KEY:-""}
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY:-""}

# Print configuration
echo "🚀 Starting Universal RAG API Server"
echo "===================================="
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""
echo "Supports: Gemini, OpenAI, HuggingFace, Custom APIs"
echo "Deployable anywhere with any transformer model"
echo ""

# Start the universal RAG API server
cd rag_system
python universal_rag_api.py
