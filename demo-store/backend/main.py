"""Main Application Entrypoint for ShopAgent Demo Store Commerce API."""

import sys
from pathlib import Path

# Add backend directory to python path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from store_app.api.cart import router as cart_router
from store_app.api.products import router as products_router
from store_app.core.config import settings
from store_app.core.database import AsyncSessionLocal, Base, engine
from store_app.seed.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for database initialization and seeding."""
    # 1. Initialize Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed Initial Catalog Data
    async with AsyncSessionLocal() as session:
        await seed_database(session)

    yield

    # Cleanup connections on shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Probes (SRE Department Standards)
@app.get("/health/live", tags=["Health"])
async def liveness_probe() -> JSONResponse:
    """Liveness probe to check if the application process is running."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "live", "version": settings.VERSION},
    )


@app.get("/health/ready", tags=["Health"])
async def readiness_probe() -> JSONResponse:
    """Readiness probe to check if the database is accessible."""
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "database": "connected"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )


# Mount API Routers
app.include_router(products_router, prefix=settings.API_V1_PREFIX)
app.include_router(cart_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
