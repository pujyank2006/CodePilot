from app.llm.client import LLMClient
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.services.vector_store import VectorStore

class RetrievalService:
    def __init__(
            self,
            llm_client: LLMClient,
            vector_store: VectorStore,
    ):
        self.llm_client = llm_client
        self.vector_store = vector_store

    async def retrieve(
            self,
            query: str,
            top_k: int = 5,
            filter_language: str | None = None
    ) -> RetrievalResponse:
        cleaned_query = query.strip()
        if not cleaned_query:
            return RetrievalResponse(query = "", chunks = [], total_found = 0)

        query_vector = await self.llm_client.embed(cleaned_query)

        raw_results = self.vector_store.search(
            query_vector = query_vector,
            limit = top_k,
            filter_language = filter_language
        )

        retrieved_chunks: list[RetrievedChunk] = []
        for item in raw_results:
            payload = item["payload"]

            retrieved_chunks.append(
                RetrievedChunk(
                    content = payload["content"],
                    path = payload["path"],
                    language = payload["language"],
                    start_line = payload["start_line"],
                    end_line = payload["end_line"],
                    score = item["score"]
                )
            )

        return RetrievalResponse(
            query = cleaned_query,
            chunks = retrieved_chunks,
            total_found = len(retrieved_chunks)
        )