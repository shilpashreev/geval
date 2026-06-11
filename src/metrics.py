"""Factory for the three DeepEval metrics, all wired to the Claude judge.

Threshold semantics (important — they are NOT all the same direction):

* AnswerRelevancyMetric  -> higher is better, passes when score >= THRESHOLD
* FaithfulnessMetric     -> higher is better, passes when score >= THRESHOLD
* HallucinationMetric    -> LOWER  is better, passes when score <= THRESHOLD
                            (the score is the *fraction of context contradicted*)

So a trustworthy answer has high relevancy, high faithfulness, and a LOW
hallucination score. Keep this inversion in mind when reading results.
"""
from __future__ import annotations

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)

from . import config
from .judge import get_judge

# Metrics whose score should be >= threshold to pass.
HIGHER_IS_BETTER = {"Answer Relevancy", "Faithfulness"}
# Metrics whose score should be <= threshold to pass.
LOWER_IS_BETTER = {"Hallucination"}


def answer_relevancy() -> AnswerRelevancyMetric:
    """Is the answer relevant to the question that was asked?"""
    return AnswerRelevancyMetric(
        threshold=config.THRESHOLD,
        model=get_judge(),
        include_reason=True,
    )


def faithfulness() -> FaithfulnessMetric:
    """Does the answer stay faithful to the retrieved requirement context?"""
    return FaithfulnessMetric(
        threshold=config.THRESHOLD,
        model=get_judge(),
        include_reason=True,
    )


def hallucination() -> HallucinationMetric:
    """Does the answer contradict the ground-truth requirement facts?"""
    return HallucinationMetric(
        threshold=config.THRESHOLD,
        model=get_judge(),
        include_reason=True,
    )


def all_metrics():
    """Return fresh instances of all three metrics (metrics are stateful)."""
    return [answer_relevancy(), faithfulness(), hallucination()]


def passed(metric_name: str, score: float) -> bool:
    """Apply the correct pass rule for a metric given its raw score."""
    if metric_name in LOWER_IS_BETTER:
        return score <= config.THRESHOLD
    return score >= config.THRESHOLD
