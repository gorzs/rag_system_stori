import os
import re
import json
import numpy as np
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

# The selected model is one of the top-performing open-source embedding models
model = SentenceTransformer("intfloat/e5-base-v2")

input_folder = "input"
os.makedirs("output", exist_ok=True)

# This function splits text into chunks based on sentence length
# keeping each chunk under a max character length (default 500)
def split_by_sentences(text, max_len=500):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_len:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return [chunk for chunk in chunks if len(chunk.strip()) > 30]

# This function splits text using uppercase headings
# This is the initial attempt at chunking by titles, but it can produce large chunks
def split_by_titles(text):
    # Use regex to detect uppercase headings as delimiters
    sections = re.split(r'\n(?:[A-ZÁÉÍÓÚÜÑ ]{5,})\n', text)
    return [s.strip() for s in sections if len(s.strip()) > 50]

# Process all PDF files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(input_folder, filename)

        print(f"Processing: {filename}")

        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        base_name = os.path.splitext(filename)[0]

        if filename.startswith("1_"):
            print("Strategy: Chunking by sentences.")
            sections = split_by_sentences(full_text)
        elif filename.startswith("2_"):
            print("Strategy: Chunking by titles.")
            sections = split_by_titles(full_text)
        else:
            print("File not processed: Missing prefix (e.g. '1_' or '2_').\n")
            continue

        print(f"Generated {len(sections)} chunks.")

        # Generate vector embeddings
        embeddings = model.encode(sections, show_progress_bar=True)

        # Create FAISS index and store vectors
        dimension = embeddings[0].shape[0]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))

        faiss.write_index(index, f"output/{base_name}_index.faiss")
        with open(f"output/{base_name}_chunks.json", "w", encoding="utf-8") as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)

        print(f"Saved: output/{base_name}_index.faiss and .json\n")
