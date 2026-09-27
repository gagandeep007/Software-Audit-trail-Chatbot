import os
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import tempfile

from services.rag_pipeline import RAGService
from core.config import settings

app = FastAPI(title="Software Audit Trail API")

# Initialize RAG Service
try:
    rag_service = RAGService()
    is_ready = True
except ValueError as e:
    rag_service = None
    is_ready = False
    print(f"Failed to initialize RAGService: {e}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class AWSIngestRequest(BaseModel):
    log_group: str

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/api/upload")
async def upload_logs(file: UploadFile = File(...)):
    if not is_ready:
        raise HTTPException(status_code=500, detail="System not ready.")
    
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        result = rag_service.ingest_logs(tmp_path, file.filename)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

@app.post("/api/ingest_aws")
async def ingest_aws_logs(req: AWSIngestRequest):
    if not is_ready:
        raise HTTPException(status_code=500, detail="System not ready.")
    
    try:
        result = rag_service.ingest_cloudwatch_logs(req.log_group)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat")
async def chat_endpoint(q: str):
    if not is_ready:
        raise HTTPException(status_code=500, detail="System not ready.")
    
    async def event_generator():
        import json
        try:
            async for chunk in rag_service.ask_question_astream(q):
                yield {"data": json.dumps(chunk)}
        except Exception as e:
            yield {"data": json.dumps(f"\n\nError: {str(e)}")}
            
    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
