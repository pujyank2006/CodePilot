from app.schemas.retrieval import RetrievedChunk
from app.services.citation_service import CitationService

def main():
    sample_text = (
        "The scanner reads ignore patterns [source: services/repository_scanner.py:30-50]. "
        "Also, authentication uses passwords [source: fake/secret.py:1-10]."
    )
    
    valid_chunk = RetrievedChunk(
        content = "code...",
        path = "services/repository_scanner.py",
        language = "python",
        start_line = 1,
        end_line = 60,
        score = 0.85
    )
    
    citations = CitationService.extract_citations(sample_text)
    print(f"Extracted {len(citations)} citations:")
    for c in citations:
        print(f" - {c.path} (Lines {c.start_line}-{c.end_line})")
        
    valid, hallucinated = CitationService.verify_citations(citations, [valid_chunk])
    print(f"\nValid Citations: {[c.path for c in valid]}")
    print(f"Hallucinated Citations: {[c.path for c in hallucinated]}")
    

if __name__ == "__main__":
    main()