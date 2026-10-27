from app.schemas.retrieval import RetrievedChunk

RAG_SYSTEM_INSTRUCTION = """\
You are CodePilot, an expert codebase engineering assistant.

Your task is to answer technical questions about a software repository using ONLY the retrieved code snippets provided in the prompt.

Guidelines:
1. Grounding: Answer strictly using facts and implementations found in the retrieved snippets. Do not speculate or assume nonexistent code.
2. Inline Citations: Every time you reference a function, variable, logic, or fact from a snippet, include an explicit inline citation in this exact format:
   [source: <file_path>:<start_line>-<end_line>]
   Example: "Files are filtered using PathSpec patterns [source: app/services/repository_scanner.py:24-45]."
3. Code Clarity: When providing code examples, match the existing style and conventions of the repository.
4. Insufficient Context: If the provided snippets do not contain enough information to answer the question accurately, explicitly state:
   "Based on the currently indexed codebase, I cannot find sufficient information to answer this question."
"""

class RAGPromptBuilder:
    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant codebase context found."

        formatted_sections = []
        for idx, chunk in enumerate(chunks, start = 1):
            header = f"--- [Snippet #{idx}] File: {chunk.path} (Lines {chunk.start_line}-{chunk.end_line}) | Relevance: {chunk.score:.2f} ---"
            code_fence = f"```{chunk.language}\n{chunk.content}\n```"
            formatted_sections.append(f"{header}\n{code_fence}")

        return "\n\n".join(formatted_sections)

    @classmethod
    def build_user_prompt(cls, query: str, chunks: list[RetrievedChunk]) -> str:
        context_block = cls.format_context(chunks)

        return f"""\
### Retrieved Codebase Context:
{context_block}
### Developer Question:
{query}
Answer the developer question accurately based on the context above."""