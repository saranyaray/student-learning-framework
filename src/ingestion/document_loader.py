from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentLoader:
    def __init__(self):
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
        
    def load(self, document_path):
        """Load and process PDF document with safety checks"""
        try:
            # Load PDF
            loader = PyPDFLoader(document_path)
            documents = loader.load()
            
            # Safety check: ensure documents loaded
            if not documents:
                raise ValueError("PDF loader returned no documents")
            
            # Filter out pages with no content
            valid_pages = []
            for doc in documents:
                if doc.page_content and doc.page_content.strip():
                    valid_pages.append(doc)
                else:
                    print(f"⚠️ Skipping empty page")
            
            if not valid_pages:
                raise ValueError("All pages in PDF are empty or unreadable")
            
            # Split documents with safety checks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            split_docs = text_splitter.split_documents(valid_pages)
            
            # Final safety check
            if not split_docs:
                raise ValueError("Document splitting produced no chunks")
            
            return split_docs
            
        except Exception as e:
            raise Exception(f"Failed to load document: {e}")
