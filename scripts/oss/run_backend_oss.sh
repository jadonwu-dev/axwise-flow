#!/bin/bash

# AxWise Flow OSS - Backend Startup Script
# This script starts the backend in OSS mode with the appropriate configuration

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AxWise Flow OSS - Backend Startup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

echo -e "${GREEN}Repository root:${NC} $REPO_ROOT"
echo -e "${GREEN}Backend directory:${NC} $BACKEND_DIR"
echo ""

# Check if .env.oss exists
if [ ! -f "$BACKEND_DIR/.env.oss" ]; then
    echo -e "${RED}Error: .env.oss file not found in backend directory${NC}"
    echo -e "${YELLOW}Please create backend/.env.oss with the required configuration${NC}"
    echo ""
    echo "Example configuration:"
    echo "  OSS_MODE=true"
    echo "  DATABASE_URL=***REDACTED***
    echo "  GEMINI_API_KEY=***REMOVED***"
    exit 1
fi

# Load environment variables from .env.oss
echo -e "${GREEN}Loading environment from .env.oss...${NC}"
export $(grep -v '^#' "$BACKEND_DIR/.env.oss" | xargs)

# Verify required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}Error: GEMINI_API_KEY not set in .env.oss${NC}"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL not set in .env.oss${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo -e "${GREEN}✓ OSS_MODE:${NC} ${OSS_MODE:-false}"
echo -e "${GREEN}✓ DATABASE_URL=***REDACTED*** ${DATABASE_URL}"
echo -e "${GREEN}✓ GEMINI_API_KEY=***REMOVED*** ${GEMINI_API_KEY=***REMOVED***"
echo ""

# Check if PostgreSQL is running
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
if command -v psql &> /dev/null; then
    if psql "$DATABASE_URL" -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running and accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Cannot connect to PostgreSQL${NC}"
        echo -e "${YELLOW}  Make sure PostgreSQL is running and the database exists${NC}"
        echo -e "${YELLOW}  You can create the database with:${NC}"
        echo -e "${YELLOW}    createdb axwise${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠ Warning: psql command not found, skipping database check${NC}"
fi

# Check if Python virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ] && [ ! -d "$REPO_ROOT/venv" ]; then
    echo -e "${YELLOW}⚠ Warning: No virtual environment found${NC}"
    echo -e "${YELLOW}  Consider creating one with: python -m venv venv${NC}"
    echo ""
fi

# Change to backend directory
cd "$BACKEND_DIR"

# Check if dependencies are installed
echo -e "${BLUE}Checking Python dependencies...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Warning: FastAPI not found${NC}"
    echo -e "${YELLOW}  Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    echo ""
fi

# Run database migrations
echo -e "${BLUE}Running database migrations...${NC}"
if [ -f "$BACKEND_DIR/run_migrations.py" ]; then
    python run_migrations.py || echo -e "${YELLOW}⚠ Warning: Migration failed (this may be normal for first run)${NC}"
else
    echo -e "${YELLOW}⚠ Warning: run_migrations.py not found, skipping migrations${NC}"
fi
echo ""

# Start the backend server
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Starting Backend Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server will be available at:${NC} http://localhost:${UVICORN_PORT:-8000}"
echo -e "${GREEN}Health check endpoint:${NC} http://localhost:${UVICORN_PORT:-8000}/health"
echo -e "${GREEN}API documentation:${NC} http://localhost:${UVICORN_PORT:-8000}/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start uvicorn with the backend app
# Set PYTHONPATH to include the repository root so imports work correctly
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

python -m uvicorn backend.api.app:app \
    --host "${UVICORN_HOST:-0.0.0.0}" \
    --port "${UVICORN_PORT:-8000}" \
    --reload

