from pydantic import BaseModel, Field

class RetrievedChunk(BaseModel):
    content: str
    path: str
    language: str
    start_line: str
    end_line: str
    score: float = Field(..., description = "Cosine similarity score (0.0 to 1.0)")

class RetrievalResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
    total_found: int