# MedVision AI Agent Instructions

MedVision AI is a research and educational clinical decision-support prototype for explainable medical image analysis. It is not a certified medical device, not a clinical diagnostic system, and not a replacement for qualified clinicians.

The existing repository structure and contracts are authoritative. Future tasks must extend the existing architecture instead of creating competing structures.

## Permanent Rules

- Preserve the root project name `medvision-ai`.
- Inspect the existing code before modifying files.
- Do not arbitrarily rename directories, files, modules, classes, or public contracts.
- Do not move code across architectural layers unless a future phase explicitly requires it.
- Do not create duplicate modules for the same responsibility.
- Do not implement future phases unless explicitly instructed.
- Preserve backward compatibility for existing APIs, tests, and documented commands.
- Update documentation only when architecture or developer workflow actually changes.

## Directory Ownership

- `backend/` contains the FastAPI application, API routers, configuration, logging, exceptions, and database session foundation.
- `frontend/` contains the React TypeScript application shell and future UI architecture.
- `ml/` contains ML development boundaries for data loading, preprocessing, model architecture, training, evaluation, explainability, and inference.
- `data/` is for local and DVC-managed data only. Do not commit medical datasets directly.
- `configs/` is for non-secret shared configuration templates.
- `tests/` contains Python unit and integration tests.
- `scripts/` is for repeatable developer automation.
- `docs/` contains architecture, development, and roadmap documentation.
- `docker/` contains Docker build files.

## Backend And API Rules

- Keep the backend modular. Do not create a monolithic FastAPI application.
- Use `/api/v1` as the API versioning foundation.
- Add future API areas through routers under `backend/app/api/v1/`.
- Keep application settings centralized in `backend/app/core/config.py`.
- Keep logging centralized in `backend/app/core/logging.py`.
- Keep controlled exception handling in `backend/app/core/exceptions.py`.
- Do not add authentication, prediction, upload, reporting, or review features during foundation-only tasks.

## ML Separation Rules

- Do not put ML training code inside the FastAPI application package.
- Keep ML development under `ml/`.
- Keep API/inference integration separate from training and experimentation.
- Do not add CNNs, transfer learning, Grad-CAM, inference logic, or model evaluation unless a future phase explicitly asks for them.

## Dependency Rules

- Prefer free and open-source technologies.
- Add dependencies only when they are required for the current phase.
- Avoid overlapping tools that solve the same formatting, linting, or testing responsibility.
- Defer deep learning libraries until the ML implementation phases require them.

## Security Rules

- Never hard-code passwords, JWT secrets, database credentials, API keys, or patient data.
- Use environment variables for secrets and environment-specific configuration.
- Keep `.env` ignored and maintain `.env.example` with placeholders only.
- Do not require real patient data for local development or tests.

## Testing Rules

- Run relevant tests after changes.
- Add tests for new behavior and architecture contracts.
- Do not create fake ML tests for features that do not exist.
- Keep tests focused on the current phase and changed behavior.

## Architecture Change Rule

Never silently modify architecture. If a future task requires a structural change, document the reason, update the relevant docs, and preserve existing contracts where possible.
