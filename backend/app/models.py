"""
Pydantic request/response models with strict validation.

Replaces the loose models in the MVP `main.py` with validated, typed
schemas. All user-supplied strings are length-bounded to prevent prompt
injection and resource exhaustion via oversized payloads.
"""
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Allowed enum-like values (mirrors the Supabase CHECK constraints) ──
ALLOWED_SECTORS = {"web_dev", "mobile_dev", "data_ai", "cloud_devops", "cybersecurity"}
ALLOWED_DIFFICULTIES = {"Easy", "Medium", "Hard"}
ALLOWED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"}


class GenerateTestRequest(BaseModel):
    sector: str = Field(..., description="Target sector for the challenge")
    problem_description: str = Field(
        ..., min_length=10, max_length=2000,
        description="Problem context the generated challenge should address",
    )
    difficulty: str = Field(default="Medium")
    num_questions: int = Field(default=5, ge=1, le=20)

    @field_validator("sector")
    @classmethod
    def _validate_sector(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ALLOWED_SECTORS:
            raise ValueError(f"sector must be one of {sorted(ALLOWED_SECTORS)}")
        return v

    @field_validator("difficulty")
    @classmethod
    def _validate_difficulty(cls, v: str) -> str:
        v = v.capitalize().strip()
        if v not in ALLOWED_DIFFICULTIES:
            raise ValueError(f"difficulty must be one of {sorted(ALLOWED_DIFFICULTIES)}")
        return v


class SubmissionEval(BaseModel):
    code: str = Field(..., min_length=1, max_length=50_000)
    language: str = Field(default="python")
    test_cases: List[dict] = Field(default_factory=list)

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ALLOWED_LANGUAGES:
            raise ValueError(f"language must be one of {sorted(ALLOWED_LANGUAGES)}")
        return v


class RecommendationRequest(BaseModel):
    user_skills: List[str] = Field(..., min_length=1, max_length=20)
    performance_score: int = Field(..., ge=0, le=100)
    sector: str = Field(...)

    @field_validator("sector")
    @classmethod
    def _validate_sector(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ALLOWED_SECTORS:
            raise ValueError(f"sector must be one of {sorted(ALLOWED_SECTORS)}")
        return v

    @field_validator("user_skills")
    @classmethod
    def _validate_skills(cls, v: List[str]) -> List[str]:
        # Strip + de-dup + cap each skill at 50 chars
        seen = set()
        cleaned = []
        for s in v:
            s = s.strip()[:50]
            if s and s not in seen:
                seen.add(s)
                cleaned.append(s)
        if not cleaned:
            raise ValueError("user_skills must contain at least one non-empty skill")
        return cleaned


class IntegrityReport(BaseModel):
    applicant_id: str = Field(..., min_length=1, max_length=200)
    challenge_id: str = Field(..., min_length=1, max_length=200)
    warnings: int = Field(..., ge=0, le=100)
    events: List[dict] = Field(default_factory=list, max_length=500)


class FutureProofRequest(BaseModel):
    sector: str = Field(..., min_length=2, max_length=100)
    tech_stack: str = Field(..., min_length=2, max_length=500)
    business_challenge: str = Field(..., min_length=10, max_length=2000)


# ── Response models (so OpenAPI docs + clients get typed contracts) ──


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    supabase_configured: bool
    groq_configured: bool


class GenerateTestResponse(BaseModel):
    title: str
    round1_questions: List[dict]
    round2_problem: str
    round3_scenario: str


class EvaluateCodeResponse(BaseModel):
    stdout: str
    stderr: str
    success: bool
    exit_code: Optional[int] = None
    language: str
