<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Review and enhance description for my github repo based on my open source version for better visibility and more details. Dont need to add business details, just so it will be cool for devs and other people

# AxWise Flow OSS - Scripts

This directory contains scripts for running AxWise Flow in OSS (Open Source Software) mode.

## Prerequisites

Before running the backend in OSS mode, ensure you have:

1. **Python 3.11+** installed
2. **PostgreSQL** installed and running
3. **Gemini API Key** from Google AI Studio

## Quick Start

### 1. Set up the environment

The `.env.oss` file in the `backend/` directory contains the configuration for OSS mode. Update it with your credentials:

```bash
# In repo root
export OSS_MODE=true \
  DATABASE_URL=***REDACTED*** \
  GEMINI_API_KEY=***REMOVED***
```

Or edit `backend/.env.oss` directly with your Gemini API key.

### 2. Create the PostgreSQL database

```bash
# Create the database
createdb axwise


# Or using psql
psql -U postgres -c "CREATE DATABASE axwise;"
```


### 3. Install Python dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


# Install dependencies
cd backend
pip install -r requirements.txt
```


### 4. Run the backend

```bash
# From the repository root
scripts/oss/run_backend_oss.sh
```


### 5. Verify the backend is running

In another terminal:

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T..."
}
```


## Configuration

### Environment Variables

The following environment variables are configured in `backend/.env.oss`:


| Variable | Description | Default |
| :-- | :-- | :-- |
| `OSS_MODE` | Enable OSS mode (disables authentication) | `true` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://USER:PASS@HOST:PORT/DB |
| `GEMINI_API_KEY` | Google Gemini API key | *Required* |
| `UVICORN_PORT` | Backend server port | `8000` |
| `ENABLE_CLERK_VALIDATION` | Enable Clerk authentication | `false` (disabled in OSS mode) |

##***REMOVED*** Configuration

The default database configuration expects:

- **Host**: localhost
- **Port**: 5432
- **Database**: axwise
- **User**: postgres
- **Password**: postgres

You can modify these in `backend/.env.oss` if your PostgreSQL setup is different.

## Troubleshooting

### PostgreSQL Connection Issues

If you see database connection errors:

1. Verify PostgreSQL is running:

```bash
pg_isready
```

2. Check if the database exists:

```bash
psql -U postgres -l | grep axwise
```

3. Create the database if it doesn't exist:

```bash
createdb axwise
```


### Missing Dependencies

If you see import errors:

```bash
cd backend
pip install -r requirements.txt
```


### Port Already in Use

If port 8000 is already in use, you can change it in `backend/.env.oss`:

```bash
UVICORN_PORT=8001
```


## API Documentation

Once the backend is running, you can access:

- **Health Check**: http://localhost:8000/health
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc


## Development

### Running with Auto-reload

The script runs with `--reload` flag by default, which automatically restarts the server when code changes are detected.

### Viewing Logs

The backend logs are printed to stdout. You can redirect them to a file:

```bash
scripts/oss/run_backend_oss.sh 2>&1 | tee backend.log
```


## Next Steps

After the backend is running:

1. Set up the frontend (see `frontend/README.md`)
2. Explore the API documentation at http://localhost:8000/docs
3. Try the example requests in the API docs

## Support

For issues and questions:

- Check the main [README.md](../../README.md)
- Open an issue on GitHub
- Review the [backend documentation](../../backend/README.md)

Based on my review of your AxWise documentation and research into GitHub best practices, here's an enhanced README that will make your repo stand out for developers:

***

# 🚀 AxWise Flow OSS - AI-Powered Product Research Automation

[
[
[
[

> Transform weeks of customer research into minutes with AI-powered workflows. Go from idea to validated Product Requirement Document (PRD) in 17 minutes instead of 6 weeks.

**AxWise Flow OSS** is an open-source AI workflow automation platform that revolutionizes product development research. Built on a multi-agent architecture, it automates customer discovery, generates synthetic personas, conducts simulated interviews, and produces evidence-backed PRDs with full traceability.

***

## ✨ Key Features

### 🤖 Four-Module AI Workflow Engine

- **Research Helper**: Scopes problems and identifies key exploration areas
- **Context Builder**: Maps stakeholders and creates comprehensive frameworks
- **Synthetic Generator**: Simulates 100+ realistic customer personas and interviews
- **Analysis Engine**: Outputs traceable PRDs with confidence-scored insights


### 🏗️ Technical Highlights

- **JSON-driven modular architecture** for rapid deployment and customization
- **AttributedField system** ensures 100% traceability from insight to source evidence
- **Multi-agent orchestration** with parallel and sequential workflow patterns
- **RESTful API** architecture for seamless integration
- **PostgreSQL backend** for robust data persistence
- **Gemini-powered** LLM integration with swappable model support


### 🎯 What Makes This Different

- **Evidence-linked outputs**: Every insight traces back to source data with confidence scores
- **No black box**: Full transparency in AI reasoning and decision paths
- **Enterprise-ready**: Built with GDPR compliance, role-based access, and audit trails in mind
- **OSS mode**: Run completely locally without external auth dependencies

***

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download Python](https://www.python.org/downloads/))
- **PostgreSQL** installed and running ([Installation Guide](https://www.postgresql.org/download/))
- **Google Gemini API Key** from [Google AI Studio](https://ai.google.dev/)


### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/axwise-flow-oss.git
cd axwise-flow-oss
```


#### 2. Set up your environment

Edit the `.env.oss` file in the `backend/` directory:

```bash
# Required: Add your Gemini API key
GEMINI_API_KEY=***REMOVED***

***REMOVED*** configuration (update if needed)
DATABASE_URL=***REDACTED***

# OSS mode (authentication disabled)
OSS_MODE=true
ENABLE_CLERK_...=***REMOVED***

# Optional: Customize port
UVICORN_PORT=8000
```

Or export as environment variables:

```bash
export OSS_MODE=true
export DATABASE_URL=***REDACTED***
export GEMINI_API_KEY=***REMOVED***
```


#### 3. Create the PostgreSQL database

```bash
# Option 1: Using createdb
createdb axwise

# Option 2: Using psql
psql -U postgres -c "CREATE DATABASE axwise;"
```


#### 4. Install Python dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```


#### 5. Run the backend

```bash
# From the repository root
./scripts/oss/run_backend_oss.sh
```


#### 6. Verify it's working

Open a new terminal and check the health endpoint:

```bash
curl http://localhost:8000/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T20:37:42.123Z",
  "version": "1.0.0-oss"
}
```

🎉 **You're all set!** The backend is now running at `http://localhost:8000`

***

## 📚 API Documentation

Once the backend is running, explore the interactive API docs:


| Documentation | URL | Description |
| :-- | :-- | :-- |
| **Swagger UI** | http://localhost:8000/docs | Interactive API explorer with request/response examples |
| **ReDoc** | http://localhost:8000/redoc | Clean, readable API reference documentation |
| **Health Check** | http://localhost:8000/health | System health and status endpoint |


***

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
| :-- | :-- | :-- | :-- |
| `OSS_MODE` | Enable OSS mode (disables authentication) | `true` | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://USER:PASS@HOST:PORT/DB | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key for LLM capabilities | - | ✅ |
| `UVICORN_PORT` | Backend server port | `8000` | ❌ |
| `ENABLE_CLERK_VALIDATION` | Enable Clerk authentication (disabled in OSS) | `false` | ❌ |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) | `INFO` | ❌ |

##***REMOVED*** Configuration

The default PostgreSQL setup expects:

- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `axwise`
- **User**: `postgres`
- **Password**: `postgres`

Customize by updating `DATABASE_URL` in `backend/.env.oss`.

***

## 🛠️ Development

### Running with Auto-reload

The script runs with `--reload` by default, automatically restarting when code changes are detected:

```bash
./scripts/oss/run_backend_oss.sh
```


### Viewing Logs

Logs are printed to stdout. Redirect to a file:

```bash
./scripts/oss/run_backend_oss.sh 2>&1 | tee backend.log
```


### Running Tests

```bash
cd backend
pytest tests/
```


### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```


***

## 🔧 Troubleshooting

### PostgreSQL Connection Issues

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**

1. **Verify PostgreSQL is running:**

```bash
pg_isready
# Expected: /tmp:5432 - accepting connections
```

2. **Check if database exists:**

```bash
psql -U postgres -l | grep axwise
```

3. **Create database if missing:**

```bash
createdb axwise
```

4. **Test connection manually:**

```bash
psql -U postgres -d axwise -c "SELECT version();"
```


### Missing Dependencies

**Symptom:** `ModuleNotFoundError: No module named 'X'`

**Solution:**

```bash
cd backend
pip install -r requirements.txt
```


### Port Already in Use

**Symptom:** `OSError: [Errno 48] Address already in use`

**Solution:** Change port in `backend/.env.oss`:

```bash
UVICORN_PORT=8001
```

Or find and kill the process:

```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```


### Gemini API Issues

**Symptom:** `401 Unauthorized` or `Invalid API key`

**Solutions:**

1. Verify your API key is correct in `.env.oss`
2. Check API key is active at [Google AI Studio](https://ai.google.dev/)
3. Ensure no extra spaces or quotes in the key value

***

## 🗺️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AxWise Flow OSS                         │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   Research   │──▶│   Context    │──▶│  Synthetic   │   │
│  │    Helper    │   │   Builder    │   │  Generator   │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│         │                   │                   │           │
│         └───────────────────┴──────────┬────────┘           │
│                                        │                    │
│                               ┌────────▼────────┐           │
│                               │    Analysis     │           │
│                               │     Engine      │           │
│                               └─────────────────┘           │
│                                        │                    │
│                               ┌────────▼────────┐           │
│                               │  Traceable PRD  │           │
│                               │  with Confidence│           │
│                               │     Scores      │           │
│                               └─────────────────┘           │
└─────────────────────────────────────────────────────────────┘
          │                                          │
          ▼                                          ▼
  ┌───────────────┐                          ┌──────────────┐
  │  PostgreSQL   │                          │ Gemini API   │
  │   Database    │                          │     (LLM)    │
  └───────────────┘                          └──────────────┘
```


### Key Components

- **Multi-Agent System**: Four specialized agents working in orchestrated sequence
- **Evidence Tracking**: AttributedField architecture links every insight to source
- **Confidence Scoring**: All AI-generated insights include reliability metrics
- **Modular Design**: JSON-driven configuration enables easy customization
- **API-First**: RESTful endpoints for all workflow operations

***

## 🎯 Use Cases

### Product Development

- **Validate ideas** before building
- **Generate evidence-backed** PRDs in minutes
- **Identify stakeholders** and their concerns automatically


### Customer Research

- **Automate discovery** workflows
- **Simulate customer interviews** with realistic personas
- **Extract insights** from transcripts and documents


### Requirements Engineering

- **Map stakeholder ecosystems**
- **Generate comprehensive requirements** documentation
- **Track requirement sources** with full traceability


### Consulting \& Advisory

- **Accelerate client discovery** by 90%
- **Reduce pre-sales costs** with automated scoping
- **Generate professional deliverables** faster

***

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug reports and fixes
- ✨ Feature requests and implementations
- 📝 Documentation improvements
- 🧪 Test coverage enhancements
- 🎨 UI/UX improvements

Please see our [Contributing Guidelines](CONTRIBUTING.md) (coming soon) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

***

## 📋 Roadmap

- [ ] Support for additional LLM providers (OpenAI, Anthropic, local models)
- [ ] Frontend UI for visual workflow building
- [ ] Advanced analytics dashboard
- [ ] Export to multiple PRD formats (Confluence, Jira, Notion)
- [ ] Custom persona training from historical data
- [ ] Real-time collaboration features
- [ ] Docker Compose one-command setup
- [ ] Kubernetes deployment templates

***

## 📖 Documentation

- **Getting Started**: You're reading it! 📍
- **API Reference**: http://localhost:8000/docs (after starting server)
- **Architecture Deep Dive**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (coming soon)
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) (coming soon)
- **Advanced Configuration**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md) (coming soon)

***

## 🔐 Security

AxWise Flow OSS runs in **OSS mode** with authentication disabled by default for ease of local development. For production deployments:

- Enable authentication (set `OSS_MODE=false`)
- Use strong PostgreSQL credentials
- Secure your Gemini API key
- Run behind a reverse proxy (nginx, Caddy)
- Implement rate limiting
- Regular security updates

**Found a security issue?** Please email security@axwise.de instead of opening a public issue.

***

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

***

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for blazing-fast API performance
- Powered by [Google Gemini](https://ai.google.dev/) for advanced LLM capabilities
- Uses [PostgreSQL](https://www.postgresql.org/) for robust data persistence
- Inspired by the need to make product research accessible to everyone

***

## 💬 Community \& Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-username/axwise-flow-oss/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/your-username/axwise-flow-oss/discussions)
- **Website**: [axwise.de](https://axwise.de)
- **Twitter**: [@axwise_de](https://twitter.com/axwise_de)

***

## ⭐ Star History

If you find this project useful, please consider giving it a star! It helps others discover the project.

[

***

## 🚀 Next Steps

After getting the backend running:

1. ✅ **Explore the API**: Visit http://localhost:8000/docs
2. 🎨 **Set up the frontend**: See `frontend/README.md` for instructions
3. 🧪 **Try example workflows**: Check `examples/` directory
4. 📚 **Read the architecture docs**: Understand the system design
5. 🤝 **Join the community**: Share your use case and learnings

***

**Built with ❤️ by the AxWise team**

*From idea to validated PRD in 17 minutes, not 6 weeks.*
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^3][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^4][^40][^41][^42][^43][^44][^45][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: AxWise_Investment_Proposal_Final-2.pdf

[^2]: AxWise_-Enterprise-AI-That-Scales_v2-1.pdf

[^3]: AxWise_-High-Pain-B2B-Discovery-Use-Cases-1.pdf

[^4]: From-Pain-to-Progress_-axwise-for-SINC.pptx

[^5]: https://www.codemotion.com/magazine/dev-life/github-project/

[^6]: https://dev.to/github/how-to-create-the-perfect-readme-for-your-open-source-project-1k69

[^7]: https://docs.github.com/en/contributing/collaborating-on-github-docs/about-contributing-to-github-docs

[^8]: https://github.com/mattinannt/repository-best-practices

[^9]: https://tilburgsciencehub.com/topics/collaborate-share/share-your-work/content-creation/readme-best-practices/

[^10]: https://github.com/readme/featured/contributor-onboarding

[^11]: https://gitprotect.io/blog/how-to-put-a-project-on-github-best-practices/

[^12]: https://www.freecodecamp.org/news/how-to-write-a-good-readme-file/

[^13]: https://github.blog/news-insights/contributing-guidelines/

[^14]: https://dev.to/pwd9000/github-repository-best-practices-23ck

[^15]: https://dev.to/kwing25/how-to-write-a-good-readme-for-your-project-1l10

[^16]: https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github

[^17]: https://www.freecodecamp.org/news/increase-engagement-on-your-public-github-repositories/

[^18]: https://www.makeareadme.com

[^19]: https://docs.github.com/contributing

[^20]: https://joost.blog/healthy-github-repository/

[^21]: https://enoei.github.io/papers/liu2022readme.pdf

[^22]: https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project

[^23]: https://www.youtube.com/watch?v=xiL2C7npqsU

[^24]: https://github.com/othneildrew/Best-README-Template

[^25]: https://dev.to/kosa12/making-your-github-repository-stand-out-5gef

[^26]: https://arxiv.org/html/2407.12821v1

[^27]: https://aws.amazon.com/what-is/ai-agents/

[^28]: https://drlongnecker.com/blog/2025/10/api-first-ai-integration-architecture-patterns-success/

[^29]: https://research.aimultiple.com/llm-automation/

[^30]: https://fme.safe.com/guides/ai-agent-architecture/

[^31]: https://www.linkedin.com/pulse/apis-key-integrating-scaling-ai-enterprise-vivek-sahay-h1cwe

[^32]: https://arxiv.org/html/2411.10478v1

[^33]: https://cloud.google.com/architecture/multiagent-ai-system

[^34]: https://dev.to/stellaacharoiro/5-essential-api-design-patterns-for-successful-ai-model-implementation-2dkk

[^35]: https://blog.n8n.io/llm-agents/

[^36]: https://www.lindy.ai/blog/ai-agent-architecture

[^37]: https://sparkco.ai/blog/enterprise-api-integration-patterns-agent-tool-orchestration

[^38]: https://apix-drive.com/en/blog/other/llm-workflow-automation

[^39]: https://google.github.io/adk-docs/

[^40]: https://anshadameenza.com/blog/technology/modern-api-ai/

[^41]: https://www.merge.dev/blog/llm-powered-agents-intelligent-workflow-automations

[^42]: https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf

[^43]: https://www.hannes-lehmann.com/en/blog/ai-integration-patterns/

[^44]: https://www.v7labs.com/blog/ai-workflow-automation

[^45]: https://www.anthropic.com/research/building-effective-agents

