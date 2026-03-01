# Evaluation

## What It Does

Measures pipeline quality using RAGAS metrics: faithfulness, answer relevancy, context precision, and context recall. Outputs scores as percentages with color-coded indicators.

## Why It Exists

Without metrics, there's no way to measure if the system is improving or degrading. Evaluation quantifies retrieval precision, generation accuracy, and overall RAG quality.

## How It Fits In

```
[User Questions] → [Generator] → Answers + Contexts
                                               ↓
                                    [RAGEvaluator]
                                               ↓
                              Metrics: Faithfulness, Relevancy, Precision, Recall
```

## Key Design Decisions

- **4 core metrics**: Covers both retrieval and generation aspects
- **Percentage display**: More intuitive than raw scores
- **Color coding**: Green (>70%), yellow (40-70%), red (<40%)

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `EVAL_DATASET_SIZE` | 20 | Q&A pairs for evaluation |
| `EVAL_OUTPUT_PATH` | data/eval_report.json | Report save location |

## Code Walkthrough

`src/evaluation/evaluator.py` - `RAGEvaluator.evaluate()`:
```python
def evaluate(self, questions: list[str]) -> dict:
    results = []
    for question in questions:
        result = self.generator.generate(question)
        results.append({
            "question": question,
            "answer": result["answer"],
            "contexts": [s["content"] for s in result["sources"]],
        })
    metrics = self._calculate_metrics(results)
    return {"results": results, "metrics": metrics}
```

`src/evaluation/eval_dataset.py` - generates test questions from document topics.

## Common Errors & Fixes

- **Error**: Evaluation takes very long
  - Fix: Normal for LLM calls; reduce `EVAL_DATASET_SIZE`

- **Error**: All scores are zero
  - Fix: Check documents are ingested; check LLM is working

- **Error**: No ground truth available
  - Fix: System uses self-evaluation; not as accurate as human-labeled data

## Related Files

- `src/evaluation/evaluator.py` - RAGEvaluator class
- `src/evaluation/eval_dataset.py` - Test question generation
- `src/api/routes/evaluate.py` - API endpoint
