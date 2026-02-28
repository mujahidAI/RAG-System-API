/**
 * SourceCard - Displays a single retrieved source document.
 * Props: source (object with page_content, metadata)
 */

import { useState } from 'react';

export function SourceCard({ source }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const filename = source.metadata?.source_file || 'Unknown source';
  const content = source.page_content || '';
  const displayContent = isExpanded ? content : content.substring(0, 200);
  const needsTruncation = content.length > 200;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 transition-all duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded">
          {filename}
        </span>
        {needsTruncation && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-accent hover:text-accent-hover transition-colors duration-200"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>

      {/* Content */}
      <p className="text-sm text-gray-600 whitespace-pre-wrap">
        {displayContent}
        {!isExpanded && needsTruncation && '...'}
      </p>
    </div>
  );
}
