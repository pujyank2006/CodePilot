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
            top_k: int = 4,
            min_score: float = 0.0,
            filter_language: str | None = None,
            max_characters: int | None = None
    ) -> RetrievalResponse:
        cleaned_query = query.strip()
        if not cleaned_query:
            return RetrievalResponse(query = "", chunks = [], total_found = 0)

        query_vector = await self.llm_client.embed(cleaned_query)

        fetch_limit = max(top_k * 2, 10)
        raw_results = self.vector_store.search(
            query_vector = query_vector,
            limit = fetch_limit,
            filter_language = filter_language
        )

        selected_chunks: list[RetrievedChunk] = []
        total_chars = 0

        for item in raw_results:
            score = item["score"]
            if score < min_score:
                continue
        
            payload = item["payload"]

            chunk = RetrievedChunk(
                    content = payload["content"],
                    path = payload["path"],
                    language = payload["language"],
                    start_line = payload["start_line"],
                    end_line = payload["end_line"],
                    score = score
                )

            if max_characters and (total_chars + len(chunk.content) > max_characters):
                break

            selected_chunks.append(chunk)
            total_chars += len(chunk.content)

            if len(selected_chunks) >= top_k:
                break

        return RetrievalResponse(
            query = cleaned_query,
            chunks = selected_chunks,
            total_found = len(selected_chunks)
        )