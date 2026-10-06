# This is a script to test the Repository Scanner + Code chunker pipeline.
from pathlib import Path

from app.services.repository_scanner import RepositoryScanner
from app.services.code_chunker import CodeChunker

def detect_language(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".json": "json",
        ".md": "markdown",
        ".css": "css",
        ".html": "html"
    }

    return mapping.get(ext, "text")

def run_pipeline(repo_path: str):
    root = Path(repo_path).resolve()
    scanner = RepositoryScanner()
    chunker = CodeChunker(chunk_size = 30, overlap = 5)

    relative_paths = scanner.scan(root)
    print(f"Scanned {len(relative_paths)} files from {root}\n")

    all_chunks = []

    for rel_path in relative_paths:
        full_path = root / rel_path

        try:
            content = full_path.read_text(encoding = "utf-8", errors = "replace")
        except Exception as e:
            print(f"Skipping {rel_path} due to errors: {e}")
            continue

        language = detect_language(rel_path)
        chunks = chunker.chunk(
            content = content,
            path = rel_path,
            language = language
        )
        all_chunks.extend(chunks)

    print(f"Total Chunks Generated: {len(all_chunks)}")
    print("=" * 50)

    for chunk in all_chunks[:3]:
        print(f"File: {chunk.path} [{chunk.language}] (Lines {chunk.start_line}-{chunk.end_line})")
        print(chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content)
        print("-" * 50)

if __name__ == "__main__":
    repo_root = r"D:\FSD\Hyperlocal-Marketplace"
    run_pipeline(str(repo_root))