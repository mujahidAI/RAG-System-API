# Evaluation

## What This Component Does

Evaluates RAG pipeline using RAGAS metrics: faithfulness, answer relevancy, context precision, context recall.

## Why It's Needed

- Quantifies pipeline quality
- Identifies weaknesses
- Guides improvements

## Key Design Decisions

1. **RAGAS**: Industry-standard RAG evaluation
2. **Metrics**: Faithfulness, Relevancy, Precision, Recall
3. **Dataset**: 20 Q&A pairs from documents

## Code Walkthrough

See `src/evaluation/evaluator.py`:

```python
metrics = {
    "faithfulness": score,
    "answer_relevancy": score,
    "context_precision": score,
    "context_recall": score,
}
```

## Connection to Other Components

- Input: Questions, generator
- Output: Metrics report to API
