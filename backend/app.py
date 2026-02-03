from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from endee_client import EndeeClient
import json
import os

app = Flask(__name__)

# Load model, client, and doc map
print("Loading resources...")
model = SentenceTransformer("all-MiniLM-L6-v2")
client = EndeeClient()
COLLECTION_NAME = "semantic_docs"
DOC_MAP_FILE = "doc_map.json"
doc_map = {}

# Load document mapping if exists
if os.path.exists(DOC_MAP_FILE):
    with open(DOC_MAP_FILE, "r") as f:
        doc_map = json.load(f)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Query required"}), 400

    # Vectorize query
    vector = model.encode(query).tolist()

    # Search Endee
    # Returns list of matches, likely: [[id, distance], ...] or list of structs
    # MsgPack unpack usually returns generic types.
    results = client.search(COLLECTION_NAME, vector, top_k=5)
    
    formatted_results = []
    
    # Endee MessagePack result structure (ResultSet):
    # Typically struct { vector_results: ..., id_results: ... } or just list of items
    # We need to adapt based on what `unpackb` returns.
    # Assuming result is a list of results (or similar).
    # Since we can't test, we'll write robust handling:
    
    # If results is list of items
    try:
        # Check if results is a dict (ResultSet) or list
        items = []
        if isinstance(results, dict):
            # Maybe it has 'results' key?
             items = results.get("results", [])
        elif isinstance(results, list):
            items = results
            
        for item in items:
            # Item might be tuple (id, score) or dict
            doc_id = None
            score = 0.0
            
            # MessagePack might unpack to list/tuple [id, score]
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                # Assuming first is id, second is score (or vice versa? Usually ID, Distance)
                # But Endee C++ returns explicit objects.
                # Let's assume it returns a list of result objects.
                pass 
                
            # If Client returns list of dicts from some normalization:
            # Wait, `client.search` logic needs to be robust.
            # Endee C++: pack(sbuf, search_response) where search_response is std::vector<Result> or ResultSet
            # Let's assume list of dicts for now or handle raw.
            # Safest is to just send what we got + lookup text.
            
            # Simple fallback for demo:
            # If item is struct, e.g. [id, score]
            # Verify structure in live debug? (Can't do here)
            # We'll assume the client unpacks and it resembles [ {"id": "...", "distance": ...} ]
            
            doc_id = str(item.get('id')) if isinstance(item, dict) else str(item[0]) if isinstance(item, (list, tuple)) else None
            score = float(item.get('distance', 0)) if isinstance(item, dict) else float(item[1]) if isinstance(item, (list, tuple)) else 0.0
            
            text_content = doc_map.get(doc_id, f"Document ID: {doc_id}")
            
            formatted_results.append({
                "score": score,
                "text": text_content,
                "id": doc_id
            })

    except Exception as e:
        print(f"Error parsing results: {e}")
        # Return raw for debugging if parse fails
        formatted_results = [{"text": f"Raw Result Error: {str(e)}", "raw": str(results)}]

    return jsonify({"results": formatted_results})

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json
    doc_id = data.get("id")
    if not doc_id:
        return jsonify({"error": "Document ID required"}), 400

    # 1. Get Vector for the document
    vec_obj = client.get_vector(COLLECTION_NAME, doc_id)
    if not vec_obj:
         return jsonify({"error": "Document not found"}), 404

    # Extract vector. MsgPack unpack might return dict with 'vector' key
    # or a structure. Based on C++, likely key 'vector'.
    # If unpack returns list/tuple, we have to guess. 
    # Let's assume dict for now based on usual msgpack usage.
    query_vector = []
    if isinstance(vec_obj, dict) and 'vector' in vec_obj:
        query_vector = vec_obj['vector']
    elif isinstance(vec_obj, (list, tuple)) and len(vec_obj) > 1:
        # Fallback if it is a tuple like (id, vector, ...)
        # This is a guess if dict fails.
        query_vector = vec_obj[1] 
    else:
        # Try to use it directly if it looks like a vector
        # This part is experimental without live debug
        pass

    if not query_vector:
        return jsonify({"error": "Could not extract vector from document"}), 500

    # 2. Search for similar (get k+1 to exclude self)
    results = client.search(COLLECTION_NAME, query_vector, top_k=6)
    
    formatted_results = []
    try:
        items = []
        if isinstance(results, dict):
             items = results.get("results", [])
        elif isinstance(results, list):
            items = results
            
        for item in items:
            d_id = str(item.get('id')) if isinstance(item, dict) else str(item[0]) if isinstance(item, (list, tuple)) else None
            score = float(item.get('distance', 0)) if isinstance(item, dict) else float(item[1]) if isinstance(item, (list, tuple)) else 0.0
            
            # Filter out self
            if d_id == doc_id:
                continue
                
            text_content = doc_map.get(d_id, f"Document ID: {d_id}")
            
            formatted_results.append({
                "score": score,
                "text": text_content,
                "id": d_id
            })

    except Exception as e:
        print(f"Error parsing recommend results: {e}")

    return jsonify({"results": formatted_results})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
