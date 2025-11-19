# Multi-stage Dockerfile for AI-Project
# Supports development and production environments

# =============================================================================
# Stage 1: Base image with common dependencies
# =============================================================================
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies required by OpenCV and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Stage 2: Development image
# =============================================================================
FROM base as development

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p ui/uploads

# Set environment variables
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Expose development port
EXPOSE 5000

# Run Flask development server
CMD ["python", "ui/app.py"]

# =============================================================================
# Stage 3: Production image
# =============================================================================
FROM base as production

# Copy requirements and install Python dependencies including Gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p ui/uploads

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose production port
EXPOSE 8000

# Run Gunicorn production server
# --bind: Listen on all interfaces, port 8000
# --workers: Number of worker processes (adjust based on CPU cores)
# --timeout: Request timeout in seconds
# --access-logfile: Log access to stdout
# --error-logfile: Log errors to stderr
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "ui.app:app"]
