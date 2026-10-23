import asyncio
from app.config import settings
from app.llm.client import LLMClient
from app.services.code_chunker import CodeChunker
from app.services.indexer import RepositoryIndexer
from app.services.repository_scanner import RepositoryScanner
from app.services.vector_store import VectorStore


async def main():
    llm_client = LLMClient(
        api_key = settings.gemini_api_key,
        model = settings.gemini_model,
        embedding_model = settings.gemini_embedding_model
    )

    indexer = RepositoryIndexer(
        scanner = RepositoryScanner(),
        chunker = CodeChunker(),
        llm_client = llm_client,
        vector_store = VectorStore(
            location = settings.qdrant_path,
            collection_name = settings.qdrant_collection
        )
    )


    import sys
    from pathlib import Path
    app_dir = Path(__file__).parent.parent / "app"
    await indexer.index_repository(app_dir)


    # Test questions
    questions = [
        "Where are LLM requests and embeddings created?",
        "How are files and folders excluded or ignored?",
        "Where is the Pydantic schema for code chunks defined?",
    ]

    for q in questions:
        print("\n" + "=" * 60)
        print(f"Query: {q}")
        print("=" * 60)
        results = await indexer.search(q, limit=2)
        for rank, res in enumerate(results, start=1):
            payload = res["payload"]
            print(f"  #{rank} [Score: {res['score']:.4f}] {payload['path']} (lines {payload['start_line']}-{payload['end_line']})")
    
    await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())