# CompeteIQ

AI-powered competitive intelligence platform for marketing teams. Track competitors, decode their strategy, and find your edge.

## Tech Stack

- **Frontend:** Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 16 + pgvector
- **Job Queue:** Temporal (Python SDK)
- **LLM Router:** OpenRouter API
- **Scraping:** Apify + Firecrawl
- **Auth:** Clerk
- **Storage:** AWS S3
- **Email:** Resend

## Quick Start

### 1. Start infrastructure

```bash
cd docker && docker-compose up -d
```

This starts PostgreSQL (with pgvector), Redis, Temporal, and Temporal UI.

### 2. Set up environment

```bash
cp .env.example .env
# Fill in your API keys
```

### 3. Start the API

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd apps/web
npm install
npm run dev
```

### Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Temporal UI | http://localhost:8080 |

## Project Structure

```
competeiq/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   └── shared/       # Shared types & constants
├── docker/           # Docker Compose + Dockerfiles
├── turbo.json        # Turborepo config
└── package.json      # Workspace root
```
