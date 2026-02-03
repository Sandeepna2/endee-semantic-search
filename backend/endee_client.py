import requests
import json
import msgpack

class EndeeClient:
    def __init__(self, base_url="http://localhost:8080/api/v1", token=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = token

    def create_collection(self, name, dimension):
        """
        Creates a new collection/index.
        """
        url = f"{self.base_url}/index/create"
        payload = {
            "index_name": name,
            "dim": dimension,
            "space_type": "cosine",
            "precision": "float32", # Defaulting to float32 for simplicity
            "M": 16,
            "ef_con": 200
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error creating collection: {response.text}")
                return None
        except Exception as e:
            print(f"Error creating collection: {e}")
            return None

    def insert(self, collection_name, vectors, payloads=None):
        """
        Inserts vectors into the collection.
        vectors: list of lists (embeddings)
        payloads: list of dicts (metadata) -> mapped to 'id' or stored externally?
        Endee native insert expects 'id' (string/int) and 'vector'. 
        It doesn't seem to store arbitrary payload in the index itself based on the C++ code 
        (it parses id, vector, sparse_indices/values).
        We will use the text as ID or hash it, or just store it in memory/separate DB?
        For this demo, we might need to rely on ID mapping if Endee doesn't store metadata.
        Wait, C++ code `HybridVectorObject` only has `id`, `vector`, `sparse...`. 
        So Endee is PURE vector store. We need a doc store side-by-side or use ID to lookup.
        For simplicity in this demo, we'll format ID as "doc_index" and keep a simple JSON map on disk or memory?
        Or maybe we just use the ID.
        """
        url = f"{self.base_url}/index/{collection_name}/vector/insert"
        data = []
        for i, vector in enumerate(vectors):
            # Using simple string ID for now
            doc_id = str(i)
            if payloads and i < len(payloads) and 'id' in payloads[i]:
                doc_id = str(payloads[i]['id'])
            
            item = {
                "id": doc_id,
                "vector": vector
            }
            data.append(item)
            
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    def search(self, collection_name, vector, top_k=5):
        """
        Searches the collection. Returns MessagePack binary which we decode.
        """
        url = f"{self.base_url}/index/{collection_name}/search"
        payload = {
            "vector": vector,
            "k": top_k,
            "include_vectors": False
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                # Response is MessagePack
                if response.headers.get("Content-Type") == "application/msgpack":
                    return msgpack.unpackb(response.content, raw=False)
                else:
                    return response.json()
            else:
                print(f"Search error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_vector(self, collection_name, doc_id):
        """
        Retrieves a vector by ID.
        """
        url = f"{self.base_url}/index/{collection_name}/vector/get"
        payload = {"id": doc_id}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                # Response is MessagePack
                if response.headers.get("Content-Type") == "application/msgpack":
                    return msgpack.unpackb(response.content, raw=False)
                return response.json() # Fallback
            else:
                print(f"Error getting vector: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting vector: {e}")
            return None

    def list_indexes(self):
        url = f"{self.base_url}/index/list"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return [idx['name'] for idx in data.get('indexes', [])]
            return []
        except Exception as e:
            print(f"Error listing indexes: {e}")
            return []
