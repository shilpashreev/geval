"""Run the DeepEval metrics over the labelled dataset and report results.

Two layers of reporting:

1. **Per-case scores** — relevancy, faithfulness, hallucination for every case.
2. **Meta-evaluation** — how often DeepEval's verdict matched the known label
   (``expect``). This is the answer to "how accurate is DeepEval?": run it
   against cases whose correct verdict you already know and measure agreement.

Usage:
    python -m src.run_evaluation
"""
from __future__ import annotations

import sys

from . import config, metrics
from .dataset import (
    ALL_SPECS,
    ANSWER_RELEVANCY,
    FAITHFULNESS,
    HALLUCINATION,
    EvalSpec,
)

METRIC_ORDER = [ANSWER_RELEVANCY, FAITHFULNESS, HALLUCINATION]


def _score_case(spec: EvalSpec) -> dict[str, dict]:
    """Run all three metrics on one spec; return {metric: {score, reason, passed}}."""
    tc = spec.to_llm_test_case()
    results: dict[str, dict] = {}
    metric_objs = {
        ANSWER_RELEVANCY: metrics.answer_relevancy(),
        FAITHFULNESS: metrics.faithfulness(),
        HALLUCINATION: metrics.hallucination(),
    }
    for name, metric in metric_objs.items():
        metric.measure(tc)
        results[name] = {
            "score": metric.score,
            "reason": metric.reason,
            "passed": metrics.passed(name, metric.score),
        }
    return results


def main() -> int:
    try:
        config.ensure_judge_ready()
    except EnvironmentError as exc:
        print(exc)
        return 2
    print("=" * 78)
    print("DeepEval — Google Search functional evaluation")
    print(f"Judge       : {config.judge_label()}")
    print(f"Threshold   : {config.THRESHOLD}  (relevancy/faithfulness >= ; hallucination <=)")
    print("=" * 78)

    # Meta-evaluation tally: did DeepEval agree with our known label?
    agree = 0
    total = 0

    for spec in ALL_SPECS:
        print(f"\n[{spec.id}] {spec.kind.upper()}  (maps to {spec.requirement_id})")
        print(f"  Q: {spec.user_input}")
        scored = _score_case(spec)
        for name in METRIC_ORDER:
            r = scored[name]
            verdict = "PASS" if r["passed"] else "FAIL"
            expected = spec.expect.get(name)
            match = ""
            if expected is not None:
                total += 1
                ok = r["passed"] == expected
                agree += int(ok)
                match = "  [agree]" if ok else "  [DISAGREE]"
            print(f"    {name:<16} score={r['score']:.3f}  -> {verdict}{match}")

    print("\n" + "=" * 78)
    if total:
        pct = 100.0 * agree / total
        print(f"Meta-evaluation: DeepEval agreed with {agree}/{total} known labels ({pct:.1f}%).")
        print("This is your empirical read on how accurate DeepEval is for THIS task.")
    print("=" * 78)
    # Non-zero exit if DeepEval ever disagreed with a known label.
    return 0 if agree == total else 1


if __name__ == "__main__":
    sys.exit(main())
