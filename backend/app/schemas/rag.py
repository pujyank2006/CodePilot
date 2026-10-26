from pydantic import BaseModel
from app.schemas.retrieval import RetrievedChunk

class RAGAnswer(BaseModel):
    query: str
    answer: str
    sources: list[RetrievedChunk]