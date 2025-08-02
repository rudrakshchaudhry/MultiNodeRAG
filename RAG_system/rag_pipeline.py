import os
import glob
import json
import torch
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Paths
MARKDOWN_DIR = '/home/rchaudhry_umass_edu/rag/dolphinOcr/output/markdown'
JSON_DIR = '/home/rchaudhry_umass_edu/rag/dolphinOcr/output/recognition_json'
INDEX_DIR = '/home/rchaudhry_umass_edu/rag/dolphinOcr/RAG_system/index_data'

# Embedding model
EMBED_MODEL = 'all-MiniLM-L6-v2'

# Load markdown files
md_files = sorted(glob.glob(os.path.join(MARKDOWN_DIR, '*.md')))
md_texts = []
md_filenames = []
for f in md_files:
    with open(f, 'r', encoding='utf-8') as file:
        md_texts.append(file.read())
        md_filenames.append(os.path.basename(f))

# Optionally, load JSON files for enrichment
json_files = sorted(glob.glob(os.path.join(JSON_DIR, '*.json')))
json_data = {}
for f in json_files:
    with open(f, 'r', encoding='utf-8') as file:
        json_data[os.path.basename(f)] = json.load(file)

# Build embeddings for markdown files
embedder = SentenceTransformer(EMBED_MODEL)
md_embeddings = embedder.encode(md_texts, convert_to_numpy=True, show_progress_bar=True)

# Build FAISS index
index = faiss.IndexFlatL2(md_embeddings.shape[1])
index.add(md_embeddings)

# Save all necessary objects for answer.py
os.makedirs(INDEX_DIR, exist_ok=True)
faiss.write_index(index, os.path.join(INDEX_DIR, 'faiss.index'))
with open(os.path.join(INDEX_DIR, 'md_filenames.pkl'), 'wb') as f:
    pickle.dump(md_filenames, f)
with open(os.path.join(INDEX_DIR, 'md_texts.pkl'), 'wb') as f:
    pickle.dump(md_texts, f)
with open(os.path.join(INDEX_DIR, 'json_data.pkl'), 'wb') as f:
    pickle.dump(json_data, f)
with open(os.path.join(INDEX_DIR, 'md_embeddings.npy'), 'wb') as f:
    import numpy as np
    np.save(f, md_embeddings)

print('Indexing complete. All data saved to', INDEX_DIR) 