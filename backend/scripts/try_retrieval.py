import asyncio
from app.config import settings
from app.llm.client import LLMClient
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore

async def test_query(service: RetrievalService, query: str, min_score: float):
    print("\n" + "=" * 70)
    print(f"QUERY: '{query}' (min_score = {min_score})")
    print("=" * 70)

    response = await service.retrieve(
        query = query,
        top_k = settings.rag_top_k,
        min_score = min_score
    )

    if not response.chunks:
        print(">> No relevant code chunks passed the score threshold.")
        return

    print(f"Selected {response.total_found} high-confidence chunk(s):")
    for idx, chunk in enumerate(response.chunks, start = 1):
        print(f"\n [{idx}] Score: {chunk.score:.4f} | {chunk.path}:{chunk.start_line}-{chunk.end_line} ({chunk.language})")

        first_lines = "\n".join(chunk.content.splitlines()[:3])
        print(f"    {first_lines}...")

async def main():

    llm_client = LLMClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        embedding_model=settings.gemini_embedding_model,
    )

    vector_store = VectorStore(
        location=settings.qdrant_path,
        collection_name=settings.qdrant_collection,
    )

    service = RetrievalService(llm_client=llm_client, vector_store=vector_store)

    await test_query(
        service=service,
        query="How does the repository scanner ignore files and folders?",
        min_score=settings.rag_min_score,
    )

    await test_query(
        service=service,
        query="What is the recipe for chocolate chip cookies?",
        min_score=settings.rag_min_score,
    )
    
    await llm_client.close()

if __name__ == "__main__":
    asyncio.run(main())