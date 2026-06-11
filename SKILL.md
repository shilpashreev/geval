---
name: requirement-driven-deepeval
description: >-
  Generate functional requirements and traceable test cases for a feature, then
  evaluate LLM-generated answers about it with DeepEval's Answer Relevancy,
  Faithfulness, and Hallucination metrics (Claude judge, 0.7 threshold). Use when
  asked to "create test cases and evaluate them with deepeval", build an LLM eval
  harness, or measure how accurate DeepEval is for a task.
---

# Requirement-Driven DeepEval Skill

A repeatable workflow for turning a feature into a requirements doc, traceable
functional test cases, and a DeepEval scoring harness with a built-in accuracy check.

## When to use

- "Generate functional test cases for <feature> and evaluate with DeepEval."
- "Set up Answer Relevancy / Faithfulness / Hallucination metrics with a threshold."
- "How accurate is DeepEval / how do I trust its scores for my use case?"

## Inputs to gather

1. **Feature under test** (e.g. Google Search page).
2. **Number of test cases** and **type** (here: 5 functional).
3. **Threshold** (here: 0.7) and **judge LLM** (here: Claude `claude-sonnet-4-6`).

## Steps

1. **Write the FRD.** Capture each requirement as `FR-<AREA>-NN`: inputs, trigger, output,
   rules. The FRD is the *ground truth* the metrics grade against, so write it factually.
2. **Derive test cases.** One primary case per requirement; include pre-conditions, test data,
   steps, expected result. Build a **traceability matrix** (test case ↔ requirement).
3. **Build the labelled dataset.** For each case create an `EvalSpec` with:
   - `user_input` (the question/action),
   - `actual_output` (the system/LLM answer being judged),
   - `context` (FRD text — ground truth for faithfulness & hallucination),
   - `expect` (the verdict a *correct* judge should return per metric).
   Add **adversarial** cases — deliberately irrelevant / contradictory / hallucinated answers —
   each targeting one failure mode. These prove the metrics actually catch problems.
4. **Wire the metrics** (`AnswerRelevancyMetric`, `FaithfulnessMetric`, `HallucinationMetric`),
   all using one centralised judge and one threshold. Remember **hallucination is inverted**
   (lower score is better; passes when `score <= threshold`).
5. **Run + meta-evaluate.** Score every case, then compare DeepEval's verdict to the `expect`
   labels and report agreement %. That agreement is your empirical accuracy read.
6. **Gate in CI** with `deepeval test run` / `pytest` on the golden cases.

## Getting the most accuracy out of DeepEval

- **Provide real context.** Faithfulness & hallucination are only meaningful when
  `retrieval_context` / `context` is accurate ground truth. Garbage context → garbage verdicts.
- **Use a strong judge at `temperature=0`.** Judge quality dominates metric quality.
  Claude Sonnet is a solid default; Opus for the strictest grading.
- **Label a golden + adversarial set** and track agreement over time. Never trust a metric you
  haven't validated against known-correct answers.
- **Average over runs** for borderline scores; LLM judging has variance. Treat a single score
  near the threshold as "needs review", not a hard verdict.
- **Read `metric.reason`,** not just the number — it tells you *why* a case failed and is the
  fastest route to fixing prompts or context.
- **Set `strict_mode=True`** when you want binary 1/0 verdicts instead of graded scores.

## Output artefacts

`docs/functional_requirements.md`, `docs/functional_test_cases.md`, a `src/` package
(`config`, `judge`, `metrics`, `dataset`, `run_evaluation`), a `tests/` pytest gate, and a
README documenting the workflow.
