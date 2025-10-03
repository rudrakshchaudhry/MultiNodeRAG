#!/bin/bash

# Dolphin OCR RAG System Runner
# Usage: ./run_system.sh [command]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    "pdf")
        echo "🚀 Starting PDF Processing..."
        cd src/ocr
        sbatch run.slurm
        echo "✅ PDF processing job submitted"
        ;;
    "rag")
        echo "🚀 Starting RAG Index Creation..."
        cd src/rag_indexing
        sbatch run_rag.slurm
        echo "✅ RAG indexing job submitted"
        ;;
    "adaptive")
        echo "🚀 Starting Simplified Adaptive RAG Server..."
        sbatch scripts/run_adaptive_rag.slurm
        echo "✅ Adaptive RAG server job submitted"
        ;;
    "universal")
        echo "🚀 Starting Universal RAG API Server..."
        sbatch scripts/run_universal_rag.slurm
        echo "✅ Universal RAG API server job submitted"
        ;;
    "host")
        echo "🌐 Starting RAG API Hosting Service..."
        ./scripts/manage_rag_hosting.sh start
        ;;
    "test")
        echo "🧪 Starting Adaptive RAG Tests..."
        sbatch scripts/test_adaptive_rag.slurm
        echo "✅ Adaptive RAG test job submitted"
        ;;
    "test-question-bank")
        echo "🧪 Starting Question Bank Tests..."
        sbatch scripts/question_bank_test.slurm
        echo "✅ Question bank test job submitted"
        ;;
    "setup")
        echo "⚙️ Setting up environment..."
        cd src/ocr
        ./setup_env.sh
        echo "✅ Environment setup complete"
        ;;
    "status")
        echo "📊 Checking job status..."
        squeue -u $USER
        ;;
    "logs")
        echo "📋 Recent SLURM outputs:"
        ls -la slurm_output/ | tail -10
        ;;
    "help"|*)
        echo "MultiNodeRAG System Runner"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  pdf         - Submit PDF processing job"
        echo "  rag         - Submit RAG index creation job"
        echo "  adaptive    - Submit simplified adaptive RAG server job"
        echo "  universal   - Submit universal RAG API server job (model-agnostic)"
        echo "  host        - Start RAG API hosting service (persistent)"
        echo "  test        - Submit adaptive RAG test job"
        echo "  test-question-bank - Submit question bank comprehensive test job"
        echo "  setup       - Setup environment and dependencies"
        echo "  status      - Check SLURM job status"
        echo "  logs        - Show recent SLURM outputs"
        echo "  help        - Show this help message"
        echo ""
        echo "Workflow:"
        echo "  1. ./run_system.sh setup    # Setup environment"
        echo "  2. ./run_system.sh pdf      # Process PDFs"
        echo "  3. ./run_system.sh rag      # Create RAG index"
        echo "  4. ./run_system.sh host     # Start RAG API hosting service"
        echo "  5. ./run_system.sh test     # Test the system"
        echo ""
        echo "System Features:"
        echo "  - Universal RAG API (works with any transformer model)"
        echo "  - Simplified server using query complexity analysis"
        echo "  - Automatic routing based on query complexity"
        echo "  - Next.js integration components"
        echo "  - Comprehensive test suite"
        echo "  - Question bank evaluation"
        echo ""
        echo "Python Version: 3.8.18"
        echo "GPU Requirements: A100 (8GB+ VRAM recommended)"
        ;;
esac