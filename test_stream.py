import asyncio
from services.rag_pipeline import RAGService
import time

async def main():
    rag = RAGService()
    print("Testing streaming...")
    start = time.time()
    
    count = 0
    async for chunk in rag.ask_question_astream("give me a long summary of the logs"):
        print(f"[{time.time() - start:.2f}s] Chunk: {repr(chunk[:50])}...")
        count += 1
        
    print(f"Total chunks: {count}")

if __name__ == "__main__":
    asyncio.run(main())
