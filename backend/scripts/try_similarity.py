import asyncio
from app.config import settings
from app.llm.client import LLMClient
from app.services.similarity import cosine_similarity

SNIPPETS = {
    "auth": """
def authenticate_user(username: str, password_hash: str) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    return verify_password(password_hash, user.hashed_password)
""",
    "database": """
def create_db_engine(connection_string: str):
    engine = create_engine(connection_string, pool_size=10, max_overflow=20)
    Base.metadata.create_all(bind=engine)
    return engine
""",
    "file_scanner": """
def is_ignored(path: str, ignore_patterns: list[str]) -> bool:
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
""",
}

async def main():
    client = LLMClient(
        api_key = settings.gemini_api_key,
        model = settings.gemini_model,
        embedding_model = settings.gemini_embedding_model,
    )

    print("Embedding code snippets...")
    snippet_embeddings = {}
    for name, code in SNIPPETS.items():
        snippet_embeddings[name] = await client.embed(code)

    queries = [
        "How do we verify a user's password?",
        "Where are SQL connection pools configured?",
        "How to exclude files using ignore patterns?"
    ]

    for query in queries:
        print("\n" + "=" * 60)
        print(f"Query: '{query}'")
        print("=" * 60)

        query_embedding = await client.embed(query)

        scores = []
        for name, embedding in snippet_embeddings.items():
            score = cosine_similarity(query_embedding, embedding)
            scores.append((name, score))

        scores.sort(key = lambda item: item[1], reverse = True)

        for rank, (name, score) in enumerate(scores, start = 1):
            marker = "<-- TOP MATCH" if rank == 1 else ""
            print(f"    {rank}. [{name:12s}] Similarity: {score: .4f} {marker}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
