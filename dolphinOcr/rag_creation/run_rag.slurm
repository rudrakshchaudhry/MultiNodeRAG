#!/bin/bash
#SBATCH --job-name=rag_index
#SBATCH --output=../slurm_output/rag_index_%j.out
#SBATCH --error=../slurm_output/rag_index_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=06:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/dolphinOcr/rag_creation

# Activate virtual environment
source ../venv/bin/activate

# Create necessary directories
mkdir -p ../slurm_output

# Print configuration
echo "🚀 Starting RAG Index Creation"
echo "=============================="
echo "Creating FAISS index from processed PDFs"
echo "Using BAAI/bge-small-en-v1.5 embeddings"
echo ""

# Run the RAG indexing pipeline
python rag_pipeline.py 