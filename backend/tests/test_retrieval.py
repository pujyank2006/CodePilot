import pytest
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.services.retrieval_service import RetrievalService


class DummyLLMClient:
    """Offline mock LLM client returning a dummy 4D vector."""
    async def embed(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0, 0.0]


class DummyVectorStore:
    """Offline mock vector store returning predefined search points."""
    def __init__(self, sample_points: list[dict]):
        self.sample_points = sample_points
        self.last_query_filter_language = None

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        filter_language: str | None = None,
    ) -> list[dict]:
        self.last_query_filter_language = filter_language
        # Filter points by language if specified
        results = self.sample_points
        if filter_language:
            results = [p for p in results if p["payload"]["language"] == filter_language]
        return results[:limit]


@pytest.fixture
def mock_points():
    """Provides 3 mock search results with descending similarity scores."""
    return [
        {
            "id": "1",
            "score": 0.85,
            "payload": {
                "content": "def authenticate(): return True",
                "path": "auth.py",
                "language": "python",
                "start_line": 1,
                "end_line": 5,
            },
        },
        {
            "id": "2",
            "score": 0.65,
            "payload": {
                "content": "def connect_db(): return 'db'",
                "path": "db.py",
                "language": "python",
                "start_line": 10,
                "end_line": 15,
            },
        },
        {
            "id": "3",
            "score": 0.42,  # Low-confidence distractor
            "payload": {
                "content": "console.log('unrelated')",
                "path": "index.js",
                "language": "javascript",
                "start_line": 1,
                "end_line": 3,
            },
        },
    ]


@pytest.mark.anyio
async def test_empty_query_returns_empty_response(mock_points):
    """Empty or whitespace queries must return immediately without searching."""
    service = RetrievalService(
        llm_client=DummyLLMClient(),
        vector_store=DummyVectorStore(mock_points),
    )
    result = await service.retrieve(query="   ")
    assert result.total_found == 0
    assert result.chunks == []


@pytest.mark.anyio
async def test_top_k_limits_results(mock_points):
    """Retriever must respect the top_k parameter limit."""
    service = RetrievalService(
        llm_client=DummyLLMClient(),
        vector_store=DummyVectorStore(mock_points),
    )
    result = await service.retrieve(query="test query", top_k=2)
    assert result.total_found == 2
    assert len(result.chunks) == 2
    assert result.chunks[0].score == 0.85
    assert result.chunks[1].score == 0.65


@pytest.mark.anyio
async def test_min_score_filters_noise(mock_points):
    """Chunks below min_score must be discarded."""
    service = RetrievalService(
        llm_client=DummyLLMClient(),
        vector_store=DummyVectorStore(mock_points),
    )
    # Filter with min_score=0.60 -> Chunk #3 (0.42) must be excluded
    result = await service.retrieve(query="test query", top_k=5, min_score=0.60)
    assert result.total_found == 2
    assert all(chunk.score >= 0.60 for chunk in result.chunks)
    assert "index.js" not in [c.path for c in result.chunks]


@pytest.mark.anyio
async def test_max_characters_budget(mock_points):
    """Retrieval must stop once the accumulated character budget is reached."""
    service = RetrievalService(
        llm_client=DummyLLMClient(),
        vector_store=DummyVectorStore(mock_points),
    )
    # The first chunk content is 31 chars. Budgeting 35 chars allows only 1 chunk.
    result = await service.retrieve(query="test query", top_k=5, max_characters=35)
    assert result.total_found == 1
    assert result.chunks[0].path == "auth.py"


@pytest.mark.anyio
async def test_language_filtering(mock_points):
    """Retriever must pass filter_language through to the vector store."""
    vector_store = DummyVectorStore(mock_points)
    service = RetrievalService(
        llm_client=DummyLLMClient(),
        vector_store=vector_store,
    )
    result = await service.retrieve(
        query="test query",
        top_k=5,
        filter_language="javascript",
    )
    assert vector_store.last_query_filter_language == "javascript"
    assert result.total_found == 1
    assert result.chunks[0].language == "javascript"