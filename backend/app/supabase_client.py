"""
Supabase client singleton.

Lazy-initialised so the API can boot even when Supabase is not configured
(e.g. local dev, tests). Endpoints that need Supabase check
`get_supabase()` and return a 503 if it's unavailable.
"""
from typing import Optional

from supabase import create_client, Client

from app.config import get_settings
from app.logging import get_logger

_client: Optional[Client] = None
_init_attempted = False


def get_supabase() -> Optional[Client]:
    """
    Return the cached Supabase client, or None if not configured.

    Initialisation errors are logged once and remembered so we don't
    spam the log on every request.
    """
    global _client, _init_attempted
    if _client is not None or _init_attempted:
        return _client

    _init_attempted = True
    settings = get_settings()
    log = get_logger("supabase")

    if not settings.supabase_configured:
        log.warning("supabase_not_configured",
                    msg="SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set; endpoints requiring Supabase will return 503")
        return None

    try:
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        log.info("supabase_client_initialised")
    except Exception as e:
        log.error("supabase_init_failed", error=str(e))
        _client = None

    return _client


def reset_supabase_for_tests() -> None:
    """Test-only: reset the cached client so a new config is picked up."""
    global _client, _init_attempted
    _client = None
    _init_attempted = False
