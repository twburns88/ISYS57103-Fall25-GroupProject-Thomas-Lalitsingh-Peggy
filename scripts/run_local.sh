#!/bin/bash
# Start the development environment using Docker

set -e

echo "======================================"
echo "AI-Project Development Environment"
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

# Check if .env.development exists
if [ ! -f ".env.development" ]; then
    echo "WARNING: .env.development file not found!"
    echo "Creating from .env.example if it exists..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.development
        echo "Created .env.development from .env.example"
        echo "Please edit .env.development and add your API keys before continuing."
        exit 1
    else
        echo "ERROR: Neither .env.development nor .env.example found."
        echo "Please create .env.development with your API keys."
        exit 1
    fi
fi

echo "Starting development server with Docker..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null 2>&1; then
    docker compose up --build
else
    docker-compose up --build
fi
