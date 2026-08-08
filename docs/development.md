# Development

This document describes local development for the Phase 1 foundation.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- Docker Desktop
- Git

## Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Backend

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

Open:

```text
http://localhost:8000/docs
http://localhost:8000/api/v1/health
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Tests And Quality

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
```

Frontend build validation:

```powershell
cd frontend
npm run build
npm run smoke:build
```

## Docker

```powershell
docker compose config
docker compose up --build
```

The Compose foundation includes PostgreSQL and the FastAPI backend. Frontend, MLflow, model-serving, and monitoring services are planned for later phases.

## Environment Files

Use `.env.example` as a template. Do not commit `.env` or real secrets.
