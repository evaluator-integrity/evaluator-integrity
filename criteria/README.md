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
3. Run the conformance checks against it, including
   `python -m conformance.verify_quotes --check --require-artifacts` — evidence
   that has not been re-verified is not published.
4. Add the superseded marker to the previous version. Change nothing else in it.
5. Repoint `criteria/latest`.
6. Set `date-released` in `CITATION.cff`.

After step 1 lands on `main`, the text is frozen.
