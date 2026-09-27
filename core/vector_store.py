from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from core.config import settings
import os

class VectorStoreManager:
    def __init__(self):
        # We ensure the Google API Key is set before initializing embeddings
        settings.validate()
        
        # Initialize Google Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        self.persist_directory = settings.CHROMA_DB_DIR
        
        # Initialize Chroma DB
        self.vector_store = Chroma(
            collection_name="application_logs",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents):
        """Embeds and adds new documents to the Chroma DB."""
        if not documents:
            return 0
        
        self.vector_store.add_documents(documents)
        return len(documents)

    def get_retriever(self, search_kwargs=None):
        """Returns a retriever interface for the vector store."""
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
