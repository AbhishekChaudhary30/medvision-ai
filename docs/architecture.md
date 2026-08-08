# Architecture

MedVision AI is organized as a production-oriented monorepo. Phase 1 establishes boundaries and contracts only; future phases will add the dataset pipeline, deep learning models, explainability, inference, authentication, dashboard, reports, and production operations.

## Positioning

MedVision AI is a research and educational clinical decision-support prototype. It is not a certified medical device, not a clinical diagnostic system, and not a replacement for qualified clinicians.

## Monorepo Boundaries

- `backend/` owns the FastAPI application, versioned API routing, configuration, logging, exception handling, and database session foundation.
- `frontend/` owns the React TypeScript application shell and future clinical review UI.
- `ml/` owns experimentation and ML engineering boundaries. Training code must remain outside the FastAPI application package.
- `data/` owns local and future DVC-managed dataset locations.
- `docs/` owns architecture, development, and roadmap documentation.
- `docker/` owns container build definitions.

## Backend Architecture

The backend exposes versioned API routes under `/api/v1`. The current Phase 1 endpoint is:

```text
GET /api/v1/health
```

Future routers such as auth, analysis, predictions, explainability, reports, users, and admin should be added under `backend/app/api/v1/` without changing unrelated modules.

## Configuration

Application settings are centralized in `backend/app/core/config.py` and are loaded from environment variables with `.env` support. Secrets must remain outside version control.

## Database

PostgreSQL is the primary application database. SQLAlchemy owns the engine and session foundation. Phase 1 does not define application tables.

## ML Architecture

The `ml/` tree establishes architectural boundaries for future loaders, preprocessing, validation, architectures, training, evaluation, explainability, checkpoints, and inference. Phase 1 does not implement models, training loops, Grad-CAM, metrics, or inference logic.

## DVC

DVC is included as a foundation for future dataset and pipeline tracking. Phase 1 does not download or track medical datasets.
