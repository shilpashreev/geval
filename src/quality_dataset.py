"""Labelled dataset for the G-Eval *test-case quality* metric.

Each case pairs a requirement (``input``) with a generated test case
(``actual_output``). Good cases should score >= 0.7; the poor case (vague, no
steps, no expected result) should score below it — proving G-Eval catches
low-quality generation, which is the whole point for a test-case generator.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from deepeval.test_case import LLMTestCase


@dataclass
class QualitySpec:
    id: str
    requirement_id: str
    requirement: str       # input
    generated_test_case: str  # actual_output
    expect_pass: bool      # should this score >= threshold?
    note: str = field(default="")

    def to_llm_test_case(self) -> LLMTestCase:
        return LLMTestCase(input=self.requirement, actual_output=self.generated_test_case)


QUALITY_SPECS: list[QualitySpec] = [
    QualitySpec(
        id="Q-GOOD-01",
        requirement_id="FR-GS-01",
        requirement=(
            "FR-GS-01: The system shall execute a search and show a results page of organic "
            "results when the user enters a non-empty query and presses Enter or clicks Search."
        ),
        generated_test_case=(
            "Title: Execute a keyword search.\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: query = 'weather in London'.\n"
            "Steps: 1) Click the search box. 2) Type 'weather in London'. 3) Press Enter.\n"
            "Expected result: A results page loads listing organic results relevant to "
            "'weather in London'."
        ),
        expect_pass=True,
        note="Atomic, concrete steps, explicit expected result.",
    ),
    QualitySpec(
        id="Q-GOOD-02",
        requirement_id="FR-GS-04",
        requirement=(
            "FR-GS-04: 'I'm Feeling Lucky' shall, for a non-empty query, navigate directly to "
            "the top-ranked organic result, bypassing the results page."
        ),
        generated_test_case=(
            "Title: 'I'm Feeling Lucky' direct navigation.\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: query = 'wikipedia'.\n"
            "Steps: 1) Type 'wikipedia' in the search box. 2) Click 'I'm Feeling Lucky'.\n"
            "Expected result: The browser navigates directly to wikipedia.org without showing "
            "a results page."
        ),
        expect_pass=True,
        note="Clear, traceable, verifiable.",
    ),
    QualitySpec(
        id="Q-BAD-01",
        requirement_id="FR-GS-02",
        requirement=(
            "FR-GS-02: While typing, the system shall show autocomplete suggestions that update "
            "in real time; selecting one fills the box and runs the search."
        ),
        generated_test_case=(
            "Test the search suggestions. Type something and check it works. It should be fine."
        ),
        expect_pass=False,
        note="Vague: no concrete data, no ordered steps, no verifiable expected result.",
    ),
]


def quality_specs() -> list[QualitySpec]:
    return list(QUALITY_SPECS)
