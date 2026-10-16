import asyncio
from app.config import settings
from app.llm.client import LLMClient

async def main():
    client = LLMClient(
        api_key = settings.gemini_api_key,
        model = settings.gemini_model,
        embedding_model = settings.gemini_embedding_model
    )

    sample_code = "def add(a: int, b: int) -> int:\n    return a + b"
    vector = await client.embed(sample_code)

    print(f"Embedding successful!")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 dimensions: {vector[:5]}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())