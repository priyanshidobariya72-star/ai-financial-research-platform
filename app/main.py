import asyncio
import sys

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.config.settings import settings
from app.logger import get_logger
from app.rag.router import router as rag_router

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="AI Financial Research Platform API")
logger = get_logger(__name__)

allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(rag_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("HTTP %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("HTTP %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Return a basic health check response."""
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "FastAPI is running"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    logger.debug("Health endpoint hit")
    return {"status": "healthy"}
