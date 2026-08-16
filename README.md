---
title: Medvision Api
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: gradio
python_version: '3.12'
app_file: run.py
pinned: false
---
# MedVision AI

MedVision AI is a research and educational clinical decision-support prototype for explainable medical image analysis. It performs chest X-ray binary classification for `NORMAL` and `PNEUMONIA` using an enterprise-grade ML architecture.

## Architecture & Features

This repository implements a full-stack, production-ready AI platform:

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

## Completed Roadmap

- Phase 1 - Foundation & Architecture
- Phase 2 - Dataset & Deep Learning Data Pipeline
- Phase 3 - Data Leakage Prevention & Splits
- Phase 4 - Advanced ML Pipeline & Transforms
- Phase 5 - Benchmarking (ResNet, DenseNet, EfficientNet)
- Phase 6 - Calibration, Quality Gates & OOD Detection
- Phase 7 - Explainability (Grad-CAM)
- Phase 8 - Model Registry
- Phase 9 - FastAPI Backend + PostgreSQL
- Phase 10 - React Frontend + Analysis Workspace
- Phase 11 - Pytest Verification & E2E Testing
- Phase 12 - Docker Deployment Ready

## Medical Disclaimer

MedVision AI is a research and educational clinical decision-support prototype. It is not a certified medical device, does not provide definitive medical diagnosis, and must not be used as a replacement for radiologists, clinicians, or other qualified healthcare professionals.
