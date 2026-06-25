import time
from sentence_transformers import SentenceTransformer

print("Loading model...")
start = time.time()
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print(f"Model loaded in: {time.time() - start:.2f}s")

print("\nEncoding first query...")
start = time.time()
emb1 = model.encode("test query 1")
print(f"First encoding took: {time.time() - start:.2f}s")

print("\nEncoding second query...")
start = time.time()
emb2 = model.encode("test query 2")
print(f"Second encoding took: {time.time() - start:.2f}s")
