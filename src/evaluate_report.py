"""Batch evaluation using DeepEval's native ``evaluate()`` reporter.

Unlike ``run_evaluation.py`` (which hand-rolls a meta-accuracy report), this
uses DeepEval's built-in ``evaluate()`` to produce its standard pass/fail
report across the whole dataset and all metrics at once — the idiomatic way to
get a DeepEval test run + (optionally) push it to Confident AI.

Covered here:
  * the 5 golden QA cases  -> Answer Relevancy, Faithfulness, Hallucination
  * the test-case-quality cases -> G-Eval "Test Case Quality"

Usage:
    python -m src.evaluate_report
"""
from __future__ import annotations

import sys

from deepeval import evaluate

from . import config, metrics
from .dataset import goldens
from .geval_metrics import test_case_quality
from .quality_dataset import quality_specs


def main() -> int:
    try:
        config.ensure_judge_ready()
    except EnvironmentError as exc:
        print(exc)
        return 2

    print(f"Judge: {config.judge_label()}  |  threshold: {config.THRESHOLD}\n")

    # 1) Factual QA goldens through the three core metrics.
    qa_cases = [g.to_llm_test_case() for g in goldens()]
    print(">> Evaluating factual QA goldens (relevancy / faithfulness / hallucination)")
    evaluate(test_cases=qa_cases, metrics=metrics.all_metrics())

    # 2) Generated test-case quality through G-Eval.
    quality_cases = [q.to_llm_test_case() for q in quality_specs()]
    print("\n>> Evaluating generated test-case quality (G-Eval)")
    evaluate(test_cases=quality_cases, metrics=[test_case_quality()])

    return 0


if __name__ == "__main__":
    sys.exit(main())
