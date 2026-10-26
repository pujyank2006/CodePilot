from app.schemas.retrieval import RetrievedChunk
from app.services.rag_prompt_builder import RAGPromptBuilder

def main():
    sample_chunk = RetrievedChunk(
        content="def get_db():\n    return SessionLocal()",
        path="app/database.py",
        language="python",
        start_line=15,
        end_line=16,
        score=0.82
    )
    
    prompt = RAGPromptBuilder.build_user_prompt(
        query = "How is the database session obtained?",
        chunks = [sample_chunk]
    )
    
    print("=== SYSTEM INSTRUCTION ===")
    from app.services.rag_prompt_builder import RAG_SYSTEM_INSTRUCTION
    print(RAG_SYSTEM_INSTRUCTION)
    
    print("=== GENERATED USER PROMPT ===")
    print(prompt)
    

if __name__ == "__main__":
    main()