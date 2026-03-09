# API Integration Tests

This directory contains comprehensive integration tests for the API utility module.

## Test Files

### `api.test.js`
- Tests core API functions (`generateRoadmap`, `healthCheck`, `getApiConfig`)
- Tests various error scenarios (network errors, timeouts, HTTP status codes)
- Tests successful API responses with complete data structures
- Validates API configuration and environment variable handling

### `api-interceptors.test.js`
- Tests axios instance configuration and setup
- Tests request and response interceptor registration
- Tests API error handling integration
- Tests environment variable configuration

### `api-integration.test.js`
- End-to-end integration tests with complete API workflows
- Tests complex roadmap generation scenarios with full data structures
- Tests error recovery and retry scenarios
- Tests health check functionality with various service states
- Tests configuration handling across different environments

## Running Tests

Run all API tests:
```bash
npm test -- src/utils/__tests__/
```

Run specific test file:
```bash
npm test -- src/utils/__tests__/api.test.js
```

Run tests in watch mode:
```bash
npm run test:watch -- src/utils/__tests__/
```

## Test Coverage

The tests cover:
- ✅ API request/response handling
- ✅ Mock backend responses for testing
- ✅ Error handling scenarios (network, timeout, HTTP errors)
- ✅ Axios configuration and interceptor setup
- ✅ Environment variable handling
- ✅ Complete data structure validation
- ✅ Edge cases and error recovery

## Requirements Satisfied

This test suite satisfies requirement **6.4** from the specification:
- Tests API request/response handling with Axios
- Mocks backend responses for comprehensive testing scenarios
- Tests all error handling scenarios including network, timeout, and HTTP errors
- Validates the API utility configuration and environment setup