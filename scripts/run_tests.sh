#!/bin/bash
# Run tests in Docker container

set -e

echo "======================================"
echo "AI-Project Test Suite"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "ERROR: docker-compose is not available."
    echo "Please install Docker Compose or use Docker Desktop which includes it."
    exit 1
fi

# Check if .env.testing exists
if [ ! -f ".env.testing" ]; then
    echo "WARNING: .env.testing file not found!"
    echo "Tests will run with default mock values."
fi

echo "Running tests in Docker container..."
echo ""

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null 2>&1; then
    docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
    EXIT_CODE=$?
    docker compose -f docker-compose.test.yml down
else
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    EXIT_CODE=$?
    docker-compose -f docker-compose.test.yml down
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
