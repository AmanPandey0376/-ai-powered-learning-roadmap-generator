# Deployment Guide

This guide covers deploying the Learning Roadmap Backend to various cloud platforms.

## Environment Variables

Set these environment variables in your deployment platform:

### Required
- `FLASK_ENV=production`
- `SECRET_KEY=your-secure-secret-key`
- `CORS_ORIGINS=https://your-frontend-domain.com`

### Optional
- `PORT=5000` (usually set automatically by platform)
- `LOG_LEVEL=WARNING`
- `GUNICORN_WORKERS=4`

## Platform-Specific Deployment

### Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --config gunicorn.conf.py wsgi:application`
4. Add environment variables in Render dashboard
5. Deploy

### Railway

1. Connect your GitHub repository
2. Railway will auto-detect the Procfile
3. Add environment variables in Railway dashboard
4. Deploy

### Heroku

1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set FLASK_ENV=production`
4. Deploy: `git push heroku main`

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
```

## Local Production Testing

Test production configuration locally:

```bash
# Set environment
export FLASK_ENV=production
export SECRET_KEY=test-secret
export CORS_ORIGINS=http://localhost:3000

# Run with gunicorn
gunicorn --config gunicorn.conf.py wsgi:application
```

## Health Check

The application includes a health check endpoint at `/health` for monitoring.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `CORS_ORIGINS` includes your frontend domain
2. **Port Issues**: Check that `PORT` environment variable is set correctly
3. **Import Errors**: Verify all dependencies are in requirements.txt
4. **File Not Found**: Ensure data files (JSON) are included in deployment

### Logs

Check application logs for detailed error information:
- Render: View logs in dashboard
- Railway: Use `railway logs`
- Heroku: Use `heroku logs --tail`