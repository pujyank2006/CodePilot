import asyncio
from pathlib import Path
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

    scanner = RepositoryScanner()
    chunker = CodeChunker(chunk_size = 40, overlap = 8)

    vector_store = VectorStore(
        location = settings.qdrant_path,
        collection_name = settings.qdrant_collection
    )

    indexer = RepositoryIndexer(
        scanner = scanner,
        chunker = chunker,
        llm_client = llm_client,
        vector_store = vector_store
    )

    target_dir = Path(r"D:\FSD\wp_project")
    print(f"Starting indexing for: {target_dir}")

    total = await indexer.index_repository(target_dir)
    print(f"\nDone! Total indexed chunks: {total}")

    await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())
