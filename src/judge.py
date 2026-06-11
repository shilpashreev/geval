"""The LLM-as-a-judge used by every DeepEval metric.

DeepEval ships a native ``AnthropicModel``, so we simply wire it to the project
config. Centralising it here means every metric (and the pytest suite) grades
with the *same* Claude model under the *same* settings.
"""
from __future__ import annotations

from functools import lru_cache

from deepeval.models import AnthropicModel, DeepEvalBaseLLM, GPTModel, OllamaModel

from . import config


@lru_cache(maxsize=1)
def get_judge() -> DeepEvalBaseLLM:
    """Return a singleton judge model configured from ``config``.

    Provider is selected by ``DEEPEVAL_JUDGE_PROVIDER``:
      * "ollama"    -> local model, offline (default)
      * "openai"    -> GPT via the OpenAI API
      * "anthropic" -> Claude via the Anthropic API
    """
    if config.JUDGE_PROVIDER == "ollama":
        return OllamaModel(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.JUDGE_TEMPERATURE,
        )
    if config.JUDGE_PROVIDER == "openai":
        return GPTModel(
            model=config.OPENAI_MODEL,
            api_key=config.require_openai_key(),
            temperature=config.JUDGE_TEMPERATURE,
        )
    config.require_api_key()
    return AnthropicModel(
        model=config.JUDGE_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        temperature=config.JUDGE_TEMPERATURE,
    )
