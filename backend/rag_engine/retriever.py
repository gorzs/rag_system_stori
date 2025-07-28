import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

#Directory to load FAISS indices and corresponding chunks
OUTPUT_DIR = "data/output"

#Embedding model (it has high similarity to Titan Embeddings)
embedding_model = SentenceTransformer("intfloat/e5-base-v2")

multi_indices = []

def load_indices_and_chunks():
    global multi_indices
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".faiss"):
            base_name = filename.replace("_index.faiss", "")
            json_file = os.path.join(OUTPUT_DIR, f"{base_name}_chunks.json")
            faiss_file = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(json_file):
                print(f"Loading: {faiss_file} and {json_file}")
                index = faiss.read_index(faiss_file)
                with open(json_file, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                multi_indices.append({"index": index, "chunks": chunks})
            else:
                print(f"Missing JSON file for {filename}")

# Load all FAISS indices and chunks
load_indices_and_chunks()

#Retrieves the top-k most semantically similar chunks to the input query
def retrieve_context(query, k=4):
    query_vector = embedding_model.encode([query])
    aggregated_results = []

    for source in multi_indices:
        index = source["index"]
        chunks = source["chunks"]

        distances, indices = index.search(np.array(query_vector), k)
        for i in range(len(indices[0])):
            idx = indices[0][i]
            dist = distances[0][i]
            if idx < len(chunks):
                aggregated_results.append((chunks[idx], dist))

    # Sort results by distance
    sorted_results = sorted(aggregated_results, key=lambda x: x[1])
    top_chunks = [chunk for chunk, _ in sorted_results[:k]]
    #print("TOP CHUNKS: ")
    #print(top_chunks)
    return "\n".join(top_chunks)
