# Contributing

## Setup

```bash
pip install -e ".[dev]"
git config core.hooksPath .githooks
```

**The second line is not optional.** Git does not run hooks from a versioned
directory unless it is told to, and a fresh clone starts with the hook present
but inert. Run it once per clone.

Check it took:

```bash
git config core.hooksPath        # -> .githooks
```

## The public-safety check

```bash
python scripts/check_public_safe.py
```

This repository is public. Making it public exposes its **history**, not its
current state — anything that has ever been committed here is readable forever,
including things deleted in a later commit.

[`scripts/check_public_safe.py`](scripts/check_public_safe.py) refuses material
that must not be published: the search harness and other lab directories, corpus
records from any stratum other than `framework_default`, records carrying client
or engagement fields, and anything on
[`scripts/denylist.txt`](scripts/denylist.txt).

It runs in two places and the difference is the whole design:

| | when | what it saves you |
|---|---|---|
| pre-commit hook | before the commit exists | everything |
| CI | after the commit is in history | nothing — it tells you it is too late |

**If it fails, remove the material.** Never `--no-verify`, never add an
exclusion, never soften a rule to get a commit through. The failure is the
check working. If you genuinely believe it is a false positive, fix the check
in its own commit, with the reasoning in the message, and have it reviewed as a
change to the guard — not as a change smuggled alongside the file it was
blocking.

If something private has already been committed, deleting it does not help.
Treat it as disclosed: rotate anything sensitive, then decide whether the branch
can be rewritten or has to be abandoned.

## Where things live

There is a second repository, `evaluator-integrity-lab`. It holds the research
harness, the full scored corpus, and commercial and strategy material, and it is
permanently private.

**Every artefact has exactly one home.** If a file exists in both repositories,
that is a defect. Nothing is copied between them automatically, no git history
is ever shared, and work moves in one direction at a time, by hand, deliberately.

Do not add the lab as a remote, a submodule, or a subtree. Shared history is
what makes a leak permanent.

## Criteria changes

Read [`criteria/README.md`](criteria/README.md) first.

Published versions are frozen. A pull request that edits the text of a published
`criteria/vX.Y/index.md` will be rejected regardless of how right it is —
corrections create a new version. Someone has cited the old text; editing under
them turns their citation into a claim they never made.

What is welcome:

- Argument that a criterion measures the wrong thing, or cannot be measured
  consistently. This is the most valuable contribution here.
- A score you can show is wrong, quoting the artifact it was drawn from.
- Corpus records for `framework_default` configurations, with evidence quotes
  and a pinned package digest. No digest, no quotes, no record — see
  [`conformance/corpus/README.md`](conformance/corpus/README.md).

Criteria text is written to be quoted. Assume every sentence will be pulled out
of context and pasted into a procurement document by someone who has not read
the rest. Write for that reader: plain, self-contained, no cross-reference the
quoted sentence depends on.

## Tests and CI

```bash
pytest tests/ -q
python scripts/check_public_safe.py
python -m conformance.report --check
python -m conformance.verify_quotes --check
python -m conformance.verify_citations --check
python -m conformance.coherence --check
```

CI runs exactly these on push and pull request, on Python 3.11.

The last three are three levels of the same demand — that a claim names the
thing it rests on, and still matches it.

`verify_quotes` re-reads every corpus quote out of the pinned package it cites.
It skips when the artifact tree is absent, which is the normal case here — it
says so loudly rather than passing quietly.

`verify_citations` makes the same demand of the criteria's own figures: every
quantity stated in `conformance/criteria.py` or in the published markdown has to
name the source it came from and the locator inside it. It runs for real on a
bare clone, because the ledger it checks is in the repository. Most of that
ledger is currently `unverified` — stated in the criteria, not yet read back out
of the pinned source — and the command prints how much. **`unverified` is a
value, not a gap to fill in.** Never invent a quote to clear one; an empty slot
cannot be cited by mistake and a fabricated quote can.

`coherence` checks that a criterion's question, its pass condition and its
published prose still state one requirement. C2 spent a while asking for a
held-out channel its pass condition had retired.

Publishing a criteria version requires the first two for real:

```bash
EVALINT_ARTIFACTS=/path/to/artifacts \
  python -m conformance.verify_quotes --check --require-artifacts
python -m conformance.verify_citations --check --require-sources
```

`--require-sources` turns every unverified claim into a failure, so it does not
pass today. That is the intended behaviour: it is the check that stops a version
being published while its rationale rests on figures nobody has read back out.

Keep CI green. A project telling other people to take measurement seriously does
not merge with a red build.

## Licence

Contributions are accepted under the repository's licences: Apache-2.0 for code,
CC BY 4.0 for criteria and prose. See [LICENSE](LICENSE) and
[LICENSE-DOCS](LICENSE-DOCS).
