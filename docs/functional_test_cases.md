# Functional Test Cases — Google Search Page

**Document ID:** TC-GS-001
**Linked FRD:** `functional_requirements.md` (FRD-GS-001 v1.0)
**Type:** Functional
**Total cases:** 5 (one primary case per functional requirement)

Each test case is traceable to a single functional requirement and is mirrored as a
DeepEval `LLMTestCase` in `src/dataset.py`, where the requirement text becomes the
ground-truth `context`/`retrieval_context` used by the faithfulness & hallucination metrics.

---

## TC-GS-01 — Execute a keyword search
**Maps to:** FR-GS-01
**Priority:** High

| Field | Value |
|-------|-------|
| **Pre-condition** | Browser open at `https://www.google.com` |
| **Test data** | Query: `weather in London` |
| **Steps** | 1. Click the search box. 2. Type `weather in London`. 3. Press **Enter**. |
| **Expected result** | A SERP loads showing a list of organic results relevant to "weather in London". |
| **Negative variant** | Submitting an empty query does **not** navigate to a SERP. |

## TC-GS-02 — Autocomplete suggestions while typing
**Maps to:** FR-GS-02
**Priority:** Medium

| Field | Value |
|-------|-------|
| **Pre-condition** | Browser open at `https://www.google.com` |
| **Test data** | Partial query: `new y` |
| **Steps** | 1. Click the search box. 2. Type `new y`. 3. Observe the dropdown. 4. Click a suggestion (e.g. `new york`). |
| **Expected result** | A dropdown of suggestions appears and updates per keystroke; selecting one fills the box and runs the search. |

## TC-GS-03 — Results display structure & relevance
**Maps to:** FR-GS-03
**Priority:** High

| Field | Value |
|-------|-------|
| **Pre-condition** | A SERP is displayed for query `python programming` |
| **Test data** | Query: `python programming` |
| **Steps** | 1. Search `python programming`. 2. Inspect the first three results. |
| **Expected result** | Each result shows a clickable title, a URL, and a snippet; results are ordered most-relevant first. |

## TC-GS-04 — "I'm Feeling Lucky" direct navigation
**Maps to:** FR-GS-04
**Priority:** Medium

| Field | Value |
|-------|-------|
| **Pre-condition** | Browser open at `https://www.google.com` |
| **Test data** | Query: `wikipedia` |
| **Steps** | 1. Type `wikipedia`. 2. Click **I'm Feeling Lucky**. |
| **Expected result** | The browser navigates directly to the top organic result (wikipedia.org) without showing a SERP. |

## TC-GS-05 — Spelling correction ("Did you mean")
**Maps to:** FR-GS-05
**Priority:** Medium

| Field | Value |
|-------|-------|
| **Pre-condition** | Browser open at `https://www.google.com` |
| **Test data** | Misspelled query: `recieve email` |
| **Steps** | 1. Search `recieve email`. 2. Observe the corrected-spelling banner. |
| **Expected result** | The SERP shows *"Showing results for receive email"* with results for the corrected term and a link to search the original term. |

---

## Traceability Matrix

| Test Case | Requirement | Requirement Summary | Coverage |
|-----------|-------------|---------------------|----------|
| TC-GS-01 | FR-GS-01 | Keyword search execution | ✅ |
| TC-GS-02 | FR-GS-02 | Autocomplete suggestions | ✅ |
| TC-GS-03 | FR-GS-03 | Results display & relevance | ✅ |
| TC-GS-04 | FR-GS-04 | "I'm Feeling Lucky" | ✅ |
| TC-GS-05 | FR-GS-05 | Spelling correction | ✅ |

**Coverage:** 5 / 5 requirements (100%).
