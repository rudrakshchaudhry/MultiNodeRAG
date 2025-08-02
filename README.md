# MultiNodeRAG

A comprehensive document processing and retrieval system that combines [Dolphin](https://github.com/bytedance/Dolphin) document parsing with a Retrieval Augmented Generation (RAG) pipeline.

## 🔧 System Overview

This system processes PDF documents through multiple stages:

1. **📄 Document Parsing**: Uses Dolphin to convert PDF chapters into structured markdown and JSON formats
2. **🔍 Content Extraction**: Extracts text, tables, formulas, and figures from documents 
3. **🧠 Embedding Generation**: Creates semantic embeddings using SentenceTransformers
4. **📚 Index Building**: Builds FAISS indices for efficient document retrieval
5. **💬 RAG Pipeline**: Enables question-answering over the processed documents

## 📁 Project Structure

```
MultiNodeRAG/
├── Dolphin/                    # Document parsing model (Dolphin)
│   ├── assets/                 # Demo assets and images
│   ├── checkpoints/           # Model checkpoints
│   ├── config/                # Configuration files
│   ├── demo/                  # Demo images and examples
│   ├── deployment/            # TensorRT and vLLM deployment
│   └── utils/                 # Utility functions
├── RAG_system/                # RAG pipeline implementation
│   ├── api_server.py          # API server for RAG queries
│   ├── config.py              # RAG configuration
│   └── rag_pipeline.py        # Main RAG pipeline logic
├── pdf_by_chapter/            # Input PDF files organized by chapters
├── output/                    # Processed outputs
│   ├── markdown/              # Parsed markdown files
│   └── recognition_json/      # Structured JSON recognition results
├── ocr.py                     # Main OCR processing script
└── *.slurm                    # SLURM job scripts for HPC environments
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA-compatible GPU (recommended)
- Sufficient disk space for models and processed documents

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd MultiNodeRAG
   ```

2. **Set up the environment:**
   ```bash
   chmod +x setup_env_ocr.sh
   ./setup_env_ocr.sh
   source venv/bin/activate
   ```

3. **Download Dolphin model:**
   ```bash
   cd Dolphin
   # Option A: Download from Baidu Yun or Google Drive (see Dolphin/README.md)
   # Option B: Use Hugging Face
   git clone https://huggingface.co/ByteDance/Dolphin ./hf_model
   ```

### Usage

#### 1. Process PDF Documents

Place your PDF files in the `pdf_by_chapter/` directory, then run:

```bash
python ocr.py
```

This will:
- Process each PDF using Dolphin
- Generate markdown and JSON outputs
- Save results in the `output/` directory

#### 2. Build RAG Index

```bash
cd RAG_system
python rag_pipeline.py
```

This creates FAISS indices and embeddings for retrieval.

#### 3. Start RAG API Server

```bash
cd RAG_system
python api_server.py
```

The API server will be available for document queries and retrieval.

### HPC/SLURM Usage

For high-performance computing environments:

```bash
# Submit OCR processing job
sbatch run_ocr.slurm

# Submit RAG pipeline jobs
sbatch RAG_system/rag_build.slurm
sbatch RAG_system/rag_serve.slurm
```

## 📊 Features

### Document Processing (Dolphin)
- **Multi-format Support**: Process PDF files and images
- **Structured Output**: Generate both markdown and JSON formats
- **Element Recognition**: Extract text, tables, formulas, and figures
- **Batch Processing**: Handle multiple documents efficiently
- **GPU Acceleration**: TensorRT and vLLM deployment options

### RAG System
- **Semantic Search**: Uses SentenceTransformers for embedding generation
- **Fast Retrieval**: FAISS-based vector indexing
- **Scalable**: Handles large document collections
- **API Interface**: RESTful API for integration
- **Multi-modal**: Supports both text and structured data retrieval

## 🔧 Configuration

### Dolphin Configuration
Edit `Dolphin/config/Dolphin.yaml` to customize:
- Model parameters
- Processing batch sizes
- Output formats

### RAG Configuration  
Edit `RAG_system/config.py` to customize:
- Embedding models
- Index parameters
- API settings

## 📈 Performance

The system is optimized for:
- **Batch Processing**: Parallel document processing
- **Memory Efficiency**: Streaming and chunked processing
- **GPU Utilization**: CUDA acceleration where available
- **Scalability**: HPC cluster compatibility

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project incorporates:
- **Dolphin**: MIT License (ByteDance)
- **RAG Components**: [Your License]

## 🙏 Acknowledgments

- [Dolphin](https://github.com/bytedance/Dolphin) by ByteDance for document parsing
- [SentenceTransformers](https://www.sbert.net/) for embedding generation
- [FAISS](https://github.com/facebookresearch/faiss) for vector indexing
- [Hugging Face](https://huggingface.co/) for model hosting and transformers

## 📞 Support

For issues related to:
- **Dolphin**: See [Dolphin repository](https://github.com/bytedance/Dolphin)
- **RAG System**: Open an issue in this repository
- **Integration**: Check the documentation or open a discussion

---

*MultiNodeRAG combines state-of-the-art document parsing with powerful retrieval capabilities for comprehensive document understanding and querying.*