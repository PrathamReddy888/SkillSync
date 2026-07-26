"""
API routes — all endpoints live on a single APIRouter for clarity.

Every endpoint:
  * Validates input via Pydantic models (defined in `app.models`).
  * Returns typed responses (so OpenAPI docs are useful).
  * Uses the structured logger for observability.
  * Degrades gracefully when Supabase / Groq are not configured.
"""
import json
import hashlib
from typing import List, Optional

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.auth import require_user, require_role
from app.config import get_settings
from app.fallbacks import get_fallback_challenge
from app.groq_client import call_groq, GroqError, GroqJSONError
from app.logging import get_logger
from app.models import (
    EvaluateCodeResponse,
    FutureProofRequest,
    GenerateTestRequest,
    GenerateTestResponse,
    HealthResponse,
    IntegrityReport,
    RecommendationRequest,
    SubmissionEval,
)
from app.piston_client import execute_code, PistonError
from app.rate_limit import rate_limit_dependency
from app.supabase_client import get_supabase

router = APIRouter(prefix="/api", tags=["skillsync"])
log = get_logger("routes")

# Cache generated challenges for ~5 minutes keyed by (sector, difficulty,
# problem hash, num_questions). This avoids re-paying the Groq latency
# when a company re-generates the same challenge spec.
_challenge_cache: TTLCache = TTLCache(
    maxsize=128,
    ttl=get_settings().challenge_cache_ttl_seconds,
)


def _challenge_cache_key(req: GenerateTestRequest) -> str:
    raw = f"{req.sector}|{req.difficulty}|{req.num_questions}|{req.problem_description.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ────────────────────────────────────────────────────────────────────
# Health
# ────────────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version="3.0.0",
        environment=settings.environment,
        supabase_configured=settings.supabase_configured,
        groq_configured=settings.groq_configured,
    )


# ────────────────────────────────────────────────────────────────────
# Test generation
# ────────────────────────────────────────────────────────────────────


@router.post(
    "/generate-test",
    response_model=GenerateTestResponse,
    dependencies=[Depends(rate_limit_dependency)],
)
async def generate_test(req: GenerateTestRequest) -> GenerateTestResponse:
    """Generate a challenge using Groq (or fall back to the local bank)."""
    settings = get_settings()
    cache_key = _challenge_cache_key(req)

    cached = _challenge_cache.get(cache_key)
    if cached is not None:
        log.info("generate_test_cache_hit", sector=req.sector)
        return cached

    if settings.groq_configured:
        try:
            prompt = _build_generation_prompt(req)
            parsed = await call_groq(
                prompt=prompt,
                system="You are a technical assessment author. Return ONLY valid JSON.",
                json_mode=True,
                temperature=0.7,
            )
            response = GenerateTestResponse(
                title=parsed["title"],
                round1_questions=parsed["round1_questions"],
                round2_problem=parsed["round2_problem"],
                round3_scenario=parsed["round3_scenario"],
            )
            _challenge_cache[cache_key] = response
            log.info("generate_test_ok", sector=req.sector, source="groq")
            return response
        except (GroqJSONError, KeyError) as e:
            log.warning("generate_test_groq_malformed", error=str(e), sector=req.sector)
        except GroqError as e:
            log.warning("generate_test_groq_unavailable", error=str(e), sector=req.sector)

    # Fallback
    fb = get_fallback_challenge(req.sector, req.problem_description)
    response = GenerateTestResponse(**fb)
    _challenge_cache[cache_key] = response
    log.info("generate_test_ok", sector=req.sector, source="fallback")
    return response


def _build_generation_prompt(req: GenerateTestRequest) -> str:
    return f"""
You are creating a skills assessment for a {req.sector} role at difficulty: {req.difficulty}.
Problem context: {req.problem_description}

Generate a JSON response with:
1. "title": A short challenge title (max 10 words)
2. "round1_questions": Array of {req.num_questions} MCQ objects focused on aptitude, logical reasoning, and blood relations (NOT coding questions). Keys: id, question, options (4 choices), correct (0-indexed integer)
3. "round2_problem": A LeetCode-style coding problem description (2-3 sentences)
4. "round3_scenario": A real-world industry scenario (3-4 sentences)

Return ONLY valid JSON, no markdown formatting or backticks.
"""


# ────────────────────────────────────────────────────────────────────
# Code evaluation
# ────────────────────────────────────────────────────────────────────


@router.post(
    "/evaluate-code",
    response_model=EvaluateCodeResponse,
    dependencies=[Depends(rate_limit_dependency)],
)
async def evaluate_code(req: SubmissionEval) -> EvaluateCodeResponse:
    """Execute code via Piston. Auth-free because the exam runs client-side."""
    try:
        result = await execute_code(req.code, req.language)
    except PistonError as e:
        log.error("evaluate_code_failed", language=req.language, error=str(e))
        # Return a structured failure rather than a 500 so the frontend
        # can show "execution unavailable" without crashing.
        return EvaluateCodeResponse(
            stdout="",
            stderr=str(e),
            success=False,
            exit_code=None,
            language=req.language,
        )
    return EvaluateCodeResponse(**result)


# ────────────────────────────────────────────────────────────────────
# AI recommendation
# ────────────────────────────────────────────────────────────────────


@router.post(
    "/recommendation",
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_recommendation(
    req: RecommendationRequest,
    user=Depends(require_user),
) -> dict:
    """AI-powered career recommendation via Groq. Requires auth."""
    settings = get_settings()
    if not settings.groq_configured:
        return {
            "recommendation": (
                f"Focus on deepening your {req.sector} expertise. With a score of "
                f"{req.performance_score}/100, consider practicing system design patterns "
                "and contributing to open-source projects. "
                "(Set GROQ_API_KEY for AI-powered recommendations.)"
            )
        }

    prompt = (
        f"Act as a Principal Engineer. A candidate has:\n"
        f"- Skills: {', '.join(req.user_skills)}\n"
        f"- Score: {req.performance_score}/100\n"
        f"- Sector: {req.sector}\n\n"
        f"Provide a 2-3 sentence highly actionable career recommendation. "
        f"Be specific and direct."
    )
    try:
        text = await call_groq(prompt=prompt, temperature=0.7)
        return {"recommendation": text}
    except GroqError as e:
        log.error("recommendation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recommendation service unavailable.",
        )


# ────────────────────────────────────────────────────────────────────
# Integrity report
# ────────────────────────────────────────────────────────────────────


@router.post("/integrity-report")
async def integrity_report(
    req: IntegrityReport,
    user=Depends(require_user),
) -> dict:
    """Store integrity violations in Supabase. Requires auth."""
    sb = get_supabase()
    if sb:
        try:
            sb.table("submissions").update({
                "integrity_warnings": req.warnings,
                "integrity_events": req.events,
                "status": "disqualified" if req.warnings >= 3 else None,
            }).eq("applicant_id", req.applicant_id).eq(
                "challenge_id", req.challenge_id
            ).execute()
        except Exception as e:
            # Log but don't fail the request — the proctoring data is
            # best-effort and shouldn't block the user's exam flow.
            log.error("integrity_report_supabase_failed", error=str(e))

    severity = (
        "critical" if req.warnings >= 3
        else "warning" if req.warnings > 0
        else "clean"
    )
    return {
        "status": severity,
        "warnings": req.warnings,
        "message": f"Integrity report processed. {req.warnings} violation(s) recorded.",
    }


# ────────────────────────────────────────────────────────────────────
# Future-proof strategy
# ────────────────────────────────────────────────────────────────────


@router.post(
    "/future-proof-strategy",
    dependencies=[Depends(rate_limit_dependency)],
)
async def future_proof_strategy(
    req: FutureProofRequest,
    user=Depends(require_role("company")),
) -> dict:
    """Generate a Future-Proof strategic blueprint. Requires `company` role."""
    settings = get_settings()
    if settings.groq_configured:
        prompt = (
            f"Act as a Principal Innovation Strategist.\n"
            f"Company Sector: {req.sector}\n"
            f"Current Stack: {req.tech_stack}\n"
            f"Business Challenge: {req.business_challenge}\n\n"
            "Provide a concise, 3-point strategic blueprint for how this "
            "organization can future-proof itself and remain relevant. "
            "Keep it under 100 words total. Format as bullet points."
        )
        try:
            text = await call_groq(prompt=prompt, temperature=0.7)
            return {"strategy": text}
        except GroqError as e:
            log.warning("future_proof_groq_failed", error=str(e))

    return {
        "strategy": (
            "• Modernize Legacy Architecture: Migrate core services to "
            "microservices to improve agility.\n"
            "• Upskill Workforce: Invest heavily in continuous AI-literacy "
            "training for your engineering teams.\n"
            "• Adopt Emerging Tech: Evaluate specialized open-source tools "
            "within your stack to reduce dependency lock-in."
        )
    }


# ────────────────────────────────────────────────────────────────────
# Challenges & leaderboard (read-through to Supabase)
# ────────────────────────────────────────────────────────────────────


@router.get("/challenges")
async def list_challenges(
    sector: Optional[str] = Query(default=None),
    difficulty: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> List[dict]:
    """Public: list active challenges. Returns [] when Supabase is off."""
    sb = get_supabase()
    if sb is None:
        return []

    query = sb.table("challenges").select("*").eq("is_active", True).limit(limit)
    if sector:
        query = query.eq("sector", sector)
    if difficulty:
        query = query.eq("difficulty", difficulty)

    try:
        result = query.execute()
        return result.data
    except Exception as e:
        log.error("list_challenges_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch challenges.",
        )


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    sector: Optional[str] = Query(default=None),
) -> List[dict]:
    """Public: leaderboard view. Returns [] when Supabase is off."""
    sb = get_supabase()
    if sb is None:
        return []

    query = sb.table("leaderboard").select("*").limit(limit)
    if sector:
        query = query.eq("sector", sector)

    try:
        result = query.execute()
        return result.data
    except Exception as e:
        log.error("leaderboard_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch leaderboard.",
        )
