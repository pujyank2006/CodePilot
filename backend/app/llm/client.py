from google import genai
from google.genai import types

class LLMClient:
    def __init__(self, api_key: str, model: str, embedding_model: str = "gemini-embedding-001"):
        if not api_key:
            raise ValueError("Gemini API key is missing")

        self.model = model
        self.client = genai.Client(api_key = api_key)
        self.embedding_model = embedding_model

    async def generate(
            self,
            system_instruction: str,
            user_message: str,
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model = self.model,
            contents = user_message,
            config = types.GenerateContentConfig(
                system_instruction = system_instruction,
                temperature = 0.2
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty text"
            )

        return response.text.strip()

    async def embed(self, text: str):
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("Text to embed cannot be empty")

        response = await self.client.aio.models.embed_content(
            model = self.embedding_model,
            contents = cleaned_text
        )

        if not response.embeddings or not response.embeddings[0].values:
            raise RuntimeError("Gemini returned empty embeddings")

        return response.embeddings[0].values
    
    async def close(self):
        await self.client.aio.aclose()