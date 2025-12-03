import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, PrivateAttr
import requests
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentenceTransformerEmbedding(BaseEmbedding):
    _model: SentenceTransformer = PrivateAttr()

    def __init__(self, model_name="BAAI/bge-small-en-v1.5", **kwargs):
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

print("Loading PDF and creating vector database...")
Settings.embed_model = SentenceTransformerEmbedding("BAAI/bge-small-en-v1.5")
documents = SimpleDirectoryReader(input_files=["game_manual.pdf"]).load_data()
index = VectorStoreIndex.from_documents(documents)
print("Vector database created!\n")

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
def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    query = request.message.strip()

    try:
        print(f"Searching for: {query}")

        retriever = index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(query)

        context = "\n\n".join([node.text for node in nodes])

        prompt = f"""Use the following game rules to answer the question.
    Game Rules:
    {context}
    Question: {query}
    Answer based only on the rules provided:"""

        if not API_KEY:
            raise HTTPException(
                status_code=500,
                detail="API_KEY not found in environment variables"
            )

        response = requests.post(
            "https://ai.hackclub.com/proxy/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/codestral-embed-2505",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from AI service: {response.text}"
            )

        answer = response.json()["choices"][0]["message"]["content"]
        print(f"\n Answer: {answer}\n")
        print("-" * 60)

        return ChatResponse(response=answer)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
