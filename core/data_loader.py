import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings

class LogDataLoader:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_and_split(self, file_path: str):
        """Loads a log file and splits it into smaller chunks."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks

    def save_uploaded_file(self, temp_file_path: str, original_filename: str) -> str:
        """Saves an uploaded file to the configured DATA_DIR."""
        if not os.path.exists(settings.DATA_DIR):
            os.makedirs(settings.DATA_DIR)
            
        destination_path = os.path.join(settings.DATA_DIR, original_filename)
        shutil.copy2(temp_file_path, destination_path)
        return destination_path
