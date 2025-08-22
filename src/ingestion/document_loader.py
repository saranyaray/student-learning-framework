from pathlib import Path
from typing import List

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document

from src.utils import get_logger
from src.utils.exceptions import DocumentProcessingError, ValidationError

logger = get_logger(__name__)


class DocumentLoader:
    """Document loader with enhanced error handling and validation"""

    def __init__(self):
        self.supported_extensions = {".pdf", ".docx", ".txt"}
        logger.info("DocumentLoader initialized")

    def load(self, file_path: str) -> List[Document]:
        """
        Load document based on file type with enhanced error handling

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects

        Raises:
            ValidationError: If file doesn't exist or has unsupported extension
            DocumentProcessingError: If document loading fails
        """
        file_path = Path(file_path)

        # Validate file exists
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        # Validate file extension
        extension = file_path.suffix.lower()
        if extension not in self.supported_extensions:
            raise ValidationError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(self.supported_extensions)}"
            )

        logger.info(f"Loading document: {file_path.name} ({extension})")

        try:
            if extension == ".pdf":
                return self._load_pdf(file_path)
            elif extension == ".docx":
                return self._load_docx(file_path)
            elif extension == ".txt":
                return self._load_text(file_path)
            else:
                raise ValidationError(f"Unsupported file type: {extension}")

        except Exception as e:
            logger.error(f"Failed to load document {file_path.name}: {str(e)}")
            raise DocumentProcessingError(f"Failed to load document: {str(e)}") from e

    def _load_pdf(self, file_path: Path) -> List[Document]:
        """Load PDF document"""
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            return self._validate_documents(documents, file_path.name)
        except Exception as e:
            logger.error(f"PDF loading failed for {file_path.name}: {str(e)}")
            raise DocumentProcessingError(f"PDF loading failed: {str(e)}") from e

    def _load_docx(self, file_path: Path) -> List[Document]:
        """Load DOCX document"""
        try:
            loader = Docx2txtLoader(str(file_path))
            documents = loader.load()
            return self._validate_documents(documents, file_path.name)
        except Exception as e:
            logger.error(f"DOCX loading failed for {file_path.name}: {str(e)}")
            raise DocumentProcessingError(f"DOCX loading failed: {str(e)}") from e

    def _load_text(self, file_path: Path) -> List[Document]:
        """Load text document"""
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents = loader.load()
            return self._validate_documents(documents, file_path.name)
        except Exception as e:
            logger.error(f"Text loading failed for {file_path.name}: {str(e)}")
            raise DocumentProcessingError(f"Text loading failed: {str(e)}") from e

    def _validate_documents(
        self, documents: List[Document], filename: str
    ) -> List[Document]:
        """Validate and filter documents"""
        if not documents:
            raise DocumentProcessingError(f"No content extracted from {filename}")

        # Filter out empty documents
        valid_documents = [
            doc for doc in documents if doc.page_content and doc.page_content.strip()
        ]

        if not valid_documents:
            raise DocumentProcessingError(f"No valid content found in {filename}")

        logger.info(
            f"Validated {len(valid_documents)}/{len(documents)} "
            f"document chunks from {filename}"
        )
        return valid_documents

    def get_document_info(self, file_path: str) -> dict:
        """
        Get basic information about a document without loading it

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary with document information
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        return {
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size,
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
            "supported": file_path.suffix.lower() in self.supported_extensions,
        }
