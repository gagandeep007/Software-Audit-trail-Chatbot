# Software Audit Trail Chatbot (RAG)

A highly performant, stunning web application that allows you to interactively query and analyze your application logs using Retrieval-Augmented Generation (RAG). Built with a modern custom glassmorphism UI, a lightning-fast FastAPI backend, Chroma DB for vector search, and powered by the Google Gemini LLM API.

## Features
- **✨ Custom Modern Web UI**: A beautiful, translucent Dark Glassmorphism interface with smooth animations and true token-by-token streaming markdown chat.
- **🚀 High-Performance Backend**: Powered by FastAPI with asynchronous endpoints and Server-Sent Events (SSE) for real-time text streaming.
- **☁️ AWS CloudWatch Integration**: Fetch and ingest your latest application logs directly from AWS CloudWatch Log Groups.
- **📁 Local Log Ingestion**: Drag-and-drop local `.log` or `.txt` files directly into the UI for instant vector embedding.
- **🧠 Advanced RAG Pipeline**: Utilizes Chroma DB for fast vector retrieval, LangChain for orchestration, and Google `gemini-3.5-flash` for intelligent, context-aware analysis.

## Prerequisites
- Python 3.9 or higher
- Google AI (Gemini) API Key
- (Optional) AWS Credentials with permissions to `logs:FilterLogEvents` for CloudWatch ingestion.

## Installation

1. **Clone or Navigate to the Repository**
   ```bash
   cd "Rag applications"
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory (or update the existing one) with the following credentials:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# LLM Configuration
LLM_MODEL=gemini-3.5-flash
EMBEDDING_MODEL=models/gemini-embedding-2

# Application Directories (auto-created if they don't exist)
CHROMA_DB_DIR=./db
DATA_DIR=./data

# Optional: AWS CloudWatch Configuration (for fetching remote logs)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

## Running the Application

1. **Start the FastAPI Server**
   Ensure your virtual environment is active, then run:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 7860 --reload
   ```

2. **Access the UI**
   Open your browser and navigate to:
   [http://localhost:7860](http://localhost:7860)

## Usage Guide

1. **Data Ingestion**: 
   - **Local Files**: Use the sidebar to drag and drop `.log` or `.txt` files. The app will chunk, embed, and store the logs in the local Chroma DB.
   - **AWS CloudWatch**: Enter a CloudWatch Log Group name (e.g., `/aws/ecs/my-app`) in the sidebar and click "Fetch & Ingest" to automatically download and embed the last 24 hours of logs.
2. **Chatting**: 
   - Type queries into the chat input (e.g., *"What were the most recent CRITICAL errors?"*).
   - The bot will retrieve relevant log chunks and instantly stream an analysis back to you, complete with markdown formatting!

## Notes on Rate Limits
If you are using the Google Gemini Free Tier, please be aware that the API restricts usage to **5 requests per minute**. If you exceed this limit, you may experience significant delays while the application waits for the quota to reset via exponential backoff.
