import { describe, it, expect } from 'vitest';
import { getApiConfig } from './api';

describe('API Utility', () => {
  describe('getApiConfig', () => {
    it('should return API configuration', () => {
      const config = getApiConfig();
      
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
  });

  describe('Environment Variables', () => {
    it('should use environment variables for configuration', () => {
      const config = getApiConfig();
      
      // In test environment, these should have default values
      expect(config.timeout).toBeGreaterThan(0);
      expect(config.baseURL).toBeTruthy();
    });

    it('should have proper default values', () => {
      const config = getApiConfig();
      
      // Default timeout should be 30 seconds
      expect(config.timeout).toBe(30000);
      
      // Base URL should be set (either from env or default)
      expect(config.baseURL).toMatch(/\/api$/);
    });
  });
});