/**
 * Chat.jsx - Main Q&A chat interface.
 * Default route "/" - displays chat messages and input for questions.
 */

import { useState, useRef, useEffect } from 'react';
import { SourceCard } from '../components/SourceCard';
import { queryRAG } from '../api/client';

// Example questions for empty state
const EXAMPLE_QUESTIONS = [
  "What is quantum mechanics?",
  "What was the Renaissance?",
  "How do neural networks learn?",
  "What are exoplanets?",
];

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 p-4 bg-white rounded-lg shadow-sm border border-gray-200 max-w-md">
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
    </div>
  );
}

export function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useHyde, setUseHyde] = useState(false);
  const [useMultiQuery, setUseMultiQuery] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput('');
    setError(null);

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: question },
    ]);

    setIsLoading(true);

    try {
      const response = await queryRAG(question, useHyde, useMultiQuery);

      // Add assistant message with answer and sources
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.source_documents || [],
          latency_ms: response.latency_ms,
        },
      ]);
    } catch (err) {
      setError(err.message || 'Failed to get response');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '',
          error: err.message || 'Failed to get response',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleExampleClick = (question) => {
    setInput(question);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-48px)]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
        <p className="text-gray-600 mt-1">Ask questions about your documents</p>
      </div>

      {/* Toggle Options */}
      <div className="flex gap-6 mb-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useHyde}
            onChange={(e) => setUseHyde(e.target.checked)}
            className="w-4 h-4 text-accent rounded focus:ring-accent"
          />
          <span className="text-sm text-gray-700">Use HyDE</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useMultiQuery}
            onChange={(e) => setUseMultiQuery(e.target.checked)}
            className="w-4 h-4 text-accent rounded focus:ring-accent"
          />
          <span className="text-sm text-gray-700">Use Multi-Query</span>
        </label>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {/* Empty State */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-lg">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Welcome to RAG Chat
              </h2>
              <p className="text-gray-600 mb-6">
                Ask questions about your documents and get AI-powered answers with source citations.
              </p>
              <p className="text-sm text-gray-500 mb-4">Try asking:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {EXAMPLE_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleExampleClick(q)}
                    className="px-3 py-2 text-sm bg-gray-100 hover:bg-accent hover:text-white rounded-lg transition-colors duration-200"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl ${
                msg.role === 'user'
                  ? 'bg-accent text-white px-4 py-3 rounded-2xl'
                  : 'bg-white text-gray-900 px-4 py-3 rounded-2xl shadow-sm border border-gray-200'
              }`}
            >
              {/* Error Message */}
              {msg.error ? (
                <div className="text-red-500 p-2">
                  Error: {msg.error}
                </div>
              ) : (
                <>
                  {/* Answer Content */}
                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  {/* Latency Badge */}
                  {msg.latency_ms !== undefined && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <span className="text-xs text-gray-500">
                        {(msg.latency_ms / 1000).toFixed(2)}s
                      </span>
                    </div>
                  )}

                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-200">
                      <details className="group">
                        <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-accent transition-colors duration-200">
                          Sources ({msg.sources.length})
                        </summary>
                        <div className="mt-3 space-y-2">
                          {msg.sources.map((source, sidx) => (
                            <SourceCard key={sidx} source={source} />
                          ))}
                        </div>
                      </details>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <TypingIndicator />
          </div>
        )}

        {/* Error Display */}
        {error && !isLoading && (
          <div className="flex justify-center">
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg border border-red-200">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          disabled={isLoading}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
