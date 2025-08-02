#!/bin/bash
#SBATCH --job-name=dolphin_ocr
#SBATCH --output=./slurm_output/%j.out
#SBATCH --error=./slurm_output/%j.err
#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=06:00:00

cd /home/rchaudhry_umass_edu/rag/dolphinOcr

# Load Python & activate venv
source venv/bin/activate

# Ensure output and slurm_output directories exist
mkdir -p output
mkdir -p slurm_output

# Run the Dolphin OCR script
python ocr.py
