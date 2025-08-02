#!/bin/bash
#SBATCH --job-name=rag_api_llama3
#SBATCH --output=../slurm_output/%j.out
#SBATCH --error=../slurm_output/%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=24:00:00

cd /home/rchaudhry_umass_edu/rag/dolphinOcr/RAG_system

# Load Python 3.8.18
module purge
module load python/3.8.18

# Activate venv
source ../venv/bin/activate

# Ensure slurm_output directory exists
mkdir -p ../slurm_output

# Run the API server
echo "Starting RAG API server on port 8000..."
python api_server.py 