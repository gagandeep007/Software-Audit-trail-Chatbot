from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings
from core.vector_store import VectorStoreManager
from core.data_loader import LogDataLoader
import os

class RAGService:
    def __init__(self):
        settings.validate()
        
        self.vector_store_manager = VectorStoreManager()
        self.data_loader = LogDataLoader()
        
        # Initialize Google LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.0 # Keep it deterministic for factual log analysis
        )
        
        # Define the prompt template for RAG
        self.system_prompt = (
            "You are an expert IT assistant tasked with analyzing application logs. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer or the context doesn't contain the information, "
            "just say that you don't know. Do not make up information.\n\n"
            "Context:\n{context}"
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])
        
        self._setup_chain()

    def _setup_chain(self):
        """Sets up the Retrieval-Augmented Generation chain."""
        retriever = self.vector_store_manager.get_retriever()
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt_template)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    def ask_question(self, question: str) -> str:
        """Queries the RAG pipeline."""
        if not question.strip():
            return "Please provide a valid question."
            
        try:
            response = self.rag_chain.invoke({"input": question})
            return response.get("answer", "No answer generated.")
        except Exception as e:
            return f"An error occurred while generating the answer: {str(e)}"

    def ingest_logs(self, file_path: str, original_filename: str) -> str:
        """Processes a new log file and adds it to the vector store."""
        try:
            # Save the file to the persistent data directory
            saved_path = self.data_loader.save_uploaded_file(file_path, original_filename)
            
            # Load and split the logs
            chunks = self.data_loader.load_and_split(saved_path)
            
            # Add to vector store
            num_chunks = self.vector_store_manager.add_documents(chunks)
            
            return f"Successfully ingested {original_filename}. Generated {num_chunks} chunks."
        except Exception as e:
            return f"Failed to ingest logs: {str(e)}"
