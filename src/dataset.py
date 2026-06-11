"""The evaluation dataset.

Each :class:`EvalSpec` represents one functional test case turned into an
LLM-judged evaluation. The framing: an LLM-powered *Google Search Help
Assistant* answers user questions about how search works, grounded in the
Functional Requirements Document (FRD). DeepEval then checks the assistant's
answer is relevant, faithful to the FRD, and free of hallucinations.

Why include deliberately BAD answers?
-------------------------------------
To measure *how accurate DeepEval itself is*, you need a labelled set. Every
spec carries ``expect`` — the verdict a correct judge SHOULD return for each
metric. The runner compares DeepEval's verdict to these labels and reports the
agreement rate (a confusion-matrix-style meta-evaluation). Golden cases should
pass all metrics; adversarial cases should fail the metric they target.

* ``context`` / ``retrieval_context`` are taken verbatim from the FRD so the
  faithfulness & hallucination metrics grade against real ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from deepeval.test_case import LLMTestCase

# Metric display names (must match DeepEval's ``metric.__name__``).
ANSWER_RELEVANCY = "Answer Relevancy"
FAITHFULNESS = "Faithfulness"
HALLUCINATION = "Hallucination"


@dataclass
class EvalSpec:
    """A single labelled evaluation case."""

    id: str
    requirement_id: str
    kind: str  # "golden" (good answer) or "adversarial" (bad answer)
    user_input: str
    actual_output: str
    context: list[str]  # ground-truth facts from the FRD
    # Expected pass/fail verdict per metric for a correct judge.
    expect: dict[str, bool] = field(default_factory=dict)

    @property
    def retrieval_context(self) -> list[str]:
        # In this suite the requirement text is both the retrieved context
        # (faithfulness) and the ground-truth context (hallucination).
        return self.context

    def to_llm_test_case(self) -> LLMTestCase:
        return LLMTestCase(
            input=self.user_input,
            actual_output=self.actual_output,
            retrieval_context=self.retrieval_context,
            context=self.context,
        )


# --- Ground-truth context lifted from the FRD -----------------------------
CTX = {
    "FR-GS-01": [
        "Google Search accepts free-text input in the search box. Pressing Enter or "
        "clicking the Google Search button executes a search and navigates to a results "
        "page (SERP) of organic results relevant to the query. An empty or whitespace-only "
        "query does not trigger navigation to a SERP."
    ],
    "FR-GS-02": [
        "While the user types, Google shows a dropdown of autocomplete suggestions that "
        "update in real time on each keystroke. Selecting a suggestion fills the search box "
        "with it and executes the search. An empty box shows no query-based suggestions."
    ],
    "FR-GS-03": [
        "Each organic result on the SERP shows a clickable title (a link), a destination URL, "
        "and a descriptive snippet. Results are ordered by relevance, most relevant first. "
        "Clicking a result title navigates to the destination page."
    ],
    "FR-GS-04": [
        "The 'I'm Feeling Lucky' button, for a non-empty query, bypasses the results page and "
        "navigates the user directly to the top-ranked organic result. With an empty query it "
        "does not perform a lucky navigation."
    ],
    "FR-GS-05": [
        "When a query is likely misspelled, Google shows a corrected-spelling suggestion such "
        "as 'Showing results for X' or 'Did you mean: X', returns results for the corrected "
        "term, and still offers a link to search for the original term as typed."
    ],
}


# =====================================================================
# GOLDEN CASES — one per requirement. Good answers; should pass all metrics.
# =====================================================================
GOLDEN: list[EvalSpec] = [
    EvalSpec(
        id="TC-GS-01",
        requirement_id="FR-GS-01",
        kind="golden",
        user_input="How do I run a search on Google after typing my query?",
        actual_output=(
            "Type your query into the search box and either press Enter or click the "
            "Google Search button. Google then opens a results page listing organic "
            "results relevant to your query. If the box is empty it won't run a search."
        ),
        context=CTX["FR-GS-01"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: True, HALLUCINATION: True},
    ),
    EvalSpec(
        id="TC-GS-02",
        requirement_id="FR-GS-02",
        kind="golden",
        user_input="What happens while I'm typing a query into the Google search box?",
        actual_output=(
            "As you type, a dropdown of autocomplete suggestions appears and updates with "
            "each keystroke. If you click one of the suggestions, it fills the search box "
            "and runs the search for you."
        ),
        context=CTX["FR-GS-02"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: True, HALLUCINATION: True},
    ),
    EvalSpec(
        id="TC-GS-03",
        requirement_id="FR-GS-03",
        kind="golden",
        user_input="What does each result on the Google results page contain, and how are they ordered?",
        actual_output=(
            "Each organic result shows a clickable title link, the destination URL, and a "
            "short snippet describing the page. Results are ordered by relevance, with the "
            "most relevant one listed first, and clicking a title opens that page."
        ),
        context=CTX["FR-GS-03"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: True, HALLUCINATION: True},
    ),
    EvalSpec(
        id="TC-GS-04",
        requirement_id="FR-GS-04",
        kind="golden",
        user_input="What does the 'I'm Feeling Lucky' button do?",
        actual_output=(
            "For a non-empty query, 'I'm Feeling Lucky' skips the results page and takes you "
            "straight to the top-ranked organic result for that query. With an empty box it "
            "does nothing."
        ),
        context=CTX["FR-GS-04"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: True, HALLUCINATION: True},
    ),
    EvalSpec(
        id="TC-GS-05",
        requirement_id="FR-GS-05",
        kind="golden",
        user_input="What happens if I misspell my search term?",
        actual_output=(
            "Google detects the likely misspelling and shows a corrected suggestion like "
            "'Showing results for ...' or 'Did you mean: ...', returns results for the "
            "corrected term, and still gives you a link to search your original spelling."
        ),
        context=CTX["FR-GS-05"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: True, HALLUCINATION: True},
    ),
]


# =====================================================================
# ADVERSARIAL CASES — deliberately flawed answers used to verify the
# metrics actually CATCH problems. Each targets one failure mode.
# =====================================================================
ADVERSARIAL: list[EvalSpec] = [
    # Irrelevant answer -> Answer Relevancy should FAIL.
    EvalSpec(
        id="ADV-RELEVANCY",
        requirement_id="FR-GS-01",
        kind="adversarial",
        user_input="How do I run a search on Google after typing my query?",
        actual_output=(
            "Google was founded in 1998 by Larry Page and Sergey Brin, and its headquarters "
            "is in Mountain View, California. The company also makes the Android operating "
            "system and the Chrome browser."
        ),
        context=CTX["FR-GS-01"],
        expect={ANSWER_RELEVANCY: False, FAITHFULNESS: True, HALLUCINATION: True},
    ),
    # Contradicts the retrieved requirement -> Faithfulness should FAIL.
    EvalSpec(
        id="ADV-FAITHFULNESS",
        requirement_id="FR-GS-04",
        kind="adversarial",
        user_input="What does the 'I'm Feeling Lucky' button do?",
        actual_output=(
            "'I'm Feeling Lucky' opens the full results page and shows you a random "
            "assortment of ten results, none of which are ranked by relevance."
        ),
        context=CTX["FR-GS-04"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: False, HALLUCINATION: False},
    ),
    # Invents facts not supported by (and contradicting) context -> Hallucination should FAIL.
    EvalSpec(
        id="ADV-HALLUCINATION",
        requirement_id="FR-GS-02",
        kind="adversarial",
        user_input="What happens while I'm typing a query into the Google search box?",
        actual_output=(
            "While typing, Google charges you 5 cents per suggestion and requires you to log "
            "in with a fingerprint before any autocomplete results are shown. Suggestions "
            "only appear after you finish typing and press the spacebar twice."
        ),
        context=CTX["FR-GS-02"],
        expect={ANSWER_RELEVANCY: True, FAITHFULNESS: False, HALLUCINATION: False},
    ),
]


ALL_SPECS: list[EvalSpec] = GOLDEN + ADVERSARIAL


def goldens() -> list[EvalSpec]:
    return list(GOLDEN)


def adversarials() -> list[EvalSpec]:
    return list(ADVERSARIAL)
