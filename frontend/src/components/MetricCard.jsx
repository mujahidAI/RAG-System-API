/**
 * MetricCard - Displays a single evaluation metric with score and progress bar.
 * Props: name, score (0-1), description
 */

export function MetricCard({ name, score, description }) {
  const percentage = Math.round(score * 100);

  // Determine color based on score
  const getColorClass = () => {
    if (score > 0.7) return 'bg-green-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getColorClassLight = () => {
    if (score > 0.7) return 'bg-green-100';
    if (score >= 0.4) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className={`${getColorClassLight()} rounded-xl p-6 shadow-sm border border-gray-200`}>
      {/* Metric Name */}
      <h3 className="text-lg font-semibold text-gray-800 mb-2">
        {name}
      </h3>

      {/* Score */}
      <div className="flex items-end gap-2 mb-3">
        <span className="text-4xl font-bold text-gray-900">
          {percentage}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
        <div
          className={`h-full ${getColorClass()} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600">
        {description}
      </p>
    </div>
  );
}
