# CompeteIQ — Claude Code Instructions

## Project Context
See `idea.md` for full product spec, architecture decisions, and development roadmap.

## Code Navigation
Use Grep/Glob/Read to explore the codebase. Key entry points:
- API: `apps/api/app/main.py` → routers → services/workers
- Frontend: `apps/web/src/app/` (Next.js App Router)

## Dev Setup
- API venv: `apps/api/.venv/` — always use `.venv/bin/python` / `.venv/bin/uvicorn`
- Start API: `cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000`
- Start web: `cd apps/web && npm run dev`
- No Docker available locally — Postgres/Redis not running; DB calls will error in dev

## Known Issues / Gotchas
- `PageSnapshot.metadata` was renamed to `extra_metadata` (SQLAlchemy reserved word fix)
- No `.env` file exists yet — all external API keys are empty strings by default
- Temporal worker (`apps/api/app/workers/worker.py`) requires Temporal server to be running
- `packages/shared` is a workspace package but currently empty
