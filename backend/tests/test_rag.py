import pytest
from app.schemas.retrieval import RetrievalResponse, RetrievedChunk
from app.services.rag_prompt_builder import RAGPromptBuilder
from app.services.rag_service import RAGService


class MockLLMClient:
    """Mock LLM client that records received prompts and returns a canned answer."""
    def __init__(self, reply: str = "This is a grounded answer."):
        self.reply = reply
        self.last_system_instruction = None
        self.last_user_message = None

    async def generate(self, system_instruction: str, user_message: str) -> str:
        self.last_system_instruction = system_instruction
        self.last_user_message = user_message
        return self.reply


class MockRetrievalService:
    """Mock retrieval service returning predefined RetrievalResponse."""
    def __init__(self, response: RetrievalResponse):
        self.response = response
        self.last_query = None

    async def retrieve(self, query: str, **kwargs) -> RetrievalResponse:
        self.last_query = query
        return self.response


@pytest.fixture
def sample_chunk():
    return RetrievedChunk(
        content="def calculate_total(): return 100",
        path="services/billing.py",
        language="python",
        start_line=10,
        end_line=12,
        score=0.85,
    )


def test_prompt_builder_formats_context(sample_chunk):
    """Ensure prompt builder formats chunks with file paths, lines, and fences."""
    user_prompt = RAGPromptBuilder.build_user_prompt(
        query="Where is billing handled?",
        chunks=[sample_chunk],
    )

    assert "File: services/billing.py (Lines 10-12)" in user_prompt
    assert "def calculate_total(): return 100" in user_prompt
    assert "Where is billing handled?" in user_prompt


def test_prompt_builder_empty_chunks():
    """Ensure empty chunk list formats a safe fallback message."""
    formatted = RAGPromptBuilder.format_context([])
    assert formatted == "No relevant codebase context found."


@pytest.mark.anyio
async def test_empty_query_returns_early():
    """Empty queries must return early without calling the LLM."""
    mock_llm = MockLLMClient()
    mock_retrieval = MockRetrievalService(
        RetrievalResponse(query="", chunks=[], total_found=0)
    )
    rag_service = RAGService(retrieval_service=mock_retrieval, llm_client=mock_llm)

    result = await rag_service.answer_question("   ")

    assert result.answer == "Please provide a valid question."
    assert result.sources == []
    assert mock_llm.last_user_message is None  # LLM was never called


@pytest.mark.anyio
async def test_fast_fallback_when_no_chunks_found():
    """When no chunks pass similarity threshold, return fallback without calling LLM."""
    mock_llm = MockLLMClient()
    mock_retrieval = MockRetrievalService(
        RetrievalResponse(query="make pizza", chunks=[], total_found=0)
    )
    rag_service = RAGService(retrieval_service=mock_retrieval, llm_client=mock_llm)

    result = await rag_service.answer_question("How do I make pizza?")

    assert "cannot find sufficient information" in result.answer
    assert result.sources == []
    assert mock_llm.last_user_message is None  # Verified: Zero wasted LLM tokens


@pytest.mark.anyio
async def test_grounded_answer_generation(sample_chunk):
    """When chunks are retrieved, LLM is called and citations are returned."""
    mock_llm = MockLLMClient(reply="Billing is handled in calculate_total.")
    mock_retrieval = MockRetrievalService(
        RetrievalResponse(query="billing query", chunks=[sample_chunk], total_found=1)
    )
    rag_service = RAGService(retrieval_service=mock_retrieval, llm_client=mock_llm)

    result = await rag_service.answer_question("Where is billing handled?")

    assert result.answer == "Billing is handled in calculate_total."
    assert len(result.sources) == 1
    assert result.sources[0].path == "services/billing.py"
    assert "calculate_total" in mock_llm.last_user_message