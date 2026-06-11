# CLAUDE.md

Guidance for Claude Code (and contributors) working in this repository.

## What this project is

A small, structured reference implementation that:

1. Documents **functional requirements** for the Google Search page (`docs/functional_requirements.md`).
2. Derives **functional test cases**, traced 1:1 to those requirements (`docs/functional_test_cases.md`).
3. Evaluates LLM-generated answers about that functionality using **DeepEval** with three
   LLM-as-judge metrics — **Answer Relevancy**, **Faithfulness**, **Hallucination** — at a
   **0.7 threshold**, judged by **Claude** (`claude-sonnet-4-6`).
4. Measures **how accurate DeepEval itself is** via a labelled golden/adversarial dataset
   (a meta-evaluation).

## Layout

```
docs/                       Requirements & test cases (human-readable, the source of truth)
  functional_requirements.md
  functional_test_cases.md
src/
  config.py                 Threshold (0.7), judge model, API-key handling
  judge.py                  Singleton Claude judge (deepeval AnthropicModel)
  metrics.py                The 3 metric factories + pass-rule helper
  dataset.py                Labelled EvalSpecs (5 golden + 3 adversarial), FRD context
  run_evaluation.py         Runs metrics, prints scores + meta-accuracy
tests/
  test_metrics.py           Pytest gate for the 5 golden cases
```

## Conventions — keep these intact

- **Threshold lives in one place** (`config.THRESHOLD`, default 0.7). Don't hardcode it.
- **The judge is centralised** in `judge.py`. Every metric grades with the same model/settings.
- **Hallucination is inverted.** Answer Relevancy & Faithfulness pass when `score >= threshold`;
  Hallucination passes when `score <= threshold` (the score is the fraction of context
  contradicted). Use `metrics.passed(name, score)` rather than re-deriving the rule.
- **The FRD is the ground truth.** Context strings in `dataset.py` are lifted from the FRD; if a
  requirement changes, update both the doc and the matching `CTX[...]` entry.
- **Traceability is mandatory.** Every test case maps to exactly one `FR-GS-NN`. Keep the
  matrix in `functional_test_cases.md` and the `requirement_id` fields in sync.

## Running things

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # PowerShell: $env:ANTHROPIC_API_KEY = 'sk-ant-...'

python -m src.run_evaluation                # full run + meta-accuracy report
deepeval test run tests/test_metrics.py     # rich DeepEval pytest report
pytest tests/test_metrics.py                # plain pytest (skips if no API key)
```

## When adding cases

1. Add/adjust the requirement in `docs/functional_requirements.md`.
2. Add the test case + matrix row in `docs/functional_test_cases.md`.
3. Add an `EvalSpec` in `src/dataset.py` with `context` lifted from the FRD and an honest
   `expect` label (what a correct judge *should* return). Adversarial cases must target a
   single failure mode.
4. Re-run `python -m src.run_evaluation` and confirm the meta-accuracy stays high.

## Notes for the LLM judge

- This repo uses the **Anthropic Claude API** as the DeepEval judge. Default model id is
  `claude-sonnet-4-6-20250514`; switch to an Opus model for stricter (pricier) grading.
- `temperature=0.0` is used for repeatable verdicts. Some metric-to-metric variance is
  inherent to LLM judging — treat single scores as estimates, not exact truth.
