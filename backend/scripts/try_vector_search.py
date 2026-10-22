import asyncio
from app.config import settings
from app.llm.client import LLMClient
from app.services.vector_store import VectorStore

async def search_codebase(query: str, limit: int = 3, filter_language: str | None = None):
    llm_client = LLMClient(
        api_key = settings.gemini_api_key,
        model = settings.gemini_model,
        embedding_model = settings.gemini_embedding_model
    )

    vector_store = VectorStore(
        location = settings.qdrant_path,
        collection_name = settings.qdrant_collection
    )

    print(f"\nSearching for: '{query}' (filter_language = {filter_language})")
    query_vector = await llm_client.embed(query)

    results = vector_store.search(
        query_vector = query_vector,
        limit = limit,
        filter_language = filter_language
    )

    for rank, res in enumerate(results, start=1):
        payload = res["payload"]
        print(f"\n--- Match #{rank} (Cosine Similarity: {res['score']:.4f}) ---")
        print(f"File: {payload['path']} [lines {payload['start_line']}-{payload['end_line']}]")
        print("Code Preview:")
        preview = payload["content"][:200]
        print(preview + ("..." if len(payload["content"]) > 200 else ""))

    await llm_client.close()

async def main():
    # await search_codebase("Trace what happens when a user searches for a book, from the search input to the displayed results.")
    # await search_codebase("Which features are implemented, and which are still placeholders?")
    await search_codebase("Where does the app call the public book catalog to get search results?")

if __name__ == "__main__":
    asyncio.run(main())