# MedVision AI

MedVision AI is a research and educational clinical decision-support prototype for explainable medical image analysis. The initial planned ML problem is chest X-ray binary classification for `NORMAL` and `PNEUMONIA`, but Phase 1 intentionally does not implement datasets, model training, inference, uploads, reports, authentication, or clinical workflows.

## Current Phase

Phase 1 - Foundation & Architecture.

This repository currently establishes a clean monorepo foundation for future backend, frontend, ML, data, configuration, testing, Docker, DVC, documentation, and CI work.

## High-Level Architecture

- `backend/` - FastAPI application foundation with `/api/v1` versioning.
- `frontend/` - React TypeScript application shell.
- `ml/` - ML development boundaries kept separate from the API application.
- `data/` - Local and future DVC-managed data directories. Medical datasets are not committed.
- `configs/` - Non-secret shared configuration templates.
- `tests/` - Pytest unit and integration tests.
- `docker/` - Docker build files.
- `docs/` - Architecture, development, and roadmap documentation.

## Technology Stack

- Python 3.11+
- FastAPI
- Pydantic and pydantic-settings
- SQLAlchemy
- PostgreSQL
- Pytest and HTTPX
- Ruff
- DVC foundation
- React, TypeScript, and Vite
- Docker Compose

## Repository Structure

```text
medvision-ai/
|-- backend/
|-- frontend/
|-- ml/
|-- data/
|-- configs/
|-- tests/
|-- scripts/
|-- docs/
|-- docker/
|-- .github/workflows/
|-- AGENTS.md
|-- README.md
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- pyproject.toml
`-- dvc.yaml
```

## Local Development Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- Docker Desktop
- Git

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Run the backend:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

Health endpoint:

```text
GET http://localhost:8000/api/v1/health
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Build validation:

```powershell
npm run build
npm run smoke:build
```

## Tests

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
```

## Docker

Validate the Compose file:

```powershell
docker compose config
```

Run the backend and PostgreSQL foundation:

```powershell
docker compose up --build
```

## Configuration

Configuration is environment-driven through `backend/app/core/config.py`. Use `.env.example` as a template and keep real `.env` files out of Git.

## Future Roadmap

- Phase 1 - Foundation & Architecture
- Phase 2 - Dataset & Deep Learning Data Pipeline
- Phase 3 - CNN + Transfer Learning + Evaluation
- Phase 4 - Explainability + Inference Engine
- Phase 5 - FastAPI + PostgreSQL + Authentication/RBAC
- Phase 6 - React Dashboard + Reports + Human Review
- Phase 7 - Productionization + MLOps + Testing + CI/CD + Monitoring

## Medical Disclaimer

MedVision AI is a research and educational clinical decision-support prototype. It is not a certified medical device, does not provide definitive medical diagnosis, and must not be used as a replacement for radiologists, clinicians, or other qualified healthcare professionals.
