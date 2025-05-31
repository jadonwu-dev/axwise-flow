#!/bin/bash

# Startup script for AxWise backend on Cloud Run
# This script handles the PORT environment variable properly

# Set default port if not provided by Cloud Run
PORT=${PORT:-8000}

echo "Starting AxWise backend on port $PORT"

# Start the FastAPI application with uvicorn
exec python -m uvicorn backend.api.app:app --host 0.0.0.0 --port $PORT --workers 1
