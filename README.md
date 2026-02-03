# Endee Semantic Search Project

This project demonstrates a Semantic Search application using **Endee** as the high-performance vector database. It ingests text documents, generates vector embeddings using SentenceTransformers, and provides a web interface for searching.

## Problem Statement
Traditional keyword search fails to capture the intent and context of queries. This project implements **semantic search** to find relevant documents based on meaning rather than just keyword matching, leveraging the speed of the Endee vector database.

## Technical Approach

### Architecture
- **Database**: Endee (Vector Database) running in Docker.
- **Backend**: Python (Flask).
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **Frontend**: HTML5/CSS3/JavaScript (Single Page Application).

### Data Flow
1. **Ingestion**: 
   - Text files are read from `data/`.
   - Text is split into paragraphs.
   - `SentenceTransformer` converts text to vectors.
   - Vectors + Text Payload are inserted into Endee via API.
2. **Search**:
   - User queries via Frontend.
   - Backend vectorizes the query.
   - Vector search is performed against Endee.
   - Results are returned and displayed.

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.8+

### 1. Start Endee Database
Ensure Docker Desktop is running, then:
```bash
docker-compose up -d
```
Verify it is running:
- API should be accessible at `http://localhost:8080`.

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Ingest Data
Load the sample data into Endee:
```bash
cd backend
python ingest.py
```

### 4. Run the Application
Start the search API:
```bash
# From backend/ directory
python app.py
```
Type `y` if asked to confirm anything.

### 5. Access Frontend
Open `frontend/index.html` in your browser.
Enter a query like "What is RAG?" or "How does vector search work?" to see results.

## Project Structure
```
c:/endee-semantic-search/
├── backend/
│   ├── app.py              # Flask API
│   ├── ingest.py           # Data ingestion
│   ├── endee_client.py     # Endee API wrapper
│   └── requirements.txt
├── frontend/
│   └── index.html          # UI
├── data/                   # Sample documents
└── docker-compose.yml      # Endee Service
```

## How Endee is Used
Endee is used as the core storage and retrieval engine for vector embeddings. We interact with it via REST API to:
- Create collections (if applicable).
- Insert 384-dimension vectors.
- Perform cosine similarity search (or L2/DotProduct) to find the nearest neighbors for a query vector.
