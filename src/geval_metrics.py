"""G-Eval custom metric — grades the QUALITY of a generated test case.

This is the high-leverage DeepEval feature for a test-case-generator project:
instead of only checking factual answers, we grade whether an LLM-*authored*
test case is actually good — atomic, traceable to its requirement, with concrete
steps and an explicit expected result.

G-Eval lets you express that rubric in plain English (``evaluation_steps``) and
have the judge LLM score it 0-1. We keep the same Ollama/Claude judge and the
same 0.7 threshold as the rest of the suite.
"""
from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from . import config
from .judge import get_judge

# The grading rubric. Explicit steps make G-Eval far more repeatable than a
# single free-form `criteria` string.
TEST_CASE_QUALITY_STEPS = [
    "Read the requirement in 'input' and the proposed test case in 'actual output'.",
    "Check the test case targets exactly that requirement and is a single, atomic scenario.",
    "Check it contains concrete, ordered, executable steps (not vague instructions).",
    "Check it states an explicit, verifiable expected result.",
    "Check it uses concrete test data rather than placeholders or hand-waving.",
    "Heavily penalize vagueness, missing steps, or a missing/ambiguous expected result.",
]


def test_case_quality() -> GEval:
    """Return a G-Eval metric scoring generated test-case quality."""
    return GEval(
        name="Test Case Quality",
        evaluation_steps=TEST_CASE_QUALITY_STEPS,
        evaluation_params=[
            LLMTestCaseParams.INPUT,          # the requirement
            LLMTestCaseParams.ACTUAL_OUTPUT,  # the generated test case
        ],
        model=get_judge(),
        threshold=config.THRESHOLD,
    )
