# Criteria — versioning policy

The criteria are a published standard. Third parties will cite them, and some of
those citations will sit in procurement or regulatory documents that outlive
this project's attention span. A citation written in 2028 has to still resolve
to the text its author actually read.

That single requirement decides everything below. This is policy, not
convention.

## Published versions are frozen

Every published version lives at `criteria/vX.Y/index.md`. **Once published, it
is never edited.** Not for a typo, not for a clarification, not for a broken
link.

A correction creates a new version. If v0.1 says something wrong, v0.2 says the
right thing, and v0.1 keeps saying the wrong thing forever — with a note
pointing at its successor, which is an addition of a superseded marker, not a
rewrite of the substance.

This is uncomfortable and it is the point. Someone made a decision on the basis
of the text as it stood. Editing under them turns their citation into a claim
they never made, and quietly rewriting a published standard is precisely the
kind of thing this project exists to catch other people doing.

## Nothing is deleted or moved

No version directory is ever deleted, renamed, or relocated — including versions
that are fully superseded, and including versions that were wrong. A superseded
version is marked as superseded and stays where it is.

A dead link and a moved document are the same event to a reader in 2028: the
cited text is gone.

## Where an uncitable property goes

**Where a property matters but no threshold or pass line can be cited, it
becomes an evidence requirement, not a pass condition.**

This is policy, and it has a failure on each side of it.

Put an uncitable property in a *pass condition* and you have invented a
standard. C3 required the eval environment to "document and restrict" its
retrieval paths; restricting is measured in the cited source, documenting is
not, and the conjunct was ours. C2 required a correctness signal "demonstrably
not fed back into generation or selection"; that was uncited, and the paper C2
cites reports the opposite for its own channel. Both read as though a source
stood behind them. Neither did, and a reader has no way to tell from the page.

Leave it in *prose* instead and nothing acts on it. A caveat in a rationale
paragraph is read once and never again; it does not reach the person filling in
a record, and it cannot fail a build.

The evidence requirement is the position between them. It compels disclosure of
the thing that matters without asserting a line we cannot defend, and a
submission lacking it scores `insufficient_evidence` — which says "not shown"
rather than "failed", and is the honest verdict when the honest answer is that
nobody has measured it.

Three instances, all live:

- **C1** requires the judge's own solve accuracy on the task distribution.
  Commit-first is capability-dependent and can make a weak judge worse, but no
  result fixes the floor. The source states its bound as 1 − solve-acc, so a
  reader given the number can apply the bound themselves.
- **C2** requires negative and positive controls showing the correctness signal
  discriminates. No citable result fixes how many controls suffice.
- **C4** requires per-check reachability for held-out checks. No citable result
  fixes what proportion must be reachable.

When you are tempted to write a number into a pass condition, check whether you
can cite it. If you cannot, the number belongs to the reader, and your job is to
make them able to compute it.

## Stable anchors

Each criterion has a permanent anchor id — `#C1`, `#C2`, `#C3`, `#C4` — so a
citation can address a single criterion rather than the whole page:

    criteria/v0.1/index.md#C2

An id means the same thing across every version in which it appears. If a
criterion changes enough that it is no longer the same requirement, it gets a
new id in the new version; the old id is not reused for something else. Ids are
never recycled.

The anchors must survive rendering to HTML unchanged — see
[`../site/README.md`](../site/README.md). An anchor that only exists in the
markdown source is not a citable anchor.

## Every page identifies itself

Each version's `index.md` states, in its own text:

- its version number
- its publication date
- whether it is current, provisional, or superseded (and by what)

Not in a config file, not in a template, not in the site chrome — in the
document body. Copies get printed, archived, PDF'd, and pasted into other
documents. A page that only knows which version it is because of the URL it was
served from stops knowing it the moment someone saves it.

## `criteria/latest`

`criteria/latest` is the only path here whose meaning is allowed to change. It
points at the current version and is repointed when a new one publishes.

Because it moves, it is not a citable address. Anyone quoting the criteria in a
document that needs to stay true should cite the versioned path.

## Publishing a version

1. Write `criteria/vX.Y/index.md` with the version, date, and status in the text.
2. Give each criterion its stable anchor id.
3. Run the conformance checks against it, including both re-verification
   passes — evidence that has not been re-verified is not published.

       python -m conformance.verify_quotes     --check --require-artifacts
       python -m conformance.verify_citations  --check --require-sources

   The first re-reads every corpus quote out of the pinned package it cites.
   The second is the same demand one level up: every quantity the criteria
   themselves state, read back out of the published result it rests on. Both
   run in CI in a weaker mode that reports rather than refuses; the
   `--require-*` flags are what make an unread citation a failure, and this
   step is the only place they are mandatory.
4. Add the superseded marker to the previous version. Change nothing else in it.
5. Repoint `criteria/latest`.
6. Set `date-released` in `CITATION.cff`.

After step 1 lands on `main`, the text is frozen.
