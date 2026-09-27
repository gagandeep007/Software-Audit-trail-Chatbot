import gradio as gr
import os
from services.rag_pipeline import RAGService
from core.config import settings

# Attempt to initialize RAG Service
# It will fail if GOOGLE_API_KEY is not set, which is handled gracefully in UI below
try:
    rag_service = RAGService()
    is_ready = True
    init_message = "System is ready."
except ValueError as e:
    rag_service = None
    is_ready = False
    init_message = str(e) + "\nPlease set it in the .env file and restart the application."

def process_upload(file):
    if not is_ready:
        return "System is not ready. Please check API keys."
    if file is None:
        return "No file uploaded."
    
    # Gradio passes a temporary file path
    file_path = file.name
    original_filename = os.path.basename(file_path)
    
    # If the user uploaded something, process it
    result = rag_service.ingest_logs(file_path, original_filename)
    return result

def chat_interface(message, history):
    if not is_ready:
        return "System is not ready. Please check API keys."
    
    # Query the RAG pipeline
    return rag_service.ask_question(message)

# Build the Gradio UI
with gr.Blocks(title="Software Audit Trail Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📝 Software Audit Trail Chatbot (RAG)")
    
    if not is_ready:
        gr.Markdown(f"### ⚠️ Initialization Error\n{init_message}")
    
    with gr.Tabs():
        with gr.Tab("💬 Chat"):
            gr.Markdown("Ask questions about your ingested application logs.")
            chat = gr.ChatInterface(
                fn=chat_interface,
                fill_height=True
            )
            
        with gr.Tab("⚙️ Admin / Data Ingestion"):
            gr.Markdown("### Upload Log Files")
            gr.Markdown("Upload `.log` or `.txt` files containing application logs to be chunked, embedded, and stored in Chroma DB.")
            
            with gr.Row():
                file_input = gr.File(label="Select Log File")
                upload_button = gr.Button("Process & Ingest Logs", variant="primary")
            
            upload_status = gr.Textbox(label="Ingestion Status", interactive=False)
            
            upload_button.click(
                fn=process_upload,
                inputs=[file_input],
                outputs=[upload_status]
            )

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    
    # Launch the Gradio app
    demo.launch(server_name="0.0.0.0", server_port=7860)
