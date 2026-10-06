from pydantic import BaseModel, Field

class CodeChunk(BaseModel):
    content: str
    path: str
    language: str
    start_line: int
    end_line: int