#!/bin/bash
#SBATCH --job-name=dolphin_ocr
#SBATCH --output=../slurm_output/dolphin_ocr_%j.out
#SBATCH --error=../slurm_output/dolphin_ocr_%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=06:00:00

# Load Python 3.8.18
module load python/3.8.18

# Navigate to project directory
cd /home/rchaudhry_umass_edu/rag/src/ocr

# Activate virtual environment
source ../venv/bin/activate

# Create necessary directories
mkdir -p output
mkdir -p ../slurm_output

# Print configuration
echo "🚀 Starting Dolphin OCR Processing"
echo "================================="
echo "Processing PDFs in pdf_by_chapter directory"
echo ""

# Run the Dolphin OCR script
python ocr.py
