# Version re-check, 25 August 2026

Run immediately before publication. The corpus was pinned between 8 and 10
August. This checks every pinned artifact against the version currently on
the public registry, and asks one question: **does any verdict in the census
change at current versions?**

Method: fetch the current release, extract the pinned path, compare SHA-256
against the corpus. Where the file changed, diff it and decide whether the
change touches the property the criterion tests.

## Result: no verdict changes.

| package | pinned | current | pinned file |
|---|---|---|---|
| deepeval | 4.1.5 | **4.2.0** | **changed** |
| arize-phoenix-evals | 3.3.0 | 3.5.1 | identical |
| autoevals | 0.3.0 | 0.3.0 | unchanged release |
| mlflow | 3.15.1 | 3.15.1 | unchanged release |
| evals (OpenAI) | 3.0.1.post1 | 3.0.1.post1 | unchanged release |
| openevals | 0.2.0 | 0.2.0 | unchanged release |
| ragas | 0.4.3 | 0.4.3 | unchanged release |
| langchain-classic | 1.0.8 | not re-checked | — |
| promptfoo | 0.122.0 (npm) | not re-checked | — |

The 4.1.5 hash we recorded reproduces exactly from PyPI today
(`e4705dd4…dfdaf`), which independently confirms the corpus provenance.

## DeepEval 4.1.5 → 4.2.0, in detail

`deepeval/templates/metrics/templates.json` changed
(`e4705dd4…dfdaf` → `90a529bd…264d`). Fifty-one top-level keys before and
after, none added or removed. Seven changed:

- `BiasMetric`, `KnowledgeRetentionMetric`, `MisuseMetric`, `ToxicityMetric`
  — not in our corpus.
- `HallucinationMetric.generate_reason` — a correction to how the prompt
  describes the score. It previously said the score "ranges from 0 - 1, and
  the lower the better"; it now says it "measures how well the `actual
  output` aligns with the `contexts`, and the higher the better."
- `SummarizationMetric.generate_alignment_verdicts` — removed the phrase
  "otherwise I WILL DIE" from the instruction.
- `_fragments.faithfulness_verdicts_guidelines_multimodal` — the same phrase
  removed.

**`GEval` is byte-identical between 4.1.5 and 4.2.0.** That is the
configuration under test in the experiment, so the experiment is unaffected
by the release.

Two corpus records sit on the changed metrics: `deepeval/hallucination` and
`deepeval/summarization`. Neither change touches the property C1 tests. Both
configurations remain a single call in which the candidate and any reference
appear together and the judge returns a holistic score, with no stage
emitting the judge's own parseable answer and no acceptance-by-match. Both
stay `fail`, for the same reason and on the same evidence.

## Why this is recorded rather than fixed by re-pinning

The corpus was scored against 4.1.5 and the verdicts state what that version
shipped. Re-pinning to 4.2.0 would silently restate the claim as being about
a version we did not score. Recording the re-check keeps the original claim
intact and adds a second, dated claim: we looked again on 25 August and
nothing moved.

Anyone re-running `python -m conformance.verify_quotes` against the current
release will see a hash mismatch on the five DeepEval records. That is the
mechanism working, not breaking. `--how` prints the commands to fetch 4.1.5,
against which every quote still verifies.

## Not re-checked

`langchain-classic` and `promptfoo` were not re-checked in this pass.
Both should be covered before the census is next cited as current.
