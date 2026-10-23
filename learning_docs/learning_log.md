# Day 1 Learning Log

## Learned

1. Differences between traditional ML and LLMs
2. Tokens
3. Context window
4. Inference
5. Temperature
6. Structured output

## Questions I still have

1. If an entire repo cannot fit into a context window, how can this issue be solved? You mentioned retrieval — what is it?
2. Structured output sits between an LLM and a tool call. Does this matter only during the tool-calling stage?

## Answers to today's quiz

### Questions
1. Why does an LLM need no retraining for a new task, and what does a traditional model need instead?
2. Explain the inference loop in two sentences.
3. Why can't you measure a code chunk's size in lines for context-budgeting?
4. What competes for space inside the context window besides your question?
5. Why is temperature near 0 usually right for an agent that calls tools?

### Answers
1. Retraining an LLM is a huge and expensive task. LLMs use this method called inference where it uses it's training to generate the next possible token based on the input. This is done in a loop where each generated token is attached to the input and the next token is generated based on the current attachment.
2. where each generated token is attached to the input and the next token is generated based on the current attachment.
3. can't remember
4. code generated, previous output
5. yes


---

# Week 1 Capstone (Days 5–7) Learning Log

## Learned
- **High-Dimensional Embeddings**: Text and code are projected into 3072-dimensional geometric space where conceptual similarity equals directional alignment.
- **Cosine Similarity**: Measures vector direction independent of text length (\(\cos \theta = \frac{A \cdot B}{\|A\| \|B\|}\)).
- **Vector Indexing & Qdrant**: Why brute-force linear search fails at scale and how Approximate Nearest Neighbor (ANN) vector databases provide fast top-K retrieval.
- **Context Enrichment**: Embedding raw code lines alone loses file context; prefixing chunks with file path and language significantly improves semantic retrieval precision.
- **Idempotency**: Using deterministic UUID hashing prevents duplicate vectors during re-indexing.

## Built
- `app/services/similarity.py`: Pure Python vector cosine similarity calculator.
- `app/services/vector_store.py`: Qdrant vector store with metadata filtering and idempotent upserts.
- `app/services/indexer.py`: End-to-end repository indexer with unified search.
- Automated end-to-end test suite (`test_indexing_e2e.py`, `test_vector_store.py`, `test_similarity.py`).

## What I can explain without AI
- The entire path a source file takes from disk into a vector database.
- Why overlap is required when chunking code.
- How to search a codebase semantically using natural language questions.
