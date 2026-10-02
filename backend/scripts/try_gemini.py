import asyncio

from app.config import settings
from app.llm.client import LLMClient

async def main():
    llm = LLMClient(
        api_key = settings.gemini_api_key,
        model = settings.gemini_model
    )

    try:
        response = await llm.generate(
            system_instruction = (
                "You are CodePilot, an AI coding assistant. "
                "Explain programming concepts simply."
            ),
            user_message = (
                "Explain Python decorators in 3 sentences."
            )
        )

        print("\nGemini's response\n")
        print(response)
    finally:
        await llm.close()

if __name__ == "__main__":
    asyncio.run(main())