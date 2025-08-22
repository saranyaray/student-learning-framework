from pathlib import Path
from typing import Dict, List

# Try to use the new settings system, fallback to simple config if it fails
try:
    from pydantic import BaseSettings, Field, validator

    class Settings(BaseSettings):
        """Application settings with environment variable support"""

        # Project paths
        PROJECT_ROOT: Path = Path(__file__).parent.parent
        DATA_DIR: Path = Field(
            default_factory=lambda: Path(__file__).parent.parent / "data"
        )
        VECTORSTORE_DIR: Path = Field(
            default_factory=lambda: Path(__file__).parent.parent / "vectorstore"
        )
        LOGS_DIR: Path = Field(
            default_factory=lambda: Path(__file__).parent.parent / "logs"
        )

        # Embedding configuration
        EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
        CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
        CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")

        # Agent configuration
        OLLAMA_BASE_URL: str = Field(
            default="http://localhost:11434", env="OLLAMA_BASE_URL"
        )
        OLLAMA_AGENTS: Dict[str, str] = Field(
            default={
                "tutor": "ollama/phi3:3.8b",
                "coach": "ollama/gemma:2b",
                "analyst": "ollama/qwen:1.8b",
                "synthesizer": "ollama/phi3:3.8b",
            }
        )

        # Retrieval configuration
        TOP_K_DOCUMENTS: int = Field(default=4, env="TOP_K_DOCUMENTS")
        DISTANCE_THRESHOLD: float = Field(default=1.2, env="DISTANCE_THRESHOLD")
        MMR_DIVERSITY_FACTOR: float = Field(default=0.7, env="MMR_DIVERSITY_FACTOR")
        SEARCH_METHOD: str = Field(default="smart", env="SEARCH_METHOD")

        # Upload configuration
        UPLOAD_DIR: Path = Field(
            default_factory=lambda: Path(__file__).parent.parent / "data" / "raw"
        )
        ALLOWED_EXTENSIONS: List[str] = Field(default=[".pdf", ".txt", ".docx"])
        MAX_FILE_SIZE: int = Field(
            default=50 * 1024 * 1024, env="MAX_FILE_SIZE"
        )  # 50MB

        # API configuration
        API_HOST: str = Field(default="127.0.0.1", env="API_HOST")
        API_PORT: int = Field(default=8005, env="API_PORT")
        API_WORKERS: int = Field(default=1, env="API_WORKERS")

        # Logging configuration
        LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
        LOG_FORMAT: str = Field(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Security configuration
        CORS_ORIGINS: List[str] = Field(
            default=["http://localhost:3000"], env="CORS_ORIGINS"
        )
        API_KEY: str = Field(default="", env="API_KEY")

        @validator(
            "PROJECT_ROOT", "DATA_DIR", "VECTORSTORE_DIR", "LOGS_DIR", "UPLOAD_DIR"
        )
        def create_directories(cls, v):
            """Ensure directories exist"""
            v.mkdir(parents=True, exist_ok=True)
            return v

        @validator("CHUNK_SIZE", "CHUNK_OVERLAP")
        def validate_chunk_settings(cls, v, values):
            """Validate chunk settings"""
            if "CHUNK_SIZE" in values and v >= values["CHUNK_SIZE"]:
                raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
            return v

        @validator("MMR_DIVERSITY_FACTOR")
        def validate_mmr_factor(cls, v):
            """Validate MMR diversity factor"""
            if not 0 <= v <= 1:
                raise ValueError("MMR_DIVERSITY_FACTOR must be between 0 and 1")
            return v

        @validator("SEARCH_METHOD")
        def validate_search_method(cls, v):
            """Validate search method"""
            valid_methods = ["similarity", "mmr", "smart", "detailed"]
            if v not in valid_methods:
                raise ValueError(f"SEARCH_METHOD must be one of: {valid_methods}")
            return v

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False

    # Create settings instance
    settings = Settings()

except ImportError:
    # Fallback to simple configuration if pydantic-settings is not available
    print("Warning: pydantic-settings not available, using fallback configuration")

    # Simple fallback configuration
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"
    LOGS_DIR = PROJECT_ROOT / "logs"
    UPLOAD_DIR = DATA_DIR / "raw"

    # Ensure directories exist
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Default values
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    OLLAMA_AGENTS = {
        "tutor": "ollama/phi3:3.8b",
        "coach": "ollama/gemma:2b",
        "analyst": "ollama/qwen:1.8b",
        "synthesizer": "ollama/phi3:3.8b",
    }
    TOP_K_DOCUMENTS = 4
    ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"]
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    DISTANCE_THRESHOLD = 1.2
    MMR_DIVERSITY_FACTOR = 0.7
    SEARCH_METHOD = "smart"

    # Create a simple settings object for compatibility
    class SimpleSettings:
        def __init__(self):
            self.PROJECT_ROOT = PROJECT_ROOT
            self.DATA_DIR = DATA_DIR
            self.VECTORSTORE_DIR = VECTORSTORE_DIR
            self.LOGS_DIR = LOGS_DIR
            self.UPLOAD_DIR = UPLOAD_DIR
            self.EMBEDDING_MODEL = EMBEDDING_MODEL
            self.CHUNK_SIZE = CHUNK_SIZE
            self.CHUNK_OVERLAP = CHUNK_OVERLAP
            self.OLLAMA_AGENTS = OLLAMA_AGENTS
            self.TOP_K_DOCUMENTS = TOP_K_DOCUMENTS
            self.ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
            self.MAX_FILE_SIZE = MAX_FILE_SIZE
            self.DISTANCE_THRESHOLD = DISTANCE_THRESHOLD
            self.MMR_DIVERSITY_FACTOR = MMR_DIVERSITY_FACTOR
            self.SEARCH_METHOD = SEARCH_METHOD
            self.LOG_LEVEL = "INFO"
            self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    settings = SimpleSettings()

# Backward compatibility exports
PROJECT_ROOT = settings.PROJECT_ROOT
DATA_DIR = settings.DATA_DIR
VECTORSTORE_DIR = settings.VECTORSTORE_DIR
UPLOAD_DIR = settings.UPLOAD_DIR
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP
OLLAMA_AGENTS = settings.OLLAMA_AGENTS
TOP_K_DOCUMENTS = settings.TOP_K_DOCUMENTS
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
MAX_FILE_SIZE = settings.MAX_FILE_SIZE
DISTANCE_THRESHOLD = settings.DISTANCE_THRESHOLD
MMR_DIVERSITY_FACTOR = settings.MMR_DIVERSITY_FACTOR
SEARCH_METHOD = settings.SEARCH_METHOD


def get_vectorstore_path(document_name: str) -> Path:
    """Get the vector store path for a specific document"""
    store_name = f"{Path(document_name).stem}_faiss_index"
    return VECTORSTORE_DIR / store_name


def list_available_vectorstores() -> List[Path]:
    """List all available vector stores"""
    return list(VECTORSTORE_DIR.glob("*_faiss_index"))
