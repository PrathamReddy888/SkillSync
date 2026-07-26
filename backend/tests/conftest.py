"""Pytest configuration: force test env vars BEFORE app imports."""
import os

# Set test env vars early so `get_settings()` reads the right values.
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("SUPABASE_URL", "")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-for-jwt-signing-only")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "10000")  # effectively unlimited in tests
