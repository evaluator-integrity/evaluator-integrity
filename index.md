---
layout: default
title: "Evaluator Integrity"
---

<!--
  Site index. The site publishes the criteria and the corpus behind them, and
  nothing else -- no product pages, no pricing, no roadmap, no signup. The
  reader arriving here is deciding whether to trust the method, and anything
  selling to them while they do that is evidence against it.
  See site/README.md.
-->

# Evaluator Integrity

Criteria for auditing the evaluators AI teams measure their own systems with.

An evaluator is an instrument. These criteria do not assess model quality; they
assess whether the instrument measuring model quality can be relied on. They are
drawn from published results rather than invented here, and the citation list is
doing the load-bearing work, not our authority.

## Read

- **[Criteria v0.1](criteria/v0.1/)** — four criteria, each externally cited,
  each with a stable anchor (`#C1`–`#C4`) for citing a single criterion.
  *Published 25 August 2026 and frozen. Corrections create a new version.*
- **[Configuration census](census/)** — 27 evaluator configurations shipped as
  framework defaults, scored against v0.1, with the evidence behind each
  verdict.
- **[Candidate criteria](criteria/candidates.html)** — requirements that are
  plausible but not yet supported by a result precise enough to fix a pass
  condition. Nothing on that page is a criterion, and nothing on it should be
  cited as a requirement.

## Check

The point of publishing the corpus is that you do not have to take a score on
trust. Every record names the artifact it was scored from, pinned by package
digest rather than version string, and quotes the text the verdict rests on. The
criteria's own figures are held to the same standard: every quantity C1–C4 state
is recorded against the published result it came from, with the locator inside
it, and re-read out of the source rather than asserted.

The [repository](https://github.com/idilgozel/evaluator-integrity) carries the
corpus, the scorer, and the checks that re-verify both.

## Cite

Cite the versioned path, which is frozen and always resolves:

    criteria/v0.1/index.md#C2

Not `criteria/latest` — that path moves by design and is for browsing.

## Criticism

If a criterion is wrong, unmeasurable, or missing, that is the most useful thing
you can say. Criteria for non-verifiable evaluation — summarisation quality,
helpfulness, tone — are the largest gap in v0.1 and the most useful thing a
collaborator could bring.

---

Criteria and prose are CC BY 4.0; the code is Apache-2.0. Written by
Idil Gozel, University College London.
