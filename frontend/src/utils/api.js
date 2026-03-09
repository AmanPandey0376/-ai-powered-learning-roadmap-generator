import axios from 'axios';

// Get configuration from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000;

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Create a user-friendly error object
    const userError = {
      ...error,
      userMessage: getUserFriendlyErrorMessage(error),
      isRetryable: isRetryableError(error)
    };
    
    return Promise.reject(userError);
  }
);

// Helper function to generate user-friendly error messages
const getUserFriendlyErrorMessage = (error) => {
  // Network/Connection errors
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'The request took too long to complete. Please check your internet connection and try again.';
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }
    return 'Network error. Please check your internet connection and try again.';
  }

  // Server errors (5xx)
  if (error.response.status >= 500) {
    if (error.response.status === 503) {
      return 'The service is temporarily unavailable. Please try again in a few minutes.';
    }
    return 'We\'re experiencing technical difficulties. Please try again later.';
  }

  // Client errors (4xx)
  if (error.response.status >= 400) {
    const serverMessage = error.response.data?.message || error.response.data?.error;
    
    switch (error.response.status) {
      case 400:
        return serverMessage || 'Invalid request. Please check your input and try again.';
      case 401:
        return 'Authentication required. Please refresh the page and try again.';
      case 403:
        return 'Access denied. You don\'t have permission to perform this action.';
      case 404:
        return 'The requested resource was not found. Please try again.';
      case 429:
        return 'Too many requests. Please wait a moment before trying again.';
      default:
        return serverMessage || 'Request failed. Please check your input and try again.';
    }
  }

  // Fallback for unknown errors
  return 'An unexpected error occurred. Please try again.';
};

// Helper function to determine if an error is retryable
const isRetryableError = (error) => {
  // Network errors are generally retryable
  if (!error.response) {
    return true;
  }

  // Server errors (5xx) are retryable
  if (error.response.status >= 500) {
    return true;
  }

  // Rate limiting is retryable after a delay
  if (error.response.status === 429) {
    return true;
  }

  // Client errors (4xx) are generally not retryable
  return false;
};

// API methods
export const generateRoadmap = async (skillData) => {
  try {
    const response = await api.post('/roadmap', skillData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Health check endpoint for development
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Get API configuration info (useful for debugging)
export const getApiConfig = () => {
  return {
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    environment: import.meta.env.MODE,
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
  };
};

export default api;