from sentence_transformers import SentenceTransformer

class LocalEmbeddingClient:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Text to embed cannot be empty")

        vector = self.model.encode(text, normalize_embeddings = True)
        return vector.tolist()