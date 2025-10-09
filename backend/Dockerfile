# Multi-stage Docker build for AxWise Python FastAPI backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching (context is backend/)
COPY requirements.txt /app/requirements.txt

# Show requirements for debugging in build logs
RUN echo '--- BEGIN requirements.txt ---' && cat /app/requirements.txt && echo '--- END requirements.txt ---'
# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend source into /app/backend so imports like `backend.api.app` work
COPY . /app/backend

# Make the startup script executable
RUN chmod +x /app/backend/start.sh

# Set Python path to include /app so the `backend` package resolves
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check (use PORT environment variable)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application using the startup script
CMD ["/app/backend/start.sh"]
