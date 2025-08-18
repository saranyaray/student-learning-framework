import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# UPDATED: Per-document vector stores directory (not single path)
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"

# DEPRECATED: Remove or comment out single vector store path
# VECTOR_STORE_PATH = PROJECT_ROOT / "vectorstore" / "faiss_index"

# Ensure directories exist
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Agent (Ollama) model choices
OLLAMA_AGENTS = {
    "tutor": "ollama/phi3:3.8b",        # ~2.5GB
    "coach": "ollama/gemma:2b",         # ~1.5GB
    "analyst": "ollama/qwen:1.8b",      # ~1.2GB
    "synthesizer": "ollama/phi3:3.8b"  # ~2.5GB
}

# Retrieval config
TOP_K_DOCUMENTS = 4

# Upload configuration
UPLOAD_DIR = DATA_DIR / "raw"
ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

# UPDATED: Distance-based search settings (better for FAISS)
DISTANCE_THRESHOLD = 1.2  # Distance threshold for FAISS (lower = more strict)
MMR_DIVERSITY_FACTOR = 0.7  # Balance between relevance and diversity (0-1)
SEARCH_METHOD = "smart"  # Options: "distance", "mmr", "smart"

# Helper function for per-document vector store paths
def get_vectorstore_path(document_name: str) -> Path:
    """Get the vector store path for a specific document"""
    store_name = f"{Path(document_name).stem}_faiss_index"
    return VECTORSTORE_DIR / store_name

def list_available_vectorstores() -> list[Path]:
    """List all available vector stores"""
    return list(VECTORSTORE_DIR.glob("*_faiss_index"))
