import os
import subprocess

PDF_DIR = 'pdf_by_chapter'
OUTPUT_DIR = 'output'
DEMO_SCRIPT = 'demo_page.py'
CONFIG_PATH = os.path.join('config', 'Dolphin.yaml')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List all PDF files in the input directory
pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]

for pdf_file in pdf_files:
    input_path = os.path.join(PDF_DIR, pdf_file)  # relative to current dir
    output_path = OUTPUT_DIR                      # relative to current dir
    print(f'Processing: {input_path}')
    cmd = [
        'python', DEMO_SCRIPT,
        '--config', CONFIG_PATH,
        '--input_path', input_path,
        '--save_dir', output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='Dolphin')
    if result.returncode == 0:
        print(f'Successfully processed {pdf_file}')
    else:
        print(f'Error processing {pdf_file}:')
        print(result.stderr)
