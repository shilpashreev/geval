"""Central configuration for the DeepEval evaluation suite.

All tunables live here so the metrics, runner, and pytest suite stay consistent.
"""
from __future__ import annotations

import os

# Load a local .env (gitignored) so API keys never need to live in source code
# or be exported manually. Real environment variables still take precedence.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv optional; env vars still work without it
    pass

# --- Evaluation threshold -------------------------------------------------
# A metric "passes" when its score is >= THRESHOLD.
# The requirement for this project is 0.7 and above.
THRESHOLD: float = float(os.getenv("DEEPEVAL_THRESHOLD", "0.7"))

# --- Judge LLM (LLM-as-a-judge) ------------------------------------------
# DeepEval scores every metric with an LLM. Three providers are supported:
#   * "ollama"    -> a local model via Ollama (offline, no API key)
#   * "openai"    -> GPT via the OpenAI API   (needs OPENAI_API_KEY)
#   * "anthropic" -> Claude via the Anthropic API (needs ANTHROPIC_API_KEY)
# Choose with DEEPEVAL_JUDGE_PROVIDER (default: ollama, so the suite runs
# anywhere offline). Set a hosted provider + its key for higher accuracy.
# NOTE: API keys are read from the environment / .env only — never hardcode a
# secret in source. Copy .env.example -> .env and fill it in.
JUDGE_PROVIDER: str = os.getenv("DEEPEVAL_JUDGE_PROVIDER", "ollama").lower()

# Anthropic judge: `claude-sonnet-4-6` is a strong, cost-effective default;
# switch to an Opus model for the most rigorous (and pricier) judging.
JUDGE_MODEL: str = os.getenv("DEEPEVAL_JUDGE_MODEL", "claude-sonnet-4-6-20250514")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

# OpenAI judge: gpt-4o-mini is cheap & capable; gpt-4o for stricter grading.
OPENAI_MODEL: str = os.getenv("DEEPEVAL_OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

# Ollama judge: a locally-served model (fully offline). gemma3:4b is a small,
# fast default; a larger model gives more reliable verdicts.
OLLAMA_MODEL: str = os.getenv("DEEPEVAL_OLLAMA_MODEL", "gemma3:4b")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Determinism: a low temperature makes the judge's verdicts more repeatable.
JUDGE_TEMPERATURE: float = float(os.getenv("DEEPEVAL_JUDGE_TEMPERATURE", "0.0"))


def judge_label() -> str:
    """Human-readable identifier of the active judge."""
    if JUDGE_PROVIDER == "ollama":
        return f"ollama:{OLLAMA_MODEL}"
    if JUDGE_PROVIDER == "openai":
        return f"openai:{OPENAI_MODEL}"
    return f"anthropic:{JUDGE_MODEL}"


def require_openai_key() -> str:
    """Return the OpenAI API key or raise a clear, actionable error."""
    if not OPENAI_API_KEY:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set but DEEPEVAL_JUDGE_PROVIDER=openai. "
            "Add it to .env (OPENAI_API_KEY=sk-...) or your environment."
        )
    return OPENAI_API_KEY


def ensure_judge_ready() -> None:
    """Validate that the active judge provider has what it needs to run."""
    if JUDGE_PROVIDER == "anthropic":
        require_api_key()
    elif JUDGE_PROVIDER == "openai":
        require_openai_key()
    # "ollama" needs no API key.


def judge_available() -> bool:
    """True if the active provider can run (used to skip tests gracefully)."""
    if JUDGE_PROVIDER == "ollama":
        return True
    if JUDGE_PROVIDER == "openai":
        return bool(OPENAI_API_KEY)
    return bool(ANTHROPIC_API_KEY)


def require_api_key() -> str:
    """Return the Anthropic API key or raise a clear, actionable error."""
    if not ANTHROPIC_API_KEY:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. The DeepEval metrics use Claude as the "
            "judge LLM and cannot run without it.\n"
            "  PowerShell:  $env:ANTHROPIC_API_KEY = 'sk-ant-...'\n"
            "  bash:        export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Or copy .env.example to .env and fill it in."
        )
    return ANTHROPIC_API_KEY
