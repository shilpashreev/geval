"""The 5 generated manual test cases (from docs/functional_test_cases.md).

Each is paired with its requirement so the verification metrics can grade the
test case against what it is supposed to verify. ``requirement`` is the metric
``input``; ``test_case`` is the ``actual_output`` under verification.
"""
from __future__ import annotations

from dataclasses import dataclass

from deepeval.test_case import LLMTestCase

from .dataset import CTX


@dataclass
class ManualTest:
    id: str
    requirement_id: str
    test_case: str

    @property
    def requirement(self) -> str:
        return CTX[self.requirement_id][0]

    def to_llm_test_case(self) -> LLMTestCase:
        return LLMTestCase(input=self.requirement, actual_output=self.test_case)


MANUAL_TESTS: list[ManualTest] = [
    ManualTest(
        id="TC-GS-01",
        requirement_id="FR-GS-01",
        test_case=(
            "Title: Execute a keyword search.\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: query = 'weather in London'.\n"
            "Steps: 1) Click the search box. 2) Type 'weather in London'. 3) Press Enter.\n"
            "Expected result: A results page (SERP) loads showing a list of organic results "
            "relevant to 'weather in London'.\n"
            "Negative variant: Submitting an empty query does not navigate to a SERP."
        ),
    ),
    ManualTest(
        id="TC-GS-02",
        requirement_id="FR-GS-02",
        test_case=(
            "Title: Autocomplete suggestions while typing.\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: partial query = 'new y'.\n"
            "Steps: 1) Click the search box. 2) Type 'new y'. 3) Observe the dropdown. "
            "4) Click a suggestion (e.g. 'new york').\n"
            "Expected result: A dropdown of suggestions appears and updates per keystroke; "
            "selecting one fills the box and runs the search."
        ),
    ),
    ManualTest(
        id="TC-GS-03",
        requirement_id="FR-GS-03",
        test_case=(
            "Title: Results display structure and relevance.\n"
            "Pre-condition: A SERP is displayed for query 'python programming'.\n"
            "Test data: query = 'python programming'.\n"
            "Steps: 1) Search 'python programming'. 2) Inspect the first three results.\n"
            "Expected result: Each result shows a clickable title, a URL, and a snippet; "
            "results are ordered most-relevant first."
        ),
    ),
    ManualTest(
        id="TC-GS-04",
        requirement_id="FR-GS-04",
        test_case=(
            "Title: 'I'm Feeling Lucky' direct navigation.\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: query = 'wikipedia'.\n"
            "Steps: 1) Type 'wikipedia'. 2) Click 'I'm Feeling Lucky'.\n"
            "Expected result: The browser navigates directly to the top organic result "
            "(wikipedia.org) without showing a SERP."
        ),
    ),
    ManualTest(
        id="TC-GS-05",
        requirement_id="FR-GS-05",
        test_case=(
            "Title: Spelling correction ('Did you mean').\n"
            "Pre-condition: Browser open at https://www.google.com.\n"
            "Test data: misspelled query = 'recieve email'.\n"
            "Steps: 1) Search 'recieve email'. 2) Observe the corrected-spelling banner.\n"
            "Expected result: The SERP shows 'Showing results for receive email' with results "
            "for the corrected term and a link to search the original term."
        ),
    ),
]


def manual_tests() -> list[ManualTest]:
    return list(MANUAL_TESTS)
