# Evaluator Integrity

Criteria for auditing the evaluators AI teams use to measure their own systems —
LLM judges and test harnesses.

An evaluator is a measuring instrument, and an unaudited instrument is not
evidence. These criteria describe what has to be true of one before its output
should be relied on, whether the reliance is internal, contractual, or
regulatory.

## Status: provisional

Version 0.1 is a draft. It is not published, and it should not be cited yet.
See [criteria/v0.1/index.md](criteria/v0.1/index.md).

When a version is published, its text is frozen permanently — corrections
produce a new version and never edit an existing one. That is the whole
versioning policy, and it is written down in
[criteria/README.md](criteria/README.md).

## The criteria

Four criteria, each with a stable anchor id (`#C1`–`#C4`) so a citation can
address one of them rather than the whole document.

Cite the versioned path:

    criteria/v0.1/index.md#C2

Not `criteria/latest` — that path moves by design and is for browsing.

## Scoring a configuration

```bash
pip install -e .
python -m conformance.report --check
```

The criteria exist twice: as prose in `criteria/vX.Y/index.md`, and as data in
[conformance/](conformance/). The prose is normative. Where the two disagree,
the prose is right and the code has a bug.

*(The scorer is being ported; the modules are present and marked.)*

## Verifying the evidence

The point of publishing the corpus is that you do not have to take a score on
trust.

Each record in [conformance/corpus/](conformance/corpus/) names the artifact it
was scored from, pinned by package digest rather than by version string — so you
can obtain the same bytes, not merely the same release. Each judgement quotes
the text it rests on. `conformance/verify_quotes.py` reads those quotes back out
of the artifacts and fails on any that no longer match.

Only `framework_default` records are published individually: what a framework
ships with by default, which anybody can already install and read. Scores
against organisations' own configurations are published as aggregates with no
attribution.

## Disagreeing

Disagreement is the intended use. Three kinds, handled differently:

- **A score is wrong.** Open an issue quoting the artifact. A finding that
  cannot survive its own evidence being re-read should not stand.
- **A criterion is wrong** — it measures the wrong thing, or it is unmeasurable.
  Open an issue. This is the most useful thing you can send, and it is the
  argument the criteria are published free in order to have.
- **The method is wrong.** Say so publicly, and cite the version you are
  arguing against so the argument stays legible after the criteria move on.

Published versions do not change in response to disagreement. New versions do.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Two licences, deliberately split:

- **Code** — `conformance/`, `scripts/`, `tests/` — Apache-2.0. See [LICENSE](LICENSE).
- **Criteria and prose** — `criteria/`, `self-check/`, documentation — CC BY 4.0.
  See [LICENSE-DOCS](LICENSE-DOCS).

The criteria are CC BY 4.0 so they can be quoted and redistributed with
attribution, including inside procurement and regulatory documents. A standard
nobody is allowed to reproduce is not a standard.

## Citing

[CITATION.cff](CITATION.cff). Cite the version you read.

---

Idil Gozel · University College London · <ucapgoz@ucl.ac.uk>
