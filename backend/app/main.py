"""
SkillSync API — application factory.

Replaces the MVP `main.py` with a structured, configurable app:

  * Strict CORS (no wildcards in production).
  * Structured JSON logging (structlog).
  * Per-IP rate limiting (in-memory, swappable for Redis).
  * Auth via Supabase JWT verification (HS256 shared secret).
  * All endpoints on a typed APIRouter with Pydantic request/response
    models for clean OpenAPI docs.
  * Centralised exception handler that logs + returns JSON errors.
  * Health endpoint that reports which upstreams are configured.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.logging import configure_logging, get_logger
from app.rate_limit import configure_rate_limiter
from app.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown hooks."""
    settings = get_settings()
    configure_logging()
    configure_rate_limiter(max_per_minute=settings.rate_limit_per_minute)
    log = get_logger("app")
    log.info(
        "app_starting",
        environment=settings.environment,
        supabase_configured=settings.supabase_configured,
        groq_configured=settings.groq_configured,
    )
    yield
    log.info("app_stopping")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="SkillSync API",
        version="3.0.0",
        description=(
            "SkillSync backend — challenge generation, code execution, "
            "AI recommendations, integrity reporting, and leaderboard."
        ),
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # ── CORS ──────────────────────────────────────────────────────
    # In production the allowlist MUST be explicit (no "*").
    origins = settings.cors_origins_list
    if settings.is_production and ("*" in origins or not origins):
        # Fail fast — a misconfigured prod CORS is a security incident.
        raise RuntimeError(
            "Production CORS must be an explicit allowlist. "
            f"Got: {settings.cors_origins!r}"
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],  # only "*" in dev
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # ── Routes ────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Root ──────────────────────────────────────────────────────
    @app.get("/", tags=["meta"])
    async def root():
        return {
            "name": "SkillSync API",
            "version": "3.0.0",
            "docs": "/docs" if not settings.is_production else None,
            "health": "/api/health",
        }

    # ── Centralised exception handler ─────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        log = get_logger("errors")
        log.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    return app


# Module-level instance for `uvicorn app.main:app`
app = create_app()
