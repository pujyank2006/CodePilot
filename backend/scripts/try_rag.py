import asyncio
from app.config import settings
from app.llm.client import LLMClient
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore


async def ask(rag_service: RAGService, question: str):
    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")
    print("=" * 70)

    result = await rag_service.answer_question(question)

    print("\n[AI ANSWER]:")
    print(result.answer)

    print("\n[SOURCES CITED]:")
    if not result.sources:
        print("  (No sources used)")
    else:
        for idx, src in enumerate(result.sources, start=1):
            print(f"  {idx}. {src.path} (Lines {src.start_line}-{src.end_line}) [Score: {src.score:.2f}]")


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
    retrieval_service = RetrievalService(
        llm_client=llm_client,
        vector_store=vector_store,
    )
    rag_service = RAGService(
        retrieval_service=retrieval_service,
        llm_client=llm_client,
    )

    # 1. Ask about scanner logic
    await ask(rag_service, "How does the scanner know which files to ignore?")

    # 2. Ask about chunking logic
    await ask(rag_service, "What parameters does the code chunker accept, and what are their defaults?")

    # 3. Ask an out-of-domain question
    await ask(rag_service, "What is the best way to cook pasta?")

    await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())