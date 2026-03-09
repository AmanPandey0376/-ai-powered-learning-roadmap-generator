# API Utility Documentation

## Overview

The API utility (`api.js`) provides a configured Axios instance with error handling, interceptors, and environment-based configuration for the Learning Roadmap Frontend application.

## Configuration

The API utility uses environment variables for configuration:

- `VITE_API_BASE_URL`: Base URL for API requests (default: `/api`)
- `VITE_API_TIMEOUT`: Request timeout in milliseconds (default: `30000`)

## Environment Files

- `.env.development`: Development environment configuration
- `.env.production`: Production environment configuration
- `.env.example`: Example configuration file

## Available Methods

### `generateRoadmap(skillData)`

Generates a learning roadmap for the specified skill.

```javascript
import { generateRoadmap } from '../utils/api';

const roadmapData = await generateRoadmap({
  skill: 'React Developer'
});
```

### `healthCheck()`

Performs a health check on the API endpoint.

```javascript
import { healthCheck } from '../utils/api';

const health = await healthCheck();
```

### `getApiConfig()`

Returns current API configuration for debugging.

```javascript
import { getApiConfig } from '../utils/api';

const config = getApiConfig();
console.log('API Config:', config);
```

## Error Handling

The API utility provides enhanced error handling with user-friendly messages:

- Network errors: Connection and timeout issues
- Server errors (5xx): Generic server error messages
- Client errors (4xx): Specific validation and authentication errors
- Retry logic: Determines if errors are retryable

## Error Object Structure

```javascript
{
  ...originalError,
  userMessage: 'User-friendly error message',
  isRetryable: true/false
}
```

## Request/Response Interceptors

### Request Interceptor
- Adds default headers
- Logs requests in development mode

### Response Interceptor
- Handles successful responses
- Transforms errors into user-friendly format
- Adds retry logic information

## Development Setup

1. Install dependencies: `npm install`
2. Run setup script: `npm run dev:setup`
3. Start development server: `npm run dev`

The development server includes:
- API proxy to `http://localhost:8000`
- CORS enabled
- Hot reloading
- Environment variable loading

## Production Build

For production builds, the API will use the base URL configured in `.env.production` or default to `/api` for same-origin requests.