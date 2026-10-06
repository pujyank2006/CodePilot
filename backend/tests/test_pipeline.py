# This is a script to test the Repository Scanner + Code chunker pipeline.
import pytest
from pathlib import Path
from app.services.repository_scanner import RepositoryScanner
from app.services.code_chunker import CodeChunker


def test_scanner_to_chunker_pipeline(tmp_path):
    # 1. Create dummy repository structure
    (tmp_path / "main.py").write_text("print('hello')\nprint('world')")
    
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "utils.py").write_text("\n".join([f"line_{i} = {i}" for i in range(20)]))

    # 2. Run scanner
    scanner = RepositoryScanner()
    files = scanner.scan(tmp_path)
    assert len(files) == 2

    # 3. Feed scanner output into chunker
    chunker = CodeChunker(chunk_size=10, overlap=2)
    repo_chunks = []

    for rel_path in files:
        file_path = tmp_path / rel_path
        content = file_path.read_text(encoding="utf-8")
        chunks = chunker.chunk(content=content, path=rel_path, language="python")
        repo_chunks.extend(chunks)

    # 4. Assert chunk properties
    assert len(repo_chunks) > 0
    paths = {c.path for c in repo_chunks}
    assert "main.py" in paths
    assert "app/utils.py" in paths