/**
 * Ingest.jsx - Document ingestion page.
 * Route "/ingest" - allows uploading files or specifying directory path.
 */

import { useState, useRef } from 'react';
import { ingestDirectory, ingestFiles } from '../api/client';

const ACCEPTED_TYPES = ['.txt', '.pdf', '.docx', '.html'];

export function Ingest() {
  const [activeTab, setActiveTab] = useState('files');
  const [directoryPath, setDirectoryPath] = useState('');
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Handle file selection
  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const validFiles = selectedFiles.filter((file) => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      return ACCEPTED_TYPES.includes(ext);
    });
    setFiles((prev) => [...prev, ...validFiles]);
    setError(null);
    setResult(null);
  };

  // Remove file from list
  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // Handle drag and drop
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    const validFiles = droppedFiles.filter((file) => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      return ACCEPTED_TYPES.includes(ext);
    });
    setFiles((prev) => [...prev, ...validFiles]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Submit directory path
  const handleDirectorySubmit = async () => {
    if (!directoryPath.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await ingestDirectory(directoryPath.trim());
      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to ingest directory');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit files
  const handleFilesSubmit = async () => {
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await ingestFiles(formData);
      setResult(response);
      setFiles([]);
    } catch (err) {
      setError(err.message || 'Failed to upload files');
    } finally {
      setIsLoading(false);
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Ingest Documents</h1>
        <p className="text-gray-600 mt-1">
          Upload documents or specify a directory path to add content to the RAG system
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => {
            setActiveTab('files');
            setError(null);
            setResult(null);
          }}
          className={`px-4 py-2 font-medium transition-colors duration-200 ${
            activeTab === 'files'
              ? 'border-b-2 border-accent text-accent'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Upload Files
        </button>
        <button
          onClick={() => {
            setActiveTab('directory');
            setError(null);
            setResult(null);
          }}
          className={`px-4 py-2 font-medium transition-colors duration-200 ${
            activeTab === 'directory'
              ? 'border-b-2 border-accent text-accent'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Directory Path
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'files' ? (
        <div className="space-y-4">
          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-accent hover:bg-gray-50 transition-all duration-200"
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={ACCEPTED_TYPES.join(',')}
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="text-gray-500">
              <p className="text-lg mb-2">Drag and drop files here</p>
              <p className="text-sm">or click to browse</p>
              <p className="text-xs mt-2 text-gray-400">
                Accepted: {ACCEPTED_TYPES.join(', ')}
              </p>
            </div>
          </div>

          {/* Selected Files List */}
          {files.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="p-3 bg-gray-50 border-b border-gray-200">
                <span className="font-medium text-gray-700">
                  Selected Files ({files.length})
                </span>
              </div>
              <ul className="divide-y divide-gray-100">
                {files.map((file, index) => (
                  <li
                    key={index}
                    className="px-4 py-3 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-gray-700 truncate max-w-xs">
                        {file.name}
                      </span>
                      <span className="text-sm text-gray-400">
                        {formatFileSize(file.size)}
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700 transition-colors duration-200"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleFilesSubmit}
            disabled={files.length === 0 || isLoading}
            className="w-full px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Directory Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Directory Path
            </label>
            <input
              type="text"
              value={directoryPath}
              onChange={(e) => setDirectoryPath(e.target.value)}
              placeholder="e.g., /path/to/documents or C:\documents"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200"
            />
          </div>

          {/* Submit Button */}
          <button
            onClick={handleDirectorySubmit}
            disabled={!directoryPath.trim() || isLoading}
            className="w-full px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? 'Processing...' : 'Ingest Directory'}
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="mt-6 flex items-center justify-center gap-3 text-gray-500">
          <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
          <span>Processing documents...</span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 text-red-600 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="mt-6 p-4 bg-green-50 text-green-700 rounded-lg border border-green-200">
          <p className="font-medium">Success!</p>
          <p className="mt-1">
            Processed {result.documents_loaded || result.files_processed || 0} files,
            created {result.documents_indexed || result.chunks_created || 0} chunks
          </p>
        </div>
      )}
    </div>
  );
}
