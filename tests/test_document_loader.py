"""
Tests for document loader functionality
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.ingestion.document_loader import DocumentLoader, Document
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
        assert self.loader.supported_extensions == {'.pdf', '.docx', '.txt'}
    
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
    
    def test_load_pdf_success(self):
        """Test successful PDF loading"""
        # Create test PDF file
        test_file = self.test_data_dir / "test.pdf"
        test_file.write_text("fake pdf content")
        
        try:
            result = self.loader.load(str(test_file))
            assert len(result) == 1
            assert "PDF document: test.pdf" in result[0].page_content
            assert result[0].metadata["type"] == "pdf"
        finally:
            test_file.unlink()
    
    def test_load_docx_success(self):
        """Test successful DOCX loading"""
        # Create test DOCX file
        test_file = self.test_data_dir / "test.docx"
        test_file.write_text("fake docx content")
        
        try:
            result = self.loader.load(str(test_file))
            assert len(result) == 1
            assert "DOCX document: test.docx" in result[0].page_content
            assert result[0].metadata["type"] == "docx"
        finally:
            test_file.unlink()
    
    def test_load_text_success(self):
        """Test successful text loading"""
        # Create test text file
        test_file = self.test_data_dir / "test.txt"
        test_content = "This is test content"
        test_file.write_text(test_content)
        
        try:
            result = self.loader.load(str(test_file))
            assert len(result) == 1
            assert result[0].page_content == test_content
            assert result[0].metadata["type"] == "text"
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
    
    def test_document_class(self):
        """Test the Document class"""
        doc = Document("test content", {"key": "value"})
        assert doc.page_content == "test content"
        assert doc.metadata["key"] == "value"
        
        # Test with no metadata
        doc2 = Document("test content 2")
        assert doc2.page_content == "test content 2"
        assert doc2.metadata == {}
