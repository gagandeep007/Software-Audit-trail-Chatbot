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

    def fetch_from_cloudwatch(self, log_group_name: str) -> str:
        """
        Fetches the latest logs from an AWS CloudWatch Log Group and saves them to a file.
        Requires AWS credentials to be configured in .env.
        Returns the path to the saved file.
        """
        import boto3
        import time
        from botocore.exceptions import NoCredentialsError, ClientError
        
        try:
            client = boto3.client(
                'logs',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            # Fetch logs from the last 24 hours
            start_time = int((time.time() - 24 * 3600) * 1000)
            
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=start_time,
                limit=10000 # adjust limit as needed
            )
            
            events = response.get('events', [])
            if not events:
                raise ValueError(f"No logs found in {log_group_name} in the last 24 hours.")
                
            # Create a safe filename
            safe_name = log_group_name.replace("/", "_").strip("_")
            filename = f"aws_cloudwatch_{safe_name}.log"
            filepath = os.path.join(settings.DATA_DIR, filename)
            
            if not os.path.exists(settings.DATA_DIR):
                os.makedirs(settings.DATA_DIR)
                
            with open(filepath, "w", encoding="utf-8") as f:
                for event in events:
                    f.write(f"[{event.get('timestamp')}] {event.get('message')}\n")
                    
            return filepath
            
        except NoCredentialsError:
            raise ValueError("AWS credentials not found. Please set them in .env.")
        except ClientError as e:
            raise ValueError(f"AWS Error: {e.response['Error']['Message']}")
