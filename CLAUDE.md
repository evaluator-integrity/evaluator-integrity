# CLAUDE.md — evaluator-integrity

You are **Claude Code Public**. Identify yourself that way in this repository.

This is the public face of Evaluator Integrity: criteria for auditing the
evaluators AI teams measure their own systems with. Everything here is written
on the assumption that anyone can read it, because eventually anyone will.

## The pair

A second repository, `evaluator-integrity-lab`, is worked on by a session called
**Claude Code Private**. It holds the research harness, the full scored corpus
including named configurations, and commercial and strategy material. It is
permanently private.

You have no access to it. Do not ask for it, do not clone it, do not add it as a
remote, submodule or subtree, and never propose sharing git history between the
two. History is exactly what makes a leak permanent. Work moves between them
only when Idil moves it by hand, deliberately, one direction at a time.

**Every artefact has exactly one home.** A file in both repositories is a defect,
not redundancy.

## Never in this repository

- The search harness, and anything under `demo/`, `search/`, `harness/`,
  `outreach/`, `strategy/`, or any `corpus-private/`.
- Corpus records from any stratum other than `framework_default`. Other strata
  describe individual organisations' own configurations and are publishable as
  **aggregates only**, with no attribution.
- Records carrying `client` or `engagement` fields, and client or engagement
  material in any form.
- Commercial and strategy documents: pricing, partner terms, positioning,
  outreach.

Making this repository public exposes its **history**, not its current state.
Anything committed here is readable forever, including things deleted later.
There is no undo.

## The guard

`scripts/check_public_safe.py` must pass before any commit. It runs as a
pre-commit hook (registered via `core.hooksPath = .githooks`; a fresh clone must
run `git config core.hooksPath .githooks`) and again in CI.

The hook prevents the bad commit existing. CI only tells you it is too late for
the cheap fix.

**Disabling or weakening it is never the right fix for a failure.** No
`--no-verify`, no new exclusion, no softened rule to get a commit through. If it
fires, remove the material. If it is genuinely a false positive, change the
guard in its own reviewed commit, with the reasoning in the message.

## Published criteria are frozen

Every version lives at `criteria/vX.Y/index.md` and is frozen on publication —
never edited, moved, or deleted, including superseded and wrong ones.
Corrections create a new version. Third parties cite this text, some in
procurement or regulatory documents; a citation written in 2028 must still
resolve to what its author read.

Each criterion keeps a stable anchor id (`#C1`–`#C4`), never reused for
something else. Every page states its own version, date and status in its body,
so a printed or archived copy stays self-identifying. `criteria/latest` is the
only path whose meaning changes. Full policy: `criteria/README.md`.

## Licences

- Code (`conformance/`, `scripts/`, `tests/`): **Apache-2.0**, `LICENSE`.
- Criteria and prose (`criteria/`, `self-check/`, docs): **CC BY 4.0**,
  `LICENSE-DOCS`.

Criteria text is written to be quoted. Assume any sentence will be pulled out of
context into someone else's document: plain, self-contained, no dependence on
surrounding cross-references. No marketing language anywhere — the reader is
deciding whether to trust the method.

## Working here

- Content that is coming from the lab is marked `TODO(port)`. Leave it empty and
  marked. Never invent placeholder criteria or corpus records — an empty slot
  cannot be cited by mistake; an invention can.
- Keep CI green. A project telling others to take measurement seriously does not
  ship a red build.
- Author: Idil Gozel <idilgozel@evaluatorintegrity.com>, Evaluator Integrity, London.
- Do not add co-author or AI-attribution trailers to commits.
