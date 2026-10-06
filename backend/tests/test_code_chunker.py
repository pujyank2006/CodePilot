import pytest
from app.services.code_chunker import CodeChunker


def test_init_validations():
    """Verify that invalid initialization parameters raise a ValueError."""
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        CodeChunker(chunk_size=0)

    with pytest.raises(ValueError, match="overlap cannot be negative"):
        CodeChunker(chunk_size=10, overlap=-1)

    with pytest.raises(ValueError, match="overlap must be smaller than chunk_size"):
        CodeChunker(chunk_size=10, overlap=10)


def test_empty_content_returns_empty_list():
    """Verify that empty string content produces no chunks."""
    chunker = CodeChunker(chunk_size=5, overlap=1)
    chunks = chunker.chunk(content="", path="empty.py", language="python")
    assert chunks == []


def test_content_smaller_than_chunk_size():
    """Verify files with fewer lines than chunk_size create a single chunk."""
    content = "line 1\nline 2\nline 3"
    chunker = CodeChunker(chunk_size=10, overlap=2)
    chunks = chunker.chunk(content=content, path="small.py", language="python")

    assert len(chunks) == 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 3
    assert chunks[0].path == "small.py"
    assert chunks[0].language == "python"
    assert chunks[0].content == content


def test_chunking_with_overlap():
    """Verify sliding line window math and metadata accuracy across multiple chunks."""
    lines = [f"line {i}" for i in range(1, 11)]
    content = "\n".join(lines)

    chunker = CodeChunker(chunk_size=5, overlap=2)
    chunks = chunker.chunk(content=content, path="demo.py", language="python")

    # Step size: 5 - 2 = 3 lines
    # Chunk 0: lines 1..5 (slice 0..5)
    # Chunk 1: lines 4..8 (slice 3..8)
    # Chunk 2: lines 7..10 (slice 6..10)
    assert len(chunks) == 3

    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 5
    assert chunks[0].content == "\n".join(lines[0:5])

    assert chunks[1].start_line == 4
    assert chunks[1].end_line == 8
    assert chunks[1].content == "\n".join(lines[3:8])

    assert chunks[2].start_line == 7
    assert chunks[2].end_line == 10
    assert chunks[2].content == "\n".join(lines[6:10])


def test_exact_chunk_boundary():
    """Verify chunking when total lines perfectly divide by chunk size without overlap."""
    lines = [f"line {i}" for i in range(1, 11)]
    content = "\n".join(lines)

    chunker = CodeChunker(chunk_size=5, overlap=0)
    chunks = chunker.chunk(content=content, path="exact.py", language="python")

    assert len(chunks) == 2
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 5
    assert chunks[1].start_line == 6
    assert chunks[1].end_line == 10