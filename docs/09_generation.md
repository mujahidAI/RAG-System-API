# Generation

## What This Component Does

Generates answers using LLM with retrieved context, including source citations.

## Why It's Needed

- Provides natural language answers
- Grounds responses in retrieved context
- Includes citations for verification

## Key Design Decisions

1. **Prompt**: Instructs LLM to cite sources
2. **Fallback**: Says "I don't know" if insufficient context
3. **LCEL Chain**: Query transform | Retrieve | Re-rank | Prompt | LLM

## Code Walkthrough

See `src/generation/generator.py`:

```python
chain = prompt | llm
answer = chain.invoke({"context": context, "question": query})
```

See `src/generation/prompt_templates.py`:

```
Answer only based on the provided context.
Cite sources using [Source: filename]
Say "I don't know" if insufficient context.
```

## Connection to Other Components

- Input: Re-ranked documents + question
- Output: Answer + sources to API
