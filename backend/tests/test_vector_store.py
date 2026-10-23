import pytest
from app.schemas.code_chunk import CodeChunk
from app.services.vector_store import VectorStore


@pytest.fixture
def memory_vector_store():
    """Provides a fresh, isolated in-memory VectorStore for each test."""
    return VectorStore(
        location=":memory:",
        collection_name="test_codebase",
        vector_size=4,
    )


def test_upsert_mismatch_raises_error(memory_vector_store):
    """Ensure a ValueError is raised if chunk count doesn't match embeddings count."""
    chunks = [
        CodeChunk(
            content="print('hello')",
            path="main.py",
            language="python",
            start_line=1,
            end_line=1,
        )
    ]
    # Passing 2 vectors for 1 chunk must fail
    embeddings = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]

    with pytest.raises(ValueError, match="Chunks and embeddings count must match"):
        memory_vector_store.upsert_chunks(chunks=chunks, embeddings=embeddings)


def test_upsert_and_search_retrieves_top_match(memory_vector_store):
    """Ensure search ranks by vector similarity and preserves source payload."""
    chunk_a = CodeChunk(
        content="def auth(): pass",
        path="auth.py",
        language="python",
        start_line=1,
        end_line=1,
    )
    chunk_b = CodeChunk(
        content="def db_connect(): pass",
        path="db.py",
        language="python",
        start_line=1,
        end_line=1,
    )

    # Chunk A points along axis 0; Chunk B points along axis 1
    embeddings = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
    ]

    memory_vector_store.upsert_chunks(chunks=[chunk_a, chunk_b], embeddings=embeddings)

    # Query vector is very close to Chunk A
    query_vector = [0.95, 0.05, 0.0, 0.0]
    results = memory_vector_store.search(query_vector=query_vector, limit=2)

    assert len(results) == 2
    # Chunk A should be Rank 1
    top_match = results[0]
    assert top_match["payload"]["path"] == "auth.py"
    assert top_match["payload"]["content"] == "def auth(): pass"
    assert top_match["payload"]["start_line"] == 1
    assert top_match["score"] > results[1]["score"]


def test_search_with_metadata_filtering(memory_vector_store):
    """Ensure metadata filtering restricts results to specific languages."""
    chunk_py = CodeChunk(
        content="print('python')",
        path="script.py",
        language="python",
        start_line=1,
        end_line=1,
    )
    chunk_js = CodeChunk(
        content="console.log('js')",
        path="index.js",
        language="javascript",
        start_line=1,
        end_line=1,
    )

    # Identical vectors for both
    vector = [1.0, 0.0, 0.0, 0.0]
    memory_vector_store.upsert_chunks(
        chunks=[chunk_py, chunk_js],
        embeddings=[vector, vector],
    )

    # Search with language="javascript" filter
    results = memory_vector_store.search(
        query_vector=[1.0, 0.0, 0.0, 0.0],
        limit=5,
        filter_language="javascript",
    )

    # Only JavaScript should be returned despite Python having an identical vector score
    assert len(results) == 1
    assert results[0]["payload"]["language"] == "javascript"
    assert results[0]["payload"]["path"] == "index.js"


def test_upsert_is_idempotent(memory_vector_store):
    """Ensure re-indexing the same chunk updates it instead of creating duplicates."""
    chunk = CodeChunk(
        content="version 1",
        path="app.py",
        language="python",
        start_line=1,
        end_line=5,
    )
    memory_vector_store.upsert_chunks(
        chunks=[chunk],
        embeddings=[[1.0, 0.0, 0.0, 0.0]],
    )

    # Upsert again with updated content at the same path and lines
    updated_chunk = CodeChunk(
        content="version 2",
        path="app.py",
        language="python",
        start_line=1,
        end_line=5,
    )
    memory_vector_store.upsert_chunks(
        chunks=[updated_chunk],
        embeddings=[[1.0, 0.0, 0.0, 0.0]],
    )

    # Search should return only 1 point, updated with "version 2"
    results = memory_vector_store.search(
        query_vector=[1.0, 0.0, 0.0, 0.0],
        limit=5,
    )
    assert len(results) == 1
    assert results[0]["payload"]["content"] == "version 2"