import re
from pydantic import BaseModel
from app.schemas.retrieval import RetrievedChunk

class Citation(BaseModel):
    path: str
    start_line: int
    end_line: int
    raw_citation: str
    

class CitationService:
    CITATION_PATTERN = re.compile(
       r"\[source:\s*([^:\s]+):(\d+)-(\d+)\]"
    )
    
    @classmethod
    def extract_citations(cls, text: str) -> list[Citation]:
        citations: list[Citation] = []
        matches = cls.CITATION_PATTERN.findall(text)
        
        for path, start, end in matches:
            citations.append(
                Citation(
                    path = path.strip(),
                    start_line = int(start),
                    end_line = int(end),
                    raw_citation = f"[source: {path}: {start}-{end}]",
                )
            )
        return citations
    
    @classmethod
    def verify_citations(
        cls,
        citations: list[Citation],
        retrieved_chunks: list[RetrievedChunk],
    ) -> tuple[list[Citation], list[Citation]]:
        valid_paths = {chunk.path for chunk in retrieved_chunks}
        
        valid_citations: list[Citation] = []
        hallucinated_citations: list[Citation] = []
        
        for citation in citations:
            if any(citation.path.endswith(vp) or vp.endswith(citation.path) for vp in valid_paths):
                valid_citations.append(citation)
            else:
                hallucinated_citations.append(citation)
        
        return valid_citations, hallucinated_citations