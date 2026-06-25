# app.py - FINAL VERSION
import os
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, PrivateAttr
from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer

API_KEY = ""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_client = httpx.AsyncClient(timeout=60.0)

class SentenceTransformerEmbedding(BaseEmbedding):
    _model: SentenceTransformer = PrivateAttr()
    
    def __init__(self, model_name="all-MiniLM-L6-v2", **kwargs):  # MUCH faster model
        super().__init__(**kwargs)
        object.__setattr__(self, '_model', SentenceTransformer(model_name))
    
    def _get_query_embedding(self, query: str):
        return self._model.encode(query).tolist()
    
    def _get_text_embedding(self, text: str):
        return self._model.encode(text).tolist()
    
    async def _aget_query_embedding(self, query: str):
        return self._get_query_embedding(query)
    
    async def _aget_text_embedding(self, text: str):
        return self._get_text_embedding(text)

Settings.embed_model = SentenceTransformerEmbedding("all-MiniLM-L6-v2")

STORAGE_DIR = "./storage"
storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
index = load_index_from_storage(storage_context)
print("Vector index loaded!")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"message": "FTC RAG Backend API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    query = request.message.strip()
    
    try:
        print(f"Searching for: {query}")
        
        retrieval_start = time.time()
        retriever = index.as_retriever(similarity_top_k=2)
        nodes = retriever.retrieve(query)
        context = "\n\n".join([node.text for node in nodes])
        retrieval_time = time.time() - retrieval_start
        print(f"⏱️ Retrieval took: {retrieval_time:.2f}s")
        
        prompt = f"""Use the following game rules to answer the question.

Game Rules:
{context}

Question: {query}

Answer based only on the rules provided:"""
        
        api_start = time.time()
        response = await http_client.post(
            "https://ai.hackclub.com/proxy/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3-32b",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        api_time = time.time() - api_start
        print(f"⏱️ AI API call took: {api_time:.2f}s")
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error from AI service: {response.text}")
        
        answer = response.json()["choices"][0]["message"]["content"]
        
        total_time = time.time() - start_time
        print(f"⏱️ Total request took: {total_time:.2f}s")
        print(f"\nAnswer: {answer}\n{'-'*60}")
        
        return ChatResponse(response=answer)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
