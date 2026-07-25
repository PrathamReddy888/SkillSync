"""
SkillSync backend configuration.

All settings are loaded from environment variables (with sensible
defaults for local development). Pydantic-settings validates types and
gives clear errors on misconfiguration.

Environment variables:
    SUPABASE_URL                     — Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY        — Supabase service-role key (server only!)
    SUPABASE_JWT_SECRET              — Supabase JWT secret (for verifying user JWTs)
    GROQ_API_KEY                     — Groq API key
    GROQ_MODEL                       — Groq model (default: llama-3.1-8b-instant)
    PISTON_API_URL                   — Piston code-execution API URL
    CORS_ORIGINS                     — comma-separated allowlist (no wildcards in prod)
    ENVIRONMENT                      — "development" | "staging" | "production"
    LOG_LEVEL                        — "DEBUG" | "INFO" | "WARNING" | "ERROR"
    RATE_LIMIT_PER_MINUTE            — per-IP request budget (default: 60)
    GROQ_TIMEOUT_SECONDS             — per-call timeout (default: 15)
    PISTON_TIMEOUT_SECONDS           — per-call timeout (default: 10)
    CHALLENGE_CACHE_TTL_SECONDS      — TTL for generated-challenge cache (default: 300)
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ────────────────────────────────────────────────
    environment: str = Field(
        default="development",
        description="deployment environment: development | staging | production",
    )
    log_level: str = Field(default="INFO")

    @field_validator("environment")
    @classmethod
    def _validate_env(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("development", "staging", "production"):
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")
        return v

    # ── Supabase ───────────────────────────────────────────────────
    supabase_url: str = Field(default="")
    supabase_service_role_key: str = Field(default="")
    supabase_jwt_secret: str = Field(default="")

    # ── Groq ───────────────────────────────────────────────────────
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama-3.1-8b-instant")
    groq_timeout_seconds: float = Field(default=15.0)

    # ── Piston ─────────────────────────────────────────────────────
    piston_api_url: str = Field(default="https://emkc.org/api/v2/piston/execute")
    piston_timeout_seconds: float = Field(default=10.0)

    # ── CORS ───────────────────────────────────────────────────────
    # Comma-separated allowlist. In production this MUST NOT contain "*".
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ── Rate limiting ──────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=60)

    # ── Cache ──────────────────────────────────────────────────────
    challenge_cache_ttl_seconds: int = Field(default=300)

    # ── Derived flags ──────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency."""
    return Settings()
