from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import health, users, brands, competitors, competitor_detail, dashboard, kpi_config, collection_jobs

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="CompeteIQ API",
    description="Competitive Intelligence Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(brands.router, prefix="/api", tags=["Brands"])
app.include_router(competitors.router, prefix="/api", tags=["Competitors"])
app.include_router(kpi_config.router, prefix="/api", tags=["KPI Config"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(competitor_detail.router, prefix="/api", tags=["Competitor Detail"])
app.include_router(collection_jobs.router, prefix="/api", tags=["Collection Jobs"])
