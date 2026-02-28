/**
 * API client for communicating with the FastAPI backend.
 * Uses axios with interceptors for request/response handling.
 */

import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - log requests in development
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    console.error('[API Error]', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

/**
 * Send a question to the RAG system and get an answer.
 * @param {string} question - The question to ask
 * @param {boolean} useHyde - Whether to use HyDE query transformation
 * @param {boolean} useMultiQuery - Whether to use multi-query expansion
 * @returns {Promise<Object>} - The answer and source documents
 */
export async function queryRAG(question, useHyde = false, useMultiQuery = false) {
  const response = await apiClient.post('/query', {
    question,
    use_hyde: useHyde,
    use_multi_query: useMultiQuery,
  });
  return response.data;
}

/**
 * Ingest documents from a directory path.
 * @param {string} directoryPath - Path to the directory containing documents
 * @returns {Promise<Object>} - Ingestion result
 */
export async function ingestDirectory(directoryPath) {
  const response = await apiClient.post('/ingest', {
    directory_path: directoryPath,
  });
  return response.data;
}

/**
 * Ingest documents via file upload.
 * @param {FormData} formData - FormData containing files
 * @returns {Promise<Object>} - Ingestion result
 */
export async function ingestFiles(formData) {
  const response = await apiClient.post('/ingest/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

/**
 * Run the RAG evaluation.
 * @returns {Promise<Object>} - Evaluation metrics
 */
export async function runEvaluation() {
  const response = await apiClient.post('/evaluate');
  return response.data;
}

/**
 * Check the backend health status.
 * @returns {Promise<Object>} - Health status
 */
export async function checkHealth() {
  const response = await apiClient.get('/health');
  return response.data;
}

export default apiClient;
