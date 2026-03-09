import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock axios completely for integration testing
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('API Integration End-to-End Tests', () => {
  let mockAxiosInstance;
  let generateRoadmap, healthCheck;

  beforeEach(async () => {
    mockAxiosInstance = {
      post: vi.fn(),
      get: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    };

    mockedAxios.create.mockReturnValue(mockAxiosInstance);
    vi.clearAllMocks();
    vi.resetModules();
    
    // Import the API functions after mocking
    const apiModule = await import('../api.js');
    generateRoadmap = apiModule.generateRoadmap;
    healthCheck = apiModule.healthCheck;
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Complete Roadmap Generation Flow', () => {
    it('should handle complete successful roadmap generation workflow', async () => {
      const skillInput = {
        skill: 'Full Stack JavaScript Development',
        level: 'intermediate',
        timeframe: '6 months'
      };

      const completeRoadmapResponse = {
        data: {
          roadmap: {
            title: 'Full Stack JavaScript Development Learning Path',
            modules: [
              {
                id: 'mod-1',
                name: 'Advanced JavaScript Concepts',
                description: 'Master closures, prototypes, and async programming',
                miniProjects: [
                  {
                    id: 'proj-1-1',
                    name: 'Promise-based HTTP Client',
                    description: 'Build a custom HTTP client using Promises',
                    estimatedHours: 12
                  },
                  {
                    id: 'proj-1-2',
                    name: 'Event-driven Architecture Demo',
                    description: 'Create a pub-sub system',
                    estimatedHours: 8
                  }
                ]
              },
              {
                id: 'mod-2',
                name: 'Node.js Backend Development',
                description: 'Build scalable server-side applications',
                miniProjects: [
                  {
                    id: 'proj-2-1',
                    name: 'RESTful API with Express',
                    description: 'Create a complete REST API',
                    estimatedHours: 16
                  },
                  {
                    id: 'proj-2-2',
                    name: 'Database Integration',
                    description: 'Connect API to MongoDB',
                    estimatedHours: 10
                  }
                ]
              },
              {
                id: 'mod-3',
                name: 'React Frontend Development',
                description: 'Build modern user interfaces',
                miniProjects: [
                  {
                    id: 'proj-3-1',
                    name: 'Component Library',
                    description: 'Create reusable UI components',
                    estimatedHours: 20
                  },
                  {
                    id: 'proj-3-2',
                    name: 'State Management with Redux',
                    description: 'Implement complex state management',
                    estimatedHours: 14
                  }
                ]
              }
            ],
            majorProject: {
              id: 'major-proj-1',
              name: 'Social Media Platform',
              description: 'Build a complete social media application with real-time features',
              requirements: [
                'User authentication and authorization',
                'Real-time messaging with WebSockets',
                'File upload and media handling',
                'Responsive design',
                'API rate limiting',
                'Database optimization'
              ],
              estimatedHours: 80
            }
          },
          resources: {
            free: [
              {
                id: 'free-1',
                platform: 'freeCodeCamp',
                creator: 'freeCodeCamp Team',
                title: 'JavaScript Algorithms and Data Structures',
                link: 'https://freecodecamp.org/learn/javascript-algorithms-and-data-structures/',
                type: 'course'
              },
              {
                id: 'free-2',
                platform: 'YouTube',
                creator: 'Traversy Media',
                title: 'Node.js Crash Course',
                link: 'https://youtube.com/watch?v=fBNz5xF-Kx4',
                type: 'tutorial'
              },
              {
                id: 'free-3',
                platform: 'React Docs',
                creator: 'React Team',
                title: 'React Official Documentation',
                link: 'https://react.dev/',
                type: 'documentation'
              }
            ],
            paid: [
              {
                id: 'paid-1',
                platform: 'Udemy',
                creator: 'Jonas Schmedtmann',
                title: 'The Complete JavaScript Course 2024',
                link: 'https://udemy.com/course/the-complete-javascript-course/',
                type: 'course'
              },
              {
                id: 'paid-2',
                platform: 'Pluralsight',
                creator: 'Kyle Simpson',
                title: 'Advanced JavaScript',
                link: 'https://pluralsight.com/courses/advanced-javascript',
                type: 'course'
              },
              {
                id: 'paid-3',
                platform: 'Frontend Masters',
                creator: 'Scott Moss',
                title: 'Complete Intro to React',
                link: 'https://frontendmasters.com/courses/complete-react-v8/',
                type: 'course'
              }
            ]
          }
        }
      };

      mockAxiosInstance.post.mockResolvedValue(completeRoadmapResponse);

      const result = await generateRoadmap(skillInput);

      // Verify API call
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', skillInput);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);

      // Verify response structure
      expect(result).toEqual(completeRoadmapResponse.data);
      
      // Verify roadmap structure
      expect(result.roadmap.title).toBe('Full Stack JavaScript Development Learning Path');
      expect(result.roadmap.modules).toHaveLength(3);
      expect(result.roadmap.majorProject).toBeDefined();
      
      // Verify modules structure
      result.roadmap.modules.forEach(module => {
        expect(module).toHaveProperty('id');
        expect(module).toHaveProperty('name');
        expect(module).toHaveProperty('description');
        expect(module).toHaveProperty('miniProjects');
        expect(Array.isArray(module.miniProjects)).toBe(true);
      });

      // Verify mini projects structure
      const firstModule = result.roadmap.modules[0];
      expect(firstModule.miniProjects).toHaveLength(2);
      firstModule.miniProjects.forEach(project => {
        expect(project).toHaveProperty('id');
        expect(project).toHaveProperty('name');
        expect(project).toHaveProperty('description');
        expect(project).toHaveProperty('estimatedHours');
        expect(typeof project.estimatedHours).toBe('number');
      });

      // Verify major project structure
      const majorProject = result.roadmap.majorProject;
      expect(majorProject).toHaveProperty('id');
      expect(majorProject).toHaveProperty('name');
      expect(majorProject).toHaveProperty('description');
      expect(majorProject).toHaveProperty('requirements');
      expect(majorProject).toHaveProperty('estimatedHours');
      expect(Array.isArray(majorProject.requirements)).toBe(true);
      expect(majorProject.requirements.length).toBeGreaterThan(0);

      // Verify resources structure
      expect(result.resources).toHaveProperty('free');
      expect(result.resources).toHaveProperty('paid');
      expect(Array.isArray(result.resources.free)).toBe(true);
      expect(Array.isArray(result.resources.paid)).toBe(true);
      
      // Verify resource items structure
      [...result.resources.free, ...result.resources.paid].forEach(resource => {
        expect(resource).toHaveProperty('id');
        expect(resource).toHaveProperty('platform');
        expect(resource).toHaveProperty('creator');
        expect(resource).toHaveProperty('title');
        expect(resource).toHaveProperty('link');
        expect(resource).toHaveProperty('type');
        expect(['course', 'tutorial', 'documentation']).toContain(resource.type);
      });
    });

    it('should handle partial data responses gracefully', async () => {
      const skillInput = { skill: 'Basic HTML' };
      
      const partialResponse = {
        data: {
          roadmap: {
            title: 'HTML Basics',
            modules: [
              {
                id: 'html-1',
                name: 'HTML Fundamentals',
                description: 'Learn basic HTML tags',
                miniProjects: []
              }
            ],
            majorProject: {
              id: 'html-major',
              name: 'Personal Website',
              description: 'Create a simple personal website',
              requirements: ['HTML structure', 'Basic styling'],
              estimatedHours: 10
            }
          },
          resources: {
            free: [
              {
                id: 'html-free-1',
                platform: 'MDN',
                creator: 'Mozilla',
                title: 'HTML Basics',
                link: 'https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics',
                type: 'documentation'
              }
            ],
            paid: []
          }
        }
      };

      mockAxiosInstance.post.mockResolvedValue(partialResponse);

      const result = await generateRoadmap(skillInput);

      expect(result.roadmap.modules).toHaveLength(1);
      expect(result.roadmap.modules[0].miniProjects).toHaveLength(0);
      expect(result.resources.free).toHaveLength(1);
      expect(result.resources.paid).toHaveLength(0);
    });
  });

  describe('Error Recovery Scenarios', () => {
    it('should handle sequential API failures and retries', async () => {
      const skillInput = { skill: 'React' };
      
      // First call fails with network error
      const networkError = new Error('Network Error');
      networkError.code = 'ERR_NETWORK';
      
      // Second call fails with server error
      const serverError = new Error('Server Error');
      serverError.response = { status: 500 };
      
      // Third call succeeds
      const successResponse = {
        data: {
          roadmap: {
            title: 'React Learning Path',
            modules: [],
            majorProject: {
              id: 'react-major',
              name: 'React App',
              description: 'Build a React application',
              requirements: ['React basics'],
              estimatedHours: 20
            }
          },
          resources: { free: [], paid: [] }
        }
      };

      mockAxiosInstance.post
        .mockRejectedValueOnce(networkError)
        .mockRejectedValueOnce(serverError)
        .mockResolvedValueOnce(successResponse);

      // First attempt should fail
      await expect(generateRoadmap(skillInput)).rejects.toThrow('Network Error');
      
      // Second attempt should fail
      await expect(generateRoadmap(skillInput)).rejects.toThrow('Server Error');
      
      // Third attempt should succeed
      const result = await generateRoadmap(skillInput);
      expect(result).toEqual(successResponse.data);
    });

    it('should handle malformed response data', async () => {
      const skillInput = { skill: 'JavaScript' };
      
      const malformedResponse = {
        data: {
          // Missing roadmap property
          resources: { free: [], paid: [] }
        }
      };

      mockAxiosInstance.post.mockResolvedValue(malformedResponse);

      const result = await generateRoadmap(skillInput);
      
      expect(result).toEqual(malformedResponse.data);
      expect(result.roadmap).toBeUndefined();
      expect(result.resources).toBeDefined();
    });
  });

  describe('Health Check Integration', () => {
    it('should perform comprehensive health check', async () => {
      const healthResponse = {
        data: {
          status: 'healthy',
          timestamp: '2024-01-15T10:30:00Z',
          version: '1.2.3',
          services: {
            database: 'connected',
            cache: 'operational',
            ai_service: 'available'
          },
          uptime: 86400,
          memory_usage: '45%',
          cpu_usage: '12%'
        }
      };

      mockAxiosInstance.get.mockResolvedValue(healthResponse);

      const result = await healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(healthResponse.data);
      expect(result.status).toBe('healthy');
      expect(result.services).toBeDefined();
      expect(result.services.database).toBe('connected');
    });

    it('should handle degraded service health check', async () => {
      const degradedHealthResponse = {
        data: {
          status: 'degraded',
          timestamp: '2024-01-15T10:30:00Z',
          version: '1.2.3',
          services: {
            database: 'connected',
            cache: 'slow_response',
            ai_service: 'unavailable'
          },
          warnings: [
            'Cache response time above threshold',
            'AI service temporarily unavailable'
          ]
        }
      };

      mockAxiosInstance.get.mockResolvedValue(degradedHealthResponse);

      const result = await healthCheck();

      expect(result.status).toBe('degraded');
      expect(result.warnings).toHaveLength(2);
      expect(result.services.ai_service).toBe('unavailable');
    });
  });

  describe('Configuration and Environment Tests', () => {
    it('should handle different API base URLs', async () => {
      // Test that the API utility can work with different base URLs
      const skillInput = { skill: 'Python' };
      const response = { data: { roadmap: {}, resources: {} } };

      mockAxiosInstance.post.mockResolvedValue(response);

      await generateRoadmap(skillInput);

      // Verify that axios.create was called (indicating configuration setup)
      expect(mockedAxios.create).toHaveBeenCalled();
      
      // Verify the API call was made
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/roadmap', skillInput);
    });

    it('should handle timeout configuration', async () => {
      const skillInput = { skill: 'Java' };
      
      // Simulate timeout
      const timeoutError = new Error('Timeout');
      timeoutError.code = 'ECONNABORTED';
      
      mockAxiosInstance.post.mockRejectedValue(timeoutError);

      await expect(generateRoadmap(skillInput)).rejects.toThrow('Timeout');
    });
  });
});