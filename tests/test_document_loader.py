"""
Tests for document loader functionality
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from langchain.schema import Document

from src.ingestion.document_loader import DocumentLoader
from src.utils.exceptions import DocumentProcessingError, ValidationError


class TestDocumentLoader:
    """Test cases for DocumentLoader class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.loader = DocumentLoader()
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up test files if they exist
        pass

    def test_loader_initialization(self):
        """Test DocumentLoader initialization"""
        assert self.loader.supported_extensions == {".pdf", ".docx", ".txt"}

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist"""
        with pytest.raises(ValidationError, match="File not found"):
            self.loader.load("nonexistent_file.pdf")

    def test_load_unsupported_extension(self):
        """Test loading a file with unsupported extension"""
        # Create a temporary file with unsupported extension
        test_file = self.test_data_dir / "test.xyz"
        test_file.write_text("test content")

        try:
            with pytest.raises(ValidationError, match="Unsupported file type"):
                self.loader.load(str(test_file))
        finally:
            test_file.unlink()

    @patch("src.ingestion.document_loader.PyPDFLoader")
    def test_load_pdf_success(self, mock_pdf_loader):
        """Test successful PDF loading"""
        # Mock PDF loader
        mock_loader_instance = Mock()
        mock_documents = [
            Document(page_content="Page 1 content", metadata={"page": 1}),
            Document(page_content="Page 2 content", metadata={"page": 2}),
        ]
        mock_loader_instance.load.return_value = mock_documents
        mock_pdf_loader.return_value = mock_loader_instance

        # Create test PDF file
        test_file = self.test_data_dir / "test.pdf"
        test_file.write_text("fake pdf content")

        try:
            result = self.loader.load(str(test_file))
            assert len(result) == 2
            assert result[0].page_content == "Page 1 content"
            assert result[1].page_content == "Page 2 content"
        finally:
            test_file.unlink()

    @patch("src.ingestion.document_loader.PyPDFLoader")
    def test_load_pdf_failure(self, mock_pdf_loader):
        """Test PDF loading failure"""
        # Mock PDF loader to raise exception
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("PDF loading failed")
        mock_pdf_loader.return_value = mock_loader_instance

        # Create test PDF file
        test_file = self.test_data_dir / "test.pdf"
        test_file.write_text("fake pdf content")

        try:
            with pytest.raises(DocumentProcessingError, match="PDF loading failed"):
                self.loader.load(str(test_file))
        finally:
            test_file.unlink()

    @patch("src.ingestion.document_loader.PyPDFLoader")
    def test_load_empty_pdf(self, mock_pdf_loader):
        """Test loading PDF with no content"""
        # Mock PDF loader to return empty documents
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = []
        mock_pdf_loader.return_value = mock_loader_instance

        # Create test PDF file
        test_file = self.test_data_dir / "test.pdf"
        test_file.write_text("fake pdf content")

        try:
            with pytest.raises(DocumentProcessingError, match="No content extracted"):
                self.loader.load(str(test_file))
        finally:
            test_file.unlink()

    def test_get_document_info(self):
        """Test getting document information"""
        # Create test file
        test_file = self.test_data_dir / "test.txt"
        test_content = "This is test content"
        test_file.write_text(test_content)

        try:
            info = self.loader.get_document_info(str(test_file))

            assert info["filename"] == "test.txt"
            assert info["extension"] == ".txt"
            assert info["size_bytes"] == len(test_content)
            assert info["supported"] is True
        finally:
            test_file.unlink()

    def test_get_document_info_nonexistent(self):
        """Test getting info for nonexistent file"""
        with pytest.raises(ValidationError, match="File not found"):
            self.loader.get_document_info("nonexistent_file.txt")
