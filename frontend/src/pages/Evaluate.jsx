/**
 * Evaluate.jsx - Evaluation results page.
 * Route "/evaluate" - displays RAG evaluation metrics.
 */

import { useState } from 'react';
import { runEvaluation } from '../api/client';
import { MetricCard } from '../components/MetricCard';

const METRIC_DESCRIPTIONS = {
  'Faithfulness': 'Measures how factually accurate the answer is based on the retrieved context.',
  'Answer Relevancy': 'Measures how relevant the generated answer is to the asked question.',
  'Context Precision': 'Measures how precise the retrieved context is for answering the question.',
  'Context Recall': 'Measures how much of the relevant information was retrieved.',
};

export function Evaluate() {
  const [isLoading, setIsLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [hasRunEvaluation, setHasRunEvaluation] = useState(false);

  const handleEvaluate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await runEvaluation();
      
      // Handle both possible response formats
      setMetrics({
        faithfulness: result.metrics?.faithfulness ?? result.faithfulness ?? 0,
        answer_relevancy: result.metrics?.answer_relevancy ?? result.answer_relevancy ?? 0,
        context_precision: result.metrics?.context_precision ?? result.context_precision ?? 0,
        context_recall: result.metrics?.context_recall ?? result.context_recall ?? 0,
      });
      setHasRunEvaluation(true);
    } catch (err) {
      setError(err.message || 'Failed to run evaluation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Evaluate</h1>
        <p className="text-gray-600 mt-1">
          Evaluate the RAG pipeline performance using RAGAS metrics
        </p>
      </div>

      {/* Evaluate Button */}
      <div className="mb-8">
        <button
          onClick={handleEvaluate}
          disabled={isLoading}
          className="px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? 'Running Evaluation...' : 'Run Evaluation'}
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600">
            Running evaluation... This may take 30-60 seconds.
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-lg border border-red-200 mb-6">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!hasRunEvaluation && !isLoading && !metrics && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-lg">
            <div className="text-4xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              No Evaluation Yet
            </h2>
            <p className="text-gray-600">
              Click "Run Evaluation" to assess the RAG pipeline's performance.
              The evaluation measures retrieval quality and answer accuracy.
            </p>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      {metrics && !isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            name="Faithfulness"
            score={metrics.faithfulness}
            description={METRIC_DESCRIPTIONS['Faithfulness']}
          />
          <MetricCard
            name="Answer Relevancy"
            score={metrics.answer_relevancy}
            description={METRIC_DESCRIPTIONS['Answer Relevancy']}
          />
          <MetricCard
            name="Context Precision"
            score={metrics.context_precision}
            description={METRIC_DESCRIPTIONS['Context Precision']}
          />
          <MetricCard
            name="Context Recall"
            score={metrics.context_recall}
            description={METRIC_DESCRIPTIONS['Context Recall']}
          />
        </div>
      )}
    </div>
  );
}
