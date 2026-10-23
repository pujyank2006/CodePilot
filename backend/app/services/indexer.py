import asyncio
from pathlib import Path
from typing import Any
from app.llm.client import LLMClient
from app.schemas.code_chunk import CodeChunk
from app.services.code_chunker import CodeChunker
from app.services.repository_scanner import RepositoryScanner
from app.services.vector_store import VectorStore

# Skipped for now, takes more time in CPU
# from app.llm.local_embeddings import LocalEmbeddingClient

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
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".yaml": "yaml",
        ".yml": "yaml"
    }
    return mapping.get(ext, "text")

class RepositoryIndexer:
    def __init__(
            self,
            scanner: RepositoryScanner,
            chunker: CodeChunker,
            llm_client: LLMClient,
            vector_store: VectorStore
    ):
        self.scanner = scanner
        self.chunker = chunker
        self.llm_client = llm_client
        self.vector_store = vector_store

    async def index_repository(self, repository_path: str | Path) -> int:
        root = Path(repository_path).resolve()
        relative_files = self.scanner.scan(root)
        print(f"[Indexer] Discoverd {len(relative_files)} files to index.")

        all_chunks: list[CodeChunk] = []

        for rel_path in relative_files:
            file_path = root / rel_path
            try:
                content = file_path.read_text(encoding = "utf-8", errors = "replace")
            except Exception as e:
                print(f"[Indexer] Skipping {rel_path} due to read error: {e}")
                continue

            language = detect_language(rel_path)
            file_chunks = self.chunker.chunk(
                content = content,
                path = rel_path,
                language = language
            )
            all_chunks.extend(file_chunks)

        print(f"[Indexer] Generated {len(all_chunks)} code chunks. Generating embeddings...")

        if not all_chunks:
            return 0

        embeddings: list[list[float]] = []
        for idx, chunk in enumerate(all_chunks, start = 1):
            if idx % 5 == 0 or idx == len(all_chunks):
                print(f"[Indexer] Embedding chunk {idx}/{len(all_chunks)}...")

            text_to_embed = f"File: {chunk.path}\nLanguage: {chunk.language}\n\n{chunk.content}"
            vector = await self.llm_client.embed(text_to_embed)
            embeddings.append(vector)

            await asyncio.sleep(1.0)

        print("[Indexer] Persisting vectors and metadata into Qdrant...")
        self.vector_store.upsert_chunks(chunks = all_chunks, embeddings=embeddings)
        print(f"[Indexer] Successfully indexed and persisted {len(all_chunks)} chunks.")

        return len(all_chunks)

    async def search(
            self,
            query: str,
            limit: int = 5,
            filter_language: str | None = None,
    ) -> list[dict[str, Any]]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        query_vector = await self.llm_client.embed(cleaned_query)
        return self.vector_store.search(
            query_vector = query_vector,
            limit = limit,
            filter_language = filter_language
        )
