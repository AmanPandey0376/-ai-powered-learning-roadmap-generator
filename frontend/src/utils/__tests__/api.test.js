import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('API Integration Tests', () => {
  let mockAxiosInstance;
  let generateRoadmap, healthCheck, getApiConfig;

  beforeEach(async () => {
    // Create a mock axios instance
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
    
    // Clear all mocks
    vi.clearAllMocks();
    
    // Reset modules to ensure fresh import
    vi.resetModules();
    
    // Import the API functions after mocking
    const apiModule = await import('../api.js');
    generateRoadmap = apiModule.generateRoadmap;
    healthCheck = apiModule.healthCheck;
    getApiConfig = apiModule.getApiConfig;
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('generateRoadmap', () => {
    it('should successfully generate roadmap with valid skill data', async () => {
      const mockSkillData = {
        skill: 'React Development',
        level: 'beginner',
        timeframe: '3 months'
      };

      const mockResponse = {
        data: {
          roadmap: {
            title: 'React Development Learning Path',
            modules: [
              {
                id: '1',
                name: 'JavaScript Fundamentals',
                description: 'Learn core JavaScript concepts',
                miniProjects: [
                  {
                    id: '1-1',
                    name: 'Todo App',
                    description: 'Build a simple todo application',
                    estimatedHours: 8
                  }
                ]
              }
            ],
            majorProject: {
              id: 'major-1',
              name: 'E-commerce Website',
              description: 'Build a full-featured e-commerce site',
              requirements: ['React', 'State Management', 'API Integration'],
              estimatedHours: 40
            }
          },
          resources: {
            free: [
              {
                id: 'free-1',
                platform: 'YouTube',
                creator: 'Traversy Media',
                title: 'React Crash Course',
                link: 'https://youtube.com/watch?v=example',
                type: 'course'
              }
            ],
            paid: [
              {
                id: 'paid-1',
                platform: 'Udemy',
                creator: 'Maximilian Schwarzmüller',
                title: 'React - The Complete Guide',
                link: 'https://udemy.com/course/example',
                type: 'course'
              }
            ]
          }
        }
      };

      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await generateRoadmap(mockSkillData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', mockSkillData);
      expect(result).toEqual(mockResponse.data);
      expect(result.roadmap.title).toBe('React Development Learning Path');
      expect(result.roadmap.modules).toHaveLength(1);
      expect(result.resources.free).toHaveLength(1);
      expect(result.resources.paid).toHaveLength(1);
    });

    it('should handle network errors gracefully', async () => {
      const mockSkillData = { skill: 'Python' };
      const networkError = new Error('Network Error');
      networkError.code = 'ERR_NETWORK';

      mockAxiosInstance.post.mockRejectedValue(networkError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Network Error');
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', mockSkillData);
    });

    it('should handle timeout errors', async () => {
      const mockSkillData = { skill: 'JavaScript' };
      const timeoutError = new Error('Timeout');
      timeoutError.code = 'ECONNABORTED';

      mockAxiosInstance.post.mockRejectedValue(timeoutError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Timeout');
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', mockSkillData);
    });

    it('should handle 400 Bad Request errors', async () => {
      const mockSkillData = { skill: '' }; // Invalid empty skill
      const badRequestError = new Error('Bad Request');
      badRequestError.response = {
        status: 400,
        data: {
          message: 'Skill field is required'
        }
      };

      mockAxiosInstance.post.mockRejectedValue(badRequestError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Bad Request');
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', mockSkillData);
    });

    it('should handle 404 Not Found errors', async () => {
      const mockSkillData = { skill: 'NonexistentSkill' };
      const notFoundError = new Error('Not Found');
      notFoundError.response = {
        status: 404,
        data: {
          message: 'Skill not found in our database'
        }
      };

      mockAxiosInstance.post.mockRejectedValue(notFoundError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Not Found');
    });

    it('should handle 500 Internal Server Error', async () => {
      const mockSkillData = { skill: 'React' };
      const serverError = new Error('Internal Server Error');
      serverError.response = {
        status: 500,
        data: {
          message: 'Internal server error occurred'
        }
      };

      mockAxiosInstance.post.mockRejectedValue(serverError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Internal Server Error');
    });

    it('should handle 503 Service Unavailable errors', async () => {
      const mockSkillData = { skill: 'Vue.js' };
      const serviceUnavailableError = new Error('Service Unavailable');
      serviceUnavailableError.response = {
        status: 503,
        data: {
          message: 'Service temporarily unavailable'
        }
      };

      mockAxiosInstance.post.mockRejectedValue(serviceUnavailableError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Service Unavailable');
    });

    it('should handle 429 Rate Limit errors', async () => {
      const mockSkillData = { skill: 'Angular' };
      const rateLimitError = new Error('Too Many Requests');
      rateLimitError.response = {
        status: 429,
        data: {
          message: 'Rate limit exceeded'
        }
      };

      mockAxiosInstance.post.mockRejectedValue(rateLimitError);

      await expect(generateRoadmap(mockSkillData)).rejects.toThrow('Too Many Requests');
    });
  });

  describe('healthCheck', () => {
    it('should successfully perform health check', async () => {
      const mockHealthResponse = {
        data: {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          version: '1.0.0'
        }
      };

      mockAxiosInstance.get.mockResolvedValue(mockHealthResponse);

      const result = await healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockHealthResponse.data);
      expect(result.status).toBe('healthy');
    });

    it('should handle health check failures', async () => {
      const healthError = new Error('Health check failed');
      healthError.response = {
        status: 503,
        data: {
          status: 'unhealthy',
          message: 'Database connection failed'
        }
      };

      mockAxiosInstance.get.mockRejectedValue(healthError);

      await expect(healthCheck()).rejects.toThrow('Health check failed');
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
    });
  });

  describe('getApiConfig', () => {
    it('should return correct API configuration', () => {
      const config = getApiConfig();

      // Test that the function returns the expected structure
      expect(config).toHaveProperty('baseURL');
      expect(config).toHaveProperty('timeout');
      expect(config).toHaveProperty('environment');
      expect(config).toHaveProperty('isDevelopment');
      expect(config).toHaveProperty('isProduction');
      
      // Verify types
      expect(typeof config.baseURL).toBe('string');
      expect(typeof config.timeout).toBe('number');
      expect(typeof config.environment).toBe('string');
      expect(typeof config.isDevelopment).toBe('boolean');
      expect(typeof config.isProduction).toBe('boolean');
    });

    it('should use default values when environment variables are not set', () => {
      const originalEnv = import.meta.env;
      import.meta.env = {
        ...originalEnv,
        VITE_API_BASE_URL: undefined,
        VITE_API_TIMEOUT: undefined,
        MODE: 'test',
        DEV: false,
        PROD: false
      };

      const config = getApiConfig();

      expect(config.baseURL).toBe('/api');
      expect(config.timeout).toBe(30000);
      expect(config.environment).toBe('test');

      // Restore original env
      import.meta.env = originalEnv;
    });
  });
});