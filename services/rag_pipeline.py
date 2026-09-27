from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings
from core.vector_store import VectorStoreManager
from core.data_loader import LogDataLoader
import os

class RAGService:
    """
    RAGService acts as the central orchestrator for the Retrieval-Augmented Generation application.
    It manages the ingestion of new log files into the vector database and handles querying the LLM
    with context retrieved from those logs.
    """
    
    def __init__(self):
        # Ensure all required environment variables are set before proceeding
        settings.validate()
        
        # Initialize dependencies
        self.vector_store_manager = VectorStoreManager()
        self.data_loader = LogDataLoader()
        
        # Initialize Google LLM via LangChain.
        # Temperature is set to 0.0 to ensure the model produces highly deterministic and factual 
        # answers based strictly on the log data, minimizing hallucinations.
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.0 
        )
        
        # Define the system prompt guiding the LLM's behavior.
        # It strictly instructs the LLM to use the provided context and avoid making up answers.
        self.system_prompt = (
            "You are an expert IT assistant tasked with analyzing application logs. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer or the context doesn't contain the information, "
            "just say that you don't know. Do not make up information.\n\n"
            "Context:\n{context}"
        )
        
        # Construct a prompt template combining the system instructions and the user input
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])
        
        # Build the RAG chain upon initialization
        self._setup_chain()

    def _setup_chain(self):
        """
        Sets up the LangChain Retrieval-Augmented Generation pipeline.
        
        1. Gets the retriever from the vector store manager.
        2. Creates a 'stuff' document chain (which stuffs all retrieved chunks into the prompt).
        3. Combines the retriever and the document chain into a final end-to-end RAG chain.
        """
        retriever = self.vector_store_manager.get_retriever()
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt_template)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    def ask_question(self, question: str) -> str:
        """
        Queries the RAG pipeline with a user question.
        
        Args:
            question (str): The user's question about the application logs.
            
        Returns:
            str: The LLM's response based on the retrieved context, or an error message.
        """
        if not question.strip():
            return "Please provide a valid question."
            
        try:
            # Invoke the LangChain RAG chain with the input question.
            # This automatically retrieves relevant log chunks and passes them to the LLM.
            response = self.rag_chain.invoke({"input": question})
            return response.get("answer", "No answer generated.")
        except Exception as e:
            return f"An error occurred while generating the answer: {str(e)}"

    def ingest_logs(self, file_path: str, original_filename: str) -> str:
        """
        Processes a new log file and adds it to the vector store.
        
        Args:
            file_path (str): The path to the uploaded log file (e.g., a temporary file).
            original_filename (str): The original name of the uploaded file.
            
        Returns:
            str: A status message indicating success or failure.
        """
        try:
            # Step 1: Save the temporary uploaded file to our persistent data directory
            saved_path = self.data_loader.save_uploaded_file(file_path, original_filename)
            
            # Step 2: Load the saved file and split it into smaller text chunks suitable for embedding
            chunks = self.data_loader.load_and_split(saved_path)
            
            # Step 3: Embed the chunks and store them in Chroma DB
            num_chunks = self.vector_store_manager.add_documents(chunks)
            
            return f"Successfully ingested {original_filename}. Generated {num_chunks} chunks."
        except Exception as e:
            return f"Failed to ingest logs: {str(e)}"
