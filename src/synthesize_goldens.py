"""Auto-generate evaluation *goldens* from the FRD using DeepEval's Synthesizer.

Instead of hand-writing every test input, the Synthesizer reads ground-truth
context (here, the requirement text from the FRD) and generates realistic
question/expected-output pairs (``Golden`` objects) you can then run metrics on.
This automates the "generate test cases from a document" half of the workflow.

We feed contexts directly (``generate_goldens_from_contexts``) so it stays fully
offline — no embedding/retrieval step needed. The synthesizer model is the same
configurable judge (Ollama by default).

Usage:
    python -m src.synthesize_goldens                # default 1 golden per requirement
    python -m src.synthesize_goldens --per 2        # 2 per requirement
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deepeval.synthesizer import Synthesizer

from . import config
from .dataset import CTX
from .judge import get_judge

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "synthetic_goldens.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthesize goldens from the FRD.")
    parser.add_argument("--per", type=int, default=1, help="goldens per requirement")
    args = parser.parse_args()

    try:
        config.ensure_judge_ready()
    except EnvironmentError as exc:
        print(exc)
        return 2

    print(f"Synthesizer model: {config.judge_label()}")
    print(f"Generating up to {args.per} golden(s) per requirement from the FRD context...\n")

    # One context group per requirement -> grounded, traceable goldens.
    contexts = [ctx for ctx in CTX.values()]

    synthesizer = Synthesizer(model=get_judge())
    goldens = synthesizer.generate_goldens_from_contexts(
        contexts=contexts,
        include_expected_output=True,
        max_goldens_per_context=args.per,
    )

    records = [
        {
            "input": g.input,
            "expected_output": g.expected_output,
            "context": g.context,
        }
        for g in goldens
    ]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\nGenerated {len(records)} golden(s).")
    for i, r in enumerate(records, 1):
        print(f"\n[{i}] Q: {r['input']}")
        if r["expected_output"]:
            print(f"    A: {r['expected_output']}")
    print(f"\nSaved to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
