#!/bin/bash
#SBATCH --job-name=question_bank_test
#SBATCH --output=slurm_output/question_bank_test_%j.out
#SBATCH --error=slurm_output/question_bank_test_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64GB
#SBATCH --time=04:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/dolphinOcr

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p slurm_output
mkdir -p question_bank_reports

# Install pandas if not available
pip install pandas

# Set environment variables for adaptive RAG
export ADAPTIVE_RAG_RETRIEVAL_K=3
export ADAPTIVE_RAG_MODEL_MAX_TOKENS=512
export ADAPTIVE_RAG_MODEL_TEMPERATURE=0.7
export ADAPTIVE_RAG_ENABLE_TELEMETRY=true

# Print configuration
echo "🧪 Starting Question Bank Test Suite"
echo "==================================="
echo "Retrieval K: $ADAPTIVE_RAG_RETRIEVAL_K"
echo "Max Tokens: $ADAPTIVE_RAG_MODEL_MAX_TOKENS"
echo "Temperature: $ADAPTIVE_RAG_MODEL_TEMPERATURE"
echo "Telemetry: $ADAPTIVE_RAG_ENABLE_TELEMETRY"
echo ""

# Run the question bank test
python question_bank_test.py