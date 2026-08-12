# Corpus

The corpus is the evidence behind every number this project publishes. One
record is one evaluator configuration, scored against one version of the
criteria.

A record exists so a reader does not have to trust the score. It should be
possible to take a record, fetch the artifact it names, find the quoted text,
and reach the same conclusion — or show that you cannot.

## What a record must carry

TODO(port): the record schema, from the lab harness. `_TEMPLATE.json` is a
marker, not a schema — it will be replaced by the real one. Files whose names
begin with `_` are treated as templates rather than records and are skipped by
the record checks.

Whatever the ported schema looks like, a record is not evidence unless it
carries all of:

- **The criteria version it was scored against**, e.g. `0.1`. Scores from
  different versions are not comparable, and versions are never edited in place,
  so this stays meaningful.
- **The stratum.** See below; this decides whether the record may be here at all.
- **A pinned artifact.** A package digest, not a version string. "The evaluator
  in langchain 0.2.1" is not something a reader can obtain identically; a digest
  is. See [`../provenance.py`](../provenance.py).
- **Evidence quotes**, each an exact span from the pinned artifact, with enough
  location to find it again. Re-verified by
  [`../verify_quotes.py`](../verify_quotes.py).
- **The score, and the reasoning that produced it**, per criterion id (`C1`–`C4`).

A judgement with no quote behind it is an opinion. It can be published as such,
but not as a finding.

## Which records may live in this repository

**Only `stratum: framework_default`.**

That stratum covers what an evaluation framework ships with out of the box — the
default judge prompt, the default rubric, the default harness settings. It is
already public: anyone can install the package and read it. Publishing a score
against it reveals nothing that was not already there, and it is the part
readers can check for themselves.

Every other stratum describes a configuration some organisation wrote for
itself. Those records stay in `evaluator-integrity-lab` and are published **as
aggregates only**, with no attribution — "n of m configurations in this stratum
failed C2", never which ones.

Records carrying a `client` or `engagement` field never appear here in any form.
The work they came from was done under an expectation that it would not be
published, and that expectation does not weaken because a finding turned out to
be interesting.

[`../../scripts/check_public_safe.py`](../../scripts/check_public_safe.py)
enforces all of this on every commit. It fails closed: a record with no
`stratum` field is refused, because a record that cannot be shown to be
publishable has not been shown to be safe.

## Adding a record

Records are produced by the lab harness and moved here deliberately, one
direction, by hand. Do not hand-write a record to fill a gap — a fabricated
record in a corpus published as evidence is the exact failure this project
exists to detect elsewhere.
