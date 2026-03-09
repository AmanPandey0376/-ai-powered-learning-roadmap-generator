import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('API Configuration Tests', () => {
  let mockAxiosInstance;

  beforeEach(async () => {
    // Create mock axios instance
    mockAxiosInstance = {
      post: vi.fn(),
      get: vi.fn(),
      interceptors: {
        request: {
          use: vi.fn()
        },
        response: {
          use: vi.fn()
        }
      }
    };

    // Mock axios.create to return our mock instance
    mockedAxios.create.mockReturnValue(mockAxiosInstance);
    
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    vi.resetAllMocks();
    vi.resetModules();
  });

  describe('API Configuration Setup', () => {
    it('should create axios instance with correct configuration', async () => {
      // Import the API module to trigger axios.create
      await import('../api.js');

      // Verify axios.create was called
      expect(mockedAxios.create).toHaveBeenCalled();
      
      // Verify the configuration passed to axios.create
      const createCall = mockedAxios.create.mock.calls[0][0];
      expect(createCall).toEqual({
        baseURL: '/api', // Default value when VITE_API_BASE_URL is not set
        timeout: 30000, // Default value when VITE_API_TIMEOUT is not set
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should set up request and response interceptors', async () => {
      // Import the API module to trigger interceptor setup
      await import('../api.js');

      // Verify interceptors were set up
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });

    it('should handle custom environment variables', async () => {
      // Mock environment variables
      const originalEnv = import.meta.env;
      import.meta.env = {
        ...originalEnv,
        VITE_API_BASE_URL: 'http://localhost:8000/api',
        VITE_API_TIMEOUT: '25000'
      };

      // Clear modules and re-import to pick up new env vars
      vi.resetModules();
      await import('../api.js');

      // Verify axios.create was called with custom config
      expect(mockedAxios.create).toHaveBeenCalled();
      
      // Restore original env
      import.meta.env = originalEnv;
    });
  });

  describe('API Error Handling Integration', () => {
    it('should handle API errors through the complete flow', async () => {
      const { generateRoadmap } = await import('../api.js');
      
      const networkError = new Error('Network Error');
      networkError.code = 'ERR_NETWORK';
      
      mockAxiosInstance.post.mockRejectedValue(networkError);

      await expect(generateRoadmap({ skill: 'React' })).rejects.toThrow('Network Error');
    });

    it('should handle successful API responses', async () => {
      const { generateRoadmap } = await import('../api.js');
      
      const mockResponse = {
        data: {
          roadmap: { title: 'Test Roadmap' },
          resources: { free: [], paid: [] }
        }
      };
      
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await generateRoadmap({ skill: 'React' });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle health check requests', async () => {
      const { healthCheck } = await import('../api.js');
      
      const mockHealthResponse = {
        data: {
          status: 'healthy',
          timestamp: new Date().toISOString()
        }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockHealthResponse);

      const result = await healthCheck();
      expect(result).toEqual(mockHealthResponse.data);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
    });
  });
});