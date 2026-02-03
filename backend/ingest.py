import os
import json
from sentence_transformers import SentenceTransformer
from endee_client import EndeeClient

# Configuration
DATA_DIR = "../data"
COLLECTION_NAME = "semantic_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
DOC_MAP_FILE = "doc_map.json"

def main():
    print("Initializing embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Initializing Endee client...")
    client = EndeeClient()
    
    # 1. Read Data
    documents = []
    print("Reading documents...")
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple chunking by paragraph
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                documents.extend(paragraphs)

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Found {len(documents)} text chunks to ingest.")

    # 2. Embed Data
    print("Generating embeddings...")
    embeddings = model.encode(documents).tolist()
    dimension = len(embeddings[0])
    print(f"Embedding dimension: {dimension}")

    # 3. Create Collection
    # Check if exists first
    existing_indexes = client.list_indexes()
    if COLLECTION_NAME not in existing_indexes:
        print(f"Creating index '{COLLECTION_NAME}'...")
        client.create_collection(COLLECTION_NAME, dimension)
    else:
        print(f"Index '{COLLECTION_NAME}' already exists.")

    # 4. Insert into Endee & Save Map
    print("Inserting into Endee...")
    payloads = []
    doc_map = {}
    
    for i, doc in enumerate(documents):
        doc_id = str(i)
        payloads.append({"id": doc_id, "text": doc})
        doc_map[doc_id] = doc # Store text in local map since Endee is vector-only

    # Save mapping
    with open(DOC_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(doc_map, f)
    
    success = client.insert(COLLECTION_NAME, embeddings, payloads)
    if success:
        print("Ingestion complete!")
    else:
        print("Ingestion failed.")

if __name__ == "__main__":
    main()
