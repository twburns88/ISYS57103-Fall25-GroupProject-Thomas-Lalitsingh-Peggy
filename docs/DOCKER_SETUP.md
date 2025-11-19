# Docker Development Environment

This guide explains how to use Docker to run the AI-Project application in a consistent, isolated environment.

## Prerequisites

- **Docker Desktop** (Mac/Windows) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum version: Docker 20.10+, Docker Compose v2.0+

## Quick Start

### 1. Set Up Environment Variables

Copy the development environment template and add your API keys:

```bash
cp .env.development .env.development.local
```

Edit `.env.development` and add your actual API keys:
- `SERPAPI_KEY`: Get from https://serpapi.com/
- `GOOGLE_CLOUD_API_KEY`: Get from https://console.cloud.google.com/

### 2. Start the Development Server

Using the helper script (recommended):
```bash
./scripts/run_local.sh
```

Or manually:
```bash
docker-compose up --build
```

The application will be available at: **http://localhost:5000**

### 3. Stop the Server

Press `Ctrl+C` in the terminal, or run:
```bash
docker-compose down
```

## Docker Architecture

### Multi-Stage Dockerfile

The project uses a multi-stage Dockerfile with three stages:

1. **base**: Common dependencies (Python 3.11, OpenCV libraries)
2. **development**: Flask development server with hot reload
3. **production**: Gunicorn production server with 4 workers

### Environment Files

- `.env.development` - Development environment (hot reload, debug mode)
- `.env.testing` - Testing environment (mock APIs, test data)
- `.env.production.example` - Production template (never commit actual .env.production)

## Common Commands

### Development

```bash
# Start development server
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after dependency changes
docker-compose up --build

# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Testing

```bash
# Run all tests
./scripts/run_tests.sh

# Run tests manually
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Run specific tests
docker-compose -f docker-compose.test.yml run test pytest tests/test_specific.py -v
```

### Debugging

```bash
# Access shell in running container
docker-compose exec web bash

# View container logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web

# Inspect container
docker inspect ai-project-dev
```

## How Hot Reload Works

The development container mounts your local code as a volume:

```yaml
volumes:
  - .:/app  # Your code is mounted into /app
```

This means:
- Code changes are reflected immediately (no rebuild needed)
- Flask's debug mode auto-reloads on file changes
- The `.venv` directory is excluded to prevent conflicts

## Production Deployment

### Building Production Image

```bash
# Build production image
docker build --target production -t ai-project:latest .

# Run production container
docker run -d \
  --name ai-project-prod \
  -p 8000:8000 \
  --env-file .env.production \
  ai-project:latest
```

### Production Differences

- Uses Gunicorn instead of Flask dev server
- 4 worker processes (configurable)
- Debug mode disabled
- Different port (8000 vs 5000)
- Stricter configuration validation

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, change it in `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Use 5001 on host, 5000 in container
```

### Permission Errors

On Linux, if you encounter permission errors:

```bash
# Fix ownership of created files
sudo chown -R $USER:$USER .
```

### API Key Errors

If you see "API key not configured" errors:

1. Check that `.env.development` exists and has your keys
2. Restart the container: `docker-compose restart`
3. Verify keys are loaded: `docker-compose exec web env | grep API`

### Container Won't Start

```bash
# View detailed logs
docker-compose logs web

# Remove and rebuild
docker-compose down
docker-compose up --build
```

### Changes Not Reflected

If code changes aren't showing:

1. Check that volume is mounted: `docker-compose exec web ls -la /app`
2. Restart Flask manually: `docker-compose restart web`
3. Rebuild if dependencies changed: `docker-compose up --build`

### Clean Slate

To start completely fresh:

```bash
# Stop and remove everything
docker-compose down -v

# Remove all AI-Project images
docker images | grep ai-project | awk '{print $3}' | xargs docker rmi -f

# Rebuild from scratch
docker-compose up --build
```

## Environment Variables Reference

### Flask Configuration

- `FLASK_ENV`: Environment name (development/testing/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)
- `FLASK_SECRET_KEY`: Session encryption key (use random string in production)

### API Keys

- `SERPAPI_KEY`: SerpAPI key for product search
- `GOOGLE_CLOUD_API_KEY`: Google Cloud Vision API key for OCR

### Application Settings

- `USER_LOCATION`: Default search location
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes (default: 10MB)
- `UPLOAD_FOLDER`: Directory for uploaded files (default: ui/uploads)

## Best Practices

1. **Never commit API keys**: All `.env.*` files are gitignored (except `.example`)
2. **Use separate API keys per environment**: Development, testing, production
3. **Rebuild after dependency changes**: `docker-compose up --build`
4. **Monitor logs**: `docker-compose logs -f` to catch issues early
5. **Clean up uploads**: The `ui/uploads/` directory can grow large over time

## Next Steps

- Set up CI/CD pipeline with GitHub Actions
- Deploy to cloud platform (AWS ECS, Google Cloud Run, etc.)
- Add Redis for session management in production
- Implement cloud storage for uploaded files (S3, GCS)

## Getting Help

- Check logs: `docker-compose logs -f`
- Verify configuration: `docker-compose config`
- Test health endpoint: `curl http://localhost:5000/health`

For more information, see the main [QUICKSTART.md](../QUICKSTART.md) guide.
