import requests
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer
from pydantic import Field, PrivateAttr

load_dotenv()
API_KEY = os.getenv("API_KEY")

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
print("✓ Vector database created!\n")

def ask_question(query):
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
        raise ValueError("API_KEY not found in environment variables. Please set it in .env file.")
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
    answer = response.json()["choices"][0]["message"]["content"]
    print(f"\n Answer: {answer}\n")
    print("-" * 60)
    
    return answer


print("\n Ask your own questions (type 'quit' to exit):")
while True:
    user_query = input("\nYour question: ")
    if user_query.lower() in ['quit', 'exit', 'q']:
        break
    ask_question(user_query)