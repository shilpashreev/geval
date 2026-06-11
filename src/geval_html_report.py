"""Run the G-Eval test-case-quality metric and write a standalone HTML report.

Produces ``reports/geval_report.html`` — a self-contained page (no external
assets) showing, per generated test case: the requirement, the generated test
case, the G-Eval score, pass/fail vs the 0.7 threshold, the expected label,
agreement, and the judge's reasoning.

Usage:
    python -m src.geval_html_report
"""
from __future__ import annotations

import datetime as _dt
import html
import sys
from pathlib import Path

from . import config
from .geval_metrics import test_case_quality
from .quality_dataset import quality_specs

OUT_PATH = Path(__file__).resolve().parent.parent / "reports" / "geval_report.html"


def _row(spec, score: float, reason: str) -> str:
    passed = score >= config.THRESHOLD
    verdict = "PASS" if passed else "FAIL"
    agree = passed == spec.expect_pass
    return f"""
      <tr class="{'pass' if passed else 'fail'}">
        <td class="id">{html.escape(spec.id)}<br><span class="req">{html.escape(spec.requirement_id)}</span></td>
        <td class="tc">{html.escape(spec.generated_test_case)}</td>
        <td class="score"><span class="badge {'b-pass' if passed else 'b-fail'}">{score:.3f}</span><br>{verdict}</td>
        <td class="exp">{'pass' if spec.expect_pass else 'fail'}<br>
            <span class="{'ok' if agree else 'bad'}">{'agree' if agree else 'DISAGREE'}</span></td>
        <td class="reason">{html.escape(reason or '')}</td>
      </tr>"""


def build_html(rows: list[str], n_pass: int, n_total: int, n_agree: int) -> str:
    ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>DeepEval G-Eval — Test Case Quality Report</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; color:#1b1f24; background:#f6f8fa; }}
  h1 {{ font-size: 1.4rem; margin-bottom: .2rem; }}
  .meta {{ color:#57606a; font-size:.9rem; margin-bottom:1rem; }}
  .cards {{ display:flex; gap:1rem; margin:1rem 0 1.5rem; }}
  .card {{ background:#fff; border:1px solid #d0d7de; border-radius:10px; padding:.8rem 1.1rem; }}
  .card .k {{ font-size:1.6rem; font-weight:700; }}
  .card .l {{ color:#57606a; font-size:.8rem; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid #d0d7de; border-radius:10px; overflow:hidden; }}
  th, td {{ text-align:left; padding:.7rem .8rem; vertical-align:top; border-bottom:1px solid #eaeef2; font-size:.88rem; }}
  th {{ background:#f0f3f6; font-size:.78rem; text-transform:uppercase; letter-spacing:.03em; color:#57606a; }}
  td.tc, td.reason {{ white-space:pre-wrap; max-width:34ch; }}
  td.reason {{ max-width:40ch; color:#3a4149; }}
  .id {{ font-weight:600; }} .req {{ color:#57606a; font-weight:400; font-size:.8rem; }}
  .badge {{ display:inline-block; padding:.1rem .5rem; border-radius:999px; font-weight:700; color:#fff; }}
  .b-pass {{ background:#1a7f37; }} .b-fail {{ background:#cf222e; }}
  tr.pass {{ }} tr.fail td {{ background:#fff8f8; }}
  .ok {{ color:#1a7f37; font-weight:600; }} .bad {{ color:#cf222e; font-weight:600; }}
  .legend {{ color:#57606a; font-size:.82rem; margin-top:1rem; }}
</style></head>
<body>
  <h1>DeepEval &middot; G-Eval &mdash; Test Case Quality</h1>
  <div class="meta">Judge: <b>{html.escape(config.judge_label())}</b> &nbsp;|&nbsp;
     Threshold: <b>{config.THRESHOLD}</b> (pass when score &ge; threshold) &nbsp;|&nbsp; Generated: {ts}</div>
  <div class="cards">
    <div class="card"><div class="k">{n_total}</div><div class="l">test cases graded</div></div>
    <div class="card"><div class="k">{n_pass}</div><div class="l">passed (&ge; {config.THRESHOLD})</div></div>
    <div class="card"><div class="k">{n_agree}/{n_total}</div><div class="l">agreed with expected label</div></div>
  </div>
  <table>
    <thead><tr>
      <th>Case</th><th>Generated test case</th><th>G-Eval score</th><th>Expected</th><th>Judge reasoning</th>
    </tr></thead>
    <tbody>{''.join(rows)}
    </tbody>
  </table>
  <div class="legend">G-Eval rubric: atomic &amp; traceable to the requirement, concrete ordered steps,
     explicit verifiable expected result, concrete test data. Vagueness is heavily penalised.</div>
</body></html>"""


def main() -> int:
    try:
        config.ensure_judge_ready()
    except EnvironmentError as exc:
        print(exc)
        return 2

    print(f"Judge: {config.judge_label()} | grading {len(quality_specs())} test cases...")
    rows: list[str] = []
    n_pass = n_agree = 0
    for spec in quality_specs():
        metric = test_case_quality()
        metric.measure(spec.to_llm_test_case())
        passed = metric.score >= config.THRESHOLD
        n_pass += int(passed)
        n_agree += int(passed == spec.expect_pass)
        rows.append(_row(spec, metric.score, metric.reason))
        print(f"  {spec.id}: {metric.score:.3f} -> {'PASS' if passed else 'FAIL'}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        build_html(rows, n_pass, len(quality_specs()), n_agree), encoding="utf-8"
    )
    print(f"\nHTML report written to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
