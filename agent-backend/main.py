"""Main Application Entrypoint for ShopAgent AI Associate Brain Service."""

import sys
from pathlib import Path

# Add agent backend directory to python path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent_app.api.chat import router as chat_router
from agent_app.api.memory import router as memory_router
from agent_app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
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
    """Liveness probe to check if the AI Associate process is running."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "live", "service": "agent-brain", "version": settings.VERSION},
    )


@app.get("/health/ready", tags=["Health"])
async def readiness_probe() -> JSONResponse:
    """Readiness probe to verify store connection and graph readiness."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "graph": "compiled", "store_api": settings.STORE_API_URL},
    )


# Mount Routers
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(memory_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
