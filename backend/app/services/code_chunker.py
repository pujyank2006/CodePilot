from app.schemas.code_chunk import CodeChunk

class CodeChunker:
    def __init__(self, chunk_size: int = 50, overlap: int = 10):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
            self,
            content: str,
            path: str,
            language: str,
    ) -> list[CodeChunk]:
        lines = content.splitlines()

        if not lines:
            return []

        chunks = []

        step = self.chunk_size - self.overlap
        start = 0

        while start < len(lines):
            end = min(start + self.chunk_size, len(lines))

            chunk_content = "\n".join(lines[start:end])

            chunks.append(
                CodeChunk(
                    content = chunk_content,
                    path = path,
                    language = language,
                    start_line = start + 1,
                    end_line = end
                )
            )

            if end >= len(lines):
                break
        
            start += step
        return chunks