from pydantic import BaseModel, Field

class RetrievedChunk(BaseModel):
    content: str
    path: str
    language: str
    start_line: int
    end_line: int
    score: float = Field(..., description = "Cosine similarity score (0.0 to 1.0)")

class RetrievalResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
    total_found: int