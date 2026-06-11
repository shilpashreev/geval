"""Verify the generated manual test cases across every verification dimension.

Scores each manual test case (from manual_test_dataset.py) on all metrics in
verification_metrics.py, prints a verification matrix to the console, and writes
an HTML dashboard to reports/manual_test_verification.html.

Usage:
    python -m src.verify_manual_tests
"""
from __future__ import annotations

import datetime as _dt
import html
import sys
from pathlib import Path

from . import config
from .manual_test_dataset import manual_tests
from .verification_metrics import VERIFICATION_METRICS

OUT_PATH = Path(__file__).resolve().parent.parent / "reports" / "manual_test_verification.html"


def _score_matrix():
    """Return (matrix, reasons): matrix[test_id][metric_key] = score."""
    matrix: dict[str, dict[str, float]] = {}
    reasons: dict[str, dict[str, str]] = {}
    for mt in manual_tests():
        matrix[mt.id] = {}
        reasons[mt.id] = {}
        tc = mt.to_llm_test_case()
        for vm in VERIFICATION_METRICS:
            metric = vm.build()
            metric.measure(tc)
            matrix[mt.id][vm.key] = metric.score
            reasons[mt.id][vm.key] = metric.reason or ""
            print(f"  {mt.id} / {vm.name:<15} {metric.score:.3f}")
    return matrix, reasons


def _cell(score: float) -> str:
    passed = score >= config.THRESHOLD
    cls = "b-pass" if passed else "b-fail"
    return f'<td class="num"><span class="badge {cls}">{score:.2f}</span></td>'


def build_html(matrix, reasons) -> str:
    ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metric_cols = "".join(
        f'<th title="{html.escape(vm.description)}">{html.escape(vm.name)}</th>'
        for vm in VERIFICATION_METRICS
    )
    rows = []
    total = passed = 0
    for tid, scores in matrix.items():
        cells = "".join(_cell(scores[vm.key]) for vm in VERIFICATION_METRICS)
        row_pass = sum(1 for vm in VERIFICATION_METRICS if scores[vm.key] >= config.THRESHOLD)
        total += len(VERIFICATION_METRICS)
        passed += row_pass
        verdict = "PASS" if row_pass == len(VERIFICATION_METRICS) else f"{row_pass}/{len(VERIFICATION_METRICS)}"
        rows.append(
            f'<tr><th class="rid">{html.escape(tid)}</th>{cells}'
            f'<td class="num"><b>{verdict}</b></td></tr>'
        )

    legend = "".join(
        f"<li><b>{html.escape(vm.name)}</b> — {html.escape(vm.description)}</li>"
        for vm in VERIFICATION_METRICS
    )
    pct = 100.0 * passed / total if total else 0
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Manual Test Case Verification — DeepEval</title>
<style>
  body {{ font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif; margin:2rem; color:#1b1f24; background:#f6f8fa; }}
  h1 {{ font-size:1.4rem; margin-bottom:.2rem; }}
  .meta {{ color:#57606a; font-size:.9rem; margin-bottom:1rem; }}
  table {{ border-collapse:collapse; background:#fff; border:1px solid #d0d7de; border-radius:10px; overflow:hidden; }}
  th,td {{ padding:.55rem .7rem; border-bottom:1px solid #eaeef2; font-size:.85rem; text-align:center; }}
  thead th {{ background:#f0f3f6; font-size:.72rem; text-transform:uppercase; letter-spacing:.02em; color:#57606a; writing-mode:horizontal-tb; }}
  th.rid, th.corner {{ text-align:left; font-weight:700; background:#f0f3f6; }}
  .num {{ font-variant-numeric:tabular-nums; }}
  .badge {{ display:inline-block; min-width:2.4em; padding:.12rem .4rem; border-radius:6px; font-weight:700; color:#fff; }}
  .b-pass {{ background:#1a7f37; }} .b-fail {{ background:#cf222e; }}
  .summary {{ margin:1rem 0; font-size:.95rem; }}
  ul.legend {{ color:#3a4149; font-size:.82rem; line-height:1.5; max-width:70ch; }}
</style></head>
<body>
  <h1>Manual Test Case Verification</h1>
  <div class="meta">Judge: <b>{html.escape(config.judge_label())}</b> &nbsp;|&nbsp;
     Threshold: <b>{config.THRESHOLD}</b> (pass when score &ge; threshold) &nbsp;|&nbsp;
     {len(matrix)} test cases &times; {len(VERIFICATION_METRICS)} verification metrics &nbsp;|&nbsp; {ts}</div>
  <table>
    <thead><tr><th class="corner">Test case</th>{metric_cols}<th>Overall</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="summary"><b>{passed}/{total}</b> metric checks passed ({pct:.0f}%).
     Green &ge; {config.THRESHOLD}, red below.</div>
  <h3>What each metric verifies</h3>
  <ul class="legend">{legend}</ul>
</body></html>"""


def main() -> int:
    try:
        config.ensure_judge_ready()
    except EnvironmentError as exc:
        print(exc)
        return 2

    n_tests = len(manual_tests())
    n_metrics = len(VERIFICATION_METRICS)
    print(f"Judge: {config.judge_label()} | verifying {n_tests} manual tests "
          f"x {n_metrics} metrics = {n_tests * n_metrics} checks...\n")

    matrix, reasons = _score_matrix()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(build_html(matrix, reasons), encoding="utf-8")
    print(f"\nVerification dashboard written to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
