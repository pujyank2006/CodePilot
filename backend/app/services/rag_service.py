from app.config import settings
from app.llm.client import LLMClient
from app.schemas.rag import RAGAnswer
from app.services.rag_prompt_builder import (
    RAG_SYSTEM_INSTRUCTION,
    RAGPromptBuilder
)
from app.services.retrieval_service import RetrievalService

class RAGService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_client: LLMClient
    ):
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client
    
    async def answer_question(
        self,
        query: str,
        top_k: int = settings.rag_top_k,
        min_score: float = settings.rag_min_score,
        filter_language: str | None = None
    ) -> RAGAnswer:
        cleaned_query = query.strip()
        if not cleaned_query:
            return RAGAnswer(
                query = "",
                answer = "Please provide a valid question.",
                sources = []
            )
        
        retrieval_response = await self.retrieval_service.retrieve(
            query = cleaned_query,
            top_k = top_k,
            min_score = min_score,
            filter_language = filter_language
        )
        
        if not retrieval_response.chunks:
            return RAGAnswer(
                query = cleaned_query,
                answer = "Based on the currently indexed codebase, I cannot find sufficient information to answer this question.",
                sources = []
            )

        user_prompt = RAGPromptBuilder.build_user_prompt(
            query = cleaned_query,
            chunks = retrieval_response.chunks
        )
        
        generated_answer = await self.llm_client.generate(
            system_instruction = RAG_SYSTEM_INSTRUCTION,
            user_message = user_prompt
        )
        
        return RAGAnswer(
            query = cleaned_query,
            answer = generated_answer,
            sources = retrieval_response.chunks
        )