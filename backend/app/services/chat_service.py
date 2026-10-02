from app.config import settings
from app.llm.client import LLMClient

SYSTEM_INSTRUCTIONS = """
You are CodePilot, an AI coding assistant.

Your responsibilities:
- Explain programming concepts clearly.
- Help users understand and debug code.
- Provide accurate and practical programming guidance.
- Use simple examples when helpful.
- Do not claim to have executed code unless a
  tool has actually executed it.
"""

class ChatService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def send_message(self, user_message: str) -> str:

        response = await self.llm_client.generate(
            system_instruction = SYSTEM_INSTRUCTIONS,
            user_message = user_message
        )

        return response

llm_client = LLMClient(
    api_key = settings.gemini_api_key,
    model = settings.gemini_model
)

chat_service = ChatService(llm_client = llm_client)