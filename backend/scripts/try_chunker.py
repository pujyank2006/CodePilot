from app.services.code_chunker import CodeChunker


content = """line 1
line 2
line 3
line 4
line 5
line 6
line 7
line 8
line 9
line 10
line 11
line 12"""


chunker = CodeChunker(
    chunk_size=5,
    overlap=2,
)

chunks = chunker.chunk(
    content=content,
    path="example.py",
    language="python",
)

for chunk in chunks:
    print(
        f"{chunk.path} "
        f"[lines {chunk.start_line}-{chunk.end_line}]"
    )
    print(chunk.content)
    print("-" * 40)