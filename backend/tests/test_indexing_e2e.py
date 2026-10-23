import pytest
from app.services.code_chunker import CodeChunker
from app.services.indexer import RepositoryIndexer
from app.services.repository_scanner import RepositoryScanner
from app.services.vector_store import VectorStore


class MockLLMClient:
    """Mock LLM client that produces deterministic 4D vectors for testing without APIs."""
    async def embed(self, text: str) -> list[float]:
        # Simple semantic simulation based on keywords
        text_lower = text.lower()
        if "password" in text_lower or "auth" in text_lower:
            return [1.0, 0.0, 0.0, 0.0]  # Auth vector
        elif "database" in text_lower or "sql" in text_lower:
            return [0.0, 1.0, 0.0, 0.0]  # Database vector
        return [0.0, 0.0, 0.1, 0.1]      # Neutral vector

    async def close(self):
        pass


@pytest.mark.anyio
async def test_full_indexing_and_retrieval_pipeline(tmp_path):
    # 1. Arrange: Create a realistic miniature project structure
    auth_dir = tmp_path / "auth"
    auth_dir.mkdir()
    (auth_dir / "login.py").write_text(
        "def verify_password(hash: str, pwd: str):\n"
        "    return hash == pwd\n"
    )

    db_dir = tmp_path / "db"
    db_dir.mkdir()
    (db_dir / "connection.py").write_text(
        "def get_database_pool():\n"
        "    return 'sql_connection_pool'\n"
    )

    # 2. Instantiate all real pipeline components
    scanner = RepositoryScanner()
    chunker = CodeChunker(chunk_size=10, overlap=2)
    mock_llm = MockLLMClient()
    vector_store = VectorStore(
        location=":memory:",
        collection_name="test_pipeline",
        vector_size=4,
    )

    indexer = RepositoryIndexer(
        scanner=scanner,
        chunker=chunker,
        llm_client=mock_llm,
        vector_store=vector_store,
    )

    # 3. Act: Run the indexing pipeline on the directory
    total_indexed = await indexer.index_repository(tmp_path)
    assert total_indexed == 2

    # 4. Act: Query the vector store for auth-related code
    query_vector = await mock_llm.embed("How to check password authentication?")
    results = vector_store.search(query_vector=query_vector, limit=1)

    # 5. Assert: Verify the top retrieved code chunk is the exact auth snippet
    assert len(results) == 1
    top_match = results[0]
    payload = top_match["payload"]

    assert payload["path"] == "auth/login.py"
    assert "verify_password" in payload["content"]
    assert payload["language"] == "python"
    assert payload["start_line"] == 1
    assert payload["end_line"] == 2