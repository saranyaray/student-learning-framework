
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.schema import Document
from pathlib import Path

class DocumentLoader:
    def load(self, file_path: str):
        """Load document based on file type"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
                return loader.load()
            
            elif extension == '.docx':
                loader = Docx2txtLoader(str(file_path))
                return loader.load()
            
            elif extension == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
                return loader.load()
            
            else:
                raise ValueError(f"Unsupported file type: {extension}")
                
        except Exception as e:
            raise Exception(f"Failed to load document: {e}")
