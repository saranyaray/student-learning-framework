import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL


class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

    def create_vectorstore_for_document(
        self, document, doc_id, dir_path="vectorstores"
    ):
        """
        Make a vector store just for this document and save under a unique path.
        """
        # Split the document into chunks
        chunks = self.text_splitter.split_documents([document])
        # Build the FAISS vector store for these chunks
        vectordb = FAISS.from_documents(chunks, self.embeddings)
        # Define save directory
        save_path = os.path.join(dir_path, f"{doc_id}_faiss_index")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        vectordb.save_local(save_path)
        return save_path  # Return location for later retrieval

    def from_documents(self, documents, save_path):
        """
        If you want a single vector store from multiple documents.
        """
        chunks = self.text_splitter.split_documents(documents)
        vectordb = FAISS.from_documents(chunks, self.embeddings)
        vectordb.save_local(save_path)
        return vectordb

    def load(self, load_path):
        """
        Loads a FAISS vectorstore from a given path.
        """
        return FAISS.load_local(
            load_path, self.embeddings, allow_dangerous_deserialization=True
        )
