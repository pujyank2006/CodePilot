import uuid
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.schemas.code_chunk import CodeChunk

class VectorStore:
    def __init__(
            self,
            location: str = "./qdrant_data",
            collection_name: str = "codebase",
            vector_size: int = 768,
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size

        if location == ":memory":
            self.client = QdrantClient(location = ":memory:")
        else:
            self.client = QdrantClient(path = location)

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections_response = self.client.get_collections()
        existing_names = [c.name for c in collections_response.collections]

        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config = models.VectorParams(
                    size = self.vector_size,
                    distance = models.Distance.COSINE
                ),
            )

    def upsert_chunks(
            self,
            chunks: list[CodeChunk],
            embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count must watch")

        if not chunks:
            return

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"))

            payload = {
                "content": chunk.content,
                "path": chunk.path,
                "language": chunk.language,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line
            }

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name = self.collection_name,
            points = points
        )

    def search(
            self,
            query_vector: list[float],
            limit: int = 5,
            filter_language: str | None = None,
    ) -> list[dict[str, Any]]:
        query_filter = None
        if filter_language:
            query_filter = models.Filter(
                must = [
                    models.FieldCondition(
                        key = "language",
                        match = models.MatchValue(value = filter_language)
                    )
                ]
            )

        search_result = self.client.query_points(
            collection_name = self.collection_name,
            query = query_vector,
            limit = limit,
            query_filter = query_filter
        )

        results = []
        for point in search_result.points:
            results.append({
                "id": point.id,
                "score": point.score,
                "payload": point.payload
            })
        return results