"""Pytest suite — gate the golden cases through DeepEval's metrics.

Run with:
    deepeval test run tests/test_metrics.py      # rich DeepEval report
    pytest tests/test_metrics.py                  # plain pytest

Each golden QA case must satisfy all three core metrics at the 0.7 threshold,
and each good test-case-quality sample must satisfy the G-Eval metric. The
adversarial cases are intentionally bad and are exercised by
``src/run_evaluation.py`` (the meta-evaluation), not asserted here.

This is the CI gate: it fails the build when answer or test-case quality
regresses. By default it judges with the local Ollama model (no key needed);
it only skips if neither a local Ollama judge nor an Anthropic key is available.
"""
from __future__ import annotations

import pytest

from deepeval import assert_test

from src import config
from src.dataset import goldens
from src.geval_metrics import test_case_quality
from src.metrics import answer_relevancy, faithfulness, hallucination
from src.quality_dataset import quality_specs

pytestmark = pytest.mark.skipif(
    not config.judge_available(),
    reason="No judge available (set DEEPEVAL_JUDGE_PROVIDER + the matching API key).",
)


@pytest.mark.parametrize("spec", goldens(), ids=lambda s: s.id)
def test_golden_case_relevancy(spec):
    tc = spec.to_llm_test_case()
    metric = answer_relevancy()
    metric.measure(tc)
    assert metric.score >= config.THRESHOLD, f"{spec.id}: {metric.reason}"


@pytest.mark.parametrize("spec", goldens(), ids=lambda s: s.id)
def test_golden_case_faithfulness(spec):
    tc = spec.to_llm_test_case()
    metric = faithfulness()
    metric.measure(tc)
    assert metric.score >= config.THRESHOLD, f"{spec.id}: {metric.reason}"


@pytest.mark.parametrize("spec", goldens(), ids=lambda s: s.id)
def test_golden_case_hallucination(spec):
    # Hallucination is inverted: LOWER is better, so it must stay <= threshold.
    tc = spec.to_llm_test_case()
    metric = hallucination()
    metric.measure(tc)
    assert metric.score <= config.THRESHOLD, f"{spec.id}: {metric.reason}"


# Only the "good" generated test cases are gated; the deliberately poor sample
# is expected to fall below threshold and is checked in run_evaluation, not here.
_good_quality = [q for q in quality_specs() if q.expect_pass]


@pytest.mark.parametrize("spec", _good_quality, ids=lambda s: s.id)
def test_generated_test_case_quality(spec):
    # assert_test is DeepEval's idiomatic CI assertion (raises on failure).
    assert_test(spec.to_llm_test_case(), [test_case_quality()])
