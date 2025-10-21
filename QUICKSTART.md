# AxWise Flow OSS - Quick Start Guide

Get up and running with AxWise Flow in 5 minutes!

## Step 1: Prerequisites Check

Ensure you have:
- ✅ Python 3.11+ installed
- ✅ PostgreSQL running
- ✅ Gemini API Key

### Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Step 2: Database Setup

Create the PostgreSQL database:

```bash
# Option 1: Using createdb command
createdb axwise

# Option 2: Using psql
psql -U postgres -c "CREATE DATABASE axwise;"

# Verify the database was created
psql -U postgres -l | grep axwise
```

## Step 3: Configure Environment

The Gemini API key has already been added to `backend/.env.oss`:

```bash
GEMINI_API_KEY=***REMOVED***
```

If you need to use a different database configuration, edit `backend/.env.oss`:

```bash
# Example: Different database credentials
DATABASE_URL=***REDACTED***
```

## Step 4: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Return to repo root
cd ..
```

## Step 5: Start the Backend

```bash
# From repository root
scripts/oss/run_backend_oss.sh
```

You should see output like:

```
========================================
  AxWise Flow OSS - Backend Startup
========================================

Repository root: /path/to/axwise-flow-oss
Backend directory: /path/to/axwise-flow-oss/backend

Loading environment from .env.oss...
✓ Environment variables loaded
✓ OSS_MODE: true
✓ DATABASE_URL=***REDACTED***
✓ GEMINI_API_KEY=***REMOVED***

========================================
  Starting Backend Server
========================================
Server will be available at: http://localhost:8000
Health check endpoint: http://localhost:8000/health
API documentation: http://localhost:8000/docs

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 6: Test the Backend

Open a new terminal and run:

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T18:30:00.000000+00:00"
}
```

## Step 7: Explore the API

Open your browser and visit:

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Next Steps

### Try the API

1. Go to http://localhost:8000/docs
2. Explore the available endpoints
3. Try the "Try it out" feature on any endpoint

### Set Up the Frontend (Optional)

Option A (recommended)

```bash
# From repository root
scripts/oss/run_frontend_oss.sh
```

This will:
- Copy frontend/.env.local.oss to frontend/.env.local
- Ensure NEXT_PUBLIC_...=***REMOVED***
- Install npm deps if needed
- Start Next.js on http://localhost:3000

Option B (manual)

```bash
cd frontend
npm install
cp .env.local.oss .env.local
# Ensure:
# NEXT_PUBLIC_...=***REMOVED***
npm run dev
```

Then visit http://localhost:3000

## Troubleshooting

### Issue: "Cannot connect to PostgreSQL"

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start it
# macOS (Homebrew):
brew services start postgresql

# Linux (systemd):
sudo systemctl start postgresql

# Windows:
# Start PostgreSQL service from Services app
```

### Issue: "Database 'axwise' does not exist"

**Solution:**
```bash
createdb axwise
```

### Issue: "GEMINI_API_KEY not set"

**Solution:**
Edit `backend/.env.oss` and ensure the GEMINI_API_KEY line is present and uncommented.

### Issue: "Port 8000 already in use"

**Solution:**
Either stop the process using port 8000, or change the port in `backend/.env.oss`:
```bash
UVICORN_PORT=8001
```

### Issue: "Module not found" errors

**Solution:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

## Environment Variables Reference

Key variables in `backend/.env.oss`:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `OSS_MODE` | Enable OSS mode | `true` |
| `GEMINI_API_KEY` | Google Gemini API key | *Provided* |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://USER:PASS@HOST:PORT/DB |
| `UVICORN_PORT` | Backend server port | `8000` |
| `ENABLE_CLERK_VALIDATION` | Enable authentication | `false` (disabled in OSS) |

## Manual Start (Alternative)

If the script doesn't work, you can start the backend manually:

```bash
# From repository root
cd backend

# Load environment variables
export $(grep -v '^#' .env.oss | xargs)

# Start the server
python -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --reload
```

## Getting Help

- 📖 Read the full [README.md](README.md)
- 📚 Check [scripts/oss/README.md](scripts/oss/README.md)
- 🐛 Report issues on [GitHub](https://github.com/AxWise-GmbH/axwise-flow-oss/issues)

---

**Success!** 🎉 You now have AxWise Flow running locally!

