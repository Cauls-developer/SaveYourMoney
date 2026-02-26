# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: Flask API, domain logic, SQLite repositories, and use cases.
- `backend/tests/`: Pytest suite with `test_*.py` files.
- `frontend/`: Electron app (`main.js`, `preload.js`), pages in `frontend/pages/`, assets in `frontend/assets/`.
- Generated build outputs in `backend/build/`, `backend/dist/`, and `frontend/dist/`.
- Root scripts/docs: `deploy-installer.bat`, `build-backend.bat`, `DEPLOY-INSTALLER.txt`.

## Build, Test, and Development Commands
- `cd backend` then `python -m venv .venv` and `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- Run backend from repo root: `backend\.venv\Scripts\python.exe -m backend.app`.
- `cd frontend` then `npm install`.
- Run Electron: `npm run start`.
- Build installer (recommended): `.\deploy-installer.bat`.
- Manual build: `.\build-backend.bat`, then `cd frontend` and `npm run build:win`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case` for functions/vars, `PascalCase` for classes.
- JavaScript: 2-space indentation, `camelCase`, single quotes, semicolons.
- Frontend: keep shared styles in `frontend/pages/styles.css`, pages in `frontend/pages/*.html`, and page scripts alongside them (example: `calculator-widget.js`).
- Prefer consistent class naming already used in pages (ex: `app-header`, `kpi-card`) and reuse CSS variables from `:root`.

## Testing Guidelines
- Framework: `pytest` in `backend/tests/`.
- Naming: `test_*.py`.
- Run tests: `cd backend` then `python -m pytest`.
- Add tests for API behavior or repository logic changes.

## Commit & Pull Request Guidelines
- Commits are short and imperative; many follow Conventional Commits like `feat(core): ...`, `fix(...)`, `chore:`.
- Prefer `type(scope): summary` (example: `fix(api): handle null category`).
- PRs should include a clear summary, test evidence, screenshots for UI changes, and linked issues when relevant.

## Security & Configuration Tips
- Backend data directory is controlled by `SAVEYOURMONEY_DATA_DIR`.
- Debug mode: `SAVEYOURMONEY_DEBUG=1`.
- Skip backend auto-start in Electron: `SAVEYOURMONEY_SKIP_BACKEND=1`.

# Task Execution System

## Mandatory Flow

1.  Read Tasks.md
2.  Identify first task with Status: TODO
3.  Confirm understanding in max 3 bullets
4.  Implement minimal changes required
5.  Run relevant validations:
    -   Backend: cd backend && python -m pytest
    -   Frontend: cd frontend && npm install / npm run ...
6.  If successful:
    -   Update Tasks.md → DONE
    -   Append entry to progress.md (What / How / Why / Evidence)
7.  If blocked:
    -   Update status → BLOCKED
    -   Log reason in progress.md
8.  Repeat until no TODO remain
9.  Print short completion message

## Token Efficiency Rules

-   Use repository files as source of truth
-   Avoid long explanations
-   Do not invent new tasks
-   Keep diffs small and focused
-   Work only in relevant project areas
