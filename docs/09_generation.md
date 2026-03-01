# Generation

## What It Does

Generates natural language answers by combining retrieved context with user question via LLM. Includes source citations and fallback for insufficient context.

## Why It Exists

Without generation, retrieval only returns documents. The LLM synthesizes information into a readable answer with citations—making the system useful for end users.

## How It Fits In

```
[Retriever] → Top docs → [Reranker] → Top-3 → [Generator]
                                                        ↓
                                              [Prompt Template]
                                                        ↓
                                                      [LLM]
                                                        ↓
                                            Answer + Sources
```

## Key Design Decisions

- **Cite sources**: Prompt instructs LLM to include `[Source: filename]`
- **"I don't know" fallback**: If context is insufficient, LLM is instructed to say so
- **LCEL chain**: Enables future extensibility (retries, fallbacks)

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `LLM_PROVIDER` | ollama | LLM backend |
| `OLLAMA_MODEL` | mistral | Model name |
| `LLM_TEMPERATURE` | 0.1 | Creativity vs determinism |
| `LLM_MAX_TOKENS` | 512 | Max response length |

## Code Walkthrough

`src/generation/generator.py` - `Generator.generate()`:
```python
def generate(self, query: str) -> dict:
    # 1. Transform query (if enabled)
    transformed_queries = [query]
    if self.query_transformer:
        transformed_queries = self.query_transformer.transform(query)
    
    # 2. Retrieve and rerank
    all_docs = []
    for q in transformed_queries:
        docs = self.retriever.retrieve(q)
        all_docs.extend(docs)
    final_docs = self._deduplicate_documents(all_docs)
    
    # 3. Re-rank if enabled
    if self.reranker:
        reranked = self.reranker.rerank(query, final_docs)
        final_docs = [doc for doc, score in reranked]
    
    # 4. Generate
    context = format_context(final_docs)
    answer = self.chain.invoke({"context": context, "question": query})
    return {"answer": answer, "sources": format_sources(final_docs)}
```

Prompt in `src/generation/prompt_templates.py`:
```python
ANSWER_GENERATION_TEMPLATE = '''Answer based on the context.
If insufficient, say "I don't know."
Cite sources as [Source: filename].

Context: {context}
Question: {question}'''
```

## Common Errors & Fixes

- **Error**: LLM not responding
  - Fix: Check Ollama running: `ollama list`

- **Error**: Context too long
  - Fix: Reduce `RERANKER_TOP_K` or chunk size

- **Error**: No citations in answer
  - Fix: Check prompt includes citation instruction; verify metadata present

## Related Files

- `src/generation/generator.py` - Generator class
- `src/generation/prompt_templates.py` - All prompts
- `src/utils/config.py` - LLMSettings
