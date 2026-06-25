# app.py
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.cohere import CohereEmbedding

API_KEY = ""
COHERE_API_KEY = ""  # Free from dashboard.cohere.com/api-keys

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
http_client = httpx.AsyncClient(timeout=60.0)

Settings.embed_model = CohereEmbedding(
    cohere_api_key=COHERE_API_KEY,
    model_name="embed-english-light-v3.0",
)

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"message": "Running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start = time.time()
    query = request.message.strip()
    
    ret_start = time.time()
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = await retriever.aretrieve(query)
    context = "\n\n".join([node.text for node in nodes])
    print(f"⏱️ Retrieval: {time.time() - ret_start:.2f}s")
    
    prompt = f"""You are an FTC game rules expert. Use the following game rules to provide a comprehensive and detailed answer to the question.

Game Rules:
{context}

Question: {query}

Provide a thorough one-paragraph max answer based on the rules provided. Include:
- Main answer with specific details
- Relevant rule numbers/sections when applicable
- Any important exceptions or edge cases
- Examples if helpful
- Use bullet points where applicable and make sure its easily readable to all humans 
Answer:"""    
    api_start = time.time()
    response = await http_client.post(
        "https://ai.hackclub.com/proxy/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "qwen/qwen3-32b", "messages": [{"role": "user", "content": prompt}]}
    )
    print(f"⏱️ AI API: {time.time() - api_start:.2f}s")
    
    answer = response.json()["choices"][0]["message"]["content"]
    print(f"⏱️ Total: {time.time() - start:.2f}s")
    return ChatResponse(response=answer)
