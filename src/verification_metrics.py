"""Verification metrics for *manually-authored / generated* test cases.

A good manual test case is judged on several independent qualities, not one. This
module encodes the standard QA verification dimensions as DeepEval **G-Eval**
metrics — each with its own plain-English rubric, all sharing the configured
judge and the 0.7 threshold. Together they form a verification *matrix*: every
test case is scored on every dimension.

Dimensions (the things a reviewer verifies on a manual test case):
  1. Atomicity        — one focused scenario, not many bundled together
  2. Traceability     — clearly exercises the stated requirement
  3. Clarity          — unambiguous, understandable wording
  4. Completeness     — has pre-conditions, steps, test data, expected result
  5. Reproducibility  — concrete & deterministic; anyone can repeat it identically
  6. Correctness      — the expected result is actually correct for the requirement
  7. Coverage         — exercises the requirement's behaviour (incl. negative/boundary)
  8. Verifiability    — expected result is explicit and observable/checkable
  9. Independence     — self-contained; no hidden dependence on other test cases
"""
from __future__ import annotations

from dataclasses import dataclass, field

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from . import config
from .judge import get_judge

# In every metric the judge sees the requirement (input) and the test case (output).
_PARAMS = [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]


@dataclass
class VerificationMetric:
    """One verification dimension, expressed as a G-Eval rubric."""

    key: str
    name: str
    description: str
    steps: list[str] = field(default_factory=list)

    def build(self) -> GEval:
        return GEval(
            name=self.name,
            evaluation_steps=self.steps,
            evaluation_params=_PARAMS,
            model=get_judge(),
            threshold=config.THRESHOLD,
        )


# The registry — order is the report's column order.
VERIFICATION_METRICS: list[VerificationMetric] = [
    VerificationMetric(
        key="atomicity",
        name="Atomicity",
        description="Tests a single, focused scenario rather than many bundled together.",
        steps=[
            "Read the requirement (input) and the test case (actual output).",
            "Judge whether the test case verifies exactly one focused scenario.",
            "Penalize test cases that bundle several unrelated checks into one.",
        ],
    ),
    VerificationMetric(
        key="traceability",
        name="Traceability",
        description="Clearly and directly exercises the stated requirement.",
        steps=[
            "Read the requirement (input) and the test case (actual output).",
            "Judge whether the test case clearly maps to and exercises that requirement.",
            "Penalize test cases that drift to unrelated behaviour or are only loosely related.",
        ],
    ),
    VerificationMetric(
        key="clarity",
        name="Clarity",
        description="Unambiguous, understandable wording an executor can follow.",
        steps=[
            "Read the test case (actual output).",
            "Judge whether the wording is clear, specific, and unambiguous.",
            "Penalize vague verbs ('check it works'), undefined terms, or ambiguous phrasing.",
        ],
    ),
    VerificationMetric(
        key="completeness",
        name="Completeness",
        description="Includes pre-conditions, concrete steps, test data, and an expected result.",
        steps=[
            "Read the test case (actual output).",
            "Check it contains: a pre-condition/setup, ordered steps, concrete test data, "
            "and an expected result.",
            "Penalize proportionally for each of these elements that is missing or empty.",
        ],
    ),
    VerificationMetric(
        key="reproducibility",
        name="Reproducibility",
        description="Concrete and deterministic so any executor repeats it identically.",
        steps=[
            "Read the test case (actual output).",
            "Judge whether two different testers following it would do the exact same thing "
            "and reach the same outcome.",
            "Penalize placeholders, missing data, or non-deterministic/ambiguous instructions.",
        ],
    ),
    VerificationMetric(
        key="correctness",
        name="Correctness",
        description="The expected result is actually correct for the requirement.",
        steps=[
            "Read the requirement (input) and the test case's expected result (actual output).",
            "Judge whether the stated expected result is factually correct per the requirement.",
            "Penalize expected results that contradict or misstate the requirement.",
        ],
    ),
    VerificationMetric(
        key="coverage",
        name="Coverage",
        description="Exercises the requirement's behaviour, including negative/boundary where relevant.",
        steps=[
            "Read the requirement (input) and the test case (actual output).",
            "Judge how well the test case covers the requirement's behaviour, including any "
            "relevant negative, empty, or boundary condition the requirement implies.",
            "Penalize test cases that only touch the happy path when the requirement states rules "
            "or edge conditions.",
        ],
    ),
    VerificationMetric(
        key="verifiability",
        name="Verifiability",
        description="The expected result is explicit and observable/checkable.",
        steps=[
            "Read the test case's expected result (actual output).",
            "Judge whether the expected result is explicit, observable, and objectively checkable "
            "(a tester can clearly decide pass/fail).",
            "Penalize vague, subjective, or missing expected results.",
        ],
    ),
    VerificationMetric(
        key="independence",
        name="Independence",
        description="Self-contained; does not secretly depend on other test cases' state.",
        steps=[
            "Read the test case (actual output).",
            "Judge whether it is self-contained — its pre-conditions establish all needed state.",
            "Penalize hidden dependence on the outcome or leftover state of another test case.",
        ],
    ),
]

# key -> metric, for lookups.
BY_KEY = {m.key: m for m in VERIFICATION_METRICS}


def all_verification_metrics() -> list[GEval]:
    """Fresh G-Eval instances for every verification dimension."""
    return [m.build() for m in VERIFICATION_METRICS]
