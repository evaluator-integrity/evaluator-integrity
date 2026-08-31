# Evaluator Integrity

Criteria for auditing the evaluators AI teams use to measure their own systems —
LLM judges and test harnesses.

An evaluator is a measuring instrument, and an unaudited instrument is not
evidence. These criteria describe what has to be true of one before its output
should be relied on, whether the reliance is internal, contractual, or
regulatory. They do not assess model quality. They assess whether the thing
measuring model quality can be relied on.

**[Criteria v0.1](criteria/v0.1/index.md)** — four criteria, published and
frozen on 25 August 2026. **[Configuration census](census/index.md)** — 28
evaluator configurations scored against them.

## Don't trust this. Check it.

Every number here is meant to be re-derived by you, from bytes you fetch
yourself. That is the point of the project, so it goes first.

**Check a score against the evaluator it describes.** Each corpus record names
the artifact it was scored from, pinned by package digest rather than version
string — so you obtain the same bytes, not merely the same release — and quotes
the text the verdict rests on.

```bash
pip install -e .

# Rebuild the artifact tree from the public registries (the commands are printed
# for you; the tree is not committed here because it is large).
python -m conformance.verify_quotes --how

EVALINT_ARTIFACTS=artifacts/x \
  python -m conformance.verify_quotes --check --require-artifacts
```

That re-reads every evidence quote out of the shipped package it cites and fails
on any that no longer matches. A digest that has moved is a finding about the
vendor, not a reason to loosen the check.

**Check the criteria's own figures the same way.** Every quantity C1–C4 state —
in the prose that gets cited and in the module that scores — is recorded against
the published result it came from, the locator inside it, and the verbatim span
it was read from.

```bash
python -m conformance.verify_citations             # print the ledger
python -m conformance.verify_citations --require-sources
```

The ledger has four statuses, and the awkward ones are the point. `verified` was
read back out of the pinned source. `unsupported` means the source was read and
contradicts us — a finding against our own text, which stays visible until the
text changes. `unverified` means nobody has read it back out yet, and carries no
quote, because inventing one is the exact failure this project exists to detect.
`ours` marks a figure we computed rather than read, and the check requires the
criterion text itself to say so, because a figure of ours reads exactly like a
sourced one and the reader has only the text.

**Re-derive the published numbers from the corpus.**

```bash
python -m conformance.report --check    # fails if any published figure no longer follows
```

**Or run everything CI runs**, which is the whole gate:

```bash
pytest tests/ -q
python scripts/check_public_safe.py
python scripts/check_public_safe.py --history
python -m conformance.report --check
python -m conformance.verify_quotes --check
python -m conformance.verify_citations --check
python -m conformance.coherence --check
python scripts/build_census.py --check
```

## What the census found

28 framework-default configurations — what ten packages from nine vendors ship
out of the box — scored against v0.1.

- **0 of 25** in-scope configurations satisfy C1. None commits an answer of its
  own before it is shown the candidate.
- **10 of 25** are recompute variants: they tell the judge to solve the problem
  first, in a prompt that already contains the candidate. The cited source
  measures that as a failure, not a partial fix.
- **13 of 25** are handed a reference answer. A reference given to the judge is
  not a channel independent of the judge.

These are defaults, not indictments. The same framework can be configured to
pass or fail every criterion here; what is scored is a configuration. Full table
and per-verdict evidence: **[census](census/index.md)**.

## The criteria

Four criteria, each externally cited, each with a stable anchor id (`#C1`–`#C4`)
so a citation can address one rather than the whole document.

Cite the versioned path:

    criteria/v0.1/index.md#C2

Not `criteria/latest` — that path moves by design and is for browsing. Published
versions are frozen permanently: corrections produce a new version and never
edit an existing one, including versions that turn out to be wrong. A citation
written in 2028 has to resolve to the text its author actually read. That is the
[whole versioning policy](criteria/README.md).

## What is deliberately not here

Absences on purpose, not gaps waiting to be filled.

- **Criteria for non-verifiable evaluation.** Every result behind C1 and C2 uses
  tasks with a determinable answer. None covers summarisation quality,
  helpfulness or tone, so configurations for subjective tasks are scored
  `not applicable` rather than scored badly. This is the largest gap in v0.1 and
  the most useful thing a collaborator could bring.
- **Any criterion we cannot cite.** Requirements that are plausible but not yet
  supported by a result precise enough to fix a pass condition live in
  [candidate criteria](criteria/candidates.md), which is explicitly not a
  standard and must not be cited as one. A criterion we invented would be an
  opinion, and this project has no standing to publish opinions as criteria.
- **A self-check score.** The [self-check](self-check/README.md) outputs a
  findings list and never a verdict. Ten minutes of unverified self-inspection
  has enough evidence to find a defect and never enough to establish the absence
  of one, and a self-issued score gets extracted into a slide stripped of the
  fact that its subject issued it about themselves.
- **Configurations belonging to anyone but the frameworks themselves.** Only
  `framework_default` records are published individually — what anybody can
  already install and read. Scores against organisations' own configurations are
  published as aggregates with no attribution, and records tied to a client or
  an engagement are never published in any form.
- **The scored corpus behind those aggregates, and the research harness.** They
  live in a separate, permanently private repository. See [CLAUDE.md](CLAUDE.md)
  for the boundary and [scripts/check_public_safe.py](scripts/check_public_safe.py)
  for the check that enforces it on every commit and over the whole history.

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

Two licences, split by what the material is for:

- **Criteria and prose** — `criteria/`, `census/`, `self-check/`, documentation —
  **CC BY 4.0**. See [LICENSE-DOCS](LICENSE-DOCS).
- **Code** — `conformance/`, `scripts/`, `tests/` — **Apache-2.0**. See
  [LICENSE](LICENSE).

CC BY 4.0 for the criteria because they are written to be quoted, including
inside procurement and regulatory documents that may be proprietary. It requires
attribution, so the citation trail survives; it permits commercial use and
translation, so adoption is not gated on our permission; and it imposes no
share-alike burden that would stop a company pasting a criterion into a
contract. A standard nobody is allowed to reproduce is not a standard.

It also permits modified versions, which is the right trade rather than an
oversight: CC BY requires a modifier to indicate that changes were made, and the
protection that actually matters — that a citation resolves to the text its
author read — comes from frozen versioned paths and stable anchor ids, not from
a licence forbidding adaptation.

**The criteria text is CC BY 4.0 wherever it appears**, including the copies
embedded in [conformance/criteria.py](conformance/criteria.py). The surrounding
code in that file is Apache-2.0.

Apache-2.0 for the code because it carries an explicit patent grant, which
matters for tooling that may be embedded in commercial audit pipelines.

## Citing

[CITATION.cff](CITATION.cff). Cite the version you read.

---

Idil Gozel · Evaluator Integrity, London · <idilgozel@evaluatorintegrity.com>
