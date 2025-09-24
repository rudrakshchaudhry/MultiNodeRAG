#!/bin/bash

# 1. Load Python 3.8 (recommended for Dolphin)
module purge
module load python/3.8.18

# 2. Create & activate virtual environment
cd /home/rchaudhry_umass_edu/rag/dolphinOcr
python3 -m venv venv
chmod -R u+rwX venv
source venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r pdf_processing/Dolphin/requirements.txt
